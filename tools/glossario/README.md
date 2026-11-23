# Glossário (gerado)

Gera o índice `/glossario/` e cada verbete `/glossario/<slug>/` a partir das fontes em
`tools/glossario/verbetes/<slug>.html`. Header, footer, fontes, variáveis e JS de navegação vêm dos
partials canônicos (`tools/sinais/partials/`), os mesmos das páginas de sinal e do Aprender Libras.

```bash
python3 tools/glossario/build.py      # gera índice + verbetes, termos.csv e o bloco GLOSSARIO:SITEMAP do sitemap.xml
python3 tools/seo/links.py            # depois: "Este termo no blog" em cada verbete (bloco LSE:DOBLOG)
```

Não edite `glossario/**/index.html`: o cabeçalho de cada página diz de qual fonte ela veio.
`glossario/termos.csv` também é gerado (é a lista que o blog e o `tools/blog/novo_post.py` usam para linkar termos).

## Autoria e datas

Todo verbete é assinado por **Luis Debiasi, Equipe LIBRAS.SE** (Person no JSON-LD, com link para
`/autor/luis-debiasi/`). A assinatura e as datas ficam **no fim do verbete**, num bloco de autor:
"Publicado em …" e, se for diferente, "Atualizado em …". Ao revisar o texto de um verbete, mude `atualizado`.

## Formato da fonte

Cada arquivo começa com um bloco `<!--META {json} META-->` e depois traz as seções do texto.

```html
<!--META
{
 "termo": "Glosa",                       // nome exibido (H1, cards, breadcrumb)
 "categoria": "linguística",             // linguística | legislação | interpretação | tecnologia | cultura
 "en": "Gloss",                          // equivalente em inglês (aparece no card do índice)
 "title": "Glosa em Libras: o que é e como usar | Glossário LIBRAS.SE",
 "desc": "120 a 160 caracteres, com o termo no começo.",
 "keywords": "glosa libras, o que é glosa, ...",
 "og_title": "…", "og_desc": "…",        // opcionais (caem em title/desc)
 "sub": "Linha fina do topo, 1 ou 2 frases.",
 "definicao": "<strong>Glosa</strong> é … (HTML, um parágrafo: é o snippet de definição)",
 "resumo": "Texto puro, 1 ou 2 frases (DefinedTerm e card do índice).",
 "exemplo": "Frase de exemplo de uso, texto puro (card do índice).",
 "fonte_definicao": "Quadros & Karnopp, 2004",
 "relacionados": ["libras", "datilologia"],   // 3 a 6 slugs de outros verbetes
 "blog": ["o-que-e-libras"],                 // opcional: posts que o verbete recomenda no fim do texto
 "publicado": "2026-05-07",
 "atualizado": "2026-11-23",
 "faq": [{"q": "Pergunta?", "a": "Resposta em HTML simples."}],   // 3 a 5
 "fontes": ["Autor (ano). Título. Editora", "<a href=\"https://…\" target=\"_blank\" rel=\"noopener noreferrer\">Lei nº …</a>, Planalto"],
 "listar": false                             // opcional: fora do índice e do termos.csv (página de apoio)
}
META-->

<section id="s1" data-toc="O que é glosa?">
  <h2>O que é glosa em Libras?</h2>
  <p>Texto… <a href="/glossario/libras/" class="ilink">Libras</a> … <mark class="grifo">frase-chave</mark> …</p>
  <div class="callout"><p>Destaque curto.</p></div>
</section>
```

Regras de texto (as mesmas do blog):

- 5 a 7 seções `<section id="sN" data-toc="rótulo curto do índice">`, cada uma com um `<h2>`.
  Dentro: `<p>`, `<ul>`/`<ol>`, `<h3>`, `<div class="callout"><p>…</p></div>`.
- Link para outro verbete: `<a href="/glossario/<slug>/" class="ilink">`; para post: `<a href="/blog/<slug>/" class="ilink">`.
  Só links que existem. Primeira ocorrência por seção, sem repetir em todo parágrafo.
- **Grifo:** 1 ou 2 frases-chave por verbete em `<mark class="grifo">` (dentro de `<p>`, nunca em callout,
  título ou lista). O marca-texto passa pela frase quando ela entra na tela (`/assets/js/grifo.js`).
- Sem travessão (— ou –) e sem emoji. Marca sempre **LIBRAS.SE**. Leis com número e ano conferidos no Planalto.
- Fatos, números e datas só com fonte listada em `fontes`.
