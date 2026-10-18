/**
 * LibrasLead — captação de leads do site para o CRM interno (api.libras.se).
 *
 * Uso: LibrasLead.send({ formId, formType, contact, consent, request })
 *      LibrasLead.openWhatsApp(urlDoWaMe)  // abre o wa.me por script, com "(ref …)"
 *      Links <a href="https://wa.me/…"> ganham o "(ref …)" sozinhos (ver abaixo).
 *
 * - Aditivo e não-bloqueante: nunca lança, nunca atrasa o fluxo atual
 *   (n8n / WhatsApp continuam funcionando mesmo com a API fora do ar).
 * - Idempotente: a chave vale para o mesmo conteúdo do formulário (sessionStorage
 *   guarda só o hash), é reutilizada em retry/refresh e trocada se os dados mudam;
 *   só é limpa quando a API confirma o recebimento (`data.received`).
 * - First touch: UTMs/gclid/fbclid/landing/referrer gravados uma única vez
 *   em localStorage; visitorId anônimo preparado para a fase de analytics.
 */
(function () {
	'use strict';

	var API_BASE = 'https://api.libras.se';
	var ENDPOINT = API_BASE + '/v1/crm/lead-capture';
	var TIMEOUT_MS = 4000;
	var CONSENT_TEXT_VERSION = 'site-v1-2026-07';

	var FT_KEY = 'librasse_ft';
	var VISITOR_KEY = 'librasse_vid';
	var SESSION_KEY = 'librasse_sid';
	var IDEM_PREFIX = 'librasse_idem_';
	var pendingSubmissions = Object.create(null);

	function safeStorage(getStorage) {
		try {
			var s = getStorage();
			var probe = '__librasse_probe__';
			s.setItem(probe, '1');
			s.removeItem(probe);
			return s;
		} catch (e) {
			return null;
		}
	}

	var local = safeStorage(function () {
		return window.localStorage;
	});
	var session = safeStorage(function () {
		return window.sessionStorage;
	});

	function uuid() {
		if (window.crypto && typeof window.crypto.randomUUID === 'function') return window.crypto.randomUUID();
		return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
			var r = (Math.random() * 16) | 0;
			return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
		});
	}

	function readJson(storage, key) {
		if (!storage) return null;
		try {
			var raw = storage.getItem(key);
			return raw ? JSON.parse(raw) : null;
		} catch (e) {
			return null;
		}
	}

	function writeJson(storage, key, value) {
		if (!storage) return;
		try {
			storage.setItem(key, JSON.stringify(value));
		} catch (e) {
			/* storage cheio/bloqueado: segue sem persistir */
		}
	}

	function currentParams() {
		var params = {};
		try {
			var search = new URLSearchParams(window.location.search);
			['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'gclid', 'fbclid'].forEach(
				function (key) {
					var value = search.get(key);
					if (value) params[key] = value.slice(0, 200);
				},
			);
		} catch (e) {
			/* URLSearchParams indisponível: sem atribuição por query */
		}
		return params;
	}

	/** Grava o first touch uma única vez (nunca sobrescreve). */
	function ensureFirstTouch() {
		var existing = readJson(local, FT_KEY);
		if (existing) return existing;
		var params = currentParams();
		var ft = {
			utmSource: params.utm_source || null,
			utmMedium: params.utm_medium || null,
			utmCampaign: params.utm_campaign || null,
			utmContent: params.utm_content || null,
			utmTerm: params.utm_term || null,
			gclid: params.gclid || null,
			fbclid: params.fbclid || null,
			landingPage: window.location.href.slice(0, 500),
			referrer: (document.referrer || '').slice(0, 500) || null,
			at: new Date().toISOString(),
		};
		writeJson(local, FT_KEY, ft);
		return ft;
	}

	function visitorId() {
		if (!local) return null;
		var id = local.getItem(VISITOR_KEY);
		if (!id) {
			id = uuid();
			try {
				local.setItem(VISITOR_KEY, id);
			} catch (e) {
				return null;
			}
		}
		return id;
	}

	function sessionId() {
		if (!session) return null;
		var id = session.getItem(SESSION_KEY);
		if (!id) {
			id = uuid();
			try {
				session.setItem(SESSION_KEY, id);
			} catch (e) {
				return null;
			}
		}
		return id;
	}

	/** Uma chave por tentativa de formulário: retry/refresh reusam; sucesso limpa. */
	async function idempotencyKey(formId, payload) {
		var key = IDEM_PREFIX + formId;
		var consent = payload.consent || {};
		var fingerprint = JSON.stringify({ formType: payload.formType, contact: payload.contact, request: payload.request,
			privacy: consent.privacyPolicyAccepted, marketingEmail: consent.marketingEmail, marketingWhatsapp: consent.marketingWhatsapp });
		// No sessionStorage vai só o hash do conteúdo, nunca os dados de contato.
		var canHash = window.crypto && window.crypto.subtle;
		if (canHash) {
			var digest = await window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(fingerprint));
			fingerprint = Array.from(new Uint8Array(digest)).map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
		}
		var value = (canHash ? readJson(session, key) : null) || pendingSubmissions[key];
		if (!value || value.fingerprint !== fingerprint) {
			value = { id: uuid(), fingerprint: fingerprint };
			pendingSubmissions[key] = value;
			if (canHash) writeJson(session, key, value);
		}
		return value.id;
	}

	function clearIdempotencyKey(formId, id) {
		var key = IDEM_PREFIX + formId;
		var current = readJson(session, key) || pendingSubmissions[key];
		if (!current || current.id !== id) return;
		delete pendingSubmissions[key];
		if (session) {
			try {
				session.removeItem(key);
			} catch (e) {
				/* ignore */
			}
		}
	}

	/**
	 * Envia a captação para o CRM. Nunca lança; retorna uma Promise<boolean>
	 * (true = aceito pela API) que os formulários podem ignorar com segurança.
	 */
	async function send(payload) {
		try {
			var formId = payload.formId || payload.formType || 'form';
			var ft = ensureFirstTouch();
			var idem = await idempotencyKey(formId, payload);

			var consent = payload.consent || {};
			if (consent.consentTextVersion === undefined) consent.consentTextVersion = CONSENT_TEXT_VERSION;
			if (consent.capturedAt === undefined) consent.capturedAt = new Date().toISOString();

			var body = {
				formId: formId,
				formType: payload.formType,
				idempotencyKey: idem,
				pageUrl: window.location.href.slice(0, 500),
				pageTitle: (document.title || '').slice(0, 300),
				referrer: (document.referrer || '').slice(0, 500),
				website: payload.website || undefined, // honeypot pass-through
				contact: payload.contact || {},
				consent: consent,
				request: payload.request || undefined,
				attribution: {
					utmSource: ft.utmSource || undefined,
					utmMedium: ft.utmMedium || undefined,
					utmCampaign: ft.utmCampaign || undefined,
					utmContent: ft.utmContent || undefined,
					utmTerm: ft.utmTerm || undefined,
					gclid: ft.gclid || undefined,
					fbclid: ft.fbclid || undefined,
					landingPage: ft.landingPage || undefined,
					sessionId: sessionId() || undefined,
					anonymousVisitorId: visitorId() || undefined,
				},
			};

			var controller = typeof AbortController === 'function' ? new AbortController() : null;
			var timer = controller
				? window.setTimeout(function () {
						controller.abort();
					}, TIMEOUT_MS)
				: null;

			return window
				.fetch(ENDPOINT, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(body),
					signal: controller ? controller.signal : undefined,
					keepalive: true,
				})
				.then(async function (res) {
					if (timer) window.clearTimeout(timer);
					if (!res.ok) return false;
					var result = await res.json();
					var accepted = result.success === true && result.data && result.data.received === true;
					if (accepted) clearIdempotencyKey(formId, idem);
					return Boolean(accepted);
				})
				.catch(function () {
					if (timer) window.clearTimeout(timer);
					return false;
				});
		} catch (e) {
			return Promise.resolve(false);
		}
	}

	/* ── Clique no WhatsApp → código de origem "(ref XXXXXX)" ──────────────────
	 *
	 * A api devolve um código curto para o clique; o site põe " (ref CÓDIGO)" no fim
	 * da mensagem pronta do wa.me e, quando a mensagem chega, a api liga a página e
	 * as UTMs ao contato. Regras:
	 * - clique comum: espera o código no máximo TOUCH_TIMEOUT_MS; sem código (api
	 *   fora, lenta ou com erro) abre o link original, igual a antes;
	 * - target="_blank": a aba nova é aberta já no clique (about:blank) e navega
	 *   quando o código chega, para o bloqueador de pop-up não barrar;
	 * - Ctrl/Cmd/Shift/Alt, clique do meio ou pop-up bloqueado: o navegador segue
	 *   sozinho e o clique é só registrado (sendBeacon), sem código no texto.
	 */
	var TOUCH_ENDPOINT = API_BASE + '/v1/crm/web-touch';
	var TOUCH_TIMEOUT_MS = 1200;
	var WA_SELECTOR = 'a[href*="wa.me/"], a[href*="api.whatsapp.com/send"]';
	var REF_RE = /\(ref\s+[A-Z0-9]{6}\)/i;
	var CODE_RE = /^[A-Z0-9]{6}$/i;

	function cut(value, max) {
		return value ? String(value).slice(0, max) : undefined;
	}

	function touchBody() {
		var ft = {};
		try {
			ft = ensureFirstTouch() || {};
		} catch (e) {
			/* sem first touch: segue só com a página atual */
		}
		return JSON.stringify({
			kind: 'whatsapp_click',
			visitorId: visitorId() || undefined,
			pageUrl: cut(window.location.href, 1000),
			pageTitle: cut(document.title, 500),
			referrer: cut(document.referrer, 1000),
			landingPage: cut(ft.landingPage, 1000),
			utmSource: cut(ft.utmSource, 200),
			utmMedium: cut(ft.utmMedium, 200),
			utmCampaign: cut(ft.utmCampaign, 200),
			utmContent: cut(ft.utmContent, 200),
			utmTerm: cut(ft.utmTerm, 200),
			gclid: cut(ft.gclid, 300),
			fbclid: cut(ft.fbclid, 300),
		});
	}

	/** Registra o clique sem esperar resposta (texto puro: sem preflight do CORS). */
	function beaconTouch() {
		try {
			var body = touchBody();
			if (navigator.sendBeacon && navigator.sendBeacon(TOUCH_ENDPOINT, body)) return;
			window
				.fetch(TOUCH_ENDPOINT, {
					method: 'POST',
					headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
					body: body,
					credentials: 'omit',
					keepalive: true,
				})
				.catch(function () {});
		} catch (e) {
			/* registro é opcional */
		}
	}

	/** Promise<string|null> que sempre resolve, em até TOUCH_TIMEOUT_MS. */
	function requestCode() {
		return new Promise(function (resolve) {
			var done = false;
			var controller = typeof AbortController === 'function' ? new AbortController() : null;
			var timer = null;
			function finish(code) {
				if (done) return;
				done = true;
				if (timer) window.clearTimeout(timer);
				resolve(code);
			}
			timer = window.setTimeout(function () {
				finish(null);
				if (controller) controller.abort();
			}, TOUCH_TIMEOUT_MS);
			try {
				window
					.fetch(TOUCH_ENDPOINT, {
						method: 'POST',
						headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
						body: touchBody(),
						credentials: 'omit',
						signal: controller ? controller.signal : undefined,
					})
					.then(function (res) {
						return res.ok ? res.json() : null;
					})
					.then(function (json) {
						var code = json && json.success === true && json.data ? json.data.code : null;
						finish(typeof code === 'string' && CODE_RE.test(code) ? code.toUpperCase() : null);
					})
					.catch(function () {
						finish(null);
					});
			} catch (e) {
				finish(null);
			}
		});
	}

	/**
	 * Acrescenta " (ref CÓDIGO)" ao fim do parâmetro `text`, sem reescrever o resto
	 * da URL: o texto atual continua com o mesmo encoding ("+" ou "%20").
	 */
	function withRef(href, code) {
		if (!code || !CODE_RE.test(code)) return href;
		try {
			var hashAt = href.indexOf('#');
			var hash = hashAt >= 0 ? href.slice(hashAt) : '';
			var base = hashAt >= 0 ? href.slice(0, hashAt) : href;
			var queryAt = base.indexOf('?');
			var path = queryAt >= 0 ? base.slice(0, queryAt) : base;
			var parts = queryAt >= 0 && base.length > queryAt + 1 ? base.slice(queryAt + 1).split('&') : [];
			var found = false;
			for (var i = 0; i < parts.length; i++) {
				var eq = parts[i].indexOf('=');
				var name = eq >= 0 ? parts[i].slice(0, eq) : parts[i];
				if (name !== 'text') continue;
				found = true;
				var raw = eq >= 0 ? parts[i].slice(eq + 1) : '';
				var decoded = raw;
				try {
					decoded = decodeURIComponent(raw.replace(/\+/g, ' '));
				} catch (e) {
					/* texto mal codificado: compara cru */
				}
				if (REF_RE.test(decoded)) return href;
				var sp = raw.indexOf('+') >= 0 && raw.indexOf('%20') < 0 ? '+' : '%20';
				raw = raw.replace(/(?:\+|%20)+$/i, '') || encodeURIComponent('Olá!');
				parts[i] = 'text=' + raw + sp + '(ref' + sp + code + ')';
				break;
			}
			if (!found) parts.push('text=' + encodeURIComponent('Olá!') + '%20(ref%20' + code + ')');
			return path + '?' + parts.join('&') + hash;
		} catch (e) {
			return href;
		}
	}

	function opensNewWindow(target) {
		return !!target && !/^_(self|top|parent)$/i.test(target);
	}

	/** Abre a janela/aba já dentro do gesto do usuário; null se o navegador barrar. */
	function openBlank(target) {
		var win = null;
		try {
			win = window.open('about:blank', target || '_blank');
		} catch (e) {
			return null;
		}
		if (!win) return null;
		try {
			win.opener = null;
			win.document.title = 'Abrindo o WhatsApp…';
		} catch (e) {
			/* janela já em outra origem: só navega */
		}
		return win;
	}

	/** Busca o código e leva ao WhatsApp; sem código, vai para o link original. */
	function resolveAndGo(url, win) {
		function go(dest) {
			try {
				if (win) win.location.replace(dest);
				else window.location.assign(dest);
			} catch (e) {
				try {
					if (win) win.location.href = url;
					else window.location.href = url;
				} catch (e2) {
					/* sem saída */
				}
			}
		}
		requestCode().then(function (code) {
			go(withRef(url, code));
		});
	}

	function linkTarget(el) {
		var target = el.getAttribute('target');
		if (target) return target;
		var baseEl = document.querySelector('base[target]');
		return baseEl ? baseEl.getAttribute('target') : '';
	}

	function closestWhatsApp(e) {
		var t = e.target;
		if (t && t.nodeType !== 1) t = t.parentElement;
		return t && t.closest ? t.closest(WA_SELECTOR) : null;
	}

	function onClick(e) {
		try {
			if (e.defaultPrevented) return;
			var el = closestWhatsApp(e);
			if (!el || !el.href) return;
			if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || el.hasAttribute('download')) {
				beaconTouch();
				return;
			}
			var url = el.href;
			var target = linkTarget(el);
			var win = null;
			if (opensNewWindow(target)) {
				win = openBlank(target);
				if (!win) {
					beaconTouch(); // pop-up barrado: o clique nativo segue, sem código
					return;
				}
			}
			e.preventDefault();
			resolveAndGo(url, win);
		} catch (err) {
			/* nunca quebrar o clique: sem preventDefault o navegador segue */
		}
	}

	function onAuxClick(e) {
		try {
			if (e.button === 1 && closestWhatsApp(e)) beaconTouch();
		} catch (err) {
			/* ignore */
		}
	}

	/**
	 * Para quem abre o WhatsApp por script (ex.: formulário "reportar" dos sinais).
	 * Chame dentro do submit/clique. Retorna true quando o código vai no texto e
	 * false quando o navegador barrou a aba (aí abre o link original, sem código).
	 */
	function openWhatsApp(url) {
		var win = null;
		try {
			win = openBlank('_blank');
			if (win) {
				resolveAndGo(url, win);
				return true;
			}
			beaconTouch();
		} catch (e) {
			if (win) return true;
		}
		try {
			window.open(url, '_blank', 'noopener,noreferrer');
		} catch (e2) {
			/* sem saída */
		}
		return false;
	}

	try {
		document.addEventListener('click', onClick, false);
		document.addEventListener('auxclick', onAuxClick, false);
	} catch (e) {
		/* ignore */
	}

	// First touch é registrado já no primeiro carregamento de página
	try {
		ensureFirstTouch();
	} catch (e) {
		/* ignore */
	}

	window.LibrasLead = { send: send, openWhatsApp: openWhatsApp, whatsappWithRef: withRef };
})();
