# Áreas educativas (Aprender Libras)

Gera as páginas educativas do site e os materiais em PDF. Tudo usa o vocabulário em vídeo de
`sinal/sinais.json` (gravado pelas intérpretes da LIBRAS.SE) e os mesmos partials canônicos de
header e footer das páginas de sinal (`tools/sinais/partials/`).

| Página | Fonte | Palavra-chave principal |
|---|---|---|
| `/aprender-libras/` | `paginas/aprender-libras.html` | aprender libras |
| `/aprender-libras/sinais-basicos/` | `paginas/aprender-libras-sinais-basicos.html` | sinais básicos em libras |
| `/cultura-surda/` | `paginas/cultura-surda.html` | cultura surda |
| `/jogos/` | `paginas/jogos.html` | jogos de libras |
| `/jogos/jogo-da-memoria-libras/` | `paginas/jogos-memoria.html` | jogo da memória libras |
| `/jogos/quiz-de-libras/` | `paginas/jogos-quiz.html` | quiz de libras |
| `/atividades/` | `paginas/atividades.html` | atividades de libras para imprimir |
| `/atividades/bingo-de-libras/` | `paginas/atividades-bingo.html` | bingo de libras |
| `/atividades/caca-palavras-em-libras/` | `paginas/atividades-caca-palavras.html` | caça-palavras em libras |
| `/materiais/` | `paginas/materiais.html` | materiais / apostila de libras pdf |
| `/aprender-libras/alfabeto-em-libras/` | `paginas/aprender-libras-alfabeto.html` | alfabeto em libras (+ para imprimir) |
| `/aprender-libras/numeros-em-libras/` | `paginas/aprender-libras-numeros.html` | números em libras |
| `/jogos/desafio-da-datilologia/` | `paginas/jogos-datilologia.html` | jogo de datilologia / alfabeto |
| `/atividades/datilologia/` | `paginas/atividades-datilologia.html` | atividades de datilologia para imprimir |

## Comandos

```bash
python3 tools/aprender/build.py            # gera todas as páginas e atualiza o bloco APRENDER:SITEMAP do sitemap.xml
python3 tools/aprender/build.py jogos      # só as fontes que começam com "jogos"
python3 tools/aprender/pdf.py              # gera assets/materiais/*.pdf e as capas (precisa do Chrome e do pdftoppm)
```

Depois de editar uma fonte, rode o build e confira no navegador (`python3 -m http.server` na raiz).
Não edite os `index.html` gerados: o cabeçalho deles avisa de qual fonte vieram.

## Como uma fonte funciona

Cada arquivo em `paginas/` começa com um bloco `<!--META {json} META-->` (url, title, desc,
og_image, breadcrumb e nós extras de JSON-LD) e traz o `<style>`, o `<main>` e o `<script>` da página.
Marcadores disponíveis no corpo:

- `{{BREADCRUMB}}`: trilha de navegação a partir do `breadcrumb` do META.
- `{{SINAIS_JSON}}`: lista enxuta dos sinais com vídeo, para os jogos e geradores (JS).
- `{{SINAIS:slug1,slug2}}`: cartões estáticos e indexáveis de sinais com vídeo.
- `{{PALAVRAS_JSON}}`: listas de `palavras.json` (temas e números) para os jogos e fichas de datilologia.
- `{{LEIA_NO_BLOG:slug1,slug2,slug3}}`: cartões de posts que já existem no blog (título, resumo e capa lidos do próprio post).
  Toda página deve terminar remetendo a posts do catálogo.

O alfabeto manual usa a fonte `assets/fonts/Libras2020-Regular.woff2` (classe `.dat`), de uso autorizado pelo autor.
Ela cobre A–Z, Ç e 0–9; acentos e pontuação não têm mão e são removidos antes de soletrar.

A faixa de navegação entre as áreas entra sozinha logo depois de `<main>` (desligue com `"areas_nav": false`).

## Regras de conteúdo

- Fatos, datas e leis da página de cultura surda foram conferidos em fontes oficiais em out/2026.
  Antes de incluir um fato novo, confira em lei (Câmara/Senado/Planalto) ou fonte primária.
- Materiais de sala de aula excluem o sinal de "cerveja".
- Todo material leva o crédito "LIBRAS.SE · libras.se/..." no rodapé.
- Os sinais seguem a variante usada pela equipe em Santa Catarina; mantenha esse aviso.
- Imagens sociais: entradas `aprender-libras`, `cultura-surda`, `jogos`, `atividades` e `materiais` em `og/pages.json`.
