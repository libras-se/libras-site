#!/usr/bin/env node
/**
 * Gerador do sistema de imagens sociais (OG) da LIBRAS.SE.
 *
 * Para cada entrada de og/pages.json:
 *   1. renderiza og/template.html (Museo Sans + tokens do design system) a 1200x630 @2x
 *      via Chrome headless (puppeteer-core apontando para o Chrome instalado);
 *   2. converte o PNG para WebP em assets/img/og/<slug>.webp (ImageMagick);
 *   3. injeta og:image / twitter:image (+ alt/width/height) na <head> da página.
 *
 * Uso:
 *   npm run og                 # gera tudo + injeta meta tags
 *   npm run og -- --only=home  # só uma página (slug)
 *   npm run og -- --no-inject  # gera imagens sem tocar no HTML
 *   npm run og -- --no-webp    # mantém PNG (não converte)
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import puppeteer from 'puppeteer-core';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const TEMPLATE = join(__dirname, 'template.html');
const OUT_DIR = join(ROOT, 'assets', 'img', 'og');
const SITE = 'https://libras.se';

// ---- args ----
const args = process.argv.slice(2);
const only = (args.find((a) => a.startsWith('--only=')) || '').split('=')[1] || null;
const skip = ((args.find((a) => a.startsWith('--skip=')) || '').split('=')[1] || '')
  .split(',').map((s) => s.trim()).filter(Boolean);
const noInject = args.includes('--no-inject');
const noWebp = args.includes('--no-webp');

// ---- Chrome path (macOS / Linux fallbacks) ----
const CHROME_CANDIDATES = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium-browser',
  '/usr/bin/chromium',
];
const chromePath = process.env.CHROME_PATH || CHROME_CANDIDATES.find((p) => existsSync(p));
if (!chromePath) {
  console.error('✗ Chrome não encontrado. Defina CHROME_PATH=/caminho/para/chrome');
  process.exit(1);
}

function magick(inFile, outFile) {
  // 2400x1260 PNG -> 1200x630 WebP, alta qualidade
  execFileSync('magick', [inFile, '-resize', '1200x630', '-quality', '90', '-define', 'webp:method=6', outFile]);
}

function altText(p) {
  const title = [p.lead, p.accent, p.tail].filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
  return `LIBRAS.SE, ${p.eyebrow}: ${title}`;
}

/** Substitui o content="" de uma meta tag (property OU name) sem duplicar. */
function setMeta(html, attr, key, value) {
  const re = new RegExp(`(<meta\\s+${attr}=["']${key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["']\\s+content=["'])[^"']*(["'])`, 'i');
  if (re.test(html)) return html.replace(re, `$1${value}$2`);
  return html; // se a tag não existe, não inventa (mantém conservador)
}

function inject(page, p) {
  const file = join(ROOT, p.page);
  if (!existsSync(file)) { console.warn(`  · inject pulado (sem arquivo): ${p.page}`); return; }
  let html = readFileSync(file, 'utf8');
  const url = `${SITE}/assets/img/og/${p.slug}.webp`;
  const alt = altText(p);
  const before = html;
  html = setMeta(html, 'property', 'og:image', url);
  html = setMeta(html, 'property', 'og:image:secure_url', url);
  html = setMeta(html, 'property', 'og:image:alt', alt);
  html = setMeta(html, 'property', 'og:image:width', '1200');
  html = setMeta(html, 'property', 'og:image:height', '630');
  html = setMeta(html, 'property', 'og:image:type', 'image/webp');
  html = setMeta(html, 'name', 'twitter:image', url);
  html = setMeta(html, 'name', 'twitter:image:alt', alt);
  if (html !== before) { writeFileSync(file, html); console.log(`  ↳ meta injetada em ${p.page}`); }
  else console.log(`  ↳ meta já atualizada em ${p.page}`);
}

async function main() {
  const manifest = JSON.parse(readFileSync(join(__dirname, 'pages.json'), 'utf8'));
  let pages = manifest.pages;
  if (only) pages = pages.filter((p) => p.slug === only);
  if (skip.length) pages = pages.filter((p) => !skip.includes(p.slug));
  if (!pages.length) { console.error('Nenhuma página selecionada.'); process.exit(1); }
  if (skip.length) console.log(`(pulando: ${skip.join(', ')})`);

  mkdirSync(OUT_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: 'new',
    args: ['--no-sandbox', '--force-color-profile=srgb', '--hide-scrollbars'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 2 });
  await page.goto(pathToFileURL(TEMPLATE).href, { waitUntil: 'networkidle0' });

  console.log(`\nGerando ${pages.length} imagem(ns) → assets/img/og/\n`);
  for (const p of pages) {
    await page.evaluate((d) => window.render(d), p);
    await page.evaluate(() => document.fonts.ready);
    await new Promise((r) => setTimeout(r, 120)); // assenta layout/blur
    const card = await page.$('#card');
    const pngPath = join(OUT_DIR, `${p.slug}.png`);
    await card.screenshot({ path: pngPath });

    if (noWebp) {
      console.log(`✓ ${p.slug}.png`);
    } else {
      const webpPath = join(OUT_DIR, `${p.slug}.webp`);
      magick(pngPath, webpPath);
      execFileSync('rm', ['-f', pngPath]);
      console.log(`✓ ${p.slug}.webp`);
    }
    if (!noInject) inject(page, p);
  }

  await browser.close();
  console.log('\n✓ Concluído.');
}

main().catch((e) => { console.error(e); process.exit(1); });
