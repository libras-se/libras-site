# Prompt para Claude criar o post

Você é um desenvolvedor front-end e redator especializado em acessibilidade, Libras, cultura surda, linguística e conteúdo institucional para a LIBRAS.SE.

Crie o arquivo `blog/libras-tem-sotaque-e-giria/index.html` para o post:

**Libras tem sotaque e gíria? Entenda as variações regionais da língua**

Use rigorosamente os padrões de `blog/CLAUDE.md` e o estilo dos posts existentes:

- `blog/garantir-libras-sem-improviso/index.html`
- `blog/voce-sabe-o-que-e-datilologia/index.html`
- `blog/libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado/index.html`
- `blog/videoaulas-acessiveis-com-libras/index.html`, se já existir

Observação importante: o arquivo antigo indicado como base, `post antigo`, está vazio. Porém existe uma versão antiga publicada no site da LIBRAS.SE com o mesmo tema, usada como referência editorial: `https://www.libras.se/post/libras-tem-sotaque-e-giria`. Use a ideia, os exemplos e o tom desse post antigo como base, mas reescreva o artigo com mais contexto, melhor estrutura, fontes e formatação moderna.

## Objetivo editorial

Explicar que a Libras, como qualquer língua natural, tem variações. Essas variações podem aparecer por região, idade, comunidade, contexto de uso, contato entre pessoas surdas e ouvintes, circulação em redes sociais e mudanças culturais.

O post deve responder de forma clara:

- Sim, Libras tem variações regionais.
- A palavra "sotaque" pode ser usada de forma didática, como metáfora, mas tecnicamente é melhor falar em variação linguística, variação regional, variação lexical e variação fonológica.
- A Libras também pode ter expressões de grupo, usos informais, sinais que circulam em comunidades específicas e formas novas que lembram o papel das gírias nas línguas orais.
- Variação não é erro. É sinal de que a língua está viva.
- Uma pessoa pode encontrar sinais diferentes para a mesma ideia em São Paulo, Rio de Janeiro, Minas Gerais, Curitiba, Mato Grosso do Sul e outras regiões.
- Em tradução, interpretação, videoaulas, atendimento e materiais institucionais, essas diferenças precisam ser tratadas com respeito e planejamento.

## Tom e estilo

Use o tom dos posts do blog da LIBRAS.SE:

- didático, direto e acolhedor;
- com autoridade técnica, mas sem virar artigo acadêmico;
- com exemplos concretos e linguagem visual;
- com frases curtas e leitura fluida;
- sem corrigir a comunidade surda de fora para dentro;
- sem tratar variação como "erro" ou "falta de padrão";
- com CTA comercial suave no final.

Evite:

- dizer que Libras é "linguagem";
- dizer que existe uma Libras única, pura ou neutra;
- afirmar que uma variante regional é mais correta que outra;
- transformar os GIFs em dicionário definitivo;
- usar "surdo-mudo";
- dizer que todos os surdos usam Libras da mesma forma;
- tratar gíria como algo menor ou errado.

## SEO e metadados

Use:

```html
<title>Libras tem sotaque e gíria? Entenda as variações regionais | LIBRAS.SE</title>
<meta name="description" content="Libras também tem variações regionais, usos informais e sinais que mudam conforme comunidade, contexto e região. Entenda por que isso não é erro.">
<meta name="keywords" content="Libras tem sotaque, gíria em Libras, variação regional em Libras, regionalismo em Libras, sinais regionais, comunidade surda, língua brasileira de sinais">
```

Categoria no nav:

```html
<span class="nav-tag">Blog · Língua & Cultura</span>
```

Hero:

- Kicker: `Língua viva`
- Título: `Libras tem sotaque` com destaque em `e gíria?`
- Subtítulo: `Assim como o português muda de uma região para outra, a Libras também carrega marcas de território, comunidade, idade, uso e cultura.`
- Data: `20 de maio de 2026`
- Leitura: `7 min de leitura`

## Imagens e GIFs disponíveis

Use obrigatoriamente os GIFs da pasta:

```text
../../assets/img/blog/libras-tem-sotaque-e-giria/MAS%20EM%20LIBRAS.gif
../../assets/img/blog/libras-tem-sotaque-e-giria/CERVEJA%20EM%20LIBRAS.gif
../../assets/img/blog/libras-tem-sotaque-e-giria/VERDE%20EM%20LIBRAS.gif
../../assets/img/blog/libras-tem-sotaque-e-giria/TRISTE%20EM%20LIBRAS.gif
```

Arquivos reais na pasta:

- `MAS EM LIBRAS.gif` - compara variantes de São Paulo e Rio de Janeiro.
- `CERVEJA EM LIBRAS.gif` - compara variantes de Minas Gerais e São Paulo.
- `VERDE EM LIBRAS.gif` - compara variantes de Rio de Janeiro, São Paulo e Curitiba.
- `TRISTE EM LIBRAS.gif` - compara variantes de São Paulo, Rio de Janeiro e Mato Grosso do Sul.

Orientações de uso:

- Não use os GIFs no hero. Use hero com gradiente e elementos gráficos leves.
- Use os GIFs no corpo do artigo, próximos às seções em que os exemplos são explicados.
- Trate os GIFs como exemplos visuais de variação regional, não como lista definitiva de sinais corretos.
- Use `loading="lazy"` em todos os GIFs.
- Use `alt` descritivo e legenda textual. Como os GIFs têm informação linguística, eles não devem ser `aria-hidden`.
- Não dependa só do GIF para explicar o conteúdo. O texto precisa descrever a diferença de forma geral.
- Como GIFs animados não têm controle de pausa, evite colocar todos muito colados. Intercale texto e blocos visuais.
- Se criar CSS específico, mantenha os GIFs em proporção 16:9, com `object-fit: cover`, bordas suaves e legenda clara.

Exemplo recomendado de CSS para os GIFs:

```css
.sign-gallery {
  display: grid;
  grid-template-columns: 1fr;
  gap: 28px;
  margin: 48px 0;
}

.sign-figure {
  margin: 0;
  background: var(--white);
  border: 1px solid var(--grey-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 18px 50px rgba(30,110,110,0.12);
}

.sign-figure img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
  background: #fff;
}

.sign-figure figcaption {
  font-family: 'Lora', serif;
  font-size: 0.86rem;
  font-style: italic;
  line-height: 1.65;
  color: var(--ink-soft);
  padding: 18px 24px;
  background: var(--teal-bg);
  border-top: 1px solid var(--teal-pale);
}

.sign-figure figcaption strong {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-style: normal;
  color: var(--teal-dark);
}
```

Exemplo recomendado de HTML:

```html
<div class="sign-gallery reveal">
  <figure class="sign-figure">
    <img src="../../assets/img/blog/libras-tem-sotaque-e-giria/VERDE%20EM%20LIBRAS.gif" alt="GIF comparando variações regionais do sinal de verde em Libras no Rio de Janeiro, em São Paulo e em Curitiba." loading="lazy">
    <figcaption><strong>VERDE:</strong> o GIF mostra três formas regionais para o mesmo conceito. A diferença aparece na configuração das mãos, no movimento e no ponto de articulação.</figcaption>
  </figure>
</div>
```

## Estrutura recomendada do artigo

1. **Introdução: mandioca, aipim, macaxeira... e Libras**
   - Abrir com exemplos do português brasileiro: mandioca, aipim, macaxeira; mexerica e bergamota; rotatória, rótula ou balão.
   - Conectar com a pergunta: se o português varia em um país continental, por que a Libras seria igual em todos os lugares?
   - Usar `drop-cap` no primeiro parágrafo.

2. **Libras é língua viva**
   - Explicar que Libras é uma língua visual-motora, com estrutura gramatical própria.
   - Reforçar que línguas mudam porque são usadas por pessoas reais, em comunidades reais.
   - Incluir `law-callout` curto citando a Lei nº 10.436/2002, apenas para lembrar que Libras é reconhecida como meio legal de comunicação e expressão.

3. **Então Libras tem sotaque?**
   - Explicar que "sotaque" é uma metáfora útil para quem está chegando ao tema.
   - Em línguas orais, sotaque costuma envolver pronúncia, ritmo e entonação. Em Libras, a variação pode aparecer em aspectos visuais do sinal.
   - Usar linguagem técnica simples: configuração de mão, movimento, ponto de articulação, orientação da palma e expressões não manuais.
   - Deixar claro: o melhor termo técnico é variação linguística.

4. **Variação regional: quando o mesmo conceito ganha sinais diferentes**
   - Inserir uma `sign-gallery` com os GIFs de `VERDE`, `CERVEJA`, `TRISTE` e `MAS`.
   - Explicar cada exemplo:
     - `VERDE`: Rio de Janeiro, São Paulo e Curitiba usam formas diferentes.
     - `CERVEJA`: Minas Gerais e São Paulo mostram variação no sinal.
     - `TRISTE`: São Paulo, Rio de Janeiro e Mato Grosso do Sul apresentam diferenças de forma e nuance.
     - `MAS`: São Paulo e Rio de Janeiro variam no movimento, na configuração e no ritmo.
   - Não afirmar que esses são os únicos sinais possíveis.

5. **O que muda em um sinal**
   - Criar cards com os cinco parâmetros:
     - configuração de mão;
     - ponto de articulação ou locação;
     - movimento;
     - orientação da palma;
     - expressões faciais e corporais.
   - Explicar que uma mudança em um desses elementos pode criar uma variante regional ou, em alguns casos, outro significado.

6. **E gíria em Libras, existe?**
   - Explicar com cuidado: se entendermos gíria como uso informal, expressão de grupo, forma que circula entre pessoas de uma comunidade, jovens, redes sociais ou contextos específicos, sim, Libras também pode ter usos desse tipo.
   - Evitar tratar "gíria" como bagunça ou erro.
   - Dizer que, como em qualquer língua, alguns usos se espalham, outros ficam restritos, e outros mudam com o tempo.

7. **Variação não é falta de padrão**
   - Este é o ponto central do post.
   - Usar pull quote:
     `Quando uma língua varia, ela não fica menor. Ela mostra que pertence a pessoas, lugares, histórias e modos de viver.`
   - Explicar que padronização pode ser útil em dicionários, materiais didáticos e serviços públicos, mas não deve apagar a diversidade linguística da comunidade surda.

8. **O que isso muda para empresas, escolas e produtores de conteúdo**
   - Explicar que quem produz vídeos, cursos, eventos e atendimentos com Libras precisa entender o público.
   - Exemplo: um vídeo nacional pode precisar de escolhas mais amplamente compreendidas; um material regional pode usar sinais locais; uma videoaula pode precisar contextualizar termos.
   - Destacar a importância de intérpretes, tradutores e revisores com repertório e contato com a comunidade surda.

9. **Como lidar com sinais regionais em projetos acessíveis**
   - Criar `process-steps`:
     1. Identifique o público e a região principal.
     2. Levante termos sensíveis, técnicos ou muito locais.
     3. Consulte profissionais surdos e tradutores-intérpretes experientes.
     4. Evite corrigir uma variante sem entender o contexto.
     5. Quando necessário, explique o termo no próprio vídeo ou material.
     6. Revise o conteúdo com pessoas que conhecem o público final.

10. **Fechamento e CTA**
   - Reforçar que Libras tem variação porque é língua viva.
   - CTA:
     - Título: `Seu conteúdo em Libras precisa falar com o público certo?`
     - Texto: `A LIBRAS.SE apoia empresas, instituições e produtores na criação de vídeos acessíveis com Libras, revisão linguística, legendas e orientação para conteúdos nacionais, regionais e especializados.`
     - Botão: `Fale com a LIBRAS.SE`
     - Link: `https://www.libras.se`

## Texto-base para o artigo

Use este texto como base, reescrevendo com fluidez e adaptando ao HTML do blog:

> Mandioca, aipim, macaxeira. Mexerica, bergamota, tangerina. Rótula, rotatória, balão. Em um país do tamanho do Brasil, é normal que a mesma coisa receba nomes diferentes dependendo da região. A língua acompanha a vida das pessoas. Ela muda de cidade para cidade, de geração para geração, de grupo para grupo. Com a Libras, não é diferente.
>
> A Língua Brasileira de Sinais é uma língua visual-motora, com estrutura própria, usada por comunidades surdas brasileiras. Ela não é uma versão gestual do português. Também não é uma coleção fixa de sinais iguais em todos os lugares. Como qualquer língua viva, a Libras tem história, contato, mudança, preferência local e criação coletiva.
>
> Por isso, muita gente pergunta: Libras tem sotaque? A resposta curta é: sim, se usarmos "sotaque" como uma forma simples de falar sobre variação. Mas, tecnicamente, o mais preciso é dizer que a Libras tem variação linguística. Em vez de som, pronúncia e entonação, a variação pode aparecer na configuração das mãos, no movimento, no ponto do corpo em que o sinal acontece, na orientação da palma e nas expressões faciais e corporais.
>
> Um mesmo conceito pode ter sinais diferentes em regiões diferentes. O sinal de "verde", por exemplo, pode variar entre Rio de Janeiro, São Paulo e Curitiba. O sinal de "cerveja" pode mudar entre Minas Gerais e São Paulo. "Triste" pode ter formas parecidas em alguns lugares e mais diferentes em outros. Até um conectivo como "mas" pode carregar diferenças de movimento, configuração de mão e ritmo.
>
> Essas diferenças não tornam uma forma melhor do que a outra. Elas mostram que a Libras circula por comunidades reais. Pessoas surdas de regiões diferentes convivem, estudam, trabalham, criam sinais, mantêm sinais antigos, adaptam usos e compartilham repertórios. Às vezes uma forma se espalha. Às vezes fica mais local. Às vezes duas variantes convivem por muito tempo.
>
> Também é possível falar em usos informais na Libras. Se entendermos gíria como uma forma de expressão ligada a grupo, idade, contexto, humor, redes sociais ou pertencimento, a Libras também pode ter esse tipo de uso. Como acontece no português, algumas expressões aparecem em determinados círculos, ganham força, mudam ou desaparecem.
>
> O ponto importante é não tratar variação como erro. Em línguas vivas, variar é normal. O cuidado está em entender o contexto. Em uma aula, um vídeo institucional, uma campanha pública ou um atendimento, a escolha de sinais precisa considerar quem vai assistir, qual é a região do público, qual é o tema e se há termos técnicos ou muito locais.
>
> Para projetos acessíveis, isso muda bastante. Não basta colocar uma janela de Libras no vídeo e imaginar que todo sinal será compreendido da mesma forma por todas as pessoas. É preciso planejar, consultar profissionais qualificados, revisar o conteúdo e, quando necessário, explicar termos. Acessibilidade boa respeita a língua e também respeita a diversidade dentro da própria língua.
>
> Libras tem variação porque é língua. Tem território, memória, comunidade, criação e mudança. E é justamente isso que mostra sua riqueza.

## Pesquisa elaborada para embasar o post

Use estes pontos de pesquisa no conteúdo, em caixas de referência ou seção de referências. Parafraseie; não copie trechos longos.

### Libras é língua reconhecida por lei

- A Lei nº 10.436/2002 reconhece a Língua Brasileira de Sinais como meio legal de comunicação e expressão.
- A lei descreve a Libras como sistema linguístico de natureza visual-motora, com estrutura gramatical própria.
- Use esse ponto para sustentar que Libras é língua e, portanto, também está sujeita a variação.
- Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10436.htm

### Pessoa surda e experiência visual

- O Decreto nº 5.626/2005 considera pessoa surda aquela que compreende e interage com o mundo por experiências visuais, manifestando sua cultura principalmente pelo uso da Libras.
- Use isso para conectar variação linguística com cultura, comunidade e experiência visual.
- Fonte: https://www.planalto.gov.br/ccivil_03/_Ato2004-2006/2005/Decreto/D5626.htm

### Variação linguística em Libras

- Estudos acadêmicos analisam variações na Libras em níveis lexical e fonológico.
- A Revista Espaço, do INES, publicou artigo sobre variação linguística em preposições na Libras, analisando variantes nos sinais "sobre" e "contra".
- Use esse ponto para mostrar que variação em Libras não é apenas percepção informal; é tema de pesquisa.
- Fonte: https://seer.ines.gov.br/index.php/revista-espaco/article/view/1552

### Variação lexical e regionalismos

- Pesquisa recente em corpus lexicográfico e visão computacional discute a análise de variações lexicais e regionalismos em Libras.
- O resumo destaca que regionalismos em Libras são objeto de investigação sociolinguística e que a variação não deve ser tratada como ruído a ser eliminado.
- Use com linguagem simples, sem aprofundar em inteligência artificial.
- Fonte: https://seer.ufu.br/index.php/dominiosdelinguagem/article/view/80463

### Corpus e documentação da Libras

- O Corpus de Libras da UFSC funciona como material de guarda da língua e subsidia pesquisas e análises linguísticas.
- O Signbank Libras apresenta sinais associados a aspectos linguísticos e dados sistematizados.
- Use esses recursos como referências de documentação, não como única autoridade sobre todas as variantes.
- Fontes:
  - https://corpuslibras.ufsc.br/
  - https://signbank.libras.ufsc.br/

### Post antigo da LIBRAS.SE

- A versão antiga do post já explicava, em linguagem simples, que a Libras tem variações regionais.
- Exemplos do post antigo: `VERDE`, `CERVEJA`, `TRISTE` e `MAS`, com GIFs comparando sinais de diferentes regiões.
- Use esse conteúdo como referência de estilo e exemplos, reescrevendo com mais contexto e estrutura.
- Fonte: https://www.libras.se/post/libras-tem-sotaque-e-giria

## Sugestões visuais e de CSS

Use os componentes existentes em `blog/CLAUDE.md`:

- `law-callout` para Lei nº 10.436/2002.
- `pull-quote` para a frase central sobre variação.
- `highlight-box` para destacar que variação não é erro.
- `use-grid` para os cinco parâmetros do sinal.
- `sign-gallery` para os quatro GIFs.
- `process-steps` para orientar projetos acessíveis.
- `references` no final com fontes.
- `cta-block` no encerramento.

Também pode usar `stat-row` com 3 dados simples:

- `5` parâmetros que podem mudar em um sinal.
- `4` GIFs com exemplos regionais.
- `1` língua viva, muitas formas de uso.

## Possível formatação do artigo

Use esta sequência no HTML final:

```html
<div id="progress-bar"></div>

<nav>
  <a href="/" class="nav-logo">
    <span class="hand-icon">🤟</span>
    LIBRAS.SE
  </a>
  <span class="nav-tag">Blog · Língua & Cultura</span>
</nav>

<section class="hero" aria-label="Cabeçalho do artigo">
  <div class="hero-bg"></div>
  <div class="hero-noise"></div>
  <div class="hero-grid-overlay"></div>
  <div class="hero-circles">
    <span></span><span></span><span></span>
  </div>
  <div class="hero-content">
    <div class="hero-kicker" aria-label="Categoria do artigo">Língua viva</div>
    <h1 class="hero-title">Libras tem sotaque <em>e gíria?</em></h1>
    <p class="hero-subtitle">Assim como o português muda de uma região para outra, a Libras também carrega marcas de território, comunidade, idade, uso e cultura.</p>
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
  <p class="section-label">Língua viva</p>
  <p class="body-text drop-cap">Mandioca, aipim, macaxeira...</p>

  <div class="law-callout reveal">...</div>
  <div class="highlight-box reveal">...</div>

  <p class="section-label">Sotaque visual?</p>
  <p class="body-text">A palavra "sotaque" ajuda a explicar...</p>

  <div class="stat-row reveal">...</div>

  <p class="section-label">Exemplos regionais</p>
  <div class="sign-gallery reveal">
    <figure class="sign-figure">
      <img src="../../assets/img/blog/libras-tem-sotaque-e-giria/VERDE%20EM%20LIBRAS.gif" alt="GIF comparando variações regionais do sinal de verde em Libras no Rio de Janeiro, em São Paulo e em Curitiba." loading="lazy">
      <figcaption><strong>VERDE:</strong> um mesmo conceito aparece com sinais diferentes em três regiões, mostrando variação de forma, movimento e ponto de articulação.</figcaption>
    </figure>
    <figure class="sign-figure">
      <img src="../../assets/img/blog/libras-tem-sotaque-e-giria/CERVEJA%20EM%20LIBRAS.gif" alt="GIF comparando variações regionais do sinal de cerveja em Libras em Minas Gerais e em São Paulo." loading="lazy">
      <figcaption><strong>CERVEJA:</strong> Minas Gerais e São Paulo aparecem com formas diferentes para o sinal, um bom exemplo de variação lexical regional.</figcaption>
    </figure>
    <figure class="sign-figure">
      <img src="../../assets/img/blog/libras-tem-sotaque-e-giria/TRISTE%20EM%20LIBRAS.gif" alt="GIF comparando variações regionais do sinal de triste em Libras em São Paulo, no Rio de Janeiro e no Mato Grosso do Sul." loading="lazy">
      <figcaption><strong>TRISTE:</strong> algumas variantes podem parecer próximas, mas mudam na configuração da mão, na localização ou na nuance de uso.</figcaption>
    </figure>
    <figure class="sign-figure">
      <img src="../../assets/img/blog/libras-tem-sotaque-e-giria/MAS%20EM%20LIBRAS.gif" alt="GIF comparando variações regionais do sinal de mas em Libras em São Paulo e no Rio de Janeiro." loading="lazy">
      <figcaption><strong>MAS:</strong> até conectivos podem variar. O movimento, a pausa e a configuração das mãos podem mudar de uma comunidade para outra.</figcaption>
    </figure>
  </div>

  <blockquote class="pull-quote reveal">
    <p>Quando uma língua varia, ela não fica menor. <strong>Ela mostra que pertence a pessoas, lugares, histórias e modos de viver.</strong></p>
  </blockquote>

  <p class="section-label">Projetos acessíveis</p>
  <div class="process-steps reveal">...</div>

  <div class="references reveal">
    <h4>Referências</h4>
    <ol>
      <li><a href="https://www.planalto.gov.br/ccivil_03/leis/2002/l10436.htm">Lei nº 10.436/2002</a></li>
      <li><a href="https://www.planalto.gov.br/ccivil_03/_Ato2004-2006/2005/Decreto/D5626.htm">Decreto nº 5.626/2005</a></li>
      <li><a href="https://seer.ines.gov.br/index.php/revista-espaco/article/view/1552">Revista Espaço/INES: variação linguística em Libras</a></li>
      <li><a href="https://seer.ufu.br/index.php/dominiosdelinguagem/article/view/80463">Domínios de Lingu@gem: regionalismos e variação lexical em Libras</a></li>
      <li><a href="https://corpuslibras.ufsc.br/">Corpus de Libras/UFSC</a></li>
      <li><a href="https://signbank.libras.ufsc.br/">Signbank Libras/UFSC</a></li>
      <li><a href="https://www.libras.se/post/libras-tem-sotaque-e-giria">Post antigo da LIBRAS.SE</a></li>
    </ol>
  </div>

  <div class="cta-block reveal">
    <h2>Seu conteúdo em Libras precisa falar com o público certo?</h2>
    <p>A LIBRAS.SE apoia empresas, instituições e produtores na criação de vídeos acessíveis com Libras, revisão linguística, legendas e orientação para conteúdos nacionais, regionais e especializados.</p>
    <a href="https://www.libras.se" class="cta-btn">Fale com a LIBRAS.SE <span class="arrow">→</span></a>
  </div>
</main>
```

## Orientações finais para o Claude

- Gere um `index.html` completo, autônomo e responsivo.
- Siga o visual dos posts existentes, sem criar uma landing page.
- Use hero com gradiente puro, sem depender de imagem externa.
- Inclua barra de progresso e scroll reveal conforme `blog/CLAUDE.md`.
- Inclua os quatro GIFs no corpo do artigo, com `alt` e `figcaption`.
- Não renomeie os arquivos de imagem; use `%20` nos caminhos por causa dos espaços.
- Não apresente os GIFs como a única forma correta de sinalizar.
- Explique que "sotaque" é uma metáfora didática e que o termo técnico é variação linguística.
- Inclua seção de referências no final.
- Mantenha o texto acessível para público leigo, mas tecnicamente responsável.
