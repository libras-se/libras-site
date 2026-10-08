# Home do blog (portal)

`blog/index.html` é gerada. Para publicar um post ou mudar a curadoria:

```bash
python3 tools/blog/home.py
```

| Arquivo | Para quê |
|---|---|
| `home.py` | Gerador. Lê os cards `<article data-post>` da home (fonte da verdade), cria cards para posts novos, monta o portal e regenera `/blog/todos/`, `/blog/temas/` e o sitemap. |
| `home.html` | Template do portal (HTML, CSS e JS). Usa os partials de `tools/sinais/partials/`. |
| `home.json` | Editorias (rótulo, cor, descrição), `mais_lidas`, `destaques`, `capas_com_texto` (fora do carrossel), `materiais_destaque` e a `classificacao` de cada post. |
| `home-ld.json` | Base do JSON-LD (Blog + BreadcrumbList + ItemList). O `ItemList` é preenchido no formato do `audit/sync_blog.py`. |

O gerador é idempotente: rodar duas vezes sem mudanças não altera nada.
Miniaturas do portal ficam em `assets/img/blog/thumbs/` (geradas uma vez por post).
Detalhes editoriais em `blog/CLAUDE.md` §5.
