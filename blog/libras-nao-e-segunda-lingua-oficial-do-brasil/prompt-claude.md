# Prompt para Claude criar o post

Voce e um desenvolvedor front-end e redator especializado em acessibilidade, Libras, cultura surda, legislacao brasileira e conteudo institucional para a LIBRAS.SE.

Crie o arquivo `blog/libras-nao-e-segunda-lingua-oficial-do-brasil/index.html` para o post:

**Libras nao e a segunda lingua oficial do Brasil. Entenda o que a lei realmente diz**

Use rigorosamente os padroes de `blog/CLAUDE.md` e o estilo dos posts existentes:

- `blog/garantir-libras-sem-improviso/index.html`
- `blog/voce-sabe-o-que-e-datilologia/index.html`
- `blog/libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado/index.html`
- `blog/videoaulas-acessiveis-com-libras/index.html`, se ja existir

Observacao importante: o arquivo antigo indicado como base, `texto antigo`, esta vazio. Portanto, use o texto-base, a pesquisa e a estrutura abaixo como materia-prima do post. Mantenha o tom dos posts do blog da LIBRAS.SE: didatico, direto, acolhedor, com autoridade tecnica e sem juridiquês.

## Objetivo editorial

Explicar uma confusao muito comum: a Libras e reconhecida por lei, tem estrutura linguistica propria e e fundamental para a comunidade surda brasileira, mas isso nao significa que ela seja a segunda lingua oficial do Brasil.

O post deve corrigir a informacao sem diminuir a importancia da Libras. A ideia central e:

- A Constituicao Federal define a lingua portuguesa como o idioma oficial da Republica Federativa do Brasil.
- A Lei nº 10.436/2002 reconhece a Libras como meio legal de comunicacao e expressao.
- A lei nao diz que a Libras e "segunda lingua oficial do Brasil".
- Em contextos de educacao bilingue de surdos, a legislacao fala em Libras como primeira lingua e portugues escrito como segunda lingua para estudantes surdos optantes dessa modalidade. Isso e diferente de dizer que o pais tem uma segunda lingua oficial.
- Chamar Libras de "segunda lingua oficial" pode parecer valorizacao, mas cria uma informacao juridicamente imprecisa.
- A melhor forma de valorizar a Libras e falar dela com precisao: ela e lingua, e visual-motora, tem gramatica propria, e reconhecida legalmente como meio de comunicacao e expressao.

## Tom e estilo

Use o tom dos posts do blog da LIBRAS.SE:

- didatico, direto e acolhedor;
- com frases curtas e ritmo de leitura confortavel;
- com autoridade tecnica, mas sem transformar o texto em parecer juridico;
- sem atacar quem usa a frase errada;
- sem reduzir a importancia da Libras;
- sem tratar acessibilidade como favor;
- com CTA comercial suave no final.

Evite:

- dizer que Libras e "linguagem";
- usar "surdo-mudo";
- afirmar que toda pessoa surda usa Libras;
- dizer que a Libras deriva do portugues;
- insinuar que o reconhecimento legal da Libras e menor por ela nao ser idioma oficial do pais;
- criar um texto frio, punitivo ou excessivamente juridico.

## SEO e metadados

Use:

```html
<title>Libras nao e a segunda lingua oficial do Brasil: entenda a lei | LIBRAS.SE</title>
<meta name="description" content="Entenda por que a Libras nao e a segunda lingua oficial do Brasil, o que a Lei nº 10.436/2002 realmente reconhece e como falar sobre Libras com precisao.">
<meta name="keywords" content="Libras segunda lingua oficial, Libras e lingua oficial, Lei de Libras, Lei 10.436, lingua brasileira de sinais, acessibilidade, comunidade surda">
```

Categoria no nav:

```html
<span class="nav-tag">Blog · Libras & Lei</span>
```

Hero:

- Kicker: `Libras & cidadania`
- Titulo: `Libras nao e a segunda lingua oficial` com destaque em `do Brasil`
- Subtitulo: `A Libras e uma lingua reconhecida por lei, com estrutura propria e papel central para a comunidade surda. Mas a frase "segunda lingua oficial do Brasil" nao e o que a legislacao diz.`
- Data: `20 de maio de 2026`
- Leitura: `7 min de leitura`

## Estrutura recomendada do artigo

1. **Introducao: uma frase bem-intencionada, mas imprecisa**
   - Abrir dizendo que a frase "Libras e a segunda lingua oficial do Brasil" aparece em cursos, eventos, posts e materiais institucionais.
   - Explicar que a intencao costuma ser valorizar a Libras, mas a informacao precisa ser corrigida.
   - Usar `drop-cap` no primeiro paragrafo.

2. **O que e idioma oficial do Brasil**
   - Explicar que a Constituicao Federal, no artigo 13, define a lingua portuguesa como o idioma oficial da Republica Federativa do Brasil.
   - Evitar juridiquês. Dizer de forma simples: no plano constitucional nacional, o idioma oficial do pais e o portugues.
   - Criar `law-callout` para esse ponto.

3. **O que a Lei de Libras realmente reconhece**
   - Explicar que a Lei nº 10.436/2002 reconhece a Libras como meio legal de comunicacao e expressao.
   - Explicar que a lei descreve a Libras como sistema linguistico visual-motor, com estrutura gramatical propria.
   - Deixar claro: isso confirma que Libras e lingua, mas nao transforma a Libras em "segundo idioma oficial" do pais.

4. **Por que a confusao acontece**
   - Apontar tres fontes frequentes de confusao:
     - uso popular da expressao "oficializada";
     - materiais institucionais que simplificam a frase;
     - educacao bilingue de surdos, onde Libras pode ser primeira lingua e portugues escrito segunda lingua.
   - Usar cards ou `use-grid`.

5. **Libras como primeira lingua e portugues escrito como segunda lingua: em qual contexto?**
   - Explicar a diferenca entre "segunda lingua oficial do Brasil" e "portugues escrito como segunda lingua para estudantes surdos na educacao bilingue".
   - Citar a Lei nº 14.191/2021 e o Decreto nº 5.626/2005 como base para essa nuance.
   - Pontuar: esse e um conceito educacional e linguistico aplicado a sujeitos e contextos especificos, nao uma definicao de idioma oficial nacional.

6. **Nao ser idioma oficial nao diminui a Libras**
   - Este e o ponto mais sensivel do post.
   - Dizer que a importancia da Libras nao depende de uma frase imprecisa.
   - Reforcar que a Libras e uma lingua completa, usada por comunidades surdas brasileiras, com reconhecimento legal, valor cultural, funcao educacional e papel de acesso a direitos.
   - Usar pull quote:
     `Valorizar a Libras tambem e falar dela com precisao. Reconhecimento legal nao precisa virar mito para ser importante.`

7. **Como falar corretamente**
   - Criar bloco comparativo com frases:
     - Evite: "Libras e a segunda lingua oficial do Brasil."
     - Prefira: "Libras e reconhecida por lei como meio legal de comunicacao e expressao."
     - Prefira tambem: "Na educacao bilingue de surdos, a Libras pode ser a primeira lingua e o portugues escrito, a segunda."
     - Prefira em textos institucionais: "A Libras e uma lingua visual-motora, com gramatica propria, reconhecida pela Lei nº 10.436/2002."

8. **Por que a precisao importa em acessibilidade**
   - Mostrar que termos corretos ajudam empresas, escolas, eventos e orgaos publicos a planejar melhor.
   - Exemplo: se uma instituicao acha que basta "mencionar a lingua oficial", pode nao pensar em interpretes, janela de Libras, materiais bilingues, atendimento acessivel ou profissionais qualificados.
   - A precisao evita campanhas bonitas, mas vazias.

9. **Checklist rapido para revisar seu conteudo sobre Libras**
   - Criar `process-steps` ou checklist visual:
     1. O texto chama Libras de lingua, nao de linguagem?
     2. Evita a expressao "surdo-mudo"?
     3. Explica que Libras tem estrutura propria?
     4. Diferencia reconhecimento legal de idioma oficial?
     5. Indica recursos concretos de acessibilidade?
     6. Usa fontes oficiais quando fala de lei?

10. **Fechamento e CTA**
   - Reforcar que corrigir a frase nao e diminuir a Libras, e tratar a lingua com seriedade.
   - CTA:
     - Titulo: `Precisa comunicar acessibilidade com precisao?`
     - Texto: `A LIBRAS.SE apoia empresas, instituicoes e produtores de conteudo na criacao de materiais acessiveis com Libras, legendas, orientacao tecnica e linguagem adequada para cada contexto.`
     - Botao: `Fale com a LIBRAS.SE`
     - Link: `https://www.libras.se`

## Texto-base para o artigo

Use este texto como base, reescrevendo com fluidez e adaptando ao HTML do blog:

> Voce provavelmente ja leu ou ouviu a frase: "Libras e a segunda lingua oficial do Brasil". Ela aparece em publicacoes, cursos, eventos, campanhas e ate em materiais institucionais. Quase sempre, a intencao e boa: valorizar a Lingua Brasileira de Sinais e reconhecer sua importancia para a comunidade surda. Mas a frase, do ponto de vista legal, nao esta correta.
>
> No Brasil, a Constituicao Federal define a lingua portuguesa como o idioma oficial da Republica Federativa do Brasil. A Libras tem outro tipo de reconhecimento: a Lei nº 10.436, de 24 de abril de 2002, reconhece a Lingua Brasileira de Sinais como meio legal de comunicacao e expressao. Essa diferenca parece pequena, mas muda bastante a forma correta de explicar o tema.
>
> A Lei de Libras nao diz que a Libras e a segunda lingua oficial do pais. O que ela diz e que a Libras e uma forma legalmente reconhecida de comunicacao e expressao, usada pelas comunidades surdas brasileiras. A lei tambem descreve a Libras como um sistema linguistico de natureza visual-motora, com estrutura gramatical propria. Em outras palavras: Libras e lingua. Nao e mimica, nao e gesto solto, nao e portugues sinalizado.
>
> A confusao acontece porque muita gente usa "oficial" como sinonimo de "reconhecido por lei". A Libras foi, sim, reconhecida oficialmente por uma lei federal. Mas isso nao e o mesmo que declarar a Libras como idioma oficial da Republica Federativa do Brasil. O idioma oficial nacional, no texto constitucional, continua sendo a lingua portuguesa.
>
> Tambem existe uma segunda fonte de confusao: a educacao bilingue de surdos. A legislacao brasileira reconhece contextos em que a Libras aparece como primeira lingua e o portugues escrito como segunda lingua para estudantes surdos. A Lei nº 14.191/2021, por exemplo, trata da educacao bilingue de surdos como modalidade escolar oferecida em Libras, como primeira lingua, e em portugues escrito, como segunda lingua. Isso e muito importante. Mas esse conceito vale para a organizacao educacional e linguistica de um publico especifico. Nao significa que a Libras virou a segunda lingua oficial do Brasil.
>
> Corrigir essa frase nao diminui a Libras. Pelo contrario: mostra respeito. A Libras nao precisa ser chamada de "segunda lingua oficial" para ser reconhecida como uma lingua completa, com gramatica propria, valor cultural, papel educacional e importancia direta no acesso a direitos. A precisao ajuda a combater mitos e fortalece a forma como empresas, escolas, eventos e orgaos publicos planejam acessibilidade.
>
> Quando um material institucional diz apenas que a Libras e "segunda lingua oficial", ele pode parecer inclusivo, mas continuar sem oferecer interprete, janela de Libras, atendimento acessivel, legenda, transcricao ou profissionais qualificados. Acessibilidade nao se resolve com uma frase bonita. Ela precisa aparecer nas escolhas concretas de comunicacao.
>
> Uma forma mais correta de escrever e: "A Libras e reconhecida pela Lei nº 10.436/2002 como meio legal de comunicacao e expressao". Outra opcao e: "A Libras e uma lingua visual-motora, com estrutura gramatical propria, reconhecida legalmente no Brasil". Se o contexto for educacao bilingue de surdos, tambem e correto explicar que a Libras pode ser a primeira lingua e o portugues escrito, a segunda lingua, para estudantes surdos nessa modalidade.
>
> No fim, a pergunta nao e se a Libras merece importancia. Ela merece. A questao e falar sobre essa importancia com responsabilidade. Valorizar a Libras tambem e usar informacao correta, respeitar sua estrutura linguistica e transformar reconhecimento em acesso real.

## Pesquisa elaborada para embasar o post

Use estes pontos de pesquisa no conteudo, em caixas de referencia, `law-callout` ou secao de referencias. Parafraseie; nao copie trechos longos.

### Idioma oficial do Brasil

- A Constituicao Federal, no art. 13, estabelece que a lingua portuguesa e o idioma oficial da Republica Federativa do Brasil.
- Use esse ponto para explicar por que nao e correto dizer que a Libras e "segunda lingua oficial do Brasil".
- Fonte: https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm

### Libras e reconhecida como meio legal de comunicacao e expressao

- A Lei nº 10.436/2002 reconhece a Lingua Brasileira de Sinais como meio legal de comunicacao e expressao.
- A mesma lei descreve a Libras como sistema linguistico de natureza visual-motora, com estrutura gramatical propria.
- Use esse ponto para reforcar que Libras e lingua, mas que a lei nao a declara como idioma oficial nacional.
- Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10436.htm

### Pessoa surda e experiencia visual

- O Decreto nº 5.626/2005 regulamenta a Lei de Libras.
- O decreto considera pessoa surda aquela que, por perda auditiva, compreende e interage com o mundo por experiencias visuais e manifesta sua cultura principalmente pelo uso da Libras.
- O decreto tambem trata do ensino de Libras e do ensino da modalidade escrita da Lingua Portuguesa como segunda lingua para alunos surdos.
- Use isso para explicar a diferenca entre reconhecimento da Libras, educacao bilingue e idioma oficial nacional.
- Fonte: https://www.planalto.gov.br/ccivil_03/_Ato2004-2006/2005/Decreto/D5626.htm

### Educacao bilingue de surdos

- A Lei nº 14.191/2021 alterou a LDB para tratar da modalidade de educacao bilingue de surdos.
- A lei define essa modalidade como educacao escolar oferecida em Libras, como primeira lingua, e em portugues escrito, como segunda lingua, em escolas bilingues, classes bilingues, escolas comuns ou polos de educacao bilingue de surdos, para educandos optantes.
- Use esse ponto para explicar por que "portugues escrito como segunda lingua para surdos" nao e a mesma coisa que "Libras como segunda lingua oficial do Brasil".
- Fonte: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14191.htm

### A LBI reconhece comunicacao em sentido amplo

- A Lei Brasileira de Inclusao, Lei nº 13.146/2015, define comunicacao de modo amplo, incluindo Libras, visualizacao de textos, Braille, linguagem simples, dispositivos multimidia e tecnologias da informacao e comunicacao.
- Use esse ponto para conectar precisao terminologica com acessibilidade concreta.
- Fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm

### Dados de contexto

- O Censo 2022 apontou 14,4 milhoes de pessoas com deficiencia no Brasil, 7,3% da populacao com 2 anos ou mais, nos resultados preliminares divulgados pelo IBGE em 23 de maio de 2025.
- Entre essas pessoas, 2,6 milhoes tinham dificuldade para ouvir, mesmo com aparelho auditivo.
- Use esses dados apenas para contextualizar a relevancia de acessibilidade. Nao apresente esses numeros como quantidade de usuarios de Libras.
- Fonte: https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/43463-censo-2022-brasil-tem-14-4-milhoes-de-pessoas-com-deficiencia

## Sugestoes visuais e de CSS

Use os componentes existentes em `blog/CLAUDE.md`:

- `law-callout` para Constituicao Federal, Lei nº 10.436/2002 e Lei nº 14.191/2021.
- `pull-quote` para a frase central sobre valorizar a Libras com precisao.
- `highlight-box` para alertar que "reconhecida por lei" nao e o mesmo que "idioma oficial".
- `use-grid` para as fontes da confusao.
- `process-steps` para o checklist de revisao.
- `references` no final com as fontes.

Crie tambem, se fizer sentido, CSS novo para um bloco comparativo:

```css
.phrase-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin: 48px 0;
}

.phrase-card {
  background: var(--white);
  border: 1px solid var(--grey-light);
  border-radius: var(--radius);
  padding: 28px;
  box-shadow: 0 6px 28px rgba(30,110,110,0.06);
}

.phrase-card.warning {
  border-left: 4px solid var(--orange);
}

.phrase-card.good {
  border-left: 4px solid var(--teal-mid);
}

.phrase-card h3 {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--teal-dark);
  margin-bottom: 12px;
}

.phrase-card.warning h3 {
  color: var(--orange);
}

.phrase-card p {
  font-family: 'Lora', serif;
  font-size: 0.95rem;
  color: var(--ink-soft);
  line-height: 1.7;
}

@media (max-width: 700px) {
  .phrase-grid {
    grid-template-columns: 1fr;
  }
}
```

Exemplo de HTML para o bloco:

```html
<div class="phrase-grid reveal">
  <article class="phrase-card warning">
    <h3>Evite</h3>
    <p>"Libras e a segunda lingua oficial do Brasil."</p>
  </article>
  <article class="phrase-card good">
    <h3>Prefira</h3>
    <p>"A Libras e reconhecida pela Lei nº 10.436/2002 como meio legal de comunicacao e expressao."</p>
  </article>
  <article class="phrase-card good">
    <h3>Em educacao bilingue</h3>
    <p>"Na educacao bilingue de surdos, a Libras pode ser a primeira lingua e o portugues escrito, a segunda."</p>
  </article>
  <article class="phrase-card good">
    <h3>Em texto institucional</h3>
    <p>"A Libras e uma lingua visual-motora, com estrutura gramatical propria, reconhecida legalmente no Brasil."</p>
  </article>
</div>
```

## Possivel formatacao do artigo

Use esta sequencia no HTML final:

```html
<div id="progress-bar"></div>

<nav>
  <a href="/" class="nav-logo">
    <span class="hand-icon">🤟</span>
    LIBRAS.SE
  </a>
  <span class="nav-tag">Blog · Libras & Lei</span>
</nav>

<section class="hero" aria-label="Cabecalho do artigo">
  <div class="hero-bg"></div>
  <div class="hero-noise"></div>
  <div class="hero-grid-overlay"></div>
  <div class="hero-circles">
    <span></span><span></span><span></span>
  </div>
  <div class="hero-content">
    <div class="hero-kicker" aria-label="Categoria do artigo">Libras & cidadania</div>
    <h1 class="hero-title">Libras nao e a segunda lingua oficial <em>do Brasil</em></h1>
    <p class="hero-subtitle">A Libras e uma lingua reconhecida por lei, com estrutura propria e papel central para a comunidade surda. Mas a frase "segunda lingua oficial do Brasil" nao e o que a legislacao diz.</p>
    <div class="hero-meta">
      <span class="meta-badge">20 de maio de 2026</span>
      <span class="meta-badge">7 min de leitura</span>
      <span class="meta-badge">LIBRAS.SE</span>
    </div>
  </div>
  <div class="hero-scroll-hint" aria-hidden="true">
    <span class="scroll-dot"></span>
    <span class="scroll-dot"></span>
    <span class="scroll-dot"></span>
  </div>
</section>

<main class="article-wrapper" id="article">
  <p class="section-label">Precisao importa</p>
  <p class="body-text drop-cap">Voce provavelmente ja leu ou ouviu a frase...</p>

  <div class="law-callout reveal">...</div>
  <div class="highlight-box reveal">...</div>

  <p class="section-label">O que a lei diz</p>
  <p class="body-text">A Lei nº 10.436/2002 reconhece...</p>

  <blockquote class="pull-quote reveal">
    <p>Valorizar a Libras tambem e falar dela com precisao. <strong>Reconhecimento legal nao precisa virar mito para ser importante.</strong></p>
  </blockquote>

  <p class="section-label">Como escrever melhor</p>
  <div class="phrase-grid reveal">...</div>

  <p class="section-label">Checklist rapido</p>
  <div class="process-steps reveal">...</div>

  <section class="references reveal">
    <h2>Fontes consultadas</h2>
    <ul>
      <li><a href="https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm">Constituicao Federal, art. 13</a></li>
      <li><a href="https://www.planalto.gov.br/ccivil_03/leis/2002/l10436.htm">Lei nº 10.436/2002</a></li>
      <li><a href="https://www.planalto.gov.br/ccivil_03/_Ato2004-2006/2005/Decreto/D5626.htm">Decreto nº 5.626/2005</a></li>
      <li><a href="https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14191.htm">Lei nº 14.191/2021</a></li>
      <li><a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm">Lei Brasileira de Inclusao</a></li>
      <li><a href="https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/43463-censo-2022-brasil-tem-14-4-milhoes-de-pessoas-com-deficiencia">IBGE, Censo 2022: pessoas com deficiencia</a></li>
    </ul>
  </section>

  <section class="cta-section reveal">
    <h2>Precisa comunicar acessibilidade com precisao?</h2>
    <p>A LIBRAS.SE apoia empresas, instituicoes e produtores de conteudo na criacao de materiais acessiveis com Libras, legendas, orientacao tecnica e linguagem adequada para cada contexto.</p>
    <a href="https://www.libras.se" class="cta-button">Fale com a LIBRAS.SE</a>
  </section>
</main>
```

## Orientacoes finais para o Claude

- Gere um `index.html` completo, autonomo e responsivo.
- Siga o visual dos posts existentes, sem criar uma landing page.
- Use hero com gradiente puro, sem depender de imagem externa.
- Inclua barra de progresso e scroll reveal conforme `blog/CLAUDE.md`.
- Inclua secao de fontes consultadas no final.
- Nao copie trechos longos das fontes legais; parafraseie.
- Mantenha a correcao juridica: Libras e reconhecida por lei como meio legal de comunicacao e expressao; a lingua portuguesa e o idioma oficial do Brasil; educacao bilingue de surdos e outro contexto.
- Transforme a correcao em uma conversa util, nao em bronca.
