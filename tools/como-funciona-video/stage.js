// Timeline determinística da cena (mesma ideia de instagram/stories/cenas/stage.js).
// O Playwright chama window.__seek(t) em cada quadro: todas as animações ficam pausadas e
// recebem currentTime = t; os ganchos aCada(t) cuidam do que é calculado (contadores, flutuação, vídeo).
// Como a peça é um loop, cada elemento tem UMA trilha por grupo de propriedades cobrindo o loop
// inteiro (0 → DUR), com o estado final igual ao inicial.

export const DUR = 12;
export const FPS = 30;

export const EASE = {
	linear: "linear",
	out: "cubic-bezier(.16,1,.3,1)", // expo out
	in: "cubic-bezier(.7,0,.84,0)",
	inOut: "cubic-bezier(.83,0,.17,1)",
	suave: "cubic-bezier(.4,0,.2,1)",
	back: "cubic-bezier(.34,1.56,.64,1)",
	mola: "cubic-bezier(.2,1.25,.35,1)",
};

const animacoes = [];
const ganchos = [];

function alvos(a) {
	if (typeof a === "string") return [...document.querySelectorAll(a)];
	if (a instanceof Element) return [a];
	return [...a];
}

// trilha(alvo, [[t, {props}, ease?], ...]): pontos em segundos dentro do loop.
// O ease de um ponto vale para o trecho que SAI dele. Antes do primeiro ponto vale o primeiro
// estado e depois do último vale o último (fill both).
export function trilha(alvo, pontos) {
	const ord = [...pontos].sort((a, b) => a[0] - b[0]);
	const quadros = ord.map(([t, props, ease]) => ({ ...props, offset: t / DUR, easing: EASE[ease ?? "suave"] ?? ease }));
	if (ord[0][0] > 0) quadros.unshift({ ...ord[0][1], offset: 0 });
	if (ord.at(-1)[0] < DUR) quadros.push({ ...ord.at(-1)[1], offset: 1 });
	for (const el of alvos(alvo)) {
		const a = el.animate(quadros, { duration: DUR * 1000, fill: "both" });
		a.pause();
		animacoes.push(a);
	}
}

// Entra em "ini" e sai em "fim": atalho para elementos que aparecem e somem dentro do loop.
export function janela(alvo, { ini, fim, de, para, sai = de, dIn = 0.5, dOut = 0.4, eIn = "out", eOut = "in" }) {
	trilha(alvo, [
		[ini, de, eIn],
		[ini + dIn, para, "linear"],
		[fim, para, eOut],
		[fim + dOut, sai],
	]);
}

export function aCada(fn) {
	ganchos.push(fn);
}

export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const prog = (t, ini, fim) => clamp((t - ini) / (fim - ini));
export const easeOut = (x) => 1 - (1 - x) ** 3;
export const easeInOut = (x) => (x < 0.5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2);

// Toca uma sequência de PNG num <img>: quadro = (t - em) * fps, em loop.
export async function sequencia(img, nome, { em = 0 } = {}) {
	const midia = await (await fetch("/tools/como-funciona-video/cache/midia.json")).json();
	const m = midia[nome];
	if (!m) throw new Error(`mídia "${nome}" não preparada: rode npm run midia`);
	const src = (q) => `/${m.dir}/${String(q + 1).padStart(4, "0")}.png`;
	// pré-carrega todos os quadros para a troca não piscar
	await Promise.all(Array.from({ length: m.frames }, (_, q) => {
		const i = new Image();
		i.src = src(q);
		return i.decode().catch(() => {});
	}));
	let atual = "";
	aCada(async (t) => {
		const q = Math.floor(Math.max(0, t - em) * m.fps) % m.frames;
		const s = src(q);
		if (s === atual) return;
		atual = s;
		for (const el of alvos(img)) el.src = s;
		await Promise.all(alvos(img).map((el) => el.decode().catch(() => {})));
	});
}

export const Stage = {
	pronto: false,
	async iniciar(montar) {
		await Promise.all([300, 500, 700, 900, 1000].map((w) => document.fonts.load(`${w} 40px M`)));
		await document.fonts.ready;
		await montar?.();
		await Promise.all([...document.images].map((i) => i.decode().catch(() => {})));
		await window.__seek(0);
		Stage.pronto = true;
	},
};

window.Stage = Stage;
window.__seek = async (t) => {
	for (const a of animacoes) a.currentTime = t * 1000;
	await Promise.all(ganchos.map((g) => g(t)));
	await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
};
// Prévia no navegador comum: ?play toca a cena em loop em tempo real.
if (new URLSearchParams(location.search).has("play")) {
	const t0 = performance.now();
	const tick = async () => {
		if (Stage.pronto) {
			const t = ((performance.now() - t0) / 1000) % DUR;
			for (const a of animacoes) a.currentTime = t * 1000;
			await Promise.all(ganchos.map((g) => g(t)));
		}
		requestAnimationFrame(tick);
	};
	requestAnimationFrame(tick);
}
