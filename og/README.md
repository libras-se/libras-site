# Sistema de imagens sociais (OG) — Libras.se

Sistema replicável que gera as imagens de compartilhamento (WhatsApp, LinkedIn,
Facebook, X) de cada página a partir de **um único template** e de um
**manifesto**, e injeta as meta tags `og:image` / `twitter:image`
automaticamente no HTML.

Não há arte feita à mão por página: você edita texto no manifesto, roda um
comando e o sistema produz imagens visualmente coerentes entre si.

## Direção de arte (resumo)

- 1200×630, **título é o elemento dominante** e legível mesmo em miniatura.
- Marca `LIBRAS.SE` sempre no topo: ícone (mãos) + texto em degradê.
- Espaço em branco, cantos arredondados, card translúcido (badge), sombra suave,
  degradê vivo mas elegante, poucos elementos.
- **Sempre fundo claro** (`theme: "light"`). O degradê do título usa um teal mais
  profundo (`#0b8088 → #2bb8bd`) para nunca sumir no fundo claro.
- Título com `text-wrap: balance` — as linhas se equilibram sozinhas, sem deixar
  a primeira linha longa demais. **Sem travessões (—)** nos textos.
- O template ainda traz uma variação `deep` (fundo escuro) caso precise no futuro,
  mas hoje o padrão é tudo claro.
- Tipografia Museo Sans Rounded (mesmos arquivos `assets/fonts/`) e tokens de
  cor idênticos ao `CLAUDE.md`. O peso 1000 só aparece no logo.

## Como usar

```bash
npm install            # uma vez (instala puppeteer-core)
npm run og                            # gera TODAS as imagens + injeta as meta tags
npm run og -- --skip=jogo,glossario   # gera tudo menos Jogo/Glossário (ajustadas à parte)
npm run og -- --only=home             # apenas um slug
npm run og -- --no-inject             # gera imagens sem alterar o HTML
npm run og -- --no-webp               # mantém PNG (debug visual)
```

Requisitos no ambiente: **Google Chrome** instalado e **ImageMagick** (`magick`).
Em outro caminho/SO, defina `CHROME_PATH=/caminho/para/chrome`.

Saída: `assets/img/og/<slug>.webp` (≈20–40 KB cada).

## Adicionar uma página nova

1. Acrescente uma entrada em [`pages.json`](./pages.json):

   ```json
   {
     "slug": "minha-pagina",
     "page": "minha-pagina/index.html",
     "theme": "light",
     "eyebrow": "Categoria curta",
     "lead": "Texto antes do",
     "accent": "destaque em degradê",
     "tail": "texto depois",
     "badge": "Selo translúcido (ou false p/ ocultar)"
   }
   ```

   O título exibido é `lead` + `accent` (em degradê) + `tail`. Mantenha-o curto
   — o template reduz a fonte automaticamente (74→64→56px) se passar de 3 linhas,
   mas títulos enxutos ficam mais legíveis na miniatura.

2. `npm run og -- --only=minha-pagina`

A injeção só **substitui** o `content=""` de meta tags que já existem
(`og:image`, `og:image:alt/width/height/type/secure_url`, `twitter:image`,
`twitter:image:alt`). Não cria tags do zero — garanta que a página tenha pelo
menos `og:image` e `twitter:image`.

## Arquivos

| Arquivo         | Papel                                                        |
|-----------------|--------------------------------------------------------------|
| `template.html` | Layout visual (light/deep) + `window.render(data)`           |
| `pages.json`    | Manifesto: uma entrada por página                            |
| `generate.mjs`  | Renderiza (Chrome) → WebP (ImageMagick) → injeta meta tags   |

Para ajustar o **visual de todas as imagens de uma vez**, edite só o CSS de
`template.html` e rode `npm run og`.
