// Renderiza a cena quadro a quadro com fundo transparente e codifica para a home.
//   node render.mjs                 quadros + vídeos + imagem estática
//   node render.mjs --stills [t...] revisão: quadros sobre a cor da seção em revisao/ (+ folha de contato)
//   node render.mjs --encode        só recodifica a partir de cache/quadros
// Saída (assets/videos/como-funciona/):
//   como-funciona.webm  VP9 com alfa (Chrome, Edge, Firefox, Android)
//   como-funciona.mov   HEVC com alfa (Safari no Mac e todo navegador do iPhone/iPad)
//   como-funciona.webp         primeiro quadro com alfa (aparece enquanto o vídeo carrega; a troca é invisível)
//   como-funciona-resumo.webp  quadro do passo 3 com alfa (movimento reduzido e economia de dados)
import { execFileSync, spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";
import { prepararMidia, ROOT } from "./midia.mjs";

const AQUI = import.meta.dirname;
const W = 1440;
const H = 900;
const FPS = 30;
const DUR = 12;
const N = DUR * FPS;
const T_RESUMO = 9.3; // entrega: vídeo com a janela de Libras, aviso e selo "Fácil" na tela
const HOST = "http://cf.local";
const OUT = path.join(ROOT, "assets/videos/como-funciona");
const QUADROS = path.join(AQUI, "cache/quadros");
const REVISAO = path.join(AQUI, "revisao");
const args = process.argv.slice(2);

if (!fs.existsSync(path.join(AQUI, "cache/midia.json"))) prepararMidia();

async function abrir(browser, query = "") {
	const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
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
	await page.goto(`${HOST}/tools/como-funciona-video/cena.html${query}`);
	try {
		await page.waitForFunction(() => window.Stage?.pronto === true, null, { timeout: 60000 });
	} catch (e) {
		throw new Error(`cena não ficou pronta: ${erros.join(" | ") || e.message}`);
	}
	if (erros.length) throw new Error(erros.join(" | "));
	return page;
}

async function quadro(page, t) {
	await page.evaluate((v) => window.__seek(v), t);
	return page.screenshot({ type: "png", omitBackground: true, animations: "allow", caret: "initial" });
}

const sh = (cmd, a) => execFileSync(cmd, a, { stdio: ["ignore", "ignore", "ignore"] });

async function stills(browser) {
	const tempos = args.filter((a) => !a.startsWith("--")).map(Number);
	const lista = tempos.length ? tempos : [0, 1.0, 1.45, 2.4, 3.3, 4.3, 5.6, 6.9, 7.75, 8.6, 9.8, 10.6, 11.5];
	fs.rmSync(REVISAO, { recursive: true, force: true });
	fs.mkdirSync(REVISAO, { recursive: true });
	const page = await abrir(browser, "?fundo");
	const arquivos = [];
	for (const t of lista) {
		const f = path.join(REVISAO, `t${t.toFixed(2).padStart(5, "0")}.png`);
		fs.writeFileSync(f, await quadro(page, t));
		arquivos.push(f);
	}
	// o montage do ImageMagick reclama de fonte ausente (sai com erro) mas gera a folha
	try {
		sh("magick", ["montage", ...arquivos, "-tile", "3x", "-geometry", "720x450+6+6", "-background", "#c9d9d7", path.join(REVISAO, "folha.jpg")]);
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
		const resumo = k === 0 ? await quadro(page, T_RESUMO) : null;
		if (resumo) fs.writeFileSync(path.join(AQUI, "cache/resumo.png"), resumo);
		await page.context().close();
	}));
	console.log(`✓ ${N} quadros em ${((Date.now() - t0) / 1000).toFixed(1)}s`);
	// nada pode encostar nas bordas do palco (na página viraria um corte reto)
	try {
		execFileSync("python3.12", ["-I", path.join(AQUI, "bordas.py"), QUADROS], { stdio: "inherit" });
	} catch {
		throw new Error("há conteúdo cortado nas bordas do palco: ajuste as trajetórias em cena.html");
	}
}

function codificar(saida, enc) {
	return new Promise((ok, erro) => {
		const ff = spawn("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", path.join(QUADROS, "%04d.png"), ...enc, saida], { stdio: "inherit" });
		ff.on("close", (c) => (c === 0 ? ok() : erro(new Error(`ffmpeg saiu com ${c} (${path.basename(saida)})`))));
	});
}

async function encode() {
	fs.mkdirSync(OUT, { recursive: true });
	const webm = path.join(OUT, "como-funciona.webm");
	const mov = path.join(OUT, "como-funciona.mov");
	await Promise.all([
		// VP9 com alfa: -auto-alt-ref 0 é obrigatório para o canal alfa; GOP de 3s para o clique nos passos buscar rápido
		codificar(webm, ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "48", "-deadline", "good", "-cpu-used", "1",
			"-row-mt", "1", "-tile-columns", "2", "-auto-alt-ref", "0", "-g", "90", "-an"]),
		// HEVC com alfa (VideoToolbox): o único formato com transparência que o Safari toca.
		// O Safari lê a cor como pré-multiplicada; sem o premultiply as sombras viram halo claro.
		codificar(mov, ["-vf", "premultiply=inplace=1", "-c:v", "hevc_videotoolbox", "-pix_fmt", "bgra", "-alpha_quality", "0.4", "-q:v", "52",
			"-tag:v", "hvc1", "-g", "90", "-an", "-movflags", "+faststart"]),
	]);
	const webp = (png, nome) => sh("cwebp", ["-quiet", "-q", "78", "-alpha_q", "80", "-m", "6", "-resize", "1200", "0", png, "-o", path.join(OUT, nome)]);
	webp(path.join(QUADROS, "0001.png"), "como-funciona.webp");
	webp(path.join(AQUI, "cache/resumo.png"), "como-funciona-resumo.webp");
	for (const f of ["como-funciona.webm", "como-funciona.mov", "como-funciona.webp", "como-funciona-resumo.webp"])
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
