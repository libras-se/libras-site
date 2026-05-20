# Prompt para Claude criar o post

Você é um desenvolvedor front-end e redator especializado em acessibilidade, Libras e conteúdo institucional para a LIBRAS.SE.

Crie o arquivo `blog/libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado/index.html` para o post:

**Libras ou legendas? Entenda quando e como cada recurso deve ser usado**

Use rigorosamente os padrões de `blog/CLAUDE.md` e o estilo dos posts existentes:

- `blog/garantir-libras-sem-improviso/index.html`
- `blog/voce-sabe-o-que-e-datilologia/index.html`

Observação importante: o arquivo antigo indicado como base, `post antigo2`, está vazio. Portanto, use o texto-base, a pesquisa e a estrutura abaixo como matéria-prima do post.

## Objetivo editorial

Explicar, em linguagem clara e estratégica, que Libras e legendas não são recursos equivalentes. Cada um resolve uma necessidade diferente de comunicação acessível:

- Libras atende pessoas surdas sinalizantes, especialmente quem tem a Libras como primeira língua ou principal língua de acesso à informação.
- Legendas ajudam pessoas surdas oralizadas, ensurdecidas, pessoas em ambientes sem som, pessoas aprendendo português e usuários que preferem ou precisam do texto.
- LSE, Legenda para Surdos e Ensurdecidos, não é apenas legenda comum: deve incluir falas, identificação de quem fala e sons relevantes.
- Em muitos projetos, a melhor escolha não é "Libras ou legenda", mas "Libras e legenda", quando o objetivo é alcançar públicos diversos.

## Tom e estilo

Use o tom dos posts do blog da LIBRAS.SE:

- didático, direto e acolhedor;
- com frases curtas e ritmo de leitura confortável;
- sem juridiquês;
- sem tratar acessibilidade como favor;
- com autoridade técnica, mas sem virar artigo acadêmico;
- com CTA comercial suave no final.

Evite:

- dizer que legenda substitui Libras;
- dizer que toda pessoa surda usa Libras;
- dizer que toda pessoa surda lê português com fluência;
- usar "surdo-mudo";
- tratar a comunidade surda como homogênea.

## SEO e metadados

Use:

```html
<title>Libras ou legendas? Quando usar cada recurso de acessibilidade | LIBRAS.SE</title>
<meta name="description" content="Libras e legendas não são recursos equivalentes. Entenda quando usar janela de Libras, legenda comum e LSE em vídeos, aulas, eventos e conteúdos digitais.">
<meta name="keywords" content="Libras, legendas, LSE, legenda para surdos e ensurdecidos, acessibilidade audiovisual, janela de Libras, acessibilidade digital">
```

Categoria no nav:

```html
<span class="nav-tag">Blog · Acessibilidade</span>
```

Hero:

- Kicker: `Acessibilidade audiovisual`
- Título: `Libras ou legendas?` com complemento `quando usar cada recurso`
- Subtítulo: `Nem toda acessibilidade para pessoas surdas acontece do mesmo jeito. Entender a diferença entre Libras, legenda comum e LSE evita escolhas incompletas.`
- Data: `20 de maio de 2026`
- Leitura: `7 min de leitura`

## Estrutura recomendada do artigo

1. **Introdução: a pergunta parece simples, mas não é**
   - Abrir com a falsa equivalência entre Libras e legenda.
   - Explicar que a pergunta certa não é "qual é melhor?", mas "para quem, em qual contexto e com qual objetivo?".
   - Usar `drop-cap` no primeiro parágrafo.

2. **O que a Libras entrega**
   - Explicar que Libras é língua visual-motora, com gramática própria.
   - Reforçar que ela não é português sinalizado.
   - Indicar que janela de Libras é essencial para pessoas surdas sinalizantes e muito relevante em vídeos institucionais, aulas, eventos, lives, treinamentos e campanhas públicas.

3. **O que a legenda entrega**
   - Explicar legenda comum: texto sincronizado com falas.
   - Explicar LSE: legenda para surdos e ensurdecidos, com identificação de falantes e sons relevantes.
   - Mostrar que LSE atende pessoas que não acessam o áudio, mas usam a língua escrita como caminho principal.

4. **Quadro comparativo**
   - Criar um bloco visual responsivo com 3 colunas/cards:
     - Libras
     - Legenda comum
     - LSE
   - Para cada uma, mostrar: melhor para, cobre, não cobre, quando usar.

5. **Quando usar Libras**
   - Cards ou grid:
     - conteúdos para comunidade surda sinalizante;
     - vídeos institucionais de alto alcance;
     - aulas, cursos e treinamentos;
     - eventos ao vivo e transmissões;
     - campanhas públicas ou conteúdos de interesse coletivo.

6. **Quando usar legendas ou LSE**
   - Cards ou process steps:
     - vídeos em redes sociais;
     - ambientes em que o usuário assiste sem som;
     - conteúdos com falas rápidas ou termos técnicos, desde que a legenda esteja bem revisada;
     - materiais que precisam de busca textual, transcrição ou indexação;
     - filmes, entrevistas, webinars e vídeos com múltiplas vozes, preferencialmente com LSE.

7. **Quando usar os dois**
   - Este deve ser o ponto central do post.
   - Explicar que Libras e legenda se complementam.
   - Usar pull quote:
     `Acessibilidade boa não força a pessoa a caber no recurso. Ela oferece caminhos diferentes para que cada pessoa acesse o conteúdo com autonomia.`

8. **Erros comuns**
   - Highlight box ou cards:
     - "Já tem legenda, então não precisa de Libras."
     - "A legenda automática resolve."
     - "A janela de Libras pode ficar pequena."
     - "É só colocar o intérprete em qualquer canto."
     - "Todo surdo prefere a mesma solução."

9. **Checklist de decisão**
   - Criar timeline/process steps:
     1. Quem é o público?
     2. O conteúdo é ao vivo ou gravado?
     3. Há informação sonora importante além da fala?
     4. O conteúdo tem finalidade pública, educacional, legal ou institucional?
     5. O recurso escolhido será visível, sincronizado e confortável?

10. **Fechamento e CTA**
   - Reforçar que a decisão técnica deve começar no planejamento.
   - CTA:
     - Título: `Precisa decidir o melhor formato acessível?`
     - Texto: `A LIBRAS.SE ajuda empresas, instituições e produtores de conteúdo a escolher e executar Libras, legendas e formatos acessíveis para vídeos, eventos e treinamentos.`
     - Botão: `Fale com a LIBRAS.SE`
     - Link: `https://www.libras.se`

## Texto-base para o artigo

Use este texto como base, reescrevendo com fluidez e adaptando ao HTML do blog:

> Muita gente ainda trata Libras e legendas como se fossem duas formas diferentes de entregar exatamente a mesma coisa. Na prática, não é assim. Libras é uma língua visual, com estrutura própria, usada por grande parte da comunidade surda brasileira. Legenda é um recurso textual, baseado na língua portuguesa escrita. As duas soluções podem aparecer no mesmo vídeo, mas não atendem exatamente às mesmas pessoas nem resolvem os mesmos problemas.
>
> Quando uma pessoa surda tem a Libras como primeira língua, a janela de Libras pode ser o caminho mais natural para compreender uma explicação, uma aula, uma palestra ou uma campanha. Isso acontece porque a informação chega por uma língua visual, com expressões faciais, movimento, ritmo, espaço e gramática próprios. Reduzir Libras a "gestos do português" é um erro: Libras é língua.
>
> A legenda, por outro lado, transforma a fala em texto. Ela pode ser muito útil para pessoas surdas oralizadas, pessoas ensurdecidas, usuários que assistem sem som, pessoas que querem acompanhar termos técnicos e até para quem está em um ambiente barulhento. Mas a legenda comum geralmente registra apenas as falas. Para acessibilidade de pessoas surdas e ensurdecidas, o recurso mais adequado é a LSE, Legenda para Surdos e Ensurdecidos.
>
> A LSE precisa ir além do diálogo. Ela deve indicar quem está falando quando isso não é visualmente óbvio e também registrar sons importantes para a compreensão da cena, como música, aplausos, risos, batidas, alarmes ou ruídos que mudam o sentido do conteúdo. Em um vídeo institucional, por exemplo, a música pode indicar tom emocional. Em uma aula, um som de alerta pode orientar uma ação. Em uma entrevista, saber quem fala evita confusão.
>
> Por isso, a pergunta "Libras ou legendas?" precisa ser substituída por uma pergunta melhor: quem precisa acessar esse conteúdo e em que contexto? Em vídeos de alto alcance, cursos, campanhas públicas, eventos e materiais institucionais, muitas vezes a escolha mais responsável é usar os dois recursos. A Libras amplia o acesso para pessoas sinalizantes. A legenda amplia o acesso para quem usa o texto. Juntas, elas reduzem barreiras.
>
> Também é importante falar sobre qualidade. Legenda automática pode ajudar em rascunhos, mas não deve ser tratada como entrega final de acessibilidade. Erros de reconhecimento de fala, ausência de pontuação, nomes trocados e falta de marcação sonora podem comprometer o entendimento. Da mesma forma, uma janela de Libras pequena demais, mal posicionada ou sem contraste adequado pode virar um recurso apenas simbólico, sem utilidade real.
>
> Acessibilidade audiovisual exige planejamento. Antes de produzir, defina o público, o canal, a duração, o formato e a finalidade do conteúdo. Em um evento ao vivo, a interpretação em Libras precisa estar visível para quem está no auditório e para quem acompanha online. Em uma videoaula, é preciso pensar em janela de Libras, legenda, transcrição e materiais de apoio. Em uma campanha, o ideal é que a acessibilidade esteja integrada desde o roteiro, não adicionada no fim.
>
> No fim, Libras e legendas não competem. Elas se complementam. Quando a acessibilidade é bem planejada, cada pessoa encontra um caminho possível para acompanhar, compreender e participar.

## Pesquisa elaborada para embasar o post

Use estes pontos de pesquisa no conteúdo, em caixas de referência, law callouts ou seção de referências. Parafraseie; não copie trechos longos.

### Libras é língua reconhecida por lei

- A Lei nº 10.436/2002 reconhece a Língua Brasileira de Sinais como meio legal de comunicação e expressão.
- A mesma lei descreve Libras como sistema linguístico de natureza visual-motora, com estrutura gramatical própria.
- Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10436.htm

### Pessoa surda e experiência visual

- O Decreto nº 5.626/2005 regulamenta a Lei de Libras.
- O decreto considera pessoa surda aquela que, por perda auditiva, compreende e interage com o mundo por experiências visuais, manifestando sua cultura principalmente pelo uso de Libras.
- Fonte: https://www.planalto.gov.br/ccivil_03/_Ato2004-2006/2005/Decreto/D5626.htm

### A LBI reconhece múltiplas formas de comunicação

- A Lei Brasileira de Inclusão, Lei nº 13.146/2015, define comunicação de forma ampla.
- O conceito inclui Libras, visualização de textos, Braille, linguagem simples, dispositivos multimídia e tecnologias da informação e comunicação.
- Use isso para sustentar a ideia de que acessibilidade não é recurso único.
- Fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm

### WCAG diferencia legendas e língua de sinais

- A WCAG 2.2 trata legendas para conteúdo pré-gravado no critério 1.2.2, nível A.
- A WCAG 2.2 trata legendas ao vivo no critério 1.2.4, nível AA.
- A WCAG 2.2 trata interpretação em língua de sinais para conteúdo pré-gravado no critério 1.2.6, nível AAA.
- Isso mostra que legenda e língua de sinais são requisitos distintos, não substitutos diretos.
- Fonte: https://www.w3.org/TR/WCAG22/

### Dados de contexto

- O Censo 2022 apontou 14,4 milhões de pessoas com deficiência no Brasil, 7,3% da população com 2 anos ou mais, nos resultados preliminares divulgados pelo IBGE em 23 de maio de 2025.
- A PNS 2019 estimou 17,3 milhões de pessoas com algum tipo de deficiência no país.
- Use esses dados com cuidado: eles contextualizam acessibilidade e deficiência, mas não devem ser apresentados como número total de usuários de Libras.
- Fontes:
  - https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/43463-censo-2022-brasil-tem-14-4-milhoes-de-pessoas-com-deficiencia
  - https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/31445-pns-2019-pais-tem-17-3-milhoes-de-pessoas-com-algum-tipo-de-deficiencia

### LSE: legenda para surdos e ensurdecidos

- Explique que LSE, diferentemente da legenda comum, deve representar não só falas, mas também elementos sonoros relevantes e identificação de falantes.
- Exemplos de marcações: `[música suave]`, `[aplausos]`, `[alarme]`, `[Joana]`, `[risos]`.
- Use como orientação editorial, sem transformar em norma técnica detalhada.

### ABNT NBR 15290

- A ABNT NBR 15290 trata de acessibilidade em comunicação na televisão e traz diretrizes relacionadas a legendagem, audiodescrição, língua de sinais e alerta de emergência.
- Como o conteúdo da norma pode ser de acesso restrito, cite apenas como referência técnica geral, sem reproduzir regras específicas.
- Fonte de consulta pública sobre escopo: https://www.normas.com.br/visualizar/abnt-nbr-nm/24743/abnt-nbr15290-acessibilidade-em-comunicacao-na-televisao

## Sugestões visuais e de CSS

Use os componentes existentes em `blog/CLAUDE.md`:

- `stat-row` com 3 dados:
  - `14,4M` pessoas com deficiência no Censo 2022
  - `3` caminhos principais: Libras, legenda comum e LSE
  - `2` recursos que se complementam: Libras + legenda
- `law-callout` para Lei 10.436/2002 e LBI.
- `pull-quote` para a frase central sobre acessibilidade não forçar a pessoa a caber no recurso.
- `highlight-box` para alertar que legenda automática não é entrega final.
- `use-grid` para "quando usar Libras" e "quando usar LSE".
- `process-steps` para checklist de decisão.
- `references` no final com as fontes.

Crie também, se fizer sentido, CSS novo para um bloco comparativo:

```css
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin: 48px 0;
}

.comparison-card {
  background: var(--white);
  border: 1px solid var(--grey-light);
  border-radius: var(--radius);
  padding: 28px;
  box-shadow: 0 6px 28px rgba(30,110,110,0.06);
}

.comparison-card h3 {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 1rem;
  color: var(--teal-dark);
  margin-bottom: 14px;
}

.comparison-card dl {
  display: grid;
  gap: 12px;
}

.comparison-card dt {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--teal-mid);
}

.comparison-card dd {
  font-family: 'Lora', serif;
  font-size: 0.84rem;
  color: var(--ink-soft);
  line-height: 1.65;
}

@media (max-width: 800px) {
  .comparison-grid { grid-template-columns: 1fr; }
}
```

### Ideias de hero/imagens

Opção preferida: usar hero com gradiente puro e elementos gráficos próprios, sem precisar criar nova imagem. Para decorar o hero, crie elementos como:

- cartões flutuantes discretos com os textos `LIBRAS`, `LSE`, `CC`;
- linhas/ondas simulando trilha de áudio;
- pequenos blocos de legenda como `[música]`, `[aplausos]`;
- uma mini janela abstrata de intérprete no canto, feita em CSS.

Se usar foto/imagem, procurar ou gerar uma imagem de uma pessoa sinalizando em estúdio, com fundo limpo e espaço negativo para o texto. Salvar em:

`../../assets/img/blog/libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado/`

Gerar formatos `.avif`, `.webp` e `.png`.

### Ideias de vídeo

Não é obrigatório inserir vídeo. Se inserir, pode ser um bloco conceitual com `video-showcase` somente se houver asset real. Não use iframe aleatório sem relação direta com Libras/legendas. Uma boa alternativa é criar um "media mockup" em CSS mostrando:

- vídeo central;
- janela de Libras no canto inferior direito;
- faixa de legenda no rodapé do vídeo;
- labels `Janela de Libras` e `LSE`.

## Requisitos técnicos

- Entregar HTML completo com CSS e JS inline, seguindo o padrão do blog.
- Usar as fontes Google indicadas no `blog/CLAUDE.md`.
- Usar `progress-bar`, `reveal`, hero, nav minimalista, article wrapper, footer e CTA.
- Manter responsividade em mobile.
- Não usar dependências externas além das fontes Google.
- Não usar imagens externas hotlinkadas.
- Links externos devem ter `target="_blank"` e `rel="noopener"`.
- Incluir seção `Referências` no fim.
- Conferir se o footer usa:

```html
© 2026 <a href="https://libras.se">LIBRAS.SE</a> · Vídeos para todos · Florianópolis, Santa Catarina, Brasil
```

## Referências que devem aparecer no post

1. BRASIL. Lei nº 10.436, de 24 de abril de 2002. Disponível em: https://www.planalto.gov.br/ccivil_03/leis/2002/l10436.htm
2. BRASIL. Decreto nº 5.626, de 22 de dezembro de 2005. Disponível em: https://www.planalto.gov.br/ccivil_03/_Ato2004-2006/2005/Decreto/D5626.htm
3. BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com Deficiência. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm
4. W3C. Web Content Accessibility Guidelines (WCAG) 2.2. Disponível em: https://www.w3.org/TR/WCAG22/
5. IBGE. Censo 2022: Brasil tem 14,4 milhões de pessoas com deficiência. Disponível em: https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/43463-censo-2022-brasil-tem-14-4-milhoes-de-pessoas-com-deficiencia
6. IBGE. PNS 2019: país tem 17,3 milhões de pessoas com algum tipo de deficiência. Disponível em: https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/31445-pns-2019-pais-tem-17-3-milhoes-de-pessoas-com-algum-tipo-de-deficiencia
7. ABNT NBR 15290, escopo público de consulta. Disponível em: https://www.normas.com.br/visualizar/abnt-nbr-nm/24743/abnt-nbr15290-acessibilidade-em-comunicacao-na-televisao

## Checklist final antes de concluir

- O post explica claramente que Libras e legenda não são equivalentes.
- O post explica a diferença entre legenda comum e LSE.
- O post tem pelo menos um quadro comparativo.
- O post tem pelo menos um callout legal.
- O post tem checklist prático de decisão.
- O post inclui referências.
- O design está alinhado aos outros posts da pasta `blog`.
- O mobile não quebra textos, cards, hero ou CTA.
