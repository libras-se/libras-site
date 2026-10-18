/**
 * LibrasLead — captação de leads do site para o CRM interno (api.libras.se).
 *
 * Uso: LibrasLead.send({ formId, formType, contact, consent, request })
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

	// First touch é registrado já no primeiro carregamento de página
	try {
		ensureFirstTouch();
	} catch (e) {
		/* ignore */
	}

	window.LibrasLead = { send: send };
})();
