# CLAUDE.md — Blog Posts Libras.se

Este arquivo define os padrões exclusivos dos **artigos do blog**. O header aqui é diferente do site geral — é minimalista e focado em leitura. Para design system geral (variáveis CSS, cores, logo), consulte o `CLAUDE.md` na raiz.

---

## Estrutura de pasta

Cada post fica em sua própria subpasta:
```
blog/
  nome-do-post/
    index.html
    (imagens opcionais em ../../assets/img/blog/nome-do-post/)
```

---

## Fontes do Blog

Os posts usam Google Fonts — **não** as fontes locais do site principal.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,400;12..96,600;12..96,800&family=Lora:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet">
```

| Uso | Fonte |
|-----|-------|
| Títulos, labels, nav, UI | `Bricolage Grotesque` |
| Corpo do artigo, citações | `Lora` (serif) |

---

## Variáveis CSS do Blog

```css
:root {
  --teal-dark:   #1e6e6e;
  --teal-mid:    #2a9090;
  --teal-light:  #48bfb2;
  --teal-pale:   #a8e6df;
  --teal-bg:     #f0fafa;
  --ink:         #0f2a2a;
  --ink-soft:    #2d4f4f;
  --white:       #ffffff;
  --cream:       #f8fdfd;
  --orange:      #f4892a;
  --orange-soft: #fef3e8;
  --grey-light:  #e8f4f4;
  --radius:      16px;
  --radius-lg:   28px;
}
```

---

## CSS Base

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

body {
  font-family: 'Lora', Georgia, serif;
  background: var(--cream);
  color: var(--ink);
  line-height: 1.75;
  font-size: 18px;
  overflow-x: hidden;
}
```

---

## Barra de Progresso

```css
#progress-bar {
  position: fixed;
  top: 0; left: 0;
  height: 3px;
  width: 0%;
  background: linear-gradient(90deg, var(--teal-mid), var(--orange));
  z-index: 1000;
  transition: width 0.1s linear;
}
```

```html
<div id="progress-bar"></div>
```

---

## Header do Blog (nav minimalista)

O header do blog é **diferente do site principal** — sem menu completo, sem botão CTA, sem hamburguer. Apenas logo + tag de categoria.

### CSS do nav

```css
nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  padding: 18px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  backdrop-filter: blur(16px);
  background: rgba(240, 250, 250, 0.88);
  border-bottom: 1px solid rgba(42,144,144,0.12);
  transition: all 0.3s;
}

.nav-logo {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  font-size: 1.15rem;
  color: var(--teal-dark);
  letter-spacing: -0.02em;
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.nav-logo .hand-icon {
  width: 28px; height: 28px;
  background: linear-gradient(135deg, var(--teal-mid), var(--teal-light));
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 14px;
}

.nav-tag {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--teal-mid);
  background: var(--grey-light);
  padding: 5px 12px;
  border-radius: 20px;
}

@media (max-width: 700px) {
  nav { padding: 14px 20px; }
}
```

### HTML do nav

Substitua `[Categoria]` pela categoria real (ex: `Acessibilidade`, `Língua & Cultura`, `Tecnologia`).

```html
<nav>
  <a href="/" class="nav-logo">
    <span class="hand-icon">🤟</span>
    LIBRAS.SE
  </a>
  <span class="nav-tag">Blog · [Categoria]</span>
</nav>
```

---

## Hero Section

### Variante A — Gradiente puro (sem imagem)

Use quando não há foto de capa. Decorações opcionais: `.hero-letters` com letras flutuantes temáticas.

```css
.hero {
  min-height: 92vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: relative;
  overflow: hidden;
  padding: 120px 0 0;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(155deg,
    #0d3d3d 0%,
    #1e6e6e 35%,
    #2a9090 65%,
    #48bfb2 100%);
  z-index: 0;
}
```

```html
<section class="hero" aria-label="Cabeçalho do artigo">
  <div class="hero-bg"></div>
  <div class="hero-noise"></div>
  <div class="hero-grid-overlay"></div>
  <div class="hero-circles">
    <span></span><span></span><span></span>
  </div>
  <!-- hero-content abaixo -->
</section>
```

### Variante B — Imagem de fundo com overlay

Use quando há foto de capa. Coloque as imagens em `../../assets/img/blog/nome-do-post/`.

```css
.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-bg picture,
.hero-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
  display: block;
}

.hero-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(155deg,
    rgba(13,61,61,0.88) 0%,
    rgba(30,110,110,0.82) 35%,
    rgba(42,144,144,0.75) 65%,
    rgba(72,191,178,0.65) 100%);
}
```

```html
<div class="hero-bg">
  <picture>
    <source srcset="../../assets/img/blog/nome-do-post/imagem.avif" type="image/avif">
    <source srcset="../../assets/img/blog/nome-do-post/imagem.webp" type="image/webp">
    <img src="../../assets/img/blog/nome-do-post/imagem.png" alt="" aria-hidden="true" fetchpriority="high">
  </picture>
</div>
```

### Decorações do Hero (comuns às duas variantes)

```css
.hero-noise {
  position: absolute; inset: 0;
  opacity: 0.04; z-index: 1;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 200px;
}

.hero-grid-overlay {
  position: absolute; inset: 0; z-index: 1;
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 60px 60px;
}

.hero-circles { position: absolute; inset: 0; z-index: 1; overflow: hidden; pointer-events: none; }
.hero-circles span { position: absolute; border-radius: 50%; border: 1px solid rgba(255,255,255,0.08); }
.hero-circles span:nth-child(1) { width: 600px; height: 600px; top: -200px; right: -100px; animation: float1 14s ease-in-out infinite; }
.hero-circles span:nth-child(2) { width: 400px; height: 400px; top: 100px; right: 100px; border-color: rgba(255,255,255,0.05); animation: float1 18s ease-in-out infinite reverse; }
.hero-circles span:nth-child(3) { width: 200px; height: 200px; bottom: 80px; left: 10%; animation: float2 10s ease-in-out infinite; }

@keyframes float1 { 0%,100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-30px) scale(1.03); } }
@keyframes float2 { 0%,100% { transform: translateY(0) translateX(0); } 50% { transform: translateY(-15px) translateX(10px); } }
```

### Conteúdo do Hero

```css
.hero-content {
  position: relative; z-index: 10;
  max-width: 860px; margin: 0 auto;
  padding: 0 40px 80px; width: 100%;
}

.hero-kicker {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--teal-pale);
  margin-bottom: 28px; opacity: 0;
  animation: fadeUp 0.8s 0.2s forwards;
}
.hero-kicker::before { content: ''; width: 24px; height: 2px; background: var(--orange); display: inline-block; }

.hero-title {
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: clamp(2.2rem, 5vw, 4rem); line-height: 1.08;
  color: var(--white); letter-spacing: -0.03em;
  margin-bottom: 24px; opacity: 0;
  animation: fadeUp 0.9s 0.4s forwards;
}
.hero-title em { font-style: normal; color: var(--teal-pale); }

.hero-subtitle {
  font-family: 'Lora', serif; font-style: italic; font-size: 1.15rem;
  color: rgba(255,255,255,0.75); max-width: 580px; line-height: 1.7;
  margin-bottom: 48px; opacity: 0;
  animation: fadeUp 0.9s 0.6s forwards;
}

.hero-meta { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; opacity: 0; animation: fadeUp 0.9s 0.8s forwards; }
.meta-badge { font-family: 'Bricolage Grotesque', sans-serif; font-size: 0.78rem; font-weight: 500; color: rgba(255,255,255,0.65); display: flex; align-items: center; gap: 6px; }
.meta-badge svg { opacity: 0.6; }

.hero-scroll-hint { position: absolute; bottom: 32px; left: 50%; transform: translateX(-50%); z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 6px; opacity: 0; animation: fadeIn 1s 1.5s forwards; }
.scroll-dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.5); animation: scrollBounce 1.5s ease-in-out infinite; }
.scroll-dot:nth-child(2) { animation-delay: 0.2s; opacity: 0.3; }
.scroll-dot:nth-child(3) { animation-delay: 0.4s; opacity: 0.15; }

@keyframes scrollBounce { 0%,100% { transform: translateY(0); opacity: 0.5; } 50% { transform: translateY(6px); opacity: 0.9; } }
@keyframes fadeUp { to { opacity: 1; transform: translateY(0); } from { opacity: 0; transform: translateY(24px); } }
@keyframes fadeIn { to { opacity: 1; } from { opacity: 0; } }

@media (max-width: 700px) {
  .hero-content { padding: 0 20px 70px; }
}
```

```html
<div class="hero-content">
  <div class="hero-kicker" aria-label="Categoria do artigo">[Categoria completa]</div>
  <h1 class="hero-title">
    Título principal<br>
    com <em>destaque em teal</em>
  </h1>
  <p class="hero-subtitle">
    Subtítulo descritivo em itálico — resume o artigo em uma frase.
  </p>
  <div class="hero-meta">
    <span class="meta-badge">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
      [DD de Mês de AAAA]
    </span>
    <span class="meta-badge">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      [N] min de leitura
    </span>
    <span class="meta-badge">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      LIBRAS.SE
    </span>
  </div>
</div>

<div class="hero-scroll-hint" aria-hidden="true">
  <span class="scroll-dot"></span>
  <span class="scroll-dot"></span>
  <span class="scroll-dot"></span>
</div>
```

---

## Article Wrapper

```css
.article-wrapper {
  max-width: 760px;
  margin: 0 auto;
  padding: 80px 40px 120px;
}

@media (max-width: 700px) {
  .article-wrapper { padding: 50px 20px 80px; }
}
```

```html
<main class="article-wrapper" id="article">
  <!-- componentes do artigo aqui -->
</main>
```

---

## Scroll Reveal

Adicione `.reveal` a qualquer bloco para animá-lo na entrada. O JS cuida do resto.

```css
.reveal { opacity: 0; transform: translateY(32px); transition: opacity 0.75s ease, transform 0.75s ease; }
.reveal.visible { opacity: 1; transform: translateY(0); }
```

---

## Componentes do Artigo

### Section Label

```css
.section-label {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 0.68rem; font-weight: 700; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--teal-mid);
  display: flex; align-items: center; gap: 10px; margin-bottom: 20px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--teal-pale); max-width: 60px; }
```

```html
<p class="section-label">Título da seção</p>
```

### Body Text

```css
.body-text { font-family: 'Lora', serif; font-size: 1.05rem; color: var(--ink-soft); line-height: 1.85; margin-bottom: 28px; }
.body-text strong { color: var(--ink); font-weight: 600; }
```

```html
<p class="body-text">Texto corrido. Use <strong>negrito</strong> e <mark>destaque</mark>.</p>
```

### Drop Cap (primeiro parágrafo)

```css
.drop-cap::first-letter {
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: 3.8em; line-height: 0.75; float: left;
  margin-right: 8px; margin-top: 6px; color: var(--teal-dark);
}
```

```html
<p class="body-text drop-cap">Primeiro parágrafo com inicial maior...</p>
```

### Mark (texto em destaque)

```css
mark { background: linear-gradient(120deg, rgba(72,191,178,0.25) 0%, rgba(72,191,178,0.1) 100%); color: inherit; border-radius: 3px; padding: 1px 4px; }
```

### Pull Quote

```css
.pull-quote { margin: 56px 0; padding: 40px 48px; background: linear-gradient(135deg, var(--teal-dark) 0%, var(--teal-mid) 100%); border-radius: var(--radius-lg); position: relative; overflow: hidden; }
.pull-quote::before { content: '"'; position: absolute; top: -20px; left: 24px; font-family: 'Bricolage Grotesque', sans-serif; font-size: 10rem; font-weight: 800; color: rgba(255,255,255,0.07); line-height: 1; pointer-events: none; }
.pull-quote p { font-family: 'Lora', serif; font-style: italic; font-size: 1.3rem; color: var(--white); line-height: 1.65; position: relative; z-index: 1; }
.pull-quote p strong { color: var(--teal-pale); font-style: normal; }

@media (max-width: 700px) { .pull-quote { padding: 28px 28px; } .pull-quote p { font-size: 1.1rem; } }
```

```html
<blockquote class="pull-quote reveal">
  <p>Citação em destaque com <strong>parte em teal claro</strong>.</p>
</blockquote>
```

### Highlight Box (laranja)

```css
.highlight-box { margin: 40px 0; padding: 32px 36px; background: var(--orange-soft); border-left: 4px solid var(--orange); border-radius: 0 var(--radius) var(--radius) 0; }
.highlight-box p { font-family: 'Lora', serif; font-size: 1rem; color: #5a3200; line-height: 1.75; }
.highlight-box .highlight-label { font-family: 'Bricolage Grotesque', sans-serif; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--orange); margin-bottom: 10px; display: block; }
```

```html
<div class="highlight-box reveal">
  <span class="highlight-label">Ponto-chave</span>
  <p>Informação importante que merece atenção especial.</p>
</div>
```

### Info / Law Callout (teal)

Use para informações contextuais ou referências legais.

```css
.info-callout, .law-callout { margin: 48px 0; display: flex; gap: 24px; align-items: flex-start; background: var(--teal-bg); border: 1px solid var(--teal-pale); border-radius: var(--radius); padding: 32px 36px; }
.info-icon, .law-icon { width: 52px; height: 52px; background: linear-gradient(135deg, var(--teal-mid), var(--teal-light)); border-radius: 14px; display: grid; place-items: center; font-size: 22px; flex-shrink: 0; }
.info-content h4, .law-content h4 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 0.95rem; color: var(--teal-dark); margin-bottom: 8px; letter-spacing: -0.01em; }
.info-content p, .law-content p { font-family: 'Lora', serif; font-size: 0.9rem; color: var(--ink-soft); line-height: 1.7; }

@media (max-width: 700px) { .info-callout, .law-callout { flex-direction: column; gap: 16px; padding: 24px; } }
```

```html
<div class="info-callout reveal">
  <div class="info-icon">📚</div>
  <div class="info-content">
    <h4>Título do callout</h4>
    <p>Conteúdo informativo ou contexto adicional sobre o tema.</p>
  </div>
</div>
```

### Grid de Cards (2 colunas)

Use para casos de uso, vantagens, funcionalidades, etc.

```css
.use-grid, .advantage-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 48px 0; }
.use-card, .advantage-card { background: var(--white); border: 1px solid var(--grey-light); border-radius: var(--radius); padding: 28px; position: relative; overflow: hidden; transition: transform 0.3s, box-shadow 0.3s; }
.use-card:hover, .advantage-card:hover { transform: translateY(-3px); box-shadow: 0 10px 32px rgba(30,110,110,0.1); }
.use-card::before, .advantage-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--teal-mid), var(--teal-light)); }
.use-card .card-icon, .advantage-card .card-icon { width: 44px; height: 44px; background: var(--teal-bg); border-radius: 12px; display: grid; place-items: center; margin-bottom: 16px; font-size: 20px; }
.use-card h3, .advantage-card h3 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 0.95rem; color: var(--ink); margin-bottom: 10px; letter-spacing: -0.01em; }
.use-card p, .advantage-card p { font-family: 'Lora', serif; font-size: 0.85rem; color: var(--ink-soft); line-height: 1.7; }

@media (max-width: 700px) { .use-grid, .advantage-grid { grid-template-columns: 1fr; } }
```

```html
<div class="use-grid reveal">
  <div class="use-card">
    <div class="card-icon">🎯</div>
    <h3>Título do card</h3>
    <p>Descrição do caso de uso ou funcionalidade.</p>
  </div>
  <!-- repita para outros cards -->
</div>
```

### Case Study (bloco escuro)

```css
.case-study { margin: 56px 0; background: linear-gradient(150deg, #0a2828, #1e6e6e); border-radius: var(--radius-lg); padding: 48px; position: relative; overflow: hidden; }
.case-study::after { content: 'CASO REAL'; position: absolute; top: 20px; right: 24px; font-family: 'Bricolage Grotesque', sans-serif; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.16em; color: rgba(255,255,255,0.25); }
.case-study h3 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.5rem; color: var(--teal-pale); letter-spacing: -0.02em; margin-bottom: 16px; }
.case-study p { font-family: 'Lora', serif; color: rgba(255,255,255,0.8); font-size: 0.95rem; line-height: 1.8; }
.case-study .case-tag { display: inline-block; background: rgba(72,191,178,0.2); border: 1px solid rgba(72,191,178,0.35); color: var(--teal-pale); font-family: 'Bricolage Grotesque', sans-serif; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; padding: 5px 12px; border-radius: 20px; margin-bottom: 20px; }

@media (max-width: 700px) { .case-study { padding: 32px 24px; } }
```

```html
<div class="case-study reveal">
  <span class="case-tag">📍 Contexto do caso</span>
  <h3>Título do caso de estudo</h3>
  <p>Descrição do caso real ou curiosidade. Use <strong style="color: #a8e6df;">negrito teal</strong> para destaques.</p>
</div>
```

### Process Steps / Word Steps (timeline vertical)

```css
.process-steps, .word-steps { margin: 48px 0; display: flex; flex-direction: column; gap: 4px; position: relative; }
.process-steps::before, .word-steps::before { content: ''; position: absolute; left: 23px; top: 24px; bottom: 24px; width: 1px; background: linear-gradient(to bottom, var(--teal-mid), var(--teal-pale)); z-index: 0; }
.step, .wstep { display: flex; gap: 20px; align-items: flex-start; background: var(--white); border: 1px solid var(--grey-light); border-radius: var(--radius); padding: 20px 24px; position: relative; z-index: 1; transition: transform 0.25s, box-shadow 0.25s; }
.step:hover, .wstep:hover { transform: translateX(6px); box-shadow: 0 6px 24px rgba(30,110,110,0.08); }
.step-num { width: 36px; height: 36px; background: linear-gradient(135deg, var(--teal-mid), var(--teal-light)); border-radius: 10px; display: grid; place-items: center; font-family: 'Bricolage Grotesque', sans-serif; font-size: 0.85rem; font-weight: 800; color: white; flex-shrink: 0; }
.wstep-icon { width: 36px; height: 36px; background: linear-gradient(135deg, var(--teal-mid), var(--teal-light)); border-radius: 10px; display: grid; place-items: center; font-size: 16px; flex-shrink: 0; }
.step-body h4, .wstep-body h4 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 0.9rem; color: var(--ink); margin-bottom: 4px; letter-spacing: -0.01em; }
.step-body p, .wstep-body p { font-family: 'Lora', serif; font-size: 0.84rem; color: var(--ink-soft); line-height: 1.6; }
```

```html
<!-- Com números (process-steps) -->
<div class="process-steps reveal">
  <div class="step">
    <div class="step-num">01</div>
    <div class="step-body">
      <h4>Título do passo</h4>
      <p>Descrição do que acontece nesse passo.</p>
    </div>
  </div>
</div>

<!-- Com ícones (word-steps) -->
<div class="word-steps reveal">
  <div class="wstep">
    <div class="wstep-icon">🔤</div>
    <div class="wstep-body">
      <h4>Título do passo</h4>
      <p>Descrição do que acontece nesse passo.</p>
    </div>
  </div>
</div>
```

### Stat Row

```css
.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 48px 0; }
.stat-card { background: var(--white); border: 1px solid var(--grey-light); border-radius: var(--radius); padding: 28px 24px; text-align: center; box-shadow: 0 4px 24px rgba(30,110,110,0.06); transition: transform 0.3s, box-shadow 0.3s; cursor: default; }
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(30,110,110,0.12); }
.stat-number { font-family: 'Bricolage Grotesque', sans-serif; font-size: 2.4rem; font-weight: 800; color: var(--teal-dark); letter-spacing: -0.03em; line-height: 1; display: block; margin-bottom: 8px; }
.stat-desc { font-family: 'Lora', serif; font-size: 0.8rem; color: var(--ink-soft); line-height: 1.5; }

@media (max-width: 700px) { .stat-row { grid-template-columns: 1fr; gap: 14px; } }
```

```html
<div class="stat-row reveal">
  <div class="stat-card">
    <span class="stat-number" id="stat1">42</span>
    <span class="stat-desc">descrição do dado estatístico</span>
  </div>
  <!-- até 3 cards -->
</div>
```

### Video Block (iframe YouTube)

```css
.video-block { margin: 48px 0; border-radius: var(--radius-lg); overflow: hidden; position: relative; box-shadow: 0 20px 60px rgba(30,110,110,0.18); }
.video-block iframe { width: 100%; aspect-ratio: 16/9; border: none; display: block; }
.video-caption { background: var(--teal-dark); padding: 16px 24px; display: flex; align-items: center; gap: 12px; }
.video-caption .play-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--orange); animation: pulse 2s ease-in-out infinite; }
.video-caption span { font-family: 'Bricolage Grotesque', sans-serif; font-size: 0.78rem; font-weight: 600; color: rgba(255,255,255,0.7); letter-spacing: 0.04em; }
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } }
```

```html
<div class="video-block reveal">
  <iframe
    src="https://www.youtube.com/embed/VIDEO_ID"
    title="Descrição do vídeo"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen loading="lazy">
  </iframe>
  <div class="video-caption">
    <span class="play-dot"></span>
    <span>🎬 Legenda do vídeo</span>
  </div>
</div>
```

### Video Showcase (vídeo nativo / mp4 / webm)

```css
.video-showcase { margin: 48px 0; border-radius: var(--radius-lg); overflow: hidden; box-shadow: 0 20px 60px rgba(30,110,110,0.22); background: #0a2020; position: relative; }
.video-tag { position: absolute; top: 14px; left: 14px; z-index: 10; font-family: 'Bricolage Grotesque', sans-serif; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #fff; background: rgba(14,58,58,0.82); border: 1px solid rgba(72,191,178,0.38); padding: 6px 13px; border-radius: 20px; backdrop-filter: blur(10px); }
.video-showcase video { width: 100%; display: block; max-height: 520px; object-fit: cover; }
.video-caption { font-family: 'Lora', serif; font-style: italic; font-size: 0.82rem; color: rgba(255,255,255,0.55); text-align: center; padding: 15px 28px 18px; background: #0d2828; margin: 0; line-height: 1.65; border-top: 1px solid rgba(72,191,178,0.12); }
```

```html
<div class="video-showcase reveal">
  <span class="video-tag">📹 Rótulo do vídeo</span>
  <video controls playsinline preload="metadata" poster="caminho/para/poster.webp">
    <source src="caminho/para/video.webm" type="video/webm">
  </video>
  <p class="video-caption">Legenda descritiva do vídeo.</p>
</div>
```

### Divider

```css
.divider { width: 60px; height: 3px; background: linear-gradient(90deg, var(--teal-mid), var(--teal-pale)); border-radius: 2px; margin: 48px 0; }
```

```html
<div class="divider reveal"></div>
```

### References

```css
.references { margin: 48px 0 0; padding: 32px 36px; background: var(--white); border: 1px solid var(--grey-light); border-radius: var(--radius); }
.references h4 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--teal-mid); margin-bottom: 16px; }
.references ol { padding-left: 20px; }
.references li { font-family: 'Lora', serif; font-size: 0.78rem; color: var(--ink-soft); line-height: 1.7; margin-bottom: 8px; }
.references li a { color: var(--teal-mid); text-decoration: underline; text-underline-offset: 3px; }
```

```html
<div class="references reveal">
  <h4>Referências</h4>
  <ol>
    <li>AUTOR, Nome. <em>Título da obra.</em> Editora, Ano.</li>
  </ol>
</div>
```

### CTA Block (final do artigo)

```css
.cta-block { margin-top: 72px; background: linear-gradient(145deg, var(--teal-dark), var(--teal-mid) 60%, var(--teal-light)); border-radius: var(--radius-lg); padding: 56px 48px; text-align: center; position: relative; overflow: hidden; }
.cta-block::before { content: ''; position: absolute; width: 300px; height: 300px; border-radius: 50%; background: rgba(255,255,255,0.04); top: -100px; right: -60px; }
.cta-block::after { content: ''; position: absolute; width: 200px; height: 200px; border-radius: 50%; background: rgba(255,255,255,0.04); bottom: -80px; left: -40px; }
.cta-block h2 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.8rem; color: var(--white); letter-spacing: -0.02em; margin-bottom: 16px; line-height: 1.2; position: relative; z-index: 1; }
.cta-block p { font-family: 'Lora', serif; font-style: italic; color: rgba(255,255,255,0.75); font-size: 1rem; max-width: 480px; margin: 0 auto 36px; position: relative; z-index: 1; }
.cta-btn { display: inline-flex; align-items: center; gap: 10px; background: var(--white); color: var(--teal-dark); font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 0.9rem; padding: 16px 32px; border-radius: 100px; text-decoration: none; position: relative; z-index: 1; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 24px rgba(0,0,0,0.2); }
.cta-btn:hover { transform: translateY(-2px) scale(1.02); box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
.cta-btn .arrow { display: inline-block; transition: transform 0.2s; }
.cta-btn:hover .arrow { transform: translateX(4px); }

@media (max-width: 700px) { .cta-block { padding: 40px 24px; } .cta-block h2 { font-size: 1.4rem; } }
```

```html
<div class="cta-block reveal">
  <h2>Título chamativo<br>do CTA</h2>
  <p>Descrição em itálico do que a Libras.se oferece relacionado ao tema do artigo.</p>
  <a href="https://libras.se/solucoes" class="cta-btn" target="_blank" rel="noopener">
    Texto do botão <span class="arrow">→</span>
  </a>
</div>
```

---

## Footer do Blog (simples)

```css
footer {
  background: var(--ink);
  color: rgba(255,255,255,0.5);
  text-align: center;
  padding: 40px;
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}

footer a {
  color: var(--teal-pale);
  text-decoration: none;
}
```

```html
<footer>
  <p>© 2026 <a href="https://libras.se">LIBRAS.SE</a> · Vídeos para todos · Florianópolis, Santa Catarina, Brasil</p>
  <p style="margin-top: 8px; font-size: 0.72rem;">CNPJ 22.943.329/0001-91 · <a href="URL_DO_ARTIGO_ORIGINAL" target="_blank" rel="noopener">Ver artigo original</a></p>
</footer>
```

---

## JavaScript Obrigatório

```javascript
// ── Progress bar ──
const bar = document.getElementById('progress-bar');
window.addEventListener('scroll', () => {
  const h = document.documentElement;
  const pct = (window.scrollY / (h.scrollHeight - h.clientHeight)) * 100;
  bar.style.width = pct + '%';
});

// ── Scroll reveal ──
const revealEls = document.querySelectorAll('.reveal');
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      io.unobserve(e.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

revealEls.forEach((el, i) => {
  el.style.transitionDelay = (i % 3 * 0.08) + 's';
  io.observe(el);
});

// ── Stat counters animados (opcional, se o post tiver .stat-row) ──
function animateCounter(el, target, suffix = '') {
  const duration = 1200;
  const start = performance.now();
  const isDecimal = target % 1 !== 0;
  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const val = target * ease;
    el.textContent = (isDecimal ? val.toFixed(1) : Math.floor(val)) + suffix;
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

const statObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      // Ajuste os IDs, valores e sufixos conforme os dados do post:
      // animateCounter(document.getElementById('stat1'), 42, '%');
      statObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.5 });

const statRow = document.querySelector('.stat-row');
if (statRow) statObserver.observe(statRow);
```

---

## Estrutura HTML completa do post

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[Título do post] | LIBRAS.SE</title>
<meta name="description" content="[Descrição SEO em ~155 caracteres]">
<meta name="keywords" content="[palavra-chave1, palavra-chave2, ...]">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,400;12..96,600;12..96,800&family=Lora:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet">

<style>
  /* variáveis + base + progress-bar + nav + hero + article-wrapper
     + reveal + todos os componentes usados + footer + responsive */
</style>
</head>
<body>

<div id="progress-bar"></div>

<nav>
  <a href="/" class="nav-logo">
    <span class="hand-icon">🤟</span>
    LIBRAS.SE
  </a>
  <span class="nav-tag">Blog · [Categoria]</span>
</nav>

<section class="hero" aria-label="Cabeçalho do artigo">
  <!-- hero-bg (gradiente ou imagem) -->
  <!-- hero-noise + hero-grid-overlay + hero-circles -->
  <!-- hero-content com kicker, title, subtitle, meta -->
  <!-- hero-scroll-hint -->
</section>

<main class="article-wrapper" id="article">
  <!-- componentes do artigo -->
</main>

<footer>
  <p>© 2026 <a href="https://libras.se">LIBRAS.SE</a> · Vídeos para todos · Florianópolis, Santa Catarina, Brasil</p>
  <p style="margin-top: 8px; font-size: 0.72rem;">CNPJ 22.943.329/0001-91 · <a href="URL_ORIGINAL" target="_blank" rel="noopener">Ver artigo original</a></p>
</footer>

<script>
  /* progress bar + scroll reveal + stat counters */
</script>
</body>
</html>
```

---

## Checklist antes de publicar

- [ ] `<title>` tem o título do post + ` | LIBRAS.SE`
- [ ] `<meta name="description">` preenchida
- [ ] `nav-tag` tem a categoria correta
- [ ] Data e tempo de leitura no `hero-meta` são reais
- [ ] Links do CTA apontam para páginas reais do Libras.se
- [ ] Footer tem o link do artigo original correto
- [ ] Imagens têm `.avif` + `.webp` + fallback `.png` (quando usar Variante B do hero)
- [ ] IDs dos `stat-number` batem com o `animateCounter` no JS
