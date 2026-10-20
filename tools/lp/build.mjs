#!/usr/bin/env node
// Injeta os blocos de LP nas 11 páginas de solução e na /solucoes/.
//
//   node tools/lp/build.mjs
//
// Cada bloco fica entre <!-- lp:nome --> e <!-- /lp:nome -->, então rodar de
// novo substitui em vez de duplicar. O HTML é estático (bom para SEO); o
// comportamento está em /assets/js/lp.js e o visual em /assets/css/lp.css.

import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PAGES } from './pages.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const TODAY = new Date().toISOString().slice(0, 10);
const HUET = 'https://huet.libras.se';
const WA = '5548996367511';
const ASSET_V = '20261020b';

/* ── ícones (traço, currentColor) ─────────────────────────────────────── */
const P = {
	hand: '<path d="M18 11V6a2 2 0 0 0-4 0v5M14 10V4a2 2 0 0 0-4 0v6M10 10.5V6a2 2 0 0 0-4 0v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-6-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>',
	captions: '<rect width="18" height="14" x="3" y="5" rx="2"/><path d="M7 15h4M15 15h2M7 11h2M13 11h4"/>',
	audio: '<path d="M2 10v3M6 6v11M10 3v18M14 8v7M18 5v13M22 10v3"/>',
	calendar: '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
	file: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M10 9H8M16 13H8M16 17H8"/>',
	arrow: '<path d="M5 12h14M12 5l7 7-7 7"/>',
	check: '<path d="M20 6 9 17l-5-5"/>',
	user: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="m16 11 2 2 4-4"/>',
	film: '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 3v18M3 7.5h4M3 12h18M3 16.5h4M17 3v18M17 7.5h4M17 16.5h4"/>',
	award: '<circle cx="12" cy="8" r="6"/><path d="M15.48 12.89 17 22l-5-3-5 3 1.52-9.11"/>',
	heart: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
	layers: '<path d="m12 2 10 5-10 5L2 7l10-5Z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
	radio: '<circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/>',
	map: '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
	tv: '<rect width="20" height="15" x="2" y="7" rx="2"/><path d="m17 2-5 5-5-5"/>',
	zap: '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
	shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1Z"/><path d="m9 12 2 2 4-4"/>',
	grid: '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/>',
	chat: '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M8 12h.01M12 12h.01M16 12h.01"/>',
	book: '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
};
const ic = (name) =>
	`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="fill:none" aria-hidden="true" focusable="false">${P[name]}</svg>`;
const WA_ICON =
	'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>';

const CHIPS = {
	human: ['user', 'Intérprete humano, não é IA'],
	cinema: ['film', 'Padrão TV e cinema'],
	edital: ['file', 'Orçamento prévio para edital'],
	festival: ['award', 'Pronto para festival'],
	cultura: ['heart', 'Contexto cultural preservado'],
	lote: ['layers', 'Entrega por lote'],
	aovivo: ['radio', 'Intérprete ao vivo'],
	brasil: ['map', 'Rede em todo o Brasil'],
	streaming: ['tv', 'Pronto para streaming'],
	rapido: ['zap', 'Entrega em até 1 hora'],
	tv: ['tv', 'TV e redes sociais'],
	lbi: ['shield', 'Alinhado à LBI'],
	volume: ['layers', 'Pacotes por volume'],
	formatos: ['grid', 'TV, reels e stories'],
	glossario: ['book', 'Glossário por disciplina'],
};

const LAYER_TXT = {
	libras: ['hand', 'Janela de Libras', 'Intérpretes reais da rede LIBRAS.SE, com recorte limpo e posição que não cobre a cena.'],
	lse: ['captions', 'LSE, legenda para surdos', 'Falas com identificação de quem fala, sons e efeitos entre colchetes.'],
	ad: ['audio', 'Audiodescrição', 'Narração do que se vê, nos intervalos das falas, para pessoas cegas ou com baixa visão.'],
};

/* ── utilitários ──────────────────────────────────────────────────────── */
const esc = (s) =>
	String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const plain = (html) => String(html).replace(/<[^>]+>/g, '');

function huetUrl(p, path, cta, extra = {}) {
	const q = new URLSearchParams({
		...extra,
		utm_source: 'site',
		utm_medium: 'lp',
		utm_campaign: p.slug,
		utm_content: cta,
	});
	return `${HUET}${path}?${q.toString()}`;
}
const quoteUrl = (p, cta) =>
	p.quotePath ? huetUrl(p, p.quotePath, cta) : huetUrl(p, '/dashboard/requests/quote', cta, { service: p.quote });
/** Agendamento no próprio site (/agendar), sem login: horários reais da agenda comercial. */
const meetUrl = (p, cta) => {
	const q = new URLSearchParams({
		topic: p.ouvirTopic,
		service: p.quote,
		utm_source: 'site',
		utm_medium: 'lp',
		utm_campaign: p.slug,
		utm_content: cta,
	});
	return `/agendar/?${q.toString()}`;
};
const waUrl = (p) =>
	`https://wa.me/${WA}?text=${encodeURIComponent(`Olá! Estava na página de ${p.label} do site da LIBRAS.SE e quero conversar sobre o meu projeto.`)}`;

function picture(name, alt, { sizes = '(max-width: 768px) 100vw, 640px', eager = false, small = false } = {}) {
	const base = `/assets/img/lp/${name}`;
	const set = (ext) => (small ? `${base}-640.${ext}` : `${base}-640.${ext} 640w, ${base}.${ext} 1280w`);
	const w = small ? 640 : 1280;
	const h = Math.round((w * 2) / 3);
	return `<picture><source type="image/avif" srcset="${set('avif')}" sizes="${sizes}"><source type="image/webp" srcset="${set('webp')}" sizes="${sizes}"><img src="${small ? `${base}-640.webp` : `${base}.webp`}" alt="${esc(alt)}" width="${w}" height="${h}" loading="${eager ? 'eager' : 'lazy'}" decoding="async"></picture>`;
}

function faqFor(p) {
	const v = p.valores;
	const quoteWhere = p.quotePath
		? 'em Solicitações, Evento ao vivo, você informa a data, o horário e a duração e recebe na hora uma estimativa em PDF'
		: 'em Solicitações, Orçamento, você informa o serviço, a minutagem e o prazo e recebe na hora um orçamento prévio em PDF';
	return [
		{
			q: 'Os valores são negociáveis?',
			a: `Sim. Os valores desta página são referência para você planejar. Volume, recorrência, prazo, pacotes por lote e o orçamento aprovado no edital entram na conversa, e montamos uma proposta que caiba no seu projeto de ${p.label}. Fale com a gente pelo WhatsApp ou agende uma conversa.`,
		},
		{
			q: 'Vocês fornecem orçamento para inscrição em edital?',
			a: `Sim, de forma automatizada. No HUET (huet.libras.se), ${quoteWhere}, ${v.uso}. Se o projeto for aprovado, ajustamos o escopo final com você antes de começar.`,
		},
		{
			q: 'Posso conversar com a equipe antes de fechar?',
			a: 'Pode, e é o que recomendamos. Escolha um horário livre na nossa agenda, aqui mesmo no site, para uma conversa por vídeo, ou chame no WhatsApp. Antes de propor qualquer coisa, queremos entender o seu cenário: prazo, minutagem, destino da obra e o que o edital ou o cliente exige.',
		},
	];
}

/* ── blocos ───────────────────────────────────────────────────────────── */
function blockTela(p) {
	const layers = p.layers || ['libras', 'lse', 'ad'];
	const t = p.tela;
	const lseTxt = t.lseLabel ? ['captions', ...t.lseLabel] : LAYER_TXT.lse;
	const toggles = layers
		.map((l) => {
			const [icon, title, desc] = l === 'lse' ? lseTxt : LAYER_TXT[l];
			return `<button type="button" class="lp-tg" data-layer="${l}" aria-pressed="true"><span class="lp-tg-ic">${ic(icon)}</span><span><b>${title}</b><span>${desc}</span></span><span class="lp-tg-sw" aria-hidden="true"></span></button>`;
		})
		.join('\n          ');
	const chips = t.chips
		.map((c, i) => `<span class="lp-chip c${i + 1}" aria-hidden="true">${ic(CHIPS[c][0])}${CHIPS[c][1]}</span>`)
		.join('\n          ');
	const hasAd = layers.includes('ad');
	return `<section id="lp-tela" class="lp-sec" aria-labelledby="lp-tela-h">
  <span class="lp-orb o1" aria-hidden="true"></span>
  <div class="w">
    <div class="lp-tela-g">
      <div class="lp-tela-txt lp-rv lp-l">
        <span class="lp-lbl">Como fica na tela</span>
        <h2 class="lp-h2" id="lp-tela-h">${t.h2}</h2>
        <p class="lp-sub">${t.sub}</p>
        <div class="lp-toggles" role="group" aria-label="Recursos de acessibilidade na demonstração">
          ${toggles}
        </div>
        <p class="lp-tela-note">Cena ilustrativa criada para esta demonstração. A janela mostra uma intérprete real da rede LIBRAS.SE.</p>
      </div>
      <div class="lp-stage lp-rv lp-r">
        <div class="lp-screen" data-libras="on" data-lse="on" data-ad="${hasAd ? 'on' : 'off'}">
          <div class="lp-screen-bar" aria-hidden="true"><i></i><i></i><i></i><span>huet.libras.se · prévia da entrega</span><em>${t.duracao === 'AO VIVO' ? 'Ao vivo' : 'Acessível'}</em></div>
          <div class="lp-frame">
            ${picture(p.img, t.alt, { sizes: '(max-width: 1024px) 100vw, 680px' })}
            ${hasAd ? '<div class="lp-ad" aria-hidden="true"><span class="lp-ad-ic">AD</span><span class="lp-ad-w"><b></b><b></b><b></b><b></b><b></b></span><span class="lp-ad-t"></span></div>' : ''}
            <div class="lp-cap" aria-hidden="true"><span></span></div>
            <div class="lp-win"><video data-src="/assets/videos/lp/janela-${p.janela}.mp4" poster="/assets/videos/lp/janela.webp" muted loop playsinline preload="none" aria-label="Intérprete de Libras sinalizando"></video><span class="lp-win-tag">Libras</span></div>
          </div>
          <div class="lp-ctrl" aria-hidden="true"><span class="lp-ctrl-pl"></span><span class="lp-ctrl-tr"><b></b></span><span class="lp-ctrl-tc">00:00 / ${t.duracao}</span></div>
        </div>
          ${chips}
      </div>
    </div>
  </div>
</section>`;
}

function blockProva(p) {
	const logos = readdirSync(join(ROOT, 'assets/img/clientes'))
		.filter((f) => f.endsWith('.webp'))
		.sort();
	const name = (f) =>
		f
			.replace(/^clientes-/, '')
			.replace(/[_-]+$/, '')
			.replace(/\.webp$/, '')
			.replace(/[-_]/g, ' ')
			.replace(/\s+$/, '');
	const imgs = logos
		.map((f) => `<img src="/assets/img/clientes/${f}" alt="${esc(name(f))}" width="120" height="34" loading="lazy" decoding="async">`)
		.join('');
	const dup = logos
		.map((f) => `<img src="/assets/img/clientes/${f}" alt="" width="120" height="34" loading="lazy" decoding="async">`)
		.join('');
	const speed =
		p.slug === 'libras-ao-vivo'
			? '<div class="lp-num"><strong data-count="24" data-suffix="/7">24/7</strong><span>rede disponível para o seu evento</span></div>'
			: '<div class="lp-num"><strong data-count="1" data-suffix="h">1h</strong><span>entrega expressa pelo HUET</span></div>';
	const third =
		p.slug === 'libras-ao-vivo'
			? '<div class="lp-num"><strong data-count="2">2</strong><span>intérpretes em revezamento nos eventos longos</span></div>'
			: '<div class="lp-num"><strong data-count="3">3</strong><span>recursos num só contrato: Libras, LSE e AD</span></div>';
	return `<section class="lp-proof" aria-label="Números e clientes da LIBRAS.SE">
  <div class="w">
    <div class="lp-nums">
      <div class="lp-num"><strong data-count="50" data-prefix="+">+50</strong><span>intérpretes humanos em todo o Brasil</span></div>
      ${speed}
      ${third}
      <div class="lp-num"><strong data-count="100" data-suffix="%">100%</strong><span>feito por pessoas, nunca por avatar</span></div>
    </div>
    <p class="lp-mq-l">Marcas e instituições que já confiaram na LIBRAS.SE</p>
    <div class="lp-mq"><div class="lp-mq-t">${imgs}<span aria-hidden="true" style="display:contents">${dup}</span></div></div>
  </div>
</section>`;
}

function blockOuvir(p) {
	const quoteTitle = p.quotePath ? 'Estimativa automática no HUET' : 'Orçamento automático no HUET';
	const quoteDesc = p.quotePath
		? 'Informe data, horário e duração e receba na hora uma estimativa em PDF.'
		: 'Preencha os dados e receba na hora um orçamento prévio em PDF, pronto para edital.';
	return `<section id="lp-ouvir" class="lp-sec alt" aria-labelledby="lp-ouvir-h">
  <span class="lp-orb o2" aria-hidden="true"></span>
  <div class="w">
    <div class="lp-ouvir-g">
      <div class="lp-ouvir-txt lp-rv lp-l">
        <span class="lp-lbl">A gente escuta</span>
        <h2 class="lp-h2" id="lp-ouvir-h">Conte o que o seu projeto precisa. <span class="lp-gt">A gente resolve com você.</span></h2>
        <p class="lp-sub">Cada projeto de ${esc(p.label)} tem seu ritmo, seu orçamento e suas exigências. Antes de qualquer proposta, queremos ouvir: prazo, minutagem, destino da obra e o que o edital ou o cliente pede. <strong>Escolha o caminho mais confortável para você.</strong></p>
        <figure class="lp-photo">
          ${picture('reuniao', 'Ilustração de uma conversa por vídeo num notebook sobre a mesa', { sizes: '(max-width: 1024px) 100vw, 540px' })}
          <figcaption>Conversa por vídeo, sem compromisso</figcaption>
        </figure>
        <div class="lp-paths">
          <a class="lp-path" href="${esc(meetUrl(p, 'card-reuniao'))}" data-lp-cta="reuniao"><span class="lp-path-ic">${ic('calendar')}</span><span><b>Agendar uma conversa por vídeo</b><span>Escolha um horário livre na nossa agenda. A confirmação chega por e-mail com o convite.</span></span><span class="lp-path-go">${ic('arrow')}</span></a>
          <a class="lp-path wa" href="${esc(waUrl(p))}" target="_blank" rel="noopener noreferrer" data-lp-cta="whatsapp"><span class="lp-path-ic">${ic('chat')}</span><span><b>Falar agora no WhatsApp</b><span>Atendimento por gente de verdade. Mande o que já tiver: link, roteiro ou minutagem.</span></span><span class="lp-path-go">${ic('arrow')}</span></a>
          <a class="lp-path qt" href="${esc(quoteUrl(p, 'card-orcamento'))}" target="_blank" rel="noopener" data-lp-cta="orcamento"><span class="lp-path-ic">${ic('file')}</span><span><b>${quoteTitle}</b><span>${quoteDesc}</span></span><span class="lp-path-go">${ic('arrow')}</span></a>
        </div>
      </div>
      <div class="lp-form lp-rv lp-r">
        <form novalidate>
          <h3>Prefere que a gente chame você?</h3>
          <p>Deixe o essencial. Respondemos em horário comercial, no canal que você escolher.</p>
          <div class="lp-f2">
            <label class="lp-fl"><span>Nome</span><input class="lp-inp" name="nome" autocomplete="name" required></label>
            <label class="lp-fl"><span>WhatsApp com DDD</span><input class="lp-inp" name="whatsapp" type="tel" inputmode="tel" autocomplete="tel" placeholder="(48) 99999-9999" required></label>
          </div>
          <div class="lp-f2">
            <label class="lp-fl"><span>E-mail <em>(opcional)</em></span><input class="lp-inp" name="email" type="email" autocomplete="email"></label>
            <label class="lp-fl"><span>Empresa ou projeto <em>(opcional)</em></span><input class="lp-inp" name="empresa" autocomplete="organization"></label>
          </div>
          <label class="lp-fl"><span>Conte sobre o projeto</span><textarea class="lp-inp" name="demanda" required placeholder="Ex.: ${esc(placeholderFor(p))}"></textarea></label>
          <div class="lp-f2">
            <label class="lp-fl"><span>Minutagem ou duração <em>(opcional)</em></span><input class="lp-inp" name="minutagem" placeholder="${p.slug === 'libras-ao-vivo' ? 'Ex.: 4 horas' : 'Ex.: 60 min'}"></label>
            <label class="lp-fl"><span>Prazo</span><select class="lp-inp" name="prazo"><option value="">Ainda não sei</option><option>Sem pressa, estou planejando</option><option>Neste mês</option><option>Nesta semana</option><option>Urgente, em até 24h</option><option>Inscrição em edital</option></select></label>
          </div>
          <fieldset class="lp-pref"><legend>Como prefere seguir?</legend>
            <label><input type="radio" name="preferencia" value="whatsapp" checked><span>WhatsApp</span></label>
            <label><input type="radio" name="preferencia" value="reuniao"><span>Conversa por vídeo</span></label>
            <label><input type="radio" name="preferencia" value="email"><span>E-mail</span></label>
          </fieldset>
          <label class="lp-ck"><input type="checkbox" name="privacidade" required><span>Concordo com a <a href="/privacidade/" target="_blank" rel="noopener">política de privacidade</a> e com o contato da LIBRAS.SE sobre este pedido.</span></label>
          <label class="lp-ck"><input type="checkbox" name="novidades"><span>Pode me mandar novidades e condições especiais.</span></label>
          <div class="lp-hp" aria-hidden="true"><label>Site <input name="website" tabindex="-1" autocomplete="off"></label></div>
          <button type="submit" class="btn bp lp-send">Quero ser chamado</button>
          <p class="lp-err" role="alert"></p>
        </form>
        <div class="lp-ok" aria-live="polite">
          <div class="lp-ok-ic">${ic('check')}</div>
          <h3>Obrigado! Já estamos com o seu pedido.</h3>
          <p data-lp-ok="msg"></p>
          <div class="lp-ok-btns">
            <a class="btn bw" data-lp-ok="wa" data-lp-cta="sucesso-whatsapp" href="${esc(waUrl(p))}" target="_blank" rel="noopener noreferrer">Adiantar pelo WhatsApp</a>
            <a class="btn bp" data-lp-ok="meet" data-lp-cta="sucesso-reuniao" href="${esc(meetUrl(p, 'sucesso-reuniao'))}">Escolher horário para conversar</a>
            <a class="btn lp-ghost" data-lp-cta="sucesso-orcamento" href="${esc(quoteUrl(p, 'sucesso-orcamento'))}" target="_blank" rel="noopener">${p.quotePath ? 'Gerar estimativa no HUET' : 'Gerar orçamento prévio no HUET'}</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>`;
}

function placeholderFor(p) {
	const map = {
		'longa-metragem': 'longa de ficção, 95 min, aprovado na PNAB, precisa de Libras, LSE e AD',
		'curta-metragem': 'curta de 15 min para inscrição em festival em dezembro',
		documentario: 'documentário de 52 min com muitos depoimentos, para TV pública',
		'festival-de-cinema': 'mostra com 20 curtas e cerimônia de abertura ao vivo',
		'projetos-culturais': 'espetáculo de dança com 3 apresentações e vídeo de registro',
		serie: 'série de 8 episódios de 30 min para streaming',
		'libras-ao-vivo': 'congresso de 2 dias, transmitido no YouTube',
		'campanhas-politicas': 'programa de TV diário e cortes para redes sociais',
		empresas: '12 vídeos de treinamento de 10 min para o RH',
		publicidade: 'filme de 30 s e versões para reels e stories',
		videoaulas: 'curso EAD com 40 aulas de 15 min',
	};
	return map[p.slug] || 'conte o tipo de vídeo, a duração e o prazo';
}

function blockValores(p) {
	const v = p.valores;
	const faqs = faqFor(p)
		.map((f) => `<details class="lp-rv"><summary>${esc(f.q)}</summary><p>${esc(f.a).replace('huet.libras.se', '<a href="https://huet.libras.se/" target="_blank" rel="noopener">huet.libras.se</a>')}</p></details>`)
		.join('\n      ');
	const quoteCta = v.quoteLabel || 'Gerar orçamento prévio no HUET';
	const s2 = p.quotePath ? 'Informe data, horário e duração do evento' : 'Informe o serviço, a minutagem e o prazo';
	return `<section id="lp-valores" class="lp-sec" aria-labelledby="lp-valores-h">
  <div class="w">
    <div class="lp-val lp-rv lp-z">
      <div>
        <span class="lp-lbl">Valores e orçamento</span>
        <h2 class="lp-h2" id="lp-valores-h">Valores de referência. <span class="lp-gt">Negociação de verdade.</span></h2>
        <p class="lp-sub">${esc(v.prices)}. Esses valores são uma base para você planejar, <strong>não uma tabela fechada</strong>: volume, recorrência, prazo e o valor aprovado no edital entram na conversa, e a gente ajusta a proposta para caber no seu projeto.</p>
        <div class="lp-tags"><span>Desconto por volume</span><span>Pacotes por lote</span><span>Prazo que cabe no cronograma</span><span>Valor alinhado ao edital</span></div>
        <ol class="lp-steps" aria-label="Como sai o orçamento prévio">
          <li><b>1</b><div><strong>Crie a sua conta grátis no HUET</strong><span>Leva um minuto, com Google, WhatsApp ou e-mail.</span></div></li>
          <li><b>2</b><div><strong>${s2}</strong><span>O cálculo é feito na hora, com os valores de referência.</span></div></li>
          <li><b>3</b><div><strong>Baixe o ${p.quotePath ? 'PDF da estimativa' : 'orçamento prévio em PDF'}</strong><span>Com validade e escopo, ${esc(v.uso)}.</span></div></li>
          <li><b>4</b><div><strong>Aprovou? A gente ajusta e executa</strong><span>Revisamos o escopo final com você e negociamos o que for preciso.</span></div></li>
        </ol>
        <div class="lp-cta-row">
          <a class="btn bp" href="${esc(quoteUrl(p, 'valores-orcamento'))}" target="_blank" rel="noopener" data-lp-cta="valores-orcamento">${quoteCta}</a>
          <a class="btn lp-ghost" href="${esc(waUrl(p))}" target="_blank" rel="noopener noreferrer" data-lp-cta="valores-whatsapp">Prefiro negociar no WhatsApp</a>
        </div>
      </div>
      <div class="lp-docw">
        ${picture('edital', 'Ilustração de mesa de trabalho com notebook, orçamento impresso e claquete', { sizes: '(max-width: 1024px) 100vw, 520px' })}
        <div class="lp-doc" aria-hidden="true">
          <span class="lp-stamp">PDF pronto</span>
          <div class="lp-doc-h"><b>LIBRAS.SE</b><span>${p.quotePath ? 'Estimativa' : 'Orçamento prévio'}</span></div>
          <div class="lp-doc-l"><i style="--w:92%"></i></div>
          <div class="lp-doc-l"><i style="--w:74%"></i></div>
          <div class="lp-doc-l"><i style="--w:84%"></i></div>
          <div class="lp-doc-l"><i style="--w:58%"></i></div>
          <div class="lp-doc-t"><span>${esc(v.doc)}</span><b>${esc(v.total)}</b></div>
        </div>
      </div>
    </div>
    <div class="lp-faq">
      ${faqs}
    </div>
  </div>
</section>`;
}

function blockMais(p) {
	const cards = PAGES.filter((o) => o.dir !== p.dir)
		.map(
			(o) =>
				`<a class="lp-sol lp-rv" href="/${o.dir}/" data-lp-cta="outra-${o.slug}"><span class="lp-sol-i">${picture(o.img, '', { small: true })}</span><span class="lp-sol-b"><b>${o.card[0]}</b><span>${o.card[1]}</span><em>Ver solução ${ic('arrow').replace('<svg ', '<svg width="13" height="13" ')}</em></span></a>`,
		)
		.join('\n      ');
	return `<section id="lp-mais" class="lp-sec alt" aria-labelledby="lp-mais-h">
  <div class="w">
    <div class="lp-head lp-rv">
      <span class="lp-lbl">Outras soluções</span>
      <h2 class="lp-h2" id="lp-mais-h">Acessibilidade em Libras para <span class="lp-gt">cada tipo de projeto</span></h2>
      <p class="lp-sub">A mesma rede de intérpretes e o mesmo padrão de qualidade, do cinema à sala de aula. <a href="/solucoes/" style="color:var(--teal-dd);font-weight:700">Ver todas as soluções</a></p>
    </div>
    <div class="lp-sols">
      ${cards}
    </div>
  </div>
</section>`;
}

function blockTail(p) {
	const data = {
		slug: p.slug,
		label: p.label,
		service: p.service,
		category: p.category,
		duracao: p.tela.duracao,
		lse: p.tela.lse,
		ad: p.tela.ad.map(esc),
	};
	return `<div class="lp-prog" aria-hidden="true"></div>
<div class="lp-dock" role="region" aria-label="Atalhos de contato">
  <span class="lp-dock-t">Vamos conversar sobre o seu projeto?</span>
  <a class="btn lp-dk-ghost" href="${esc(quoteUrl(p, 'dock-orcamento'))}" target="_blank" rel="noopener" data-lp-cta="dock-orcamento">${p.quotePath ? 'Estimativa' : 'Orçamento'}</a>
  <a class="btn bp" href="${esc(meetUrl(p, 'dock-reuniao'))}" data-lp-cta="dock-reuniao">Agendar conversa</a>
  <a class="btn bw" href="${esc(waUrl(p))}" target="_blank" rel="noopener noreferrer" aria-label="Falar no WhatsApp" data-lp-cta="dock-whatsapp">${WA_ICON}<span>WhatsApp</span></a>
</div>
<script type="application/json" id="lp-data">${JSON.stringify(data).replace(/</g, '\\u003c')}</script>
<script src="/assets/js/lp.js?v=${ASSET_V}" defer></script>`;
}

/* ── injeção ──────────────────────────────────────────────────────────── */
function wrap(name, html) {
	return `<!-- lp:${name} -->\n${html}\n<!-- /lp:${name} -->`;
}

function strip(html, name) {
	const re = new RegExp(`\\n?<!-- lp:${name} -->[\\s\\S]*?<!-- /lp:${name} -->\\n?`, 'g');
	return html.replace(re, '\n');
}

/** Índice logo após o </section> que fecha a primeira <section> depois de `from`. */
function endOfFirstSection(html, from) {
	const start = html.indexOf('<section', from);
	if (start < 0) throw new Error('nenhuma <section> depois do <main>');
	const re = /<section\b|<\/section>/g;
	re.lastIndex = start;
	let depth = 0;
	for (let m = re.exec(html); m; m = re.exec(html)) {
		depth += m[0] === '</section>' ? -1 : 1;
		if (depth === 0) return m.index + m[0].length;
	}
	throw new Error('hero sem </section>');
}

function insertAt(html, index, block) {
	return `${html.slice(0, index)}\n${block}\n${html.slice(index)}`;
}

function setMeta(html, p) {
	const d = esc(p.meta);
	if (p.meta.length > 160) console.warn(`  ! meta description com ${p.meta.length} caracteres em ${p.dir}`);
	return html
		.replace(/(<meta name="description" content=")[^"]*(")/, `$1${d}$2`)
		.replace(/(<meta property="og:description" content=")[^"]*(")/, `$1${d}$2`)
		.replace(/(<meta name="twitter:description" content=")[^"]*(")/, `$1${d}$2`);
}

/** Acrescenta as perguntas novas ao FAQPage do JSON-LD e marca a data de revisão. */
function setJsonLd(html, p) {
	const faqs = faqFor(p);
	const names = new Set(faqs.map((f) => f.q));
	return html.replace(/(<script type="application\/ld\+json">)([\s\S]*?)(<\/script>)/g, (all, open, body, close) => {
		let json;
		try {
			json = JSON.parse(body);
		} catch {
			return all;
		}
		let touched = false;
		const visit = (node) => {
			if (!node || typeof node !== 'object') return;
			if (Array.isArray(node)) return node.forEach(visit);
			if (node['@type'] === 'FAQPage' && Array.isArray(node.mainEntity)) {
				node.mainEntity = node.mainEntity.filter((q) => !names.has(q.name));
				for (const f of faqs) {
					node.mainEntity.push({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } });
				}
				touched = true;
			}
			if (node['@type'] === 'WebPage') {
				node.dateModified = TODAY;
				if (node.description) node.description = p.meta;
				touched = true;
			}
			if (node['@graph']) visit(node['@graph']);
		};
		visit(json);
		if (!touched) return all;
		return `${open}\n${JSON.stringify(json, null, 2)}\n${close}`;
	});
}

function buildPage(p) {
	const file = join(ROOT, p.dir, 'index.html');
	const before = readFileSync(file, 'utf8');
	let html = before;
	for (const name of ['css', 'tela', 'ouvir', 'mais', 'tail']) html = strip(html, name);

	html = html.replace('</head>', `${wrap('css', `<link rel="stylesheet" href="/assets/css/lp.css?v=${ASSET_V}">`)}\n</head>`);

	const mainAt = html.indexOf('<main');
	if (mainAt < 0) throw new Error(`${p.dir}: sem <main>`);
	html = insertAt(html, endOfFirstSection(html, mainAt), wrap('tela', `${blockTela(p)}\n${blockProva(p)}`));

	const faqMatch = /<section[^>]*(?:id="faq"|aria-labelledby="faq[^"]*")[^>]*>/.exec(html);
	const ctaMatch = /<section[^>]*id="cta-final"[^>]*>/.exec(html);
	const anchor = faqMatch ? faqMatch.index : ctaMatch ? ctaMatch.index : html.indexOf('</main>');
	html = insertAt(html, anchor, wrap('ouvir', `${blockOuvir(p)}\n${blockValores(p)}`));

	html = html.replace('</main>', `${wrap('mais', blockMais(p))}\n</main>`);
	html = html.replace(/<\/body>(?![\s\S]*<\/body>)/, `${wrap('tail', blockTail(p))}\n</body>`);

	html = setMeta(html, p);
	html = setJsonLd(html, p);
	html = html.replace(/\n{3,}/g, '\n\n');

	if (!html.includes('/assets/js/libras-lead.js')) {
		html = html.replace('<!-- lp:tail -->', '<script src="/assets/js/libras-lead.js" defer></script>\n<!-- lp:tail -->');
	}
	return { file, before, html };
}

/* ── /solucoes/: vitrine com as 11 páginas ────────────────────────────── */
function buildSolucoes() {
	const file = join(ROOT, 'solucoes', 'index.html');
	const before = readFileSync(file, 'utf8');
	let html = before;
	for (const name of ['css', 'projetos', 'projetos-ld']) html = strip(html, name);
	html = html.replace('</head>', `${wrap('css', `<link rel="stylesheet" href="/assets/css/lp.css?v=${ASSET_V}">`)}\n</head>`);

	const cards = PAGES.map(
		(o) =>
			`<a class="lp-sol lp-rv lp-in" href="/${o.dir}/"><span class="lp-sol-i">${picture(o.img, '', { small: true })}</span><span class="lp-sol-b"><b>${o.card[0]}</b><span>${o.card[1]}</span><em>Conhecer ${ic('arrow').replace('<svg ', '<svg width="13" height="13" ')}</em></span></a>`,
	).join('\n      ');
	const block = `<section id="projetos" class="lp-sec alt" aria-labelledby="projetos-h">
  <div class="w">
    <div class="lp-head">
      <span class="lp-lbl">Soluções por tipo de projeto</span>
      <h2 class="lp-h2" id="projetos-h">Do cinema à sala de aula, <span class="lp-gt">uma solução para cada projeto</span></h2>
      <p class="lp-sub">Escolha o seu cenário e veja como a Libras, a LSE e a audiodescrição entram no seu conteúdo. Os valores são negociáveis e o orçamento prévio para edital sai na hora no HUET.</p>
    </div>
    <div class="lp-sols">
      ${cards}
    </div>
  </div>
</section>`;
	const solMatch = /<section[^>]*id="solucoes"[^>]*>/.exec(html);
	if (!solMatch) throw new Error('solucoes: sem #solucoes');
	html = insertAt(html, endOfFirstSection(html, solMatch.index), wrap('projetos', block));

	const itemList = {
		'@context': 'https://schema.org',
		'@type': 'ItemList',
		name: 'Soluções de acessibilidade em Libras por tipo de projeto',
		itemListElement: PAGES.map((o, i) => ({
			'@type': 'ListItem',
			position: i + 1,
			name: o.card[0],
			description: o.card[1],
			url: `https://libras.se/${o.dir}/`,
		})),
	};
	html = html.replace(
		'</head>',
		`${wrap('projetos-ld', `<script type="application/ld+json">\n${JSON.stringify(itemList, null, 2)}\n</script>`)}\n</head>`,
	);
	html = html.replace(/\n{3,}/g, '\n\n');
	return { file, before, html };
}

/* ── sitemap: lastmod das páginas tocadas ─────────────────────────────── */
function buildSitemap(dirs) {
	const file = join(ROOT, 'sitemap.xml');
	const before = readFileSync(file, 'utf8');
	let html = before;
	for (const dir of dirs) {
		const re = new RegExp(`(<loc>https://libras\\.se/${dir}/</loc>\\s*<lastmod>)[^<]*(</lastmod>)`);
		html = html.replace(re, `$1${TODAY}$2`);
	}
	return { file, before, html };
}

const results = [...PAGES.map(buildPage), buildSolucoes(), buildSitemap([...PAGES.map((p) => p.dir), 'solucoes'])];
let changed = 0;
for (const r of results) {
	if (r.before === r.html) continue;
	changed++;
	writeFileSync(r.file, r.html);
}
console.log(`${changed} arquivo(s) atualizado(s)`);
