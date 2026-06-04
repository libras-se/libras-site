# CLAUDE.md — Blog Libras.se

Guia único de criação e manutenção do **blog da Libras.se**: a página inicial
(`/blog/`), os posts e todas as regras editoriais, de SEO e de design.

> Para o design system geral do site (variáveis CSS, logo, fontes locais, header
> e footer canônicos) consulte o **`CLAUDE.md` da raiz**. Este arquivo só
> documenta o que é específico do blog e **não repete** o que já está na raiz —
> header, footer e JS de navegação são reaproveitados da raiz em todos os posts.

---

## 1. Os dois tipos de post (níveis de complexidade)

Todo post se encaixa em **um de dois níveis**. Escolha pelo tipo de conteúdo
**antes** de começar a escrever.

| | **Baixa complexidade** | **Alta complexidade** |
|---|---|---|
| **Quando usar** | Notícias, repostagens, factuais, releases, conteúdo curto e direto | Conteúdo evergreen, guias, explicações densas, pilar de SEO, autoridade temática |
| **Exemplos reais** | [`tradutor-de-libras-se-destaca-no-rock-in-rio`](./tradutor-de-libras-se-destaca-no-rock-in-rio/index.html), [`urnas-eletronicas-terao-video-com-libras`](./urnas-eletronicas-terao-video-com-libras/index.html) | [`voce-sabe-o-que-e-datilologia`](./voce-sabe-o-que-e-datilologia/index.html), [`libras-tem-sotaque-e-giria`](./libras-tem-sotaque-e-giria/index.html), [`libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado`](./libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado/index.html) |
| **Tipografia** | Museo Sans Rounded (`'M'`) — fontes locais do site | Bricolage Grotesque (títulos/UI) + Lora (corpo) — Google Fonts |
| **Tamanho típico** | ~250–450 linhas | ~700–1600 linhas |
| **Hero** | Título + subtítulo + meta, sem imagem de fundo dramática (`.pa-hero`) | Hero cheio com imagem/gradiente, kicker, scroll hint |
| **Componentes** | Texto, subtítulos, blockquote simples, figura, tags | Biblioteca completa: pull-quote, callouts, cards, stat-row, process-steps, vídeo, referências |
| **Tempo de leitura** | 1–3 min | 4 min ou mais |
| **Schema** | `BlogPosting` + `BreadcrumbList` | `BlogPosting` + `BreadcrumbList` (+ `FAQPage` se houver FAQ) |

**Regra de bolso:** se é uma notícia ou repostagem, vá de **baixa complexidade**.
Se é um conteúdo que queremos ranquear e manter por anos, vá de **alta complexidade**.

### O que é IGUAL nos dois níveis (regras universais)

1. **Header e footer canônicos do site** (da raiz `CLAUDE.md`), com o badge `Blog`
   no logo e `aria-current="page"` no link do Blog — ver §4.
2. **Footer da matéria com posts relacionados** ("Leia mais no blog") — ver §8.
3. **Citação ao Glossário** sempre que um termo for mencionado — ver §6.
4. **Imagens vindas do banco editorial** quando não houver foto própria — ver §7.
5. **Botão flutuante de WhatsApp** (`.wppf`) e **skip-link**.
6. `<html lang="pt-BR">`, `<meta>` SEO completos, OG/Twitter, canonical, JSON-LD.
7. Cada post é citado na **home do blog** com seu card e `data-cat` — ver §5.

---

## 2. Estrutura de pasta

Cada post vive na própria subpasta, sempre como `index.html` (URL limpa):

```
blog/
  index.html                       ← página inicial do blog (§5)
  CLAUDE.md                        ← este guia
  nome-do-post-em-kebab-case/
    index.html
```

Imagens próprias do post:

```
assets/img/blog/nome-do-post/
  nome-do-post.avif   (preferencial)
  nome-do-post.webp   (fallback moderno)
  nome-do-post.png|jpg (fallback final)
```

Slug = título em kebab-case, sem acentos, sem stopwords desnecessárias.

---

## 3. Metadados obrigatórios (bloco editorial)

Antes de escrever o HTML, defina mentalmente (ou em comentário no topo) estes
campos. Eles alimentam `<title>`, `<meta>`, OG/Twitter e o JSON-LD:

```yaml
title:                  # H1 do post
seo_title:              # <title> — título + " | Blog Libras.se"
meta_description:        # ~155 caracteres, com a palavra-chave principal
slug:                   # kebab-case
canonical_url:          # https://libras.se/blog/<slug>/
category:               # Língua & Cultura | Acessibilidade | Instrucional | Direitos | Tecnologia | Educação
tags:                   # 3–6 tags; as que existem no glossário viram link
primary_keyword:
secondary_keywords:
search_intent:          # informacional | navegacional | transacional
reading_time:           # "N min de leitura"
author:                 # "Libras.se" ou nome da pessoa
published_at:           # AAAA-MM-DD
updated_at:
cover_image:            # /assets/img/blog/<slug>/<slug>.webp
cover_alt:
og_title: / og_description: / og_image:
twitter_title: / twitter_description: / twitter_image:
schema_type:            # BlogPosting (+ FAQPage se houver FAQ)
related_glossary_terms: # termos a linkar (ver §6)
internal_links:         # outras páginas/posts a referenciar
external_references:    # fontes externas
cta_type:               # vídeo | soluções | jogo | glossário
```

### `<head>` — esqueleto comum aos dois níveis

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2GD3C5XV1L"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-2GD3C5XV1L');</script>
<title>[Título] | Blog Libras.se</title>
<meta name="description" content="[~155 caracteres]">
<meta name="keywords" content="[palavras-chave]">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="https://libras.se/blog/[slug]/">
<meta property="og:type" content="article">
<meta property="og:url" content="https://libras.se/blog/[slug]/">
<meta property="og:title" content="[Título]">
<meta property="og:description" content="[Descrição]">
<meta property="og:image" content="https://libras.se/assets/img/blog/[slug]/[slug].webp">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="675">
<meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="Libras.se">
<meta property="article:published_time" content="[ISO]">
<meta property="article:modified_time" content="[ISO]">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@librasse">
<meta name="twitter:title" content="[Título]">
<meta name="twitter:description" content="[Descrição]">
<meta name="twitter:image" content="https://libras.se/assets/img/blog/[slug]/[slug].webp">
<meta name="theme-color" content="#4fd1c5">
<link rel="icon" href="https://libras.se/assets/img/favicon/FAVICONpng.png">
```

### JSON-LD obrigatório (os dois níveis)

Dois blocos: `BlogPosting` + `BreadcrumbList`. Em posts de alta complexidade com
perguntas frequentes, adicione um terceiro bloco `FAQPage`.

```html
<script type="application/ld+json">
{ "@context":"https://schema.org","@type":"BlogPosting",
  "headline":"[Título]","description":"[Descrição]",
  "image":{"@type":"ImageObject","url":"https://libras.se/assets/img/blog/[slug]/[slug].webp","width":1200,"height":675},
  "author":{"@type":"Organization","name":"Libras.se"},
  "publisher":{"@type":"Organization","name":"Libras.se","url":"https://libras.se","logo":{"@type":"ImageObject","url":"https://libras.se/assets/img/favicon/FAVICONpng.png"}},
  "datePublished":"[ISO]","dateModified":"[ISO]","inLanguage":"pt-BR",
  "mainEntityOfPage":{"@type":"WebPage","@id":"https://libras.se/blog/[slug]/"} }
</script>
<script type="application/ld+json">
{ "@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {"@type":"ListItem","position":1,"name":"Início","item":"https://libras.se/"},
  {"@type":"ListItem","position":2,"name":"Blog","item":"https://libras.se/blog/"},
  {"@type":"ListItem","position":3,"name":"[Título]","item":"https://libras.se/blog/[slug]/"}
]}
</script>
```

---

## 4. Header do site no blog (com a marcação de conteúdo)

O blog **usa o header e o footer canônicos do site** (copie da raiz `CLAUDE.md`),
com duas marcações específicas do blog:

- **Badge `Blog` ao lado do logo** — a mesma "marcação de conteúdo" usada na home
  do blog, que identifica que estamos na seção de conteúdo:

  ```html
  <a href="/" class="nlogo" aria-label="Libras.se — Página inicial">
    <span class="nlogo-txt" aria-hidden="true">LIBRAS.SE</span>
    <span class="nsub" aria-hidden="true">Blog</span>
  </a>
  ```
  ```css
  .nlogo{display:flex;align-items:center;gap:10px}
  .nsub{font-size:.63rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--p3);background:rgba(79,209,197,.1);border:1px solid rgba(79,209,197,.2);border-radius:var(--rpill);padding:4px 10px;white-space:nowrap}
  ```

- **`aria-current="page"` no item Blog** do menu, com underline permanente:

  ```html
  <li><a href="/blog/" aria-current="page">Blog</a></li>
  ```
  ```css
  .nlinks a[aria-current="page"]{color:var(--p1)}
  .nlinks a[aria-current="page"]::after{width:100%}
  ```

No menu mobile (`.mob`) e nos links da nav, o link do Blog aponta para `/blog/`
(não para `https://libras.se/blog`). O texto do WhatsApp flutuante usa
`...estava no blog do Libras.se...`.

> **Alta complexidade:** o header/footer são os mesmos, mas reescritos com
> `font-family:'Bricolage Grotesque'` para combinar com a tipografia editorial
> (ver `voce-sabe-o-que-e-datilologia`). A estrutura HTML e as cores são idênticas.

---

## 5. A página inicial do blog (`/blog/index.html`)

A home é o índice navegável de todos os posts. **Sempre que um post novo é
publicado, ele precisa ser adicionado aqui** (card + entrada no JSON-LD `ItemList`).

### Anatomia da home

```
<head>  → schema @graph com Blog + BreadcrumbList + ItemList (TODOS os posts)
<nav>   → header canônico com badge Blog + aria-current
<main>
  <header class="bl-hero">      → título, tagline, busca, 3 feat-cards (Jogo/Sinais/Glossário)
  <section class="bl-featured">
    <div class="bl-sec-head">    → "Artigos publicados" + contador (#bl-post-count)
    <div class="bl-theme-bar">   → pílulas de filtro por tema (marcação de conteúdo)
    <div class="bl-featured__grid">
      <article class="bl-card bl-card--lg"> → POST DESTAQUE (mais recente)
      <div class="bl-featured__side">       → 2 cards médios
      ... <article class="bl-card bl-card--sm"> → demais posts (grade)
    <div id="bl-no-results">
<footer id="foot">              → footer canônico
```

### Marcação de conteúdo (categorias + busca)

Cada card carrega os atributos que alimentam o filtro e a busca:

```html
<article class="bl-card bl-card--sm rv"
  data-post
  data-search="palavras chave do título e tema para a busca textual"
  data-cat="acessibilidade instrucional língua"
  itemscope itemtype="https://schema.org/BlogPosting">
  <a href="/blog/[slug]/" class="bl-card__link-cover" aria-label="Ler artigo: [Título]"></a>
  <a href="/blog/[slug]/" class="bl-card__thumb" aria-label="[Título]">
    <picture>
      <source srcset="/assets/img/blog/[slug]/[slug].avif" type="image/avif">
      <source srcset="/assets/img/blog/[slug]/[slug].webp" type="image/webp">
      <img src="/assets/img/blog/[slug]/[slug].png" alt="[alt]" loading="lazy" decoding="async" itemprop="image" width="1200" height="675">
    </picture>
    <span class="bl-card__badge">[Categoria visível]</span>
  </a>
  <div class="bl-card__body">
    <div class="bl-card__meta"><time datetime="AAAA-MM-DD" itemprop="datePublished">DD mmm AAAA</time><span class="bl-card__dot"></span><span>N min de leitura</span></div>
    <h3 class="bl-card__title" itemprop="headline"><a href="/blog/[slug]/">[Título]</a></h3>
    <p class="bl-card__excerpt" itemprop="description">[Resumo]</p>
    <a href="/blog/[slug]/" class="bl-card__read">Ler artigo →</a>
  </div>
</article>
```

- **`data-cat`** recebe uma ou mais categorias-chave que batem com as pílulas de
  filtro. Categorias usadas hoje: `língua` (Língua & Cultura), `acessibilidade`,
  `instrucional`. Um post pode ter várias (`data-cat="acessibilidade instrucional língua"`).
- **`data-search`** repete título + termos para tornar o post localizável na busca.
- **`bl-card__badge`** é o rótulo visível (ex.: `Língua & Cultura`, `Direitos`,
  `Educação`, `Acessibilidade audiovisual`).
- O **post mais recente** ocupa o card grande (`bl-card--lg`) e os dois seguintes
  os cards laterais (`bl-featured__side`).

### Barra de filtros (pílulas)

```html
<div class="bl-theme-bar rv d1" role="group" aria-label="Filtrar por tema">
  <button class="bl-theme-pill active" data-filter="todos" type="button">Todos</button>
  <button class="bl-theme-pill" data-filter="língua" type="button">Língua &amp; Cultura</button>
  <button class="bl-theme-pill" data-filter="acessibilidade" type="button">Acessibilidade</button>
  <button class="bl-theme-pill" data-filter="instrucional" type="button">Instrucional</button>
</div>
```

### JS de busca + filtro (já presente na home — manter)

```javascript
const searchInput = document.getElementById('bl-search-input');
const allPosts    = document.querySelectorAll('[data-post]');
const pills       = document.querySelectorAll('.bl-theme-pill');
const noResults   = document.getElementById('bl-no-results');
const countEl     = document.getElementById('bl-post-count');
const sideEl      = document.getElementById('bl-featured-side');
let activeFilter  = 'todos';
let scrolled      = false;

function filterPosts() {
  const q = searchInput.value.toLowerCase().trim();
  let visible = 0;
  allPosts.forEach(post => {
    const text = ((post.dataset.search || '') + ' ' + (post.querySelector('.bl-card__title')?.textContent || '')).toLowerCase();
    const cat  = (post.dataset.cat || '').toLowerCase();
    const show = (!q || text.includes(q)) && (activeFilter === 'todos' || cat.includes(activeFilter));
    post.style.display = show ? '' : 'none';
    if (show) visible++;
  });
  if (sideEl) {
    const sideVisible = [...sideEl.querySelectorAll('[data-post]')].some(p => p.style.display !== 'none');
    sideEl.style.display = sideVisible ? '' : 'none';
  }
  noResults.classList.toggle('show', visible === 0);
  countEl.textContent = visible + (visible === 1 ? ' publicação' : ' publicações');
  if (q.length >= 1 && !scrolled) { scrolled = true; document.getElementById('posts').scrollIntoView({behavior:'smooth',block:'start'}); }
  if (!q) scrolled = false;
}
searchInput.addEventListener('input', filterPosts);
pills.forEach(pill => pill.addEventListener('click', () => {
  pills.forEach(p => p.classList.remove('active'));
  pill.classList.add('active');
  activeFilter = pill.dataset.filter;
  filterPosts();
}));
```

### Ao publicar um post, atualizar na home:

1. Adicionar o `<article class="bl-card ...">` na posição correta (o mais novo
   assume o card grande; rebaixe os anteriores).
2. Atualizar o contador estático `#bl-post-count` ("N publicações").
3. Adicionar uma entrada no JSON-LD `ItemList` (campo `position`, `headline`,
   `description`, `url`, `datePublished`).

---

## 6. Citação obrigatória ao Glossário

**Sempre que um termo da área aparecer no texto de um post, ele deve virar um
hyperlink para o Glossário.** A fonte única dos termos é
[`/glossario/termos.csv`](../glossario/termos.csv).

- Linke a **primeira ocorrência** do termo em cada seção relevante (não repita
  em todo parágrafo — evite spam de links).
- A URL é a da coluna `url` do CSV (`https://libras.se/glossario/<slug>/`); em
  posts use o caminho relativo `/glossario/<slug>/`.
- Use o termo natural na frase como texto âncora:
  `...traduzia para a <a href="/glossario/libras/">Língua Brasileira de Sinais</a>...`
- As **tags** do post que coincidam com termos do glossário também viram link
  (ex.: `<a class="pa-tag" href="/glossario/til-tils/">#tils</a>`).

### Termos disponíveis (consulte sempre o CSV — pode crescer)

| Termo | slug | Categoria |
|---|---|---|
| Datilologia | `datilologia` | linguística |
| TIL / TILS | `til-tils` | interpretação |
| Configuração de Mão (CM) | `configuracao-de-mao` | linguística |
| LBI | `lbi` | legislação |
| Libras | `libras` | linguística |
| Janela de Libras | `janela-de-libras` | tecnologia |
| Espaço de Sinalização | `espaco-de-sinalizacao` | linguística |
| Expressão Não-Manual (ENM) | `expressao-nao-manual` | linguística |
| Interpretação Simultânea | `interpretacao-simultanea` | interpretação |
| Surdo | `surdo` | cultura |
| Comunidade Surda | `comunidade-surda` | cultura |
| População Surda | `populacao-surda` | cultura |
| Acessibilidade Audiovisual | `acessibilidade-audiovisual` | tecnologia |
| Interpretação Remota (VRI) | `interpretacao-remota` | tecnologia |
| Sinal Soletrado | `sinal-soletrado` | linguística |
| Ponto de Articulação (PA) | `ponto-de-articulacao` | linguística |
| Lei 10.436/2002 | `lei-10436` | legislação |
| INES | `ines` | cultura |
| Decreto 5.626/2005 | `decreto-5626` | legislação |
| Movimento (MOV) | `movimento` | linguística |
| Orientação de Mão | `orientacao-de-mao` | linguística |
| Bilinguismo | `bilinguismo` | cultura |
| LSE: Legenda para Surdos | `lse` | tecnologia |
| Audiodescrição (AD) | `audiodescricao` | tecnologia |
| FENEIS | `feneis` | cultura |
| Glosa | `glosa` | linguística |

> Antes de linkar, confirme que o `slug` ainda existe no CSV e que `status` é
> `publicado`. Se um termo importante aparece e **não** existe no glossário,
> registre como candidato a novo verbete (não invente URL).

---

## 7. Banco de imagens editorial

Quando o post não tiver foto própria de qualidade, use o banco editorial da
Libras.se. Fonte única: [`/assets/img/banco-editorial/imagens.csv`](../assets/img/banco-editorial/imagens.csv).

**Como escolher uma imagem:**
1. Procure o tema do post nas colunas `uso`, `alt`, `meta_descricao` e `motivo`.
2. Use o caminho da coluna **`arquivo`** exatamente como está
   (ex.: `/assets/img/banco-editorial/LIBRAS.SE_2.webp`).
3. Use a coluna **`alt`** como texto alternativo da `<img>`.
4. Use a coluna **`meta_descricao`** como base para a metadescrição da imagem.

São 12 imagens (`LIBRAS.SE_1` … `LIBRAS.SE_12`), majoritariamente de intérpretes
em estúdio/chroma key, equipe e bastidores de produção acessível — ideais para
posts sobre tradução em Libras, gravação, tecnologia e a própria Libras.se. Cada
imagem tem um `.md` companheiro com a descrição completa.

> Fotos jornalísticas de notícias (Tier baixo) costumam ter imagem própria em
> `/assets/img/blog/<slug>/`. O banco editorial é o fallback institucional.

---

## 8. Fechamento "Com Barra" — obrigatório em todos os posts

Todo post termina com a sequência completa **"Com Barra"** antes do footer
canônico do site. Ordem obrigatória:

1. `.pa-tags` — tags em `#` com barra divisória superior (`border-top`)
2. `.pa-cta` — bloco escuro com CTA "Precisa do seu conteúdo em Libras?"
3. `.pa-actions` — 3 cards de recursos com **ícones SVG** (sem emojis): Jogo / Vocabulário / Glossário
4. `.pa-related` — 3 artigos variados ("Leia mais no blog") + botão lateral "Ver todos os posts"
5. `<footer id="foot">` — footer canônico do site

> **Posts relacionados variados:** escolha 3 artigos de temas **diferentes** entre si e diferentes do tema principal do post atual. Diversidade de categoria aumenta o tempo de permanência.

```html
<section class="pa-cta" aria-label="Soluções e recursos da Libras.se">
  <div class="pa-cta__lead rv">
    <h2>Precisa do seu conteúdo em Libras?</h2>
    <p>A Libras.se traduz seu conteúdo para Libras com intérpretes reais e entrega editada, pronta para publicar.</p>
    <div class="pa-cta__btns">
      <a href="https://huet.libras.se/" class="btn bw" target="_blank" rel="noopener noreferrer">Enviar vídeo agora</a>
      <a href="https://libras.se/solucoes" class="btn bp">Conhecer soluções</a>
    </div>
  </div>
  <div class="pa-actions">
    <a href="/jogo/" class="pa-act rv">
      <span class="pa-act__ic">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="11" x2="15" y2="11"/><line x1="18" y1="13" x2="18" y2="13"/><path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59c-.006.052-.01.101-.017.152C2.604 9.416 2 14.456 2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.414-1.414A2 2 0 0 1 9.828 16h4.344a2 2 0 0 1 1.414.586L17 18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.545-.604-6.584-.685-7.258-.007-.05-.011-.1-.017-.151A4 4 0 0 0 17.32 5z"/></svg>
      </span>
      <span class="pa-act__t">Joguinho de Libras</span>
      <span class="pa-act__d">Descubra o sinal do dia e aprenda brincando.</span>
      <span class="pa-act__go">Jogar agora →</span>
    </a>
    <a href="/sinal/" class="pa-act rv">
      <span class="pa-act__ic">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"/><path d="M14 10.5V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2"/><path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/></svg>
      </span>
      <span class="pa-act__t">Vocabulário</span>
      <span class="pa-act__d">Consulte sinais e amplie seu vocabulário em Libras.</span>
      <span class="pa-act__go">Ver sinais →</span>
    </a>
    <a href="/glossario/" class="pa-act rv">
      <span class="pa-act__ic">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
      </span>
      <span class="pa-act__t">Glossário</span>
      <span class="pa-act__d">Termos da área com definições claras e verificadas.</span>
      <span class="pa-act__go">Consultar →</span>
    </a>
  </div>
</section>

<section class="pa-related" aria-label="Mais posts do blog">
  <div class="pa-related__head">
    <h2>Leia mais no blog</h2>
    <a href="/blog/" class="btn bp" style="font-size:.78rem;padding:9px 18px">Ver todos os posts →</a>
  </div>
  <div class="pa-rel-grid">
    <a class="pa-rel" href="/blog/[slug-1]/">
      <span class="pa-rel__thumb"><img src="/assets/img/blog/[slug-1]/[slug-1].webp" alt="[Título 1]" loading="lazy" decoding="async" width="1200" height="675"></span>
      <span class="pa-rel__b"><span class="pa-rel__t">[Título do post 1 — tema diferente do post atual]</span></span>
    </a>
    <a class="pa-rel" href="/blog/[slug-2]/">
      <span class="pa-rel__thumb"><img src="/assets/img/blog/[slug-2]/[slug-2].webp" alt="[Título 2]" loading="lazy" decoding="async" width="1200" height="675"></span>
      <span class="pa-rel__b"><span class="pa-rel__t">[Título do post 2 — tema diferente dos outros]</span></span>
    </a>
    <a class="pa-rel" href="/blog/[slug-3]/">
      <span class="pa-rel__thumb"><img src="/assets/img/blog/[slug-3]/[slug-3].webp" alt="[Título 3]" loading="lazy" decoding="async" width="1200" height="675"></span>
      <span class="pa-rel__b"><span class="pa-rel__t">[Título do post 3 — tema diferente dos outros]</span></span>
    </a>
  </div>
</section>
```

CSS de apoio (Tier baixo / Museo Sans): ver `tradutor-de-libras-se-destaca-no-rock-in-rio`
(`.pa-cta`, `.pa-actions`, `.pa-act`, `.pa-related`, `.pa-rel`). Em alta
complexidade o bloco equivalente aparece como `.blog-more` antes do `#foot`.

Depois desse bloco, vem **o footer canônico do site** (`<footer id="foot">`,
copiado da raiz `CLAUDE.md`), com os links do Blog apontando para `/blog/`.

---

# TIER BAIXO — Post de baixa complexidade

Base: **design system principal do site** (fonte `'M'` Museo Sans Rounded,
variáveis `:root` da raiz). Header e footer canônicos. Artigo no wrapper `.pa-wrap`.
Referência viva: `tradutor-de-libras-se-destaca-no-rock-in-rio/index.html`.

### CSS do artigo (`pa-*`)

```css
main{padding-top:80px}
.pa-wrap{max-width:760px;margin:0 auto;padding:0 40px}
.pa-hero{padding:54px 0 30px}
.pa-title{font-family:'M',sans-serif;font-weight:900;font-size:clamp(1.85rem,4.2vw,2.95rem);line-height:1.12;letter-spacing:-.025em;color:var(--p1);margin:18px 0 16px}
.pa-sub{font-size:1.12rem;font-weight:300;color:var(--txs);line-height:1.6;margin-bottom:24px}
.pa-meta{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:.82rem;color:var(--txm)}
.pa-meta strong{color:var(--txs);font-weight:700}
.pa-meta .dot{width:3px;height:3px;border-radius:50%;background:var(--txm)}
.pa-fig{margin:6px 0 36px;border-radius:var(--rxl);overflow:hidden;box-shadow:var(--shm);background:var(--bg3)}
.pa-fig img{width:100%;height:auto}
.pa-body{font-size:1.075rem;line-height:1.85;color:var(--txt);font-weight:300}
.pa-body p{margin-bottom:22px}
.pa-body strong{font-weight:700;color:var(--p1)}
.pa-body a{color:var(--teal-dd);font-weight:700;text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px;transition:color .2s}
.pa-body a:hover{color:var(--p2)}
.pa-body h2{font-family:'M',sans-serif;font-weight:900;font-size:1.5rem;color:var(--p1);margin:38px 0 14px;letter-spacing:-.02em}
.pa-body h3{font-family:'M',sans-serif;font-weight:700;font-size:1.22rem;color:var(--p1);margin:30px 0 12px}
.pa-body h4{font-family:'M',sans-serif;font-weight:700;font-size:1.05rem;color:var(--p2);margin:24px 0 10px}
.pa-body blockquote{margin:28px 0;padding:18px 26px;border-left:4px solid var(--teal);background:var(--bg2);border-radius:0 var(--rmd) var(--rmd) 0;font-size:1.1rem;color:var(--p2);font-style:italic}
.pa-body .pa-cap{font-size:.82rem;color:var(--txm);font-style:italic;margin:-12px 0 26px;line-height:1.5}
.pa-tags{display:flex;flex-wrap:wrap;gap:9px;margin:40px 0 0;padding-top:26px;border-top:1px solid var(--border2)}
.pa-tag{font-size:.74rem;font-weight:700;color:var(--p3);background:rgba(79,209,197,.1);border:1px solid var(--border);border-radius:var(--rpill);padding:6px 14px}
a.pa-tag{transition:var(--tr)}
a.pa-tag:hover{background:rgba(79,209,197,.2);color:var(--p1)}
.pa-cta{margin:56px 0 0}
.pa-cta__lead{background:var(--gc);border-radius:var(--rxl);padding:40px 38px;position:relative;overflow:hidden}
.pa-cta__lead::before{content:'';position:absolute;width:280px;height:280px;border-radius:50%;background:rgba(79,209,197,.08);top:-120px;right:-80px}
.pa-cta__lead h2{font-family:'M',sans-serif;font-weight:900;font-size:1.5rem;color:#fff;letter-spacing:-.02em;margin-bottom:10px;position:relative;z-index:1}
.pa-cta__lead p{font-size:.95rem;font-weight:300;color:rgba(255,255,255,.72);line-height:1.65;margin-bottom:24px;max-width:460px;position:relative;z-index:1}
.pa-cta__btns{display:flex;gap:12px;flex-wrap:wrap;position:relative;z-index:1}
.pa-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:14px}
.pa-act{display:flex;flex-direction:column;gap:8px;background:var(--card-s);border:1px solid var(--border);border-radius:var(--rlg);padding:22px 20px;transition:var(--tr)}
.pa-act:hover{transform:translateY(-3px);box-shadow:var(--shm);border-color:rgba(79,209,197,.35)}
.pa-act__ic{width:42px;height:42px;border-radius:12px;background:rgba(79,209,197,.12);display:flex;align-items:center;justify-content:center}
.pa-act__ic svg{width:22px;height:22px;stroke:var(--teal-dd)}
.pa-act__t{font-weight:900;font-size:.98rem;color:var(--p1)}
.pa-act__d{font-size:.82rem;font-weight:300;color:var(--txs);line-height:1.5}
.pa-act__go{font-size:.78rem;font-weight:700;color:var(--teal-dd)}
.pa-related{margin:56px 0 8px}
.pa-related__head{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px}
.pa-related__head h2{font-family:'M',sans-serif;font-weight:900;font-size:1.3rem;color:var(--p1);letter-spacing:-.02em;margin:0}
.pa-rel-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.pa-rel{background:#fff;border:1px solid var(--border);border-radius:var(--rlg);overflow:hidden;transition:var(--tr);display:flex;flex-direction:column}
.pa-rel:hover{transform:translateY(-3px);box-shadow:var(--shm)}
.pa-rel__thumb{aspect-ratio:16/9;overflow:hidden;background:var(--bg3)}
.pa-rel__thumb img{width:100%;height:100%;object-fit:cover}
.pa-rel__b{padding:16px 18px}
.pa-rel__t{font-size:.92rem;font-weight:700;color:var(--p1);line-height:1.35}
@media(max-width:768px){.pa-wrap{padding:0 22px}.pa-actions{grid-template-columns:1fr}.pa-rel-grid{grid-template-columns:1fr}.pa-cta__lead{padding:30px 24px}}
@media(prefers-reduced-motion:reduce){.rv{opacity:1;transform:none;transition:none}*{transition:none!important;animation:none!important}}
```

### Estrutura do artigo (Tier baixo)

```html
<main id="main-content">
  <article class="pa-wrap">
    <header class="pa-hero">
      <span class="lbl">📰 Blog Libras.se</span>
      <h1 class="pa-title">[Título]</h1>
      <p class="pa-sub">[Subtítulo / linha-fina]</p>
      <div class="pa-meta">Por <strong>[Autor]</strong><span class="dot"></span><time datetime="AAAA-MM-DD">DD de mês de AAAA</time><span class="dot"></span>N min de leitura</div>
    </header>

    <figure class="pa-fig">
      <picture>
        <source srcset="/assets/img/blog/[slug]/[slug].webp" type="image/webp">
        <img src="/assets/img/blog/[slug]/[slug].jpg" alt="[alt]" width="1200" height="675" fetchpriority="high" decoding="async">
      </picture>
    </figure>

    <div class="pa-body">
      <p>Texto corrido. Linke termos para o glossário: <a href="/glossario/libras/">Língua Brasileira de Sinais</a>.</p>
      <h4>Subtítulo</h4>
      <p>...</p>
      <p>Fonte: Equipe LIBRAS.SE, com <a href="[url]" target="_blank" rel="noopener noreferrer">[Veículo]</a></p>
    </div>

    <div class="pa-tags" aria-label="Tags">
      <span class="pa-tag">#acessibilidade</span>
      <a class="pa-tag" href="/glossario/libras/">#libras</a>
      <a class="pa-tag" href="/glossario/til-tils/">#tils</a>
    </div>

    <!-- §8: fechamento "Com Barra" — pa-tags → pa-cta → pa-related → footer canônico -->
  </article>
</main>
```

JS: o mesmo da raiz (nav scroll, menu mobile, scroll-reveal `.rv`). Não precisa
de progress bar nem contadores.

---

# TIER ALTO — Post de alta complexidade (editorial)

Base: **tipografia editorial** (Bricolage Grotesque + Lora) sobre o header/footer
canônicos, com biblioteca de componentes ricos, hero cheio, barra de progresso e
links internos densos. Referências vivas: `voce-sabe-o-que-e-datilologia`,
`libras-tem-sotaque-e-giria`, `libras-ou-legendas-...`.

## Fontes

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,400;12..96,600;12..96,800&family=Lora:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet">
```

| Uso | Fonte |
|-----|-------|
| Títulos, labels, nav, UI | `Bricolage Grotesque` |
| Corpo do artigo, citações | `Lora` (serif) |

## Variáveis CSS do blog editorial

```css
:root{
  --teal-dark:#1e6e6e;--teal-mid:#2a9090;--teal-light:#48bfb2;--teal-pale:#a8e6df;--teal-bg:#f0fafa;
  --ink:#0f2a2a;--ink-soft:#2d4f4f;--white:#ffffff;--cream:#f8fdfd;
  --orange:#f4892a;--orange-soft:#fef3e8;--grey-light:#e8f4f4;
  --radius:16px;--radius-lg:28px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Lora',Georgia,serif;background:var(--cream);color:var(--ink);line-height:1.75;font-size:18px;overflow-x:hidden}
```

> Header e footer continuam sendo os **canônicos do site** (com badge `Blog`),
> apenas reescritos com `font-family:'Bricolage Grotesque'` nas classes de nav/logo.

## Barra de progresso

```css
#progress-bar{position:fixed;top:0;left:0;height:3px;width:0%;background:linear-gradient(90deg,var(--teal-mid),var(--orange));z-index:1000;transition:width .1s linear}
```
```html
<div id="progress-bar"></div>
```

## Hero

### Variante A — gradiente (sem foto de capa)

```css
.hero{min-height:92vh;display:flex;flex-direction:column;justify-content:flex-end;position:relative;overflow:hidden;padding:120px 0 0}
.hero-bg{position:absolute;inset:0;background:linear-gradient(155deg,#0d3d3d 0%,#1e6e6e 35%,#2a9090 65%,#48bfb2 100%);z-index:0}
```

### Variante B — imagem de fundo com overlay

```css
.hero-bg{position:absolute;inset:0;z-index:0}
.hero-bg picture,.hero-bg img{width:100%;height:100%;object-fit:cover;object-position:center top;display:block}
.hero-bg::after{content:'';position:absolute;inset:0;background:linear-gradient(155deg,rgba(13,61,61,.88) 0%,rgba(30,110,110,.82) 35%,rgba(42,144,144,.75) 65%,rgba(72,191,178,.65) 100%)}
```
```html
<div class="hero-bg">
  <picture>
    <source srcset="../../assets/img/blog/[slug]/img.avif" type="image/avif">
    <source srcset="../../assets/img/blog/[slug]/img.webp" type="image/webp">
    <img src="../../assets/img/blog/[slug]/img.png" alt="" aria-hidden="true" fetchpriority="high">
  </picture>
</div>
```

### Decorações + conteúdo do hero

```css
.hero-noise{position:absolute;inset:0;opacity:.04;z-index:1;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");background-size:200px}
.hero-grid-overlay{position:absolute;inset:0;z-index:1;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:60px 60px}
.hero-circles{position:absolute;inset:0;z-index:1;overflow:hidden;pointer-events:none}
.hero-circles span{position:absolute;border-radius:50%;border:1px solid rgba(255,255,255,.08)}
.hero-circles span:nth-child(1){width:600px;height:600px;top:-200px;right:-100px;animation:float1 14s ease-in-out infinite}
.hero-circles span:nth-child(2){width:400px;height:400px;top:100px;right:100px;border-color:rgba(255,255,255,.05);animation:float1 18s ease-in-out infinite reverse}
.hero-circles span:nth-child(3){width:200px;height:200px;bottom:80px;left:10%;animation:float2 10s ease-in-out infinite}
@keyframes float1{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-30px) scale(1.03)}}
@keyframes float2{0%,100%{transform:translateY(0) translateX(0)}50%{transform:translateY(-15px) translateX(10px)}}
.hero-content{position:relative;z-index:10;max-width:860px;margin:0 auto;padding:0 40px 80px;width:100%}
.hero-kicker{display:inline-flex;align-items:center;gap:8px;font-family:'Bricolage Grotesque',sans-serif;font-size:.72rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--teal-pale);margin-bottom:28px;opacity:0;animation:fadeUp .8s .2s forwards}
.hero-kicker::before{content:'';width:24px;height:2px;background:var(--orange);display:inline-block}
.hero-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(2.2rem,5vw,4rem);line-height:1.08;color:var(--white);letter-spacing:-.03em;margin-bottom:24px;opacity:0;animation:fadeUp .9s .4s forwards}
.hero-title em{font-style:normal;color:var(--teal-pale)}
.hero-subtitle{font-family:'Lora',serif;font-style:italic;font-size:1.15rem;color:rgba(255,255,255,.75);max-width:580px;line-height:1.7;margin-bottom:48px;opacity:0;animation:fadeUp .9s .6s forwards}
.hero-meta{display:flex;align-items:center;gap:20px;flex-wrap:wrap;opacity:0;animation:fadeUp .9s .8s forwards}
.meta-badge{font-family:'Bricolage Grotesque',sans-serif;font-size:.78rem;font-weight:500;color:rgba(255,255,255,.65);display:flex;align-items:center;gap:6px}
@keyframes fadeUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:700px){.hero-content{padding:0 20px 70px}}
```
```html
<section class="hero" aria-label="Cabeçalho do artigo">
  <div class="hero-bg"></div>
  <div class="hero-noise"></div><div class="hero-grid-overlay"></div>
  <div class="hero-circles"><span></span><span></span><span></span></div>
  <div class="hero-content">
    <div class="hero-kicker">[Categoria completa]</div>
    <h1 class="hero-title">Título <em>com destaque</em></h1>
    <p class="hero-subtitle">Subtítulo descritivo em itálico.</p>
    <div class="hero-meta">
      <span class="meta-badge">[DD de mês de AAAA]</span>
      <span class="meta-badge">[N] min de leitura</span>
      <span class="meta-badge">LIBRAS.SE</span>
    </div>
  </div>
</section>
```

## Article wrapper + scroll reveal

```css
.article-wrapper{max-width:760px;margin:0 auto;padding:80px 40px 120px}
@media(max-width:700px){.article-wrapper{padding:50px 20px 80px}}
.reveal{opacity:0;transform:translateY(32px);transition:opacity .75s ease,transform .75s ease}
.reveal.visible{opacity:1;transform:translateY(0)}
```
```html
<main class="article-wrapper" id="article"><!-- componentes --></main>
```

## Biblioteca de componentes (alta complexidade)

Use livremente para escanear, ilustrar e dar ritmo ao conteúdo denso.

### Section label, body text, drop cap, mark

```css
.section-label{font-family:'Bricolage Grotesque',sans-serif;font-size:.68rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--teal-mid);display:flex;align-items:center;gap:10px;margin-bottom:20px}
.section-label::after{content:'';flex:1;height:1px;background:var(--teal-pale);max-width:60px}
.body-text{font-family:'Lora',serif;font-size:1.05rem;color:var(--ink-soft);line-height:1.85;margin-bottom:28px}
.body-text strong{color:var(--ink);font-weight:600}
.drop-cap::first-letter{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:3.8em;line-height:.75;float:left;margin-right:8px;margin-top:6px;color:var(--teal-dark)}
mark{background:linear-gradient(120deg,rgba(72,191,178,.25) 0%,rgba(72,191,178,.1) 100%);color:inherit;border-radius:3px;padding:1px 4px}
```
```html
<p class="section-label">Título da seção</p>
<p class="body-text drop-cap">Primeiro parágrafo com inicial maior. Linke <a href="/glossario/datilologia/">datilologia</a> ao glossário.</p>
```

### Pull quote

```css
.pull-quote{margin:56px 0;padding:40px 48px;background:linear-gradient(135deg,var(--teal-dark) 0%,var(--teal-mid) 100%);border-radius:var(--radius-lg);position:relative;overflow:hidden}
.pull-quote::before{content:'"';position:absolute;top:-20px;left:24px;font-family:'Bricolage Grotesque',sans-serif;font-size:10rem;font-weight:800;color:rgba(255,255,255,.07);line-height:1;pointer-events:none}
.pull-quote p{font-family:'Lora',serif;font-style:italic;font-size:1.3rem;color:var(--white);line-height:1.65;position:relative;z-index:1}
.pull-quote p strong{color:var(--teal-pale);font-style:normal}
@media(max-width:700px){.pull-quote{padding:28px}.pull-quote p{font-size:1.1rem}}
```
```html
<blockquote class="pull-quote reveal"><p>Citação com <strong>parte em teal</strong>.</p></blockquote>
```

### Highlight box (laranja) e Info/Law callout (teal)

```css
.highlight-box{margin:40px 0;padding:32px 36px;background:var(--orange-soft);border-left:4px solid var(--orange);border-radius:0 var(--radius) var(--radius) 0}
.highlight-box p{font-family:'Lora',serif;font-size:1rem;color:#5a3200;line-height:1.75}
.highlight-box .highlight-label{font-family:'Bricolage Grotesque',sans-serif;font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--orange);margin-bottom:10px;display:block}
.info-callout,.law-callout{margin:48px 0;display:flex;gap:24px;align-items:flex-start;background:var(--teal-bg);border:1px solid var(--teal-pale);border-radius:var(--radius);padding:32px 36px}
.info-icon,.law-icon{width:52px;height:52px;background:linear-gradient(135deg,var(--teal-mid),var(--teal-light));border-radius:14px;display:grid;place-items:center;font-size:22px;flex-shrink:0}
.info-content h4,.law-content h4{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:.95rem;color:var(--teal-dark);margin-bottom:8px;letter-spacing:-.01em}
.info-content p,.law-content p{font-family:'Lora',serif;font-size:.9rem;color:var(--ink-soft);line-height:1.7}
@media(max-width:700px){.info-callout,.law-callout{flex-direction:column;gap:16px;padding:24px}}
```
```html
<div class="highlight-box reveal"><span class="highlight-label">Ponto-chave</span><p>Informação importante.</p></div>
<div class="info-callout reveal"><div class="info-icon">📚</div><div class="info-content"><h4>Título</h4><p>Contexto. Útil para citar a <a href="/glossario/lei-10436/">Lei 10.436/2002</a>.</p></div></div>
```

### Grid de cards (2 col)

```css
.use-grid,.advantage-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:48px 0}
.use-card,.advantage-card{background:var(--white);border:1px solid var(--grey-light);border-radius:var(--radius);padding:28px;position:relative;overflow:hidden;transition:transform .3s,box-shadow .3s}
.use-card:hover,.advantage-card:hover{transform:translateY(-3px);box-shadow:0 10px 32px rgba(30,110,110,.1)}
.use-card::before,.advantage-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--teal-mid),var(--teal-light))}
.use-card .card-icon,.advantage-card .card-icon{width:44px;height:44px;background:var(--teal-bg);border-radius:12px;display:grid;place-items:center;margin-bottom:16px;font-size:20px}
.use-card h3,.advantage-card h3{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:.95rem;color:var(--ink);margin-bottom:10px}
.use-card p,.advantage-card p{font-family:'Lora',serif;font-size:.85rem;color:var(--ink-soft);line-height:1.7}
@media(max-width:700px){.use-grid,.advantage-grid{grid-template-columns:1fr}}
```

### Case study, process/word steps, stat row

```css
.case-study{margin:56px 0;background:linear-gradient(150deg,#0a2828,#1e6e6e);border-radius:var(--radius-lg);padding:48px;position:relative;overflow:hidden}
.case-study::after{content:'CASO REAL';position:absolute;top:20px;right:24px;font-family:'Bricolage Grotesque',sans-serif;font-size:.65rem;font-weight:700;letter-spacing:.16em;color:rgba(255,255,255,.25)}
.case-study h3{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.5rem;color:var(--teal-pale);margin-bottom:16px}
.case-study p{font-family:'Lora',serif;color:rgba(255,255,255,.8);font-size:.95rem;line-height:1.8}
.case-study .case-tag{display:inline-block;background:rgba(72,191,178,.2);border:1px solid rgba(72,191,178,.35);color:var(--teal-pale);font-family:'Bricolage Grotesque',sans-serif;font-size:.7rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;padding:5px 12px;border-radius:20px;margin-bottom:20px}
.process-steps,.word-steps{margin:48px 0;display:flex;flex-direction:column;gap:4px;position:relative}
.process-steps::before,.word-steps::before{content:'';position:absolute;left:23px;top:24px;bottom:24px;width:1px;background:linear-gradient(to bottom,var(--teal-mid),var(--teal-pale));z-index:0}
.step,.wstep{display:flex;gap:20px;align-items:flex-start;background:var(--white);border:1px solid var(--grey-light);border-radius:var(--radius);padding:20px 24px;position:relative;z-index:1;transition:transform .25s,box-shadow .25s}
.step:hover,.wstep:hover{transform:translateX(6px);box-shadow:0 6px 24px rgba(30,110,110,.08)}
.step-num,.wstep-icon{width:36px;height:36px;background:linear-gradient(135deg,var(--teal-mid),var(--teal-light));border-radius:10px;display:grid;place-items:center;font-family:'Bricolage Grotesque',sans-serif;font-size:.85rem;font-weight:800;color:#fff;flex-shrink:0}
.step-body h4,.wstep-body h4{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:.9rem;color:var(--ink);margin-bottom:4px}
.step-body p,.wstep-body p{font-family:'Lora',serif;font-size:.84rem;color:var(--ink-soft);line-height:1.6}
.stat-row{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:48px 0}
.stat-card{background:var(--white);border:1px solid var(--grey-light);border-radius:var(--radius);padding:28px 24px;text-align:center;box-shadow:0 4px 24px rgba(30,110,110,.06);transition:transform .3s,box-shadow .3s}
.stat-card:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(30,110,110,.12)}
.stat-number{font-family:'Bricolage Grotesque',sans-serif;font-size:2.4rem;font-weight:800;color:var(--teal-dark);line-height:1;display:block;margin-bottom:8px}
.stat-desc{font-family:'Lora',serif;font-size:.8rem;color:var(--ink-soft);line-height:1.5}
@media(max-width:700px){.case-study{padding:32px 24px}.stat-row{grid-template-columns:1fr;gap:14px}}
```

### Vídeo (iframe YouTube ou nativo), divisor e referências

```css
.video-block{margin:48px 0;border-radius:var(--radius-lg);overflow:hidden;position:relative;box-shadow:0 20px 60px rgba(30,110,110,.18)}
.video-block iframe{width:100%;aspect-ratio:16/9;border:none;display:block}
.video-caption{background:var(--teal-dark);padding:16px 24px;display:flex;align-items:center;gap:12px}
.video-caption span{font-family:'Bricolage Grotesque',sans-serif;font-size:.78rem;font-weight:600;color:rgba(255,255,255,.7)}
.divider{width:60px;height:3px;background:linear-gradient(90deg,var(--teal-mid),var(--teal-pale));border-radius:2px;margin:48px 0}
.references{margin:48px 0 0;padding:32px 36px;background:var(--white);border:1px solid var(--grey-light);border-radius:var(--radius)}
.references h4{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;color:var(--teal-mid);margin-bottom:16px}
.references ol{padding-left:20px}
.references li{font-family:'Lora',serif;font-size:.78rem;color:var(--ink-soft);line-height:1.7;margin-bottom:8px}
.references li a{color:var(--teal-mid);text-decoration:underline;text-underline-offset:3px}
```
```html
<div class="references reveal"><h4>Referências</h4><ol><li>AUTOR, Nome. <em>Título.</em> Editora, Ano.</li></ol></div>
```

### CTA block (alternativa editorial ao bloco de §8)

```css
.cta-block{margin-top:72px;background:linear-gradient(145deg,var(--teal-dark),var(--teal-mid) 60%,var(--teal-light));border-radius:var(--radius-lg);padding:56px 48px;text-align:center;position:relative;overflow:hidden}
.cta-block h2{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.8rem;color:var(--white);margin-bottom:16px;position:relative;z-index:1}
.cta-block p{font-family:'Lora',serif;font-style:italic;color:rgba(255,255,255,.75);font-size:1rem;max-width:480px;margin:0 auto 36px;position:relative;z-index:1}
.cta-btn{display:inline-flex;align-items:center;gap:10px;background:var(--white);color:var(--teal-dark);font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:.9rem;padding:16px 32px;border-radius:100px;position:relative;z-index:1;transition:transform .2s,box-shadow .2s;box-shadow:0 4px 24px rgba(0,0,0,.2)}
.cta-btn:hover{transform:translateY(-2px) scale(1.02);box-shadow:0 10px 40px rgba(0,0,0,.3)}
@media(max-width:700px){.cta-block{padding:40px 24px}.cta-block h2{font-size:1.4rem}}
```

## JavaScript (alta complexidade)

Inclui, **além** do JS canônico de nav/menu da raiz: progress bar, scroll reveal
das `.reveal` e contadores opcionais.

```javascript
// Progress bar
const bar = document.getElementById('progress-bar');
window.addEventListener('scroll', () => {
  const h = document.documentElement;
  bar.style.width = (window.scrollY / (h.scrollHeight - h.clientHeight)) * 100 + '%';
});
// Scroll reveal
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); } });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal').forEach((el, i) => { el.style.transitionDelay = (i % 3 * 0.08) + 's'; io.observe(el); });
// Contadores de stat (opcional, se houver .stat-row)
function animateCounter(el, target, suffix='') {
  const dur=1200,start=performance.now(),dec=target%1!==0;
  (function up(now){const p=Math.min((now-start)/dur,1),e=1-Math.pow(1-p,3),v=target*e;
   el.textContent=(dec?v.toFixed(1):Math.floor(v))+suffix;if(p<1)requestAnimationFrame(up);})(start);
}
const statRow = document.querySelector('.stat-row');
if (statRow) new IntersectionObserver((ents,obs)=>ents.forEach(e=>{if(e.isIntersecting){/* animateCounter(...) */ obs.unobserve(e.target);}}),{threshold:.5}).observe(statRow);
```

---

## Checklist antes de publicar (os dois níveis)

- [ ] Nível de complexidade escolhido conforme o tipo de conteúdo (§1)
- [ ] `<title>` = título + ` | Blog Libras.se`; `<meta name="description">` preenchida (~155)
- [ ] OG/Twitter, canonical, `theme-color`, favicon e GA presentes
- [ ] JSON-LD `BlogPosting` + `BreadcrumbList` (+ `FAQPage` se houver FAQ)
- [ ] Header canônico com badge `Blog` e `aria-current="page"`; links do Blog → `/blog/`
- [ ] **Todo termo da área linkado ao glossário** na 1ª ocorrência (§6, conferir `termos.csv`)
- [ ] Imagem própria em `/assets/img/blog/<slug>/` **ou** do banco editorial (§7) com `alt` correto
- [ ] Imagens com `.avif` + `.webp` + fallback, `width`/`height` e `loading` corretos
- [ ] **Fechamento "Com Barra" completo** (§8): tags `#` + CTA "Precisa do seu conteúdo em Libras?" + 3 ícones SVG (jogo/vocabulário/glossário) + 3 posts variados ("Leia mais") + botão "Ver todos os posts" lateral
- [ ] Footer canônico do site (`#foot`) ao final
- [ ] Post adicionado à **home do blog**: card com `data-cat`/`data-search`, contador e `ItemList` atualizados (§5)
- [ ] CTA aponta para páginas reais (huet/soluções/jogo/sinal/glossário)
- [ ] WhatsApp flutuante e skip-link presentes
- [ ] (Alta complexidade) progress bar, `.reveal` e IDs de `.stat-number` conferidos no JS
- [ ] `prefers-reduced-motion` respeitado
```
