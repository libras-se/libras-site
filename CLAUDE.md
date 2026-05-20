# CLAUDE.md — Libras.se Site Standards

Este arquivo define o header e footer canônicos do site Libras.se.
Ao criar ou editar qualquer página, copie exatamente estes blocos.

---

## Design System

### Fontes
Arquivo local (páginas na raiz): `assets/fonts/museo-sans-rounded-*.woff2`
Arquivo absoluto (subpastas): `/assets/fonts/museo-sans-rounded-*.woff2`

```css
@font-face{font-family:'M';src:url('/assets/fonts/museo-sans-rounded-300.woff2') format('woff2');font-weight:300;font-display:swap}
@font-face{font-family:'M';src:url('/assets/fonts/museo-sans-rounded-700.woff2') format('woff2');font-weight:700;font-display:swap}
@font-face{font-family:'M';src:url('/assets/fonts/museo-sans-rounded-900.woff2') format('woff2');font-weight:900;font-display:swap}
@font-face{font-family:'M';src:url('/assets/fonts/museo-sans-rounded-900.woff2') format('woff2');font-weight:1000;font-display:swap}
```

> **O peso 1000 aponta para o arquivo 900 — é intencional.** Só use 1000 no logo LIBRAS.SE.

### Variáveis CSS obrigatórias
```css
:root{
  --bg:#f0fafa;--bg2:#e8f6f5;--bg3:#dff2f0;
  --p1:#0e3538;--p2:#154245;--p3:#2a6069;
  --teal:#4fd1c5;--tl:#81e6d9;--txl:#b2f5ea;
  --teal-d:#2eb8c0;--teal-dd:#1a9ca4;
  --green:#22c55e;
  --card:rgba(255,255,255,.72);--card-s:rgba(255,255,255,.85);
  --border:rgba(79,209,197,.18);--border2:rgba(10,34,37,.07);
  --txt:#12393d;--txs:#3d6063;--txm:#7aacad;
  --gb:linear-gradient(130deg,#1aa8b0 0%,#4fd1c5 50%,#81e6d9 100%);
  --gb2:linear-gradient(135deg,#1aa8b0,#81e6d9);
  --gc:linear-gradient(135deg,#0e3538,#2a6069);
  --gs:linear-gradient(180deg,var(--bg) 0%,var(--bg2) 100%);
  --sh:0 2px 16px rgba(10,34,37,.06);--shm:0 8px 40px rgba(10,34,37,.1);
  --shl:0 20px 72px rgba(10,34,37,.14);--shg:0 8px 40px rgba(79,209,197,.22);
  --blur:blur(22px);--blur-l:blur(40px);
  --tr:.3s cubic-bezier(.4,0,.2,1);
  --rmd:16px;--rlg:24px;--rxl:32px;--rx2:44px;--rpill:999px;
}
```

### Regras invioláveis
- Logo `LIBRAS.SE` sempre em `font-weight:1000` com gradiente `--gb`
- Cor primária escura: `#0e3538` — nunca `#0a2225` nem preto puro
- Sem `font-weight:1000` em nenhum outro elemento além do logo
- WhatsApp: `5548996367511`

---

## CSS do Header (nav + mobile menu + botão flutuante WPP)

```css
.skip-link{position:absolute;top:-100%;left:16px;background:var(--p1);color:#fff;padding:8px 16px;border-radius:0 0 var(--rmd) var(--rmd);font-size:.82rem;font-weight:700;z-index:9999;transition:top .2s}
.skip-link:focus{top:0}
.w{width:100%;max-width:1140px;margin:0 auto;padding:0 40px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:12px 26px;border-radius:var(--rpill);font-family:'M',sans-serif;font-size:.88rem;font-weight:700;cursor:pointer;border:none;outline:none;transition:var(--tr);white-space:nowrap;position:relative;overflow:hidden}
.btn::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.25),transparent);transform:translateX(-120%);transition:transform .5s ease;pointer-events:none}
.btn:hover::after{transform:translateX(120%)}
.btn:focus-visible{outline:3px solid var(--teal);outline-offset:3px}
.bp{background:var(--gc);color:#fff;box-shadow:0 4px 18px rgba(10,34,37,.22)}
.bp:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(10,34,37,.3)}
.bw{background:var(--green);color:#fff;box-shadow:0 4px 16px rgba(34,197,94,.28)}
.bw:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(34,197,94,.38)}
@keyframes wppBeat{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-2px) scale(1.02)}}
.wppf{position:fixed;bottom:26px;right:26px;z-index:900;display:flex;align-items:center;gap:8px;background:var(--green);color:#fff;border-radius:var(--rpill);padding:12px 20px;font-size:.82rem;font-weight:700;animation:wppBeat 3s ease-in-out infinite;transition:var(--tr);box-shadow:0 4px 20px rgba(34,197,94,.4)}
.wppf:hover{transform:translateY(-2px) scale(1.02);background:#16a34a}
.wppf:focus-visible{outline:3px solid #fff;outline-offset:2px}
.wppf svg{width:16px;height:16px;fill:#fff;flex-shrink:0}
@media(max-width:480px){.wppf span{display:none}.wppf{padding:13px;border-radius:50%;width:50px;height:50px;justify-content:center}}
.mob{display:none;position:fixed;inset:0;background:rgba(5,20,24,.97);backdrop-filter:var(--blur-l);z-index:999;flex-direction:column;align-items:center;justify-content:center;gap:24px}
.mob.open{display:flex}
.mob a{font-size:1.2rem;font-weight:700;color:rgba(255,255,255,.78);transition:color .2s}
.mob a:hover{color:var(--tl)}
.mob-x{position:absolute;top:20px;right:24px;font-size:1.2rem;cursor:pointer;color:rgba(255,255,255,.45);background:none;border:none;padding:8px}
.mob-x:focus-visible{outline:2px solid var(--teal);border-radius:4px}
#nav{position:fixed;top:0;left:0;right:0;z-index:800;padding:20px 0;transition:all .4s}
#nav.sc{padding:13px 0;background:rgba(240,250,250,.88);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);box-shadow:0 1px 0 rgba(79,209,197,.12),0 2px 20px rgba(10,34,37,.05)}
.navi{display:flex;align-items:center;justify-content:space-between;gap:20px}
.nlogo{text-decoration:none}
.nlogo-txt{font-family:'M',sans-serif;font-weight:1000;font-size:1.5rem;background:var(--gb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-.02em;line-height:1}
.nlinks{display:flex;align-items:center;gap:22px;list-style:none}
.nlinks a{font-size:.78rem;font-weight:700;color:var(--txs);transition:color .2s;position:relative;padding-bottom:2px}
.nlinks a::after{content:'';position:absolute;bottom:0;left:0;width:0;height:1.5px;background:var(--gb);border-radius:2px;transition:width .25s}
.nlinks a:hover{color:var(--p1)}
.nlinks a:hover::after{width:100%}
.nlinks a:focus-visible{outline:2px solid var(--teal);border-radius:3px;outline-offset:2px}
.ham{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:8px}
.ham span{display:block;width:21px;height:1.5px;background:var(--p1);border-radius:2px;transition:var(--tr)}
.ham:focus-visible{outline:2px solid var(--teal);border-radius:4px;outline-offset:4px}
.nd{display:flex}
@media(max-width:768px){.nlinks,.nd{display:none}.ham{display:flex}.w{padding:0 22px}}
```

---

## HTML do Header

Cole este bloco logo após `<body>`, antes do `<main>`:

```html
<a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>

<a href="https://wa.me/5548996367511?text=Ol%C3%A1%2C+estava+no+site+do+Libras.se+e+quero+saber+mais!" target="_blank" rel="noopener noreferrer" class="wppf" aria-label="Entrar em contato pelo WhatsApp">
  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
  <span>WhatsApp</span>
</a>

<div class="mob" id="mobm" role="dialog" aria-modal="true" aria-label="Menu de navegação">
  <button class="mob-x" id="mobx" aria-label="Fechar menu">✕</button>
  <a href="https://libras.se/proposito" onclick="cm()">Propósito</a>
  <a href="https://libras.se/tecnologia" onclick="cm()">Nossa tecnologia</a>
  <a href="https://libras.se/solucoes" onclick="cm()">Soluções</a>
  <a href="https://libras.se/portfolio" onclick="cm()">Portfólio</a>
  <a href="https://blog.libras.se/" onclick="cm()">Blog</a>
  <a href="/jogo/" onclick="cm()">Jogo</a>
  <a href="/sinal/" onclick="cm()">Vocabulário</a>
  <a href="/glossario/" onclick="cm()">Glossário</a>
  <a href="https://huet.libras.se/" class="btn bw" onclick="cm()">Enviar seu vídeo</a>
</div>

<nav id="nav" aria-label="Navegação principal">
  <div class="w">
    <div class="navi">
      <a href="/" class="nlogo" aria-label="Libras.se — Página inicial">
        <span class="nlogo-txt" aria-hidden="true">LIBRAS.SE</span>
      </a>
      <ul class="nlinks" role="list">
        <li><a href="https://libras.se/proposito">Propósito</a></li>
        <li><a href="https://libras.se/tecnologia">Nossa tecnologia</a></li>
        <li><a href="https://libras.se/solucoes">Soluções</a></li>
        <li><a href="https://libras.se/portfolio">Portfólio</a></li>
        <li><a href="https://blog.libras.se/">Blog</a></li>
      </ul>
      <a href="https://huet.libras.se/" class="btn bp nd" style="font-size:.8rem;padding:10px 20px">Enviar seu vídeo</a>
      <button class="ham" id="hamb" aria-label="Abrir menu" aria-expanded="false" aria-controls="mobm">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</nav>
```

---

## CSS do Footer

```css
#foot{background:var(--p1);padding:52px 0 24px;border-top:1px solid rgba(255,255,255,.04);position:relative;z-index:1}
.ft-top{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr 1fr;gap:40px;padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:22px}
.ft-logo{font-family:'M',sans-serif;font-weight:1000;font-size:1.6rem;background:var(--gb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:block;margin-bottom:12px;letter-spacing:-.02em}
.ft-bp{font-size:.8rem;color:rgba(255,255,255,.38);line-height:1.7;margin-bottom:16px}
.ft-socs{display:flex;gap:7px}
.ftsoc{width:40px;height:40px;border-radius:9px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.09);display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.5);transition:var(--tr)}
.ftsoc:hover{background:rgba(255,255,255,.12);color:#fff;transform:translateY(-2px)}
.ftsoc:focus-visible{outline:2px solid var(--teal);outline-offset:2px}
.ftsoc svg{width:15px;height:15px;fill:currentColor}
.ft-col h4{font-size:.63rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:rgba(255,255,255,.25);margin-bottom:14px}
.ft-col ul{list-style:none;display:flex;flex-direction:column;gap:8px}
.ft-col ul a{font-size:.8rem;color:rgba(255,255,255,.46);transition:color .2s}
.ft-col ul a:hover{color:#fff}
.ft-bot{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}
.ft-bot p{font-size:.7rem;color:rgba(255,255,255,.22)}
@media(max-width:1024px){.ft-top{grid-template-columns:1fr 1fr}}
@media(max-width:768px){.ft-top{grid-template-columns:1fr}.ft-bot{flex-direction:column;align-items:flex-start}}
```

---

## HTML do Footer

Cole este bloco após `</main>`, antes de `</body>`:

```html
<footer id="foot" aria-label="Rodapé do site">
  <div class="w">
    <div class="ft-top">
      <div>
        <a href="/" class="ft-logo" aria-label="Libras.se — Voltar ao topo">LIBRAS.SE</a>
        <p class="ft-bp">A plataforma de tradução em Libras mais ágil do Brasil. Vídeos para todos.</p>
        <div class="ft-socs" aria-label="Redes sociais">
          <a href="https://instagram.com/libras.se" class="ftsoc" target="_blank" rel="noopener noreferrer" aria-label="Instagram da Libras.se">
            <svg viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
          </a>
          <a href="https://youtube.com/@librasse" class="ftsoc" target="_blank" rel="noopener noreferrer" aria-label="YouTube da Libras.se">
            <svg viewBox="0 0 24 24"><path d="M23.495 6.205a3.007 3.007 0 0 0-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 0 0 .527 6.205a31.247 31.247 0 0 0-.522 5.805 31.247 31.247 0 0 0 .522 5.783 3.007 3.007 0 0 0 2.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 0 0 2.088-2.088 31.247 31.247 0 0 0 .5-5.783 31.247 31.247 0 0 0-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/></svg>
          </a>
          <a href="https://linkedin.com/company/librasse" class="ftsoc" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn da Libras.se">
            <svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
          </a>
          <a href="https://facebook.com/librasse" class="ftsoc" target="_blank" rel="noopener noreferrer" aria-label="Facebook da Libras.se">
            <svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
          </a>
          <a href="https://tiktok.com/@libras.se" class="ftsoc" target="_blank" rel="noopener noreferrer" aria-label="TikTok da Libras.se">
            <svg viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>
          </a>
        </div>
      </div>
      <div class="ft-col">
        <h4>Serviços</h4>
        <ul>
          <li><a href="https://libras.se/solucoes">Tradução de Vídeo</a></li>
          <li><a href="https://libras.se/solucoes">Video Aulas</a></li>
          <li><a href="https://libras.se/solucoes">Ao Vivo</a></li>
          <li><a href="https://libras.se/solucoes">Pacotes</a></li>
        </ul>
      </div>
      <div class="ft-col">
        <h4>Empresa</h4>
        <ul>
          <li><a href="https://libras.se/tecnologia">Nossa Tecnologia</a></li>
          <li><a href="/sejatils/">Seja TILs no Libras.se</a></li>
          <li><a href="https://libras.se/politica">Nossa Política</a></li>
          <li><a href="https://blog.libras.se/">Blog</a></li>
        </ul>
      </div>
      <div class="ft-col">
        <h4>Explorar</h4>
        <ul>
          <li><a href="https://blog.libras.se/" target="_blank" rel="noopener noreferrer">Blog</a></li>
          <li><a href="/jogo/">Jogo de Libras</a></li>
          <li><a href="/sinal/">Vocabulário</a></li>
          <li><a href="/glossario/">Glossário</a></li>
        </ul>
      </div>
      <div class="ft-col">
        <h4>Contato</h4>
        <ul>
          <li><a href="https://wa.me/5548996367511?text=Ol%C3%A1%2C+estava+no+site+do+Libras.se+e+quero+saber+mais!" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>
          <li><a href="mailto:contato@libras.se">contato@libras.se</a></li>
          <li><a href="https://instagram.com/libras.se" target="_blank" rel="noopener noreferrer">@libras.se</a></li>
          <li><a href="/">Florianópolis, SC</a></li>
        </ul>
      </div>
    </div>
    <div class="ft-bot">
      <p>© 2026 Libras.se · Vídeos para todos · Todos os direitos reservados.</p>
      <p>CNPJ 22.943.329/0001-91 · Florianópolis, Santa Catarina, Brasil</p>
    </div>
  </div>
</footer>
```

---

## JavaScript obrigatório (nav scroll + mobile menu)

Cole dentro de `<script>` antes de `</body>`:

```javascript
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => nav.classList.toggle('sc', scrollY > 60), { passive: true });

const mob  = document.getElementById('mobm');
const hamb = document.getElementById('hamb');
const mobx = document.getElementById('mobx');

function openMenu() {
  mob.classList.add('open');
  hamb.setAttribute('aria-expanded', 'true');
  hamb.setAttribute('aria-label', 'Fechar menu');
  mob.querySelector('a').focus();
}
function closeMenu() {
  mob.classList.remove('open');
  hamb.setAttribute('aria-expanded', 'false');
  hamb.setAttribute('aria-label', 'Abrir menu');
}
function cm() { closeMenu(); }

hamb.addEventListener('click', openMenu);
mobx.addEventListener('click', closeMenu);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && mob.classList.contains('open')) closeMenu();
});

const rvO = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('on'); rvO.unobserve(e.target); }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -24px 0px' });
document.querySelectorAll('.rv').forEach(el => rvO.observe(el));

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});
```

---

## CSS utilitário (scroll reveal + gradiente de texto)

```css
.rv{opacity:0;transform:translateY(28px);transition:opacity .8s ease,transform .8s ease}
.rv.on{opacity:1;transform:none}
.rv.rl{transform:translateX(-28px)}.rv.rl.on{transform:none}
.rv.rr{transform:translateX(28px)}.rv.rr.on{transform:none}
.d1{transition-delay:.07s}.d2{transition-delay:.14s}.d3{transition-delay:.21s}
.d4{transition-delay:.28s}.d5{transition-delay:.35s}.d6{transition-delay:.42s}
.gt{background:var(--gb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.gt2{background:var(--gb2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.lbl{display:inline-flex;align-items:center;gap:7px;font-size:.67rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--p3);background:rgba(79,209,197,.1);border:1px solid rgba(79,209,197,.2);border-radius:var(--rpill);padding:5px 14px}
.glass{background:rgba(255,255,255,.72);backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);border:1px solid rgba(255,255,255,.7);border-radius:var(--rxl);box-shadow:0 8px 40px rgba(10,34,37,.1),inset 0 1px 0 rgba(255,255,255,.9);position:relative;overflow:hidden;transition:var(--tr)}
.glass::before{content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.28),transparent);transform:skewX(-15deg);transition:left .6s ease;pointer-events:none}
.glass:hover::before{left:140%}
.glass:hover{box-shadow:0 20px 72px rgba(10,34,37,.14),inset 0 1px 0 rgba(255,255,255,.95);transform:translateY(-4px)}
```

---

## Páginas existentes e seus paths

| Página           | Path                          |
|------------------|-------------------------------|
| Home             | `/index.html`                 |
| Seja TILs        | `/sejatils/index.html`        |
| Jogo             | `/jogo/index.html`            |
| Vocabulário      | `/sinal/index.html`           |
| Glossário        | `/glossario/index.html`       |
| Portfólio        | `/portfolio/index.html`       |
| Soluções         | `/solucoes/index.html`        |
| Tecnologia       | `/tecnologia/index.html`      |
| Propósito        | `/proposito/index.html`       |
| Blog             | `https://blog.libras.se/`     |
| Plataforma Huet  | `https://huet.libras.se/`     |

## Contatos e links institucionais

- WhatsApp: `5548996367511`
- E-mail: `contato@libras.se`
- Instagram: `@libras.se`
- CNPJ: `22.943.329/0001-91`
- Sede: Florianópolis, Santa Catarina, Brasil
