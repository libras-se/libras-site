# tools/seo

Estrutura de links internos e auditoria de SEO do libras.se. A estratégia, o backlog e as regras ficam
em [`ESTRATEGIA.md`](ESTRATEGIA.md).

| Arquivo | O que faz |
|---|---|
| `links.py` | Gera os blocos entre marcadores `<!-- LSE:... -->`: banner interno no meio dos posts (`LSE:BANNER`), "Continue lendo" e ícones no fim dos posts (`LSE:MAIS`), blog nas páginas comerciais e no glossário (`LSE:DOBLOG`), ícones nos hubs (`LSE:APRENDA`) e o CSS (`LSE:CSS`). Idempotente. |
| `links.json` | Configuração: `banners` (textos, links e visual), `banner_por_editoria`, `banner_por_post`, `pilares`, `solucoes` (post → página comercial), `do_blog` (página → 3 posts) e `so_icones`. |
| `llms.py` | Refaz a lista de artigos do `llms-full.txt` (pilares primeiro, depois do mais novo ao mais antigo) e as contagens de posts no `llms.txt`. Rode depois de publicar ou despublicar um post. |
| `auditoria.py` | Lê todas as páginas publicadas e mede title, description, canonical, H1, OG, JSON-LD, links de contexto de entrada e saída, links para as áreas de engajamento, links quebrados e imagens sem alt. Grava `auditoria.json` (e `auditoria.csv` com `--csv`). |

```bash
python3 tools/blog/home.py            # antes: links.py lê os cards da home do blog
python3 tools/seo/links.py
python3 tools/seo/llms.py
python3 tools/seo/auditoria.py --csv
```

O que **não** vai para o site publicado fica em `_config.yml` (`exclude`): `tools/`, `scripts/`, `og/` e todo arquivo `.md`.
Sem essa lista, o GitHub Pages transforma cada `.md` em página pública. O `robots.txt` repete essas pastas, por garantia.

Não edite à mão o que está entre `<!-- LSE:... -->` e `<!-- /LSE:... -->`: é apagado e refeito a cada execução.

## Como mudar

- **Banner de um post:** `banner_por_post` → `"<slug>": "<id do banner>"`. Sem entrada, o post recebe um dos
  banners da sua editoria em `banner_por_editoria`. A escolha é fixa por post (hash do slug), então os posts da
  mesma editoria se alternam entre os banners da lista.
- **Novo banner:** acrescente em `banners`. O `visual` pode ser:
  - `video:<slug do sinal>`, para um vídeo de `assets/videos/sinais/`;
  - `dat:<PALAVRA>`, para a fonte Libras 2020;
  - `capa:<pdf>`, para uma capa de `assets/materiais/capas/`.

  Sem preço em nada que aparece no blog.
- **Post pilar:** inclua em `pilares[<editoria>]`. Ele ganha peso nas correlatas da editoria.
- **Página comercial ou institucional com posts do blog:** `do_blog` → `"/url/": [3 slugs]`.
- **Glossário:** automático. Cada verbete mostra 3 posts que citam aquele termo no texto, com rodízio
  para não repetir sempre os mesmos. Verbetes que nenhum post cita recebem os posts com mais palavras em comum.
