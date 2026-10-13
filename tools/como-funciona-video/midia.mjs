// Prepara a intérprete recortada (fundo do vídeo de sinais vira transparente) em sequência de PNG.
// Trocar o src do <img> quadro a quadro é o que mantém a captura determinística; <video> não garante o quadro.
//   node midia.mjs
// Saída: cache/interprete/0001.png ... + cache/midia.json
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const AQUI = import.meta.dirname;
export const ROOT = path.resolve(AQUI, "../..");
const CACHE = path.join(AQUI, "cache");

const FONTES = [
	{
		nome: "interprete",
		src: path.join(ROOT, "assets/videos/sinais/obrigado.mp4"),
		// recorte largo (a mão erguida do sinal "obrigado" fica dentro) + chave no fundo #EFF9F9;
		// o alfa encolhe ~2px e é suavizado para não sobrar contorno claro sobre o fundo escuro da janela
		filtro: "[0:v]crop=820:720:210:0,colorkey=0xEFF9F9:0.10:0.04,format=rgba,split[c][m];" +
			"[m]alphaextract,erosion,erosion,gblur=sigma=0.8[a];[c][a]alphamerge,scale=410:360:flags=lanczos,format=rgba",
	},
];

export function prepararMidia() {
	const meta = {};
	for (const f of FONTES) {
		const dir = path.join(CACHE, f.nome);
		fs.rmSync(dir, { recursive: true, force: true });
		fs.mkdirSync(dir, { recursive: true });
		execFileSync("ffmpeg", ["-v", "error", "-y", "-i", f.src, "-r", "30", "-filter_complex", f.filtro, path.join(dir, "%04d.png")]);
		const frames = fs.readdirSync(dir).length;
		meta[f.nome] = { dir: path.relative(ROOT, dir), frames, fps: 30 };
		console.log(`✓ ${f.nome}: ${frames} quadros`);
	}
	fs.writeFileSync(path.join(CACHE, "midia.json"), JSON.stringify(meta, null, 2));
	return meta;
}

if (process.argv[1] === import.meta.filename) prepararMidia();
