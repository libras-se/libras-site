// Prepara as mídias do vídeo e da página /estudio/ a partir de uma gravação nossa em fundo verde.
//   node midia.mjs
// Fonte: fonte/teste-croma.mp4 (1280×720, 6,7 s, intérprete com a camiseta "TESTE LIBRAS.SE",
//        recorte do banco de vídeos da LIBRAS.SE, direitos próprios).
// Saída:
//   cache/aula*.png                slides de aula fictícios (aula.html e variantes ?v=) em 1280×720
//   cache/{original,mascara,recorte}/0001… sequências 1024×576 para a cena (cena.html)
//   assets/img/estudio/material/*.webp  as aulas com a Bruna recortada e o material original (sem Libras)
//   assets/videos/estudio/aula-bruna.mp4 + .webp  a Bruna sinalizando sobre a aula de Scrum
// node midia.mjs --so-material   pula as sequências da cena
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const AQUI = import.meta.dirname;
export const ROOT = path.resolve(AQUI, "../..");
const CACHE = path.join(AQUI, "cache");
const FONTE = path.join(AQUI, "fonte/teste-croma.mp4");
const OUT = path.join(ROOT, "assets/videos/estudio");
const HOST = "http://estudio.local";

const ff = (args) => execFileSync("ffmpeg", ["-v", "error", "-y", ...args], { stdio: "inherit" });

// Chave por dominância do verde: o fundo tem G bem acima de R e B; pele, cabelo e a camiseta preta não.
// O verde que respinga na borda é limitado a max(R,B)+6, e o alfa encolhe 1 px e é suavizado.
const CHAVE =
	"format=rgba,geq=r='r(X,Y)':g='min(g(X,Y),max(r(X,Y),b(X,Y))+6)':b='b(X,Y)':" +
	"a='clip(255-(g(X,Y)-max(r(X,Y),b(X,Y))-14)*10,0,255)',split[c][m];" +
	"[m]alphaextract,erosion,gblur=sigma=0.7[a];[c][a]alphamerge";

const H264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an"];

export async function fotografarAulas() {
	const browser = await chromium.launch({ channel: "chrome", args: ["--force-color-profile=srgb", "--hide-scrollbars"] });
	try {
		const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
		await ctx.route(`${HOST}/**`, (route) => {
			const arquivo = path.join(ROOT, decodeURIComponent(new URL(route.request().url()).pathname));
			if (!arquivo.startsWith(ROOT) || !fs.existsSync(arquivo)) return route.fulfill({ status: 404, body: "" });
			return route.fulfill({ path: arquivo });
		});
		const page = await ctx.newPage();
		for (const v of AULAS) {
			await page.goto(`${HOST}/tools/estudio-video/aula.html?v=${v.id}`);
			await page.evaluate(() => document.fonts.ready);
			await page.screenshot({ path: fundo(v.id) });
			await page.goto(`${HOST}/tools/estudio-video/aula.html?v=${v.id}&k=${encodeURIComponent(v.prox)}`);
			await page.evaluate(() => document.fonts.ready);
			await page.screenshot({ path: path.join(CACHE, `aula-${v.id}-prox.png`) });
		}
	} finally {
		await browser.close();
	}
}

function sequencias() {
	const meta = {};
	const sai = (nome, ext) => {
		const dir = path.join(CACHE, nome);
		fs.rmSync(dir, { recursive: true, force: true });
		fs.mkdirSync(dir, { recursive: true });
		return { dir, alvo: path.join(dir, `%04d.${ext}`) };
	};
	const o = sai("original", "jpg");
	ff(["-i", FONTE, "-r", "30", "-vf", "scale=1024:576:flags=lanczos", "-q:v", "3", o.alvo]);
	const r = sai("recorte", "png");
	ff(["-i", FONTE, "-r", "30", "-filter_complex", `[0:v]scale=1024:576:flags=lanczos,${CHAVE}`, r.alvo]);
	const m = sai("mascara", "jpg");
	ff(["-i", FONTE, "-r", "30", "-filter_complex", `[0:v]scale=1024:576:flags=lanczos,${CHAVE},alphaextract,format=gray`, "-q:v", "3", m.alvo]);
	for (const [nome, ext, d] of [["original", "jpg", o.dir], ["recorte", "png", r.dir], ["mascara", "jpg", m.dir]]) {
		meta[nome] = { dir: path.relative(ROOT, d), frames: fs.readdirSync(d).length, fps: 30, ext };
		console.log(`✓ ${nome}: ${meta[nome].frames} quadros`);
	}
	fs.writeFileSync(path.join(CACHE, "midia.json"), JSON.stringify(meta, null, 2));
}

// A Bruna (vídeos do vocabulário do site, fundo claro #EFF9F9) recortada direto sobre as aulas fictícias,
// no canto inferior direito e sem caixa, como nas entregas.
const SINAIS = path.join(ROOT, "assets/videos/sinais");
const CHAVE_BRUNA =
	"colorkey=0xEFF9F9:0.10:0.04,format=rgba,split[c][m];[m]alphaextract,erosion,erosion,gblur=sigma=0.8[a];[c][a]alphamerge";
const JANELA = "scale=794:446:flags=lanczos,crop=440:446:150:0";
// "prox" é o bloco seguinte da mesma disciplina: o material original (sem Libras) que ainda vai ser gravado
const AULAS = [
	{ id: "scrum", sinal: "ensinar", t: 1.5, prox: "Tema 2 · Bloco 04" },
	{ id: "dados", sinal: "estudar", t: 1.5, prox: "Tema 3 · Bloco 03" },
	{ id: "direito", sinal: "livro", t: 1.5, prox: "Tema 1 · Bloco 05" },
	{ id: "saude", sinal: "aprender", t: 1.3, prox: "Tema 2 · Bloco 02" },
];
const fundo = (id) => path.join(CACHE, id === "scrum" ? "aula.png" : `aula-${id}.png`);

function materialBruna() {
	const IMG = path.join(ROOT, "assets/img/estudio/material");
	fs.mkdirSync(IMG, { recursive: true });
	fs.mkdirSync(OUT, { recursive: true });
	const webp = (png, alvo) => execFileSync("cwebp", ["-quiet", "-q", "80", "-m", "6", "-resize", "960", "0", png, "-o", alvo]);
	for (const a of AULAS) {
		const png = path.join(CACHE, `material-${a.id}.png`);
		ff(["-i", path.join(SINAIS, `${a.sinal}.mp4`), "-loop", "1", "-i", fundo(a.id), "-filter_complex",
			`[0:v]${CHAVE_BRUNA},${JANELA}[p];[1:v][p]overlay=840:274:shortest=1,trim=start=${a.t},setpts=PTS-STARTPTS`, "-frames:v", "1", png]);
		webp(png, path.join(IMG, `${a.id}.webp`));
		webp(path.join(CACHE, `aula-${a.id}-prox.png`), path.join(IMG, `${a.id}-original.webp`));
		console.log(`✓ material/${a.id}.webp (+ original)`);
	}
	// vídeo: cinco sinais em sequência sobre a aula de Scrum
	const lista = path.join(CACHE, "bruna.txt");
	fs.writeFileSync(lista, ["ola", "estudar", "aprender", "ensinar", "livro"].map((s) => `file '${path.join(SINAIS, `${s}.mp4`)}'`).join("\n"));
	const mp4 = path.join(OUT, "aula-bruna.mp4");
	ff(["-f", "concat", "-safe", "0", "-i", lista, "-loop", "1", "-i", fundo("scrum"), "-filter_complex",
		`[0:v]fps=30,${CHAVE_BRUNA},${JANELA}[p];[1:v][p]overlay=840:274:shortest=1,format=yuv420p`, "-r", "30", ...H264, mp4]);
	ff(["-ss", "6.4", "-i", mp4, "-frames:v", "1", path.join(CACHE, "aula-bruna.png")]);
	webp(path.join(CACHE, "aula-bruna.png"), path.join(OUT, "aula-bruna.webp"));
	console.log(`✓ aula-bruna.mp4 ${(fs.statSync(mp4).size / 1024).toFixed(0)} KB`);
}

if (process.argv[1] === import.meta.filename) {
	fs.mkdirSync(CACHE, { recursive: true });
	await fotografarAulas();
	if (!process.argv.includes("--so-material")) sequencias();
	materialBruna();
}
