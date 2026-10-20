/**
 * LP de soluções — comportamento dos blocos gerados por scripts/lp-build.mjs.
 *
 * - Vitrine "como fica na tela": camadas Libras / LSE / AD ligáveis, legenda e
 *   audiodescrição em ciclo, vídeo da janela só toca quando está na tela.
 * - Formulário "a gente escuta": vai para o CRM por LibrasLead.send (formType
 *   budget, POST /v1/crm/lead-capture). Com a api fora, o lead não se perde:
 *   a tela de sucesso oferece o WhatsApp já com o resumo do pedido.
 * - Reunião e orçamento vivem no HUET (rotas autenticadas do dashboard; quem não
 *   tem conta passa pelo login e volta para a mesma tela pelo callbackUrl).
 * - Dock fixo, barra de progresso, contadores, linha do passo a passo e eventos GA4.
 */
(function () {
	'use strict';

	var dataEl = document.getElementById('lp-data');
	var cfg = {};
	try {
		cfg = dataEl ? JSON.parse(dataEl.textContent) : {};
	} catch (e) {
		cfg = {};
	}
	var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	function track(name, params) {
		try {
			if (typeof window.gtag === 'function') {
				window.gtag('event', name, Object.assign({ lp: cfg.slug || location.pathname }, params || {}));
			}
		} catch (e) {
			/* medição é opcional */
		}
	}

	/* ── progresso de leitura ───────────────────────────────────────────── */
	var prog = document.querySelector('.lp-prog');
	var dock = document.querySelector('.lp-dock');
	var ouvir = document.getElementById('lp-ouvir');
	var foot = document.getElementById('foot');
	var steps = document.querySelector('.lp-steps');
	var ticking = false;

	function inView(el, margin) {
		if (!el) return false;
		var r = el.getBoundingClientRect();
		return r.top < innerHeight - (margin || 0) && r.bottom > 0;
	}

	function onScroll() {
		ticking = false;
		var h = document.documentElement.scrollHeight - innerHeight;
		if (prog) prog.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, scrollY / h) : 0) + ')';
		if (dock) {
			var show = scrollY > innerHeight * 0.7 && !inView(ouvir, 120) && !inView(foot, 0);
			dock.classList.toggle('on', show);
			document.documentElement.classList.toggle('lp-dock-on', show);
		}
		if (steps) {
			var r = steps.getBoundingClientRect();
			var p = Math.max(0, Math.min(1, (innerHeight * 0.75 - r.top) / r.height));
			steps.style.setProperty('--lp-p', p.toFixed(3));
			var items = steps.children;
			for (var i = 0; i < items.length; i++) {
				items[i].classList.toggle('lp-on', p >= i / Math.max(1, items.length - 1) - 0.02);
			}
		}
	}
	window.addEventListener(
		'scroll',
		function () {
			if (!ticking) {
				ticking = true;
				requestAnimationFrame(onScroll);
			}
		},
		{ passive: true },
	);
	onScroll();

	/* ── reveal + contadores + "em tela" ─────────────────────────────────── */
	function countUp(el) {
		var target = parseFloat(el.getAttribute('data-count'));
		var prefix = el.getAttribute('data-prefix') || '';
		var suffix = el.getAttribute('data-suffix') || '';
		if (isNaN(target) || reduce) {
			el.textContent = prefix + el.getAttribute('data-count') + suffix;
			return;
		}
		var start = null;
		var dur = 1400;
		function step(ts) {
			if (!start) start = ts;
			var t = Math.min(1, (ts - start) / dur);
			var eased = 1 - Math.pow(1 - t, 3);
			el.textContent = prefix + Math.round(target * eased).toLocaleString('pt-BR') + suffix;
			if (t < 1) requestAnimationFrame(step);
		}
		requestAnimationFrame(step);
	}

	if ('IntersectionObserver' in window) {
		var io = new IntersectionObserver(
			function (entries) {
				entries.forEach(function (e) {
					if (!e.isIntersecting) return;
					e.target.classList.add('lp-in', 'lp-in-view');
					if (e.target.hasAttribute('data-count')) countUp(e.target);
					io.unobserve(e.target);
				});
			},
			{ threshold: 0.15, rootMargin: '0px 0px -40px 0px' },
		);
		document.querySelectorAll('.lp-rv,[data-count],.lp-docw').forEach(function (el) {
			io.observe(el);
		});
	} else {
		document.querySelectorAll('.lp-rv,.lp-docw').forEach(function (el) {
			el.classList.add('lp-in', 'lp-in-view');
		});
		document.querySelectorAll('[data-count]').forEach(countUp);
	}

	/* ── vitrine ─────────────────────────────────────────────────────────── */
	var screen = document.querySelector('.lp-screen');
	if (screen) {
		var toggles = document.querySelectorAll('.lp-tg');
		var userTouched = false;
		var layers = ['libras', 'lse', 'ad'];

		function setLayer(name, on) {
			screen.setAttribute('data-' + name, on ? 'on' : 'off');
			var btn = document.querySelector('.lp-tg[data-layer="' + name + '"]');
			if (btn) btn.setAttribute('aria-pressed', on ? 'true' : 'false');
		}

		toggles.forEach(function (btn) {
			btn.addEventListener('click', function () {
				userTouched = true;
				var name = btn.getAttribute('data-layer');
				var on = btn.getAttribute('aria-pressed') !== 'true';
				setLayer(name, on);
				track('lp_toggle_layer', { layer: name, on: on });
			});
		});

		// Demonstração automática: liga as camadas uma a uma até alguém mexer.
		if (!reduce) {
			layers.forEach(function (l) {
				if (document.querySelector('.lp-tg[data-layer="' + l + '"]')) setLayer(l, false);
			});
			var demoIdx = 0;
			var demoStarted = false;
			var demo = function () {
				if (userTouched) return;
				if (demoIdx < layers.length) {
					var name = layers[demoIdx++];
					if (document.querySelector('.lp-tg[data-layer="' + name + '"]')) setLayer(name, true);
					setTimeout(demo, 1300);
				}
			};
			if ('IntersectionObserver' in window) {
				new IntersectionObserver(
					function (entries, obs) {
						if (entries[0].isIntersecting && !demoStarted) {
							demoStarted = true;
							setTimeout(demo, 500);
							obs.disconnect();
						}
					},
					{ threshold: 0.45 },
				).observe(screen);
			} else {
				layers.forEach(function (l) {
					setLayer(l, true);
				});
			}
		}

		function cycle(el, lines, ms) {
			if (!el || !lines || !lines.length) return;
			var i = 0;
			el.innerHTML = lines[0];
			if (reduce || lines.length < 2) return;
			setInterval(function () {
				if (document.hidden || !inView(screen)) return;
				i = (i + 1) % lines.length;
				el.style.opacity = '0';
				setTimeout(function () {
					el.innerHTML = lines[i];
					el.style.opacity = '1';
				}, 260);
			}, ms);
		}
		var capEl = screen.querySelector('.lp-cap span');
		var adEl = screen.querySelector('.lp-ad-t');
		if (capEl) capEl.style.transition = 'opacity .25s ease';
		if (adEl) adEl.style.transition = 'opacity .25s ease';
		cycle(capEl, cfg.lse, 3400);
		cycle(adEl, cfg.ad, 4600);

		var tc = screen.querySelector('.lp-ctrl-tc');
		if (tc && !reduce) {
			var secs = 0;
			setInterval(function () {
				if (document.hidden) return;
				secs = (secs + 1) % 20;
				tc.textContent = '00:' + (secs < 10 ? '0' : '') + secs + ' / ' + (cfg.duracao || '01:42:10');
			}, 1000);
		}

		// Vídeo da janela: carrega e toca só quando a vitrine aparece.
		var vid = screen.querySelector('.lp-win video');
		if (vid && 'IntersectionObserver' in window) {
			new IntersectionObserver(
				function (entries) {
					var e = entries[0];
					if (e.isIntersecting) {
						if (!vid.getAttribute('src') && vid.dataset.src) vid.setAttribute('src', vid.dataset.src);
						if (!reduce) vid.play().catch(function () {});
					} else {
						vid.pause();
					}
				},
				{ threshold: 0.2 },
			).observe(screen);
		}

		// Inclinação leve acompanhando o ponteiro (só desktop).
		var stage = document.querySelector('.lp-stage');
		if (stage && !reduce && window.matchMedia('(hover: hover) and (min-width: 1025px)').matches) {
			stage.addEventListener('mousemove', function (ev) {
				var r = stage.getBoundingClientRect();
				var x = (ev.clientX - r.left) / r.width - 0.5;
				var y = (ev.clientY - r.top) / r.height - 0.5;
				screen.style.transform = 'perspective(1400px) rotateY(' + (x * 8).toFixed(2) + 'deg) rotateX(' + (-y * 6).toFixed(2) + 'deg)';
			});
			stage.addEventListener('mouseleave', function () {
				screen.style.transform = '';
			});
		}
	}

	/* ── cliques de conversão (GA4) ──────────────────────────────────────── */
	document.addEventListener('click', function (e) {
		var a = e.target && e.target.closest ? e.target.closest('[data-lp-cta]') : null;
		if (a) track('lp_cta_click', { cta: a.getAttribute('data-lp-cta') });
	});

	/* ── formulário "a gente escuta" ─────────────────────────────────────── */
	var box = document.querySelector('.lp-form');
	var form = box ? box.querySelector('form') : null;
	if (!form) return;

	var errEl = form.querySelector('.lp-err');
	var sendBtn = form.querySelector('.lp-send');
	var okBox = box.querySelector('.lp-ok');
	var started = false;

	form.addEventListener('input', function () {
		if (!started) {
			started = true;
			track('lp_form_start');
		}
	});

	function val(name) {
		var el = form.elements[name];
		if (!el) return '';
		if (el.length && !el.tagName) {
			for (var i = 0; i < el.length; i++) if (el[i].checked) return el[i].value;
			return '';
		}
		if (el.type === 'checkbox') return el.checked;
		return String(el.value || '').trim();
	}

	function digits(s) {
		return String(s || '').replace(/\D/g, '');
	}

	function mark(name, bad) {
		var el = form.elements[name];
		if (el && el.setAttribute) el.setAttribute('aria-invalid', bad ? 'true' : 'false');
	}

	function waUrl(text) {
		return 'https://wa.me/5548996367511?text=' + encodeURIComponent(text);
	}

	function summary(d) {
		var parts = ['Olá! Vim pela página de ' + (cfg.label || 'soluções') + ' do site.'];
		if (d.name) parts.push('Sou ' + d.name + (d.company ? ', da ' + d.company : '') + '.');
		if (d.description) parts.push('Projeto: ' + d.description.replace(/[.!?]*$/, '.'));
		if (d.duration) parts.push('Minutagem: ' + d.duration + '.');
		if (d.deadline) parts.push('Prazo: ' + d.deadline + '.');
		return parts.join(' ');
	}

	form.addEventListener('submit', function (e) {
		e.preventDefault();
		if (errEl) errEl.classList.remove('on');

		var d = {
			name: val('nome'),
			whatsapp: val('whatsapp'),
			email: val('email'),
			company: val('empresa'),
			description: val('demanda'),
			deadline: val('prazo'),
			duration: val('minutagem'),
			pref: val('preferencia') || 'whatsapp',
			privacy: val('privacidade'),
			mkt: val('novidades'),
		};

		var phoneOk = digits(d.whatsapp).length >= 10;
		var emailOk = !d.email || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email);
		mark('nome', !d.name);
		mark('whatsapp', !phoneOk);
		mark('email', !emailOk);
		mark('demanda', !d.description);
		if (!d.name || !phoneOk || !emailOk || !d.description || !d.privacy) {
			if (errEl) {
				errEl.textContent =
					d.name && phoneOk && emailOk && d.description
						? 'Para seguirmos, aceite a política de privacidade.'
						: 'Confira nome, WhatsApp com DDD e uma linha sobre o projeto.';
				errEl.classList.add('on');
			}
			var firstBad = form.querySelector('[aria-invalid="true"]');
			if (firstBad) firstBad.focus();
			return;
		}

		sendBtn.disabled = true;
		sendBtn.textContent = 'Enviando…';

		var payload = {
			formId: 'lp-' + (cfg.slug || 'solucoes'),
			formType: 'budget',
			website: val('website') || undefined,
			contact: {
				name: d.name,
				whatsapp: d.whatsapp,
				phone: d.whatsapp,
				email: d.email || undefined,
				company: d.company || undefined,
			},
			consent: {
				privacyPolicyAccepted: true,
				marketingWhatsapp: Boolean(d.mkt),
				marketingEmail: Boolean(d.mkt && d.email),
			},
			request: {
				service: cfg.service || 'outro',
				serviceCategory: cfg.category || undefined,
				projectType: cfg.label || undefined,
				description: d.description,
				deadline: d.deadline || undefined,
				estimatedDuration: d.duration || undefined,
				additionalData: { origem: 'lp-solucoes', pagina: cfg.slug, canalPreferido: d.pref },
			},
		};

		var sender =
			window.LibrasLead && typeof window.LibrasLead.send === 'function'
				? window.LibrasLead.send(payload)
				: Promise.resolve(false);

		sender.then(function (accepted) {
			track('lp_form_submit', { accepted: Boolean(accepted), preferencia: d.pref });
			if (typeof window.gtag === 'function') {
				try {
					window.gtag('event', 'generate_lead', { form: 'lp-' + cfg.slug, value: 1 });
				} catch (err) {
					/* ignore */
				}
			}
			var wa = okBox.querySelector('[data-lp-ok="wa"]');
			var meet = okBox.querySelector('[data-lp-ok="meet"]');
			if (wa) wa.setAttribute('href', waUrl(summary(d)));
			var msg = okBox.querySelector('[data-lp-ok="msg"]');
			if (msg) {
				msg.textContent = accepted
					? d.pref === 'reuniao'
						? 'Recebemos o seu pedido. Escolha agora o melhor horário para conversarmos por vídeo. Leva menos de um minuto.'
						: 'Recebemos o seu pedido e vamos falar com você em horário comercial. Se quiser adiantar, é só chamar.'
					: 'Não conseguimos registrar o pedido agora. Mande pelo WhatsApp: a mensagem já vai pronta com o resumo.';
			}
			// Quem pediu reunião vê o agendamento primeiro; quem pediu WhatsApp, o WhatsApp.
			if (meet && wa && d.pref === 'reuniao' && accepted) meet.parentNode.insertBefore(meet, wa);
			box.classList.add('sent');
			okBox.classList.add('on');
			okBox.setAttribute('tabindex', '-1');
			okBox.focus();
		});
	});
})();
