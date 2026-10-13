# Home do blog (portal)

`blog/index.html` é gerada. Para publicar um post ou mudar a curadoria:

```bash
python3 tools/blog/home.py
```

| Arquivo | Para quê |
|---|---|
| `home.py` | Gerador. Refaz o card de cada post a partir do próprio post (headline, description e imagem do JSON-LD; do card antigo ficam só `data-cat` e `data-search`), monta o portal e regenera `/blog/todos/`, `/blog/temas/`, as páginas de editoria `/blog/tema/<editoria>/`, o feed Atom `blog/feed.xml` (20 posts mais recentes) e o sitemap. |
| `home.html` | Template do portal (HTML, CSS e JS). Usa os partials de `tools/sinais/partials/`. |
| `home.json` | Editorias (rótulo, cor, descrição, `seo_titulo` e `seo_desc` da página da editoria), `mais_lidas`, `destaques`, `capas_destaque` (foto limpa do carrossel), `capas_com_texto` (fora do carrossel), `materiais_destaque` e a `classificacao` de cada post. |
| `home-ld.json` | Base do JSON-LD (Blog + BreadcrumbList + ItemList). O `ItemList` é preenchido no formato do `audit/sync_blog.py`. |
| `novo_post.py` | Publicador do Agent Control: monta um post de baixa complexidade a partir de `blog/_entrada/<slug>.json` e roda os geradores do §8. Roda no workflow `.github/workflows/publicar-post.yml`. Formato e fluxo: `blog/CLAUDE.md` §9. |
| `post-simples.html` | Molde do post de baixa complexidade usado pelo `novo_post.py` (cabeçalho, rodapé e CSS dos posts, com placeholders `{{...}}`). |
| `exemplo-entrada.json` | Exemplo do JSON de entrada (versão 1). |
| `requirements-publicador.txt` | Dependências do `novo_post.py` e dos geradores que ele chama (markdown-it-py e Pillow). |

O gerador é idempotente: rodar duas vezes sem mudanças não altera nada.
Miniaturas do portal ficam em `assets/img/blog/thumbs/` (geradas uma vez por post, a partir da imagem
do JSON-LD; apague as de um post para gerar de novo). Os cards da home, de `/todos/`, `/temas/` e das
editorias usam a miniatura de 480/960 px, não a capa de 1200 px.
Detalhes editoriais em `blog/CLAUDE.md` §5.
