# Prompt para Claude criar o post

Você é um desenvolvedor front-end e redator especializado em acessibilidade, Libras, educação digital e conteúdo institucional para a LIBRAS.SE.

Crie o arquivo `blog/videoaulas-acessiveis-com-libras/index.html` para o post:

**Videoaulas acessíveis com Libras: como ampliar o acesso ao aprendizado**

Use rigorosamente os padrões de `blog/CLAUDE.md` e o estilo dos posts existentes:

- `blog/garantir-libras-sem-improviso/index.html`
- `blog/voce-sabe-o-que-e-datilologia/index.html`
- `blog/libras-ou-legendas-entenda-quando-ecomo-cada-recurso-deve-ser-usado/index.html`, se já existir

Observação importante: o arquivo antigo indicado como base, `post antigo`, está vazio. Portanto, use o texto-base, a pesquisa e a estrutura abaixo como matéria-prima do post.

## Objetivo editorial

Explicar por que videoaulas acessíveis não são apenas videoaulas com "um recurso extra" no final. Para estudantes surdos sinalizantes, a Libras pode ser o principal caminho de acesso ao conteúdo. Para outros públicos, legendas, transcrição, materiais de apoio e boa organização visual também são decisivos.

O post deve defender que acessibilidade em videoaulas precisa ser planejada desde o roteiro, não adicionada depois da gravação.

Pontos centrais:

- Libras é uma língua visual, com estrutura própria, reconhecida por lei.
- Videoaula acessível precisa respeitar a experiência visual do estudante surdo.
- Janela de Libras pequena, mal posicionada ou sem contraste não resolve.
- Legenda automática sem revisão não deve ser tratada como acessibilidade final.
- Em educação, o ideal é combinar Libras, legenda, transcrição e materiais complementares.
- Acessibilidade melhora a experiência de todos: estudantes surdos, ouvintes, pessoas em ambientes sem som, pessoas revisando conteúdo e alunos com diferentes ritmos de aprendizagem.

## Tom e estilo

Use o tom dos posts do blog da LIBRAS.SE:

- didático, direto e acolhedor;
- com autoridade técnica, mas sem virar artigo acadêmico;
- com exemplos práticos de videoaulas, cursos online, treinamentos corporativos e EAD;
- com frases curtas e leitura fluida;
- sem juridiquês;
- sem tratar acessibilidade como favor;
- com CTA comercial suave no final.

Evite:

- dizer que legenda substitui Libras;
- tratar todos os estudantes surdos como iguais;
- usar "surdo-mudo";
- prometer inclusão só porque existe um intérprete no canto da tela;
- criar um texto genérico sobre educação sem conectar com produção audiovisual.

## SEO e metadados

Use:

```html
<title>Videoaulas acessíveis com Libras: como ampliar o acesso ao aprendizado | LIBRAS.SE</title>
<meta name="description" content="Entenda como criar videoaulas acessíveis com Libras, legendas, transcrição e recursos visuais bem planejados para ampliar o acesso ao aprendizado.">
<meta name="keywords" content="videoaulas acessíveis, Libras em videoaulas, acessibilidade EAD, educação inclusiva, janela de Libras, legenda em videoaula, cursos online acessíveis">
```

Categoria no nav:

```html
<span class="nav-tag">Blog · Educação</span>
```

Hero:

- Kicker: `Educação acessível`
- Título: `Videoaulas acessíveis` com destaque em `com Libras`
- Subtítulo: `Uma videoaula só é realmente inclusiva quando o conteúdo, a imagem, a legenda e a janela de Libras são pensados para quem aprende por caminhos diferentes.`
- Data: `20 de maio de 2026`
- Leitura: `7 min de leitura`

## Estrutura recomendada do artigo

1. **Introdução: videoaula não é só vídeo**
   - Abrir com a ideia de que uma aula gravada concentra voz, imagem, ritmo, exemplos, tela compartilhada e material complementar.
   - Para muitos estudantes, basta dar play. Para outros, se o vídeo não for acessível, o conteúdo fica incompleto.
   - Usar `drop-cap` no primeiro parágrafo.

2. **Por que Libras importa nas videoaulas**
   - Explicar que Libras é língua visual-motora, com estrutura própria.
   - Conectar com a experiência visual de muitos estudantes surdos.
   - Mostrar que, em aulas complexas, a Libras pode tornar explicações, exemplos e encadeamento de ideias mais naturais para estudantes sinalizantes.

3. **Acessibilidade não é só colocar uma janela**
   - Explicar que janela de Libras precisa ter tamanho, enquadramento, contraste, iluminação e sincronização adequados.
   - A janela não pode cobrir conteúdo importante, como slides, fórmulas, rosto do professor, quadros, gráficos ou demonstrações.
   - Se a videoaula usa muitos recursos visuais, o layout deve ser pensado antes da edição.

4. **O conjunto ideal de recursos**
   - Criar um grid de cards com:
     - Libras;
     - legenda revisada ou LSE;
     - transcrição;
     - material de apoio acessível;
     - slides legíveis;
     - player com controles acessíveis.
   - Explicar que cada recurso resolve uma parte do acesso.

5. **Antes de gravar: roteiro acessível**
   - Usar `process-steps`:
     1. Definir público e contexto da aula.
     2. Separar termos técnicos com antecedência.
     3. Planejar espaço para a janela de Libras.
     4. Evitar depender apenas de "como vocês estão vendo aqui".
     5. Preparar arquivos de apoio em formato acessível.

6. **Durante a produção: imagem, ritmo e clareza**
   - Cards ou checklist:
     - professor não deve falar rápido demais;
     - slides precisam ter fonte legível e pouco texto;
     - exemplos visuais devem ser descritos oralmente;
     - cortes não devem quebrar a interpretação;
     - janela de Libras deve permanecer estável;
     - termos técnicos devem ser previamente alinhados com intérpretes.

7. **Depois da gravação: revisão importa**
   - Explicar revisão de legenda, sincronização, nomes, termos técnicos, pontuação e marcações sonoras.
   - Reforçar que legenda automática pode ser ponto de partida, não entrega final.
   - Incluir pull quote:
     `Uma videoaula acessível não nasce no botão de exportar. Ela começa no roteiro, passa pela gravação e só termina depois da revisão.`

8. **Casos em que Libras é especialmente importante**
   - Grid:
     - cursos livres e profissionalizantes;
     - treinamentos corporativos obrigatórios;
     - videoaulas de escolas, faculdades e EAD;
     - onboarding de colaboradores;
     - conteúdos públicos de saúde, segurança, direitos e cidadania.

9. **Erros comuns em videoaulas acessíveis**
   - Highlight box ou cards:
     - janela de Libras pequena demais;
     - intérprete recortado das mãos ou expressões faciais;
     - legenda automática sem revisão;
     - slide cheio de texto competindo com a janela de Libras;
     - vídeo sem transcrição ou material de apoio;
     - player sem controles claros.

10. **Checklist prático**
   - Criar checklist visual:
     - A janela de Libras é grande o suficiente?
     - As mãos e expressões do intérprete estão visíveis?
     - A legenda foi revisada por pessoa humana?
     - O conteúdo visual importante foi explicado?
     - A transcrição está disponível?
     - Os materiais complementares são acessíveis?
     - O vídeo funciona bem no celular?

11. **Fechamento e CTA**
   - Reforçar que videoaula acessível amplia aprendizagem, autonomia e permanência.
   - CTA:
     - Título: `Quer transformar suas videoaulas em conteúdo acessível?`
     - Texto: `A LIBRAS.SE apoia instituições, empresas e produtores de conteúdo na criação de videoaulas com Libras, legendas, transcrição e formatos acessíveis para cursos, treinamentos e EAD.`
     - Botão: `Fale com a LIBRAS.SE`
     - Link: `https://www.libras.se`

## Texto-base para o artigo

Use este texto como base, reescrevendo com fluidez e adaptando ao HTML do blog:

> Uma videoaula parece simples: alguém explica um conteúdo, mostra slides, apresenta exemplos e o estudante assiste no próprio ritmo. Mas, quando pensamos em acessibilidade, a videoaula é um formato mais complexo do que parece. Ela reúne fala, imagem, ritmo, textos na tela, gestos, demonstrações, gráficos e materiais complementares. Se algum desses elementos não for acessível, parte do aprendizado pode se perder.
>
> Para estudantes surdos sinalizantes, a Libras pode ser o caminho mais direto para acompanhar uma explicação. A Língua Brasileira de Sinais não é uma versão gestual do português. Ela tem estrutura própria, usa o espaço, o corpo, as expressões faciais e o movimento para construir sentido. Em uma videoaula, isso faz diferença: conceitos, relações entre ideias e exemplos podem ser compreendidos de forma mais natural quando o conteúdo é apresentado em Libras.
>
> Mas acessibilidade em videoaula não significa simplesmente colocar uma janela de Libras no canto da tela. A janela precisa ser visível, ter bom contraste, iluminação adequada e enquadramento que mostre mãos, tronco e expressões faciais. Também precisa estar posicionada de modo que não cubra slides, gráficos, fórmulas, legendas ou demonstrações. Quando tudo é decidido só na edição, é comum que algum elemento importante dispute espaço com outro.
>
> Por isso, a acessibilidade começa no roteiro. Antes de gravar, é preciso entender quem vai assistir, qual é o objetivo da aula, quais termos técnicos aparecerão e quais partes dependem de imagem. Se a aula usa slides, o layout já deve reservar uma área para a janela de Libras. Se há fórmulas, gráficos ou telas de sistema, o professor deve descrever o que está mostrando. Se há termos específicos, o ideal é compartilhar o material com intérpretes antes da gravação.
>
> As legendas também são fundamentais. Elas ajudam pessoas surdas oralizadas, pessoas ensurdecidas, estudantes que assistem sem som e qualquer pessoa que queira revisar trechos do conteúdo. Mas legendas automáticas não devem ser tratadas como entrega final. Em videoaulas, um termo técnico errado pode mudar o sentido de uma explicação inteira. A revisão humana garante pontuação, nomes corretos, sincronização e clareza.
>
> A transcrição é outro recurso importante. Ela permite buscar trechos, revisar conceitos, estudar fora do vídeo e consultar o conteúdo com tecnologias assistivas. Em cursos e treinamentos, a transcrição também ajuda quem precisa retomar uma explicação sem assistir à aula inteira de novo.
>
> Uma videoaula acessível combina recursos. Libras, legenda, transcrição, slides legíveis, materiais de apoio e um player com controles claros trabalham juntos. Não existe um único recurso capaz de resolver todas as barreiras. O objetivo é oferecer caminhos diferentes para que cada estudante acompanhe a aula com autonomia.
>
> Quando uma instituição investe em videoaulas acessíveis, ela melhora a experiência de aprendizagem para muito mais pessoas do que imagina. Estudantes surdos, ouvintes, pessoas em ambientes barulhentos, profissionais em treinamentos obrigatórios, alunos revisando conteúdo no celular e pessoas com diferentes ritmos de estudo se beneficiam de um material mais claro, organizado e planejado.
>
> Acessibilidade em videoaulas não é acabamento. É parte do projeto pedagógico e audiovisual.

## Pesquisa elaborada para embasar o post

Use estes pontos de pesquisa no conteúdo, em caixas de referência, law callouts ou seção de referências. Parafraseie; não copie trechos longos.

### Libras é língua reconhecida por lei

- A Lei nº 10.436/2002 reconhece a Língua Brasileira de Sinais como meio legal de comunicação e expressão.
- A lei descreve Libras como sistema linguístico de natureza visual-motora, com estrutura gramatical própria.
- Use esse ponto para reforçar que Libras em videoaulas não é adereço visual, mas acesso linguístico.
- Fonte: https://www.planalto.gov.br/ccivil_03/leis/2002/l10436.htm

### Pessoa surda, experiência visual e educação

- O Decreto nº 5.626/2005 regulamenta a Lei de Libras.
- O decreto considera pessoa surda aquela que compreende e interage com o mundo por experiências visuais e manifesta sua cultura principalmente pelo uso da Libras.
- O decreto também trata do ensino de Libras e do português escrito como segunda língua para alunos surdos, em perspectiva dialógica, funcional e instrumental.
- Use isso para conectar videoaulas com educação bilíngue e experiência visual.
- Fonte: https://www.planalto.gov.br/ccivil_03/_Ato2004-2006/2005/Decreto/D5626.htm

### A LBI reconhece comunicação e tecnologia assistiva

- A Lei Brasileira de Inclusão, Lei nº 13.146/2015, define comunicação de modo amplo, incluindo Libras, visualização de textos, dispositivos multimídia e tecnologias da informação e comunicação.
- A LBI também trata acessibilidade como condição para acesso, com segurança e autonomia, a informação e comunicação.
- Use isso para sustentar a combinação entre Libras, legendas, transcrição e recursos digitais.
- Fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm

### WCAG e conteúdo audiovisual

- A WCAG 2.2 trata legendas para conteúdo pré-gravado no critério 1.2.2, nível A.
- A WCAG 2.2 trata alternativas ou audiodescrição para conteúdo de vídeo pré-gravado no critério 1.2.3, nível A.
- A WCAG 2.2 trata audiodescrição para conteúdo pré-gravado no critério 1.2.5, nível AA.
- A WCAG 2.2 trata interpretação em língua de sinais para conteúdo pré-gravado no critério 1.2.6, nível AAA.
- Use esses pontos para mostrar que acessibilidade audiovisual tem camadas diferentes.
- Fonte: https://www.w3.org/TR/WCAG22/

### Educação bilíngue e Libras

- Materiais do MEC sobre atendimento educacional especializado para estudantes com surdez discutem a importância de uma abordagem bilíngue, com Libras e língua portuguesa.
- Use com cuidado, sem transformar o artigo em debate pedagógico extenso. O foco do post é produção de videoaulas acessíveis.
- Fonte de consulta: https://portal.mec.gov.br/seesp/arquivos/pdf/dificuldade6.pdf

### Dados de contexto

- O Censo 2022 apontou 14,4 milhões de pessoas com deficiência no Brasil, 7,3% da população com 2 anos ou mais, nos resultados preliminares divulgados pelo IBGE em 23 de maio de 2025.
- A PNS 2019 estimou 17,3 milhões de pessoas com algum tipo de deficiência no país.
- Use esses dados apenas para contextualizar a relevância de acessibilidade. Não apresente esses números como quantidade de estudantes surdos ou usuários de Libras.
- Fontes:
  - https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/43463-censo-2022-brasil-tem-14-4-milhoes-de-pessoas-com-deficiencia
  - https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/31445-pns-2019-pais-tem-17-3-milhoes-de-pessoas-com-algum-tipo-de-deficiencia

## Sugestões visuais e de CSS

Use os componentes existentes em `blog/CLAUDE.md`:

- `stat-row` com 3 dados:
  - `14,4M` pessoas com deficiência no Censo 2022;
  - `6` recursos de uma videoaula acessível;
  - `3` etapas de planejamento: roteiro, gravação e revisão.
- `law-callout` para Lei 10.436/2002, Decreto 5.626/2005 e LBI.
- `pull-quote` para a frase central sobre videoaula acessível nascer no roteiro.
- `highlight-box` para alertar que legenda automática não é entrega final.
- `use-grid` para recursos essenciais da videoaula acessível.
- `process-steps` para planejamento antes de gravar.
- `references` no final com as fontes.

Crie também, se fizer sentido, CSS novo para um mockup de videoaula acessível:

```css
.lesson-mockup {
  margin: 48px 0;
  background: linear-gradient(150deg, #082828, #1e6e6e);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: 0 20px 60px rgba(30,110,110,0.18);
}

.lesson-screen {
  position: relative;
  aspect-ratio: 16 / 9;
  background: #f8fdfd;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(168,230,223,0.35);
}

.slide-area {
  position: absolute;
  inset: 36px 34% 78px 36px;
  display: grid;
  gap: 12px;
  align-content: start;
}

.slide-line {
  height: 14px;
  border-radius: 999px;
  background: rgba(42,144,144,0.22);
}

.slide-line:nth-child(1) {
  width: 80%;
  height: 22px;
  background: rgba(30,110,110,0.82);
}

.libras-window {
  position: absolute;
  right: 28px;
  bottom: 76px;
  width: 24%;
  aspect-ratio: 3 / 4;
  background: linear-gradient(180deg, var(--teal-pale), var(--teal-light));
  border-radius: 16px;
  border: 4px solid var(--white);
  box-shadow: 0 10px 30px rgba(15,42,42,0.18);
}

.caption-bar {
  position: absolute;
  left: 36px;
  right: 36px;
  bottom: 28px;
  min-height: 34px;
  border-radius: 10px;
  background: rgba(15,42,42,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 18px;
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 0.78rem;
  color: var(--white);
  text-align: center;
}

.mockup-label {
  margin-top: 16px;
  font-family: 'Lora', serif;
  font-style: italic;
  font-size: 0.84rem;
  color: rgba(255,255,255,0.68);
  text-align: center;
}

@media (max-width: 700px) {
  .lesson-mockup { padding: 18px; }
  .slide-area { inset: 24px 28px 112px 24px; }
  .libras-window { width: 30%; right: 18px; bottom: 70px; }
  .caption-bar { left: 18px; right: 18px; bottom: 18px; font-size: 0.68rem; }
}
```

Exemplo de HTML para o mockup:

```html
<div class="lesson-mockup reveal">
  <div class="lesson-screen" aria-label="Exemplo visual de videoaula com slide, janela de Libras e legenda">
    <div class="slide-area" aria-hidden="true">
      <span class="slide-line"></span>
      <span class="slide-line"></span>
      <span class="slide-line"></span>
      <span class="slide-line"></span>
    </div>
    <div class="libras-window" aria-hidden="true"></div>
    <div class="caption-bar">[Professor] Vamos revisar o conceito principal da aula.</div>
  </div>
  <p class="mockup-label">O layout precisa prever slide, legenda e janela de Libras antes da edição.</p>
</div>
```

### Ideias de hero/imagens

Opção preferida: usar hero com imagem de fundo se houver asset ou se for possível gerar imagem. Tema sugerido:

- professor gravando aula em estúdio;
- tela com slide;
- pessoa sinalizando em janela lateral;
- ambiente limpo, educacional e tecnológico;
- espaço negativo para o título.

Salvar em:

`../../assets/img/blog/videoaulas-acessiveis-com-libras/`

Gerar formatos `.avif`, `.webp` e `.png`.

Se não houver imagem, use hero com gradiente puro e elementos CSS:

- cards flutuantes `Roteiro`, `Libras`, `Legenda`, `Transcrição`;
- mini player de videoaula;
- linhas de slide;
- ondas discretas de áudio;
- janela abstrata de Libras.

### Ideias de vídeo

Não inserir iframe aleatório. Só use `video-showcase` se houver asset real da LIBRAS.SE.

Se não houver vídeo, use o mockup CSS acima para representar uma videoaula acessível. Ele combina melhor com o tema e evita dependência de material externo.

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
5. MEC. Atendimento Educacional Especializado: Pessoa com Surdez. Disponível em: https://portal.mec.gov.br/seesp/arquivos/pdf/dificuldade6.pdf
6. IBGE. Censo 2022: Brasil tem 14,4 milhões de pessoas com deficiência. Disponível em: https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/43463-censo-2022-brasil-tem-14-4-milhoes-de-pessoas-com-deficiencia
7. IBGE. PNS 2019: país tem 17,3 milhões de pessoas com algum tipo de deficiência. Disponível em: https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/31445-pns-2019-pais-tem-17-3-milhoes-de-pessoas-com-algum-tipo-de-deficiencia

## Checklist final antes de concluir

- O post explica que videoaula acessível começa no roteiro.
- O post diferencia Libras, legenda, transcrição e materiais de apoio.
- O post evita dizer que legenda substitui Libras.
- O post tem pelo menos um mockup ou bloco visual de videoaula.
- O post tem pelo menos um callout legal.
- O post tem checklist prático de produção.
- O post inclui referências.
- O design está alinhado aos outros posts da pasta `blog`.
- O mobile não quebra textos, cards, mockup, hero ou CTA.
