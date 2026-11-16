// Renderiza a cena do Libras.se Estúdio quadro a quadro e codifica para a página /estudio/.
//   node render.mjs                 quadros + vídeos + cartaz
//   node render.mjs --stills [t...] revisão: alguns quadros em revisao/ (+ folha de contato)
//   node render.mjs --encode        só recodifica a partir de cache/quadros
// Saída (assets/videos/estudio/):
//   estudio-demo.mp4      1920×1080, H.264 (desktop)
//   estudio-demo-720.mp4  1280×720, H.264 (celular e economia de dados)
//   estudio-demo.webp     cartaz (gravação com o controle no celular)
import { execFileSync, spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const AQUI = import.meta.dirname;
const ROOT = path.resolve(AQUI, "../..");
const W = 1600;
const H = 900;
const ESCALA = 1.2; // 1600×900 de layout → 1920×1080 de pixels
const FPS = 30;
const DUR = 36;
const N = DUR * FPS;
const T_CARTAZ = 16.2;
const HOST = "http://estudio.local";
const OUT = path.join(ROOT, "assets/videos/estudio");
const QUADROS = path.join(AQUI, "cache/quadros");
const REVISAO = path.join(AQUI, "revisao");
const args = process.argv.slice(2);

if (!fs.existsSync(path.join(AQUI, "cache/midia.json"))) throw new Error("rode antes: node midia.mjs");

async function abrir(browser) {
	const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: ESCALA });
	await ctx.route(`${HOST}/**`, (route) => {
		const arquivo = path.join(ROOT, decodeURIComponent(new URL(route.request().url()).pathname));
		if (!arquivo.startsWith(ROOT) || !fs.existsSync(arquivo) || fs.statSync(arquivo).isDirectory())
			return route.fulfill({ status: 404, body: "" });
		return route.fulfill({ path: arquivo });
	});
	const page = await ctx.newPage();
	const erros = [];
	page.on("pageerror", (e) => erros.push(e.message));
	page.on("console", (m) => m.type() === "error" && erros.push(m.text()));
	await page.goto(`${HOST}/tools/estudio-video/cena.html`);
	try {
		await page.waitForFunction(() => window.Stage?.pronto === true, null, { timeout: 120000 });
	} catch (e) {
		throw new Error(`cena não ficou pronta: ${erros.join(" | ") || e.message}`);
	}
	if (erros.length) throw new Error(erros.join(" | "));
	return page;
}

async function quadro(page, t, type = "png") {
	await page.evaluate((v) => window.__seek(v), t);
	return page.screenshot({ type, animations: "allow", caret: "initial" });
}

const sh = (cmd, a) => execFileSync(cmd, a, { stdio: ["ignore", "ignore", "inherit"] });

async function stills(browser) {
	const tempos = args.filter((a) => !a.startsWith("--")).map(Number);
	const lista = tempos.length ? tempos : [1.4, 4.0, 5.2, 7.2, 9.0, 11.0, 13.0, 16.2, 21.0, 23.6, 27.0, 29.5, 33.8];
	fs.rmSync(REVISAO, { recursive: true, force: true });
	fs.mkdirSync(REVISAO, { recursive: true });
	const page = await abrir(browser);
	const arquivos = [];
	for (const t of lista) {
		const f = path.join(REVISAO, `t${t.toFixed(2).padStart(5, "0")}.png`);
		fs.writeFileSync(f, await quadro(page, t));
		arquivos.push(f);
	}
	try {
		sh("magick", ["montage", ...arquivos, "-tile", "3x", "-geometry", "800x450+6+6", "-background", "#c9d9d7", path.join(REVISAO, "folha.jpg")]);
	} catch {}
	console.log(`✓ ${lista.length} quadros em revisao/ (folha.jpg)`);
}

async function quadros(browser) {
	fs.rmSync(QUADROS, { recursive: true, force: true });
	fs.mkdirSync(QUADROS, { recursive: true });
	const PARALELO = 4;
	const t0 = Date.now();
	await Promise.all(Array.from({ length: PARALELO }, async (_, k) => {
		const page = await abrir(browser);
		for (let q = k; q < N; q += PARALELO)
			fs.writeFileSync(path.join(QUADROS, `${String(q + 1).padStart(4, "0")}.png`), await quadro(page, q / FPS));
		if (k === 0) fs.writeFileSync(path.join(AQUI, "cache/cartaz.png"), await quadro(page, T_CARTAZ));
		await page.context().close();
	}));
	console.log(`✓ ${N} quadros em ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}

function codificar(saida, enc) {
	return new Promise((ok, erro) => {
		const ff = spawn("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", path.join(QUADROS, "%04d.png"), ...enc, saida], { stdio: "inherit" });
		ff.on("close", (c) => (c === 0 ? ok() : erro(new Error(`ffmpeg saiu com ${c} (${path.basename(saida)})`))));
	});
}

async function encode() {
	fs.mkdirSync(OUT, { recursive: true });
	const base = ["-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-pix_fmt", "yuv420p", "-g", "60", "-movflags", "+faststart", "-an"];
	await Promise.all([
		codificar(path.join(OUT, "estudio-demo.mp4"), ["-vf", "scale=1920:1080:flags=lanczos", "-crf", "24", ...base]),
		codificar(path.join(OUT, "estudio-demo-720.mp4"), ["-vf", "scale=1280:720:flags=lanczos", "-crf", "26", ...base]),
	]);
	sh("cwebp", ["-quiet", "-q", "80", "-m", "6", "-resize", "1600", "0", path.join(AQUI, "cache/cartaz.png"), "-o", path.join(OUT, "estudio-demo.webp")]);
	for (const f of ["estudio-demo.mp4", "estudio-demo-720.mp4", "estudio-demo.webp"])
		console.log(`✓ ${f} ${(fs.statSync(path.join(OUT, f)).size / 1024).toFixed(0)} KB`);
}

if (args.includes("--encode")) {
	await encode();
} else {
	const browser = await chromium.launch({
		channel: "chrome",
		args: ["--force-color-profile=srgb", "--font-render-hinting=none", "--disable-lcd-text", "--hide-scrollbars"],
	});
	try {
		if (args.includes("--stills")) await stills(browser);
		else {
			await quadros(browser);
			await encode();
		}
	} finally {
		await browser.close();
	}
}
