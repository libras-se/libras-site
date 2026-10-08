# Estratégia de SEO do blog e do site LIBRAS.SE (out/2026)

O objetivo é um só: **mais gente chegando pela busca e ficando no site**. Cada página leva a outra.
Uma notícia leva a uma matéria correlata, a uma área de aprender ou jogar, ao glossário e, quando o
assunto pede, à página comercial.

Os três papéis do site:

| Papel | Páginas | O que mede sucesso |
|---|---|---|
| **Atrair** (busca informacional) | blog, glossário, sinais | impressões e cliques no Search Console |
| **Reter** (voltar e passar tempo) | Aprender Libras, jogos, materiais, cultura surda | páginas por sessão, retorno |
| **Converter** | soluções, `libras-para-*`, `acessibilidade-para-*`, huet | cliques em "Enviar vídeo" e orçamentos |

O blog é a porta de entrada; a estrutura de links é o que leva o leitor (e o Google) de uma camada à outra.

## 1. O que já foi feito (auditoria de 08/10/2026)

Medido com `python3 tools/seo/auditoria.py` em 220 páginas indexáveis (73 posts depois da fusão de Mandalorian, 77 sinais, 28 verbetes,
14 comerciais, 10 de aprender, 6 de jogos).

| Indicador | Antes | Depois |
|---|---|---|
| Páginas órfãs (nenhum link de contexto aponta para elas) | 9 | 1 (`/politica/`, página legal) |
| Páginas sem link para Aprender, jogos, sinais, glossário, materiais ou cultura | 20 | 1 (`/politica/`) |
| Posts com 0 ou 1 link vindo de outros posts | 42 | 0 (mínimo 2, média 4,1) |
| Páginas comerciais que linkam posts do blog | 0 | 19 (3 posts cada) |
| Verbetes do glossário que linkam posts do blog | 0 | 27 (3 posts cada) |
| `<title>` com mais de 65 caracteres | 65 | 0 |
| `description` fora de 70–165 caracteres | 77 | 0 |
| Erros de dados estruturados (`sync_blog --check`) | 1 data invertida + 34 derivados | 0 |

O que entrou nas páginas:

- **Em todo post:**
  - um **banner interno** (house ad) no meio do texto;
  - no fim, **"Continue lendo"** com 4 correlatas, a solução comercial do assunto (quando há) e 6 ícones de
    Aprenda e jogue.
- **Nas 19 páginas comerciais e institucionais:** "Conteúdo relacionado no blog", com 3 posts e os PDFs grátis.
- **Nos 27 verbetes do glossário:** "Este termo no blog", com os posts que citam o verbete. É o link de volta: os
  posts já linkavam o glossário, mas o glossário não devolvia nenhum link.
- **Nos hubs** (`/blog/todos/`, `/blog/temas/`) **e nas páginas de autor:** os ícones de Aprenda e jogue.
- **Títulos:**
  - sufixo único `| LIBRAS.SE`, no limite de 60 caracteres;
  - descriptions reescritas para 120–160 caracteres;
  - nas 75 páginas de sinal a description passou a ser gerada já no tamanho certo.
- **Correções técnicas:**
  - `/jogo/` ganhou H1 e JSON-LD;
  - favicon de `/proposito/`;
  - menu mobile de 20 posts;
  - `dateModified` invertido em `o-que-e-libras`;
  - FAQ da home, `article:modified_time` e `lastmod` do sitemap sincronizados.

## 2. Arquitetura: pilares e clusters

Cada editoria tem **pilares**: posts longos, que queremos ranquear por anos. Eles recebem mais links das
correlatas (configurados em `links.json → pilares`). Os outros posts do cluster apoiam o pilar e se apoiam
nas áreas de engajamento.

| Cluster | Pilar(es) | Engajamento ligado | Comercial ligado |
|---|---|---|---|
| Língua & Cultura | `o-que-e-libras`, `voce-sabe-o-que-e-datilologia`, `libras-tem-sotaque-e-giria` | Aprender Libras, alfabeto, sinais, quiz | — |
| Educação | `videoaulas-acessiveis-com-libras`, `papel-do-interprete-de-libras-na-escola-bilingue` | atividades, materiais, alfabeto | `/libras-para-videoaulas/` |
| Direitos | `libras-nao-e-segunda-lingua-oficial-do-brasil`, `20-anos-da-lei-de-libras-avancos-e-desafios` | cultura surda (leis), glossário (LBI, Lei 10.436) | `/libras-para-campanhas-politicas/` |
| Acessibilidade | `libras-ou-legendas-...`, `por-que-incluir-janela-de-libras-em-videos`, `garantir-libras-sem-improviso` | checklist e guia em PDF | soluções, empresas, publicidade, eventos ao vivo |
| Cultura | `oscar-coda-melhor-filme-do-mundo-sobre-surdez`, `o-que-o-filme-ganhador-do-oscar-ensina-sobre-libras` | cultura surda, sinal do dia | `acessibilidade-para-*` (audiovisual) |
| Esporte | `surdolimpiadas-as-olimpiadas-exclusivas-para-surdos` | quiz, sinal do dia | — |

Fora do blog, os hubs de cada intenção são:

- `/aprender-libras/`: aprender;
- `/jogos/`: jogar;
- `/materiais/`: baixar;
- `/glossario/`: definir;
- `/sinal/`: ver o sinal;
- `/cultura-surda/`: história e leis.

Todo conteúdo novo precisa ligar para pelo menos um desses hubs.

## 3. Regras de link interno

1. **Glossário na primeira ocorrência** de cada termo da área (regra do `blog/CLAUDE.md` §6). O verbete
   devolve o link automaticamente pelo "Este termo no blog".
2. **No corpo do texto, pelo menos 3 links de contexto:**
   - 1 para outro post do mesmo cluster (de preferência o pilar);
   - 1 para uma área de engajamento (sinal, alfabeto, jogo, material);
   - 1 para glossário ou cultura surda.

   O gerador cuida do fim da página; o meio do texto é editorial.
3. **Âncora descritiva**, com a palavra-chave da página de destino: "alfabeto em Libras",
   "janela de Libras", "intérprete de Libras". Nunca "clique aqui" nem "saiba mais" soltos.
4. **Um banner por post**, no meio do texto, nunca colado ao título nem ao fim:
   - o rótulo do serviço é "Publicidade · LIBRAS.SE";
   - **sem preço no blog**: preço só nas páginas comerciais e no huet;
   - o banner de serviço só entra em posts de mercado (B2B), configurados em `banner_por_post`;
   - posts sobre intérpretes recebem o banner Seja TILS.
5. **Pilar ganha links, notícia distribui links.** Notícia datada não vira pilar; ela aponta para o pilar.
6. **URL nunca muda.** Se um post precisar mudar de foco, atualize o conteúdo na mesma URL. Se for fundir
   dois posts, o antigo vira redirecionamento (`meta refresh` + canonical, padrão já usado em `/post/*`)
   e sai do sitemap.

## 4. Revisão das matérias publicadas (74 posts, 73 depois da fusão)

Retrato:

- **8 posts com 800 palavras ou mais**: os pilares e os guias.
- **41 posts entre 400 e 799 palavras.**
- **25 posts com menos de 400 palavras.**

A maioria é notícia de 2021–2022. Notícia curta não é problema: ela atrai busca de cauda longa e distribui
links. O ganho está em três frentes.

### 4.1 Canibalização (dois posts disputando a mesma busca)

| Posts | O que foi feito em 08/10/2026 |
|---|---|
| `libras-pode-ser-reconhecida-como-lingua-de-instrucao-em-bh` (2022) × `libras-e-reconhecida-como-lingua-de-instrucao-em-belo-horizonte` (2026) | Nada a mudar: o de 2022 já abre com a caixa "Atualização" e linka o de 2026, que é o que deve ranquear. |
| `mandalorian-fez-sua-propria-lingua-de-sinais` (2021) × `vencedor-do-oscar-ajudou-a-criar-sinais-de-the-mandalorian` (2022) | **Fundidos.** O de 2022 recebeu o trecho que só existia no de 2021. O de 2021 virou redirecionamento (noindex + canonical) e saiu da home, do sitemap, do llms-full e da página da autora. |
| `dia-nacional-da-libras-inclusao-da-comunidade-surda` (2025) × `20-anos-da-lei-de-libras-avancos-e-desafios` (2022) | O Dia Nacional da Libras virou **página permanente de todo 24 de abril**: novo title, seção "Como celebrar" (alfabeto, sinais, atividades, materiais e jogos) e dado de população corrigido (IBGE, Censo 2022). **Atualize todo março**, na mesma URL. O post dos 20 anos linka a página do dia. |
| `o-papel-do-interprete-de-libras-na-sociedade` × `papel-do-interprete-de-libras-na-escola-bilingue` | Intenções diferentes (geral × escola). Manter, e um deve linkar o outro no corpo. |

### 4.2 Correções de conteúdo (feitas em 08/10/2026)

- **Fita azul:** o post `dia-nacional-dos-surdos-conquistas-e-reflexoes` deixou de afirmar que ela vem das braçadeiras nazistas, versão que não tem
  registro documental. Agora o texto diz que a fita foi apresentada no congresso da WFD de 1999, em Brisbane, e o post linka o Dia
  Internacional das Línguas de Sinais.
- **Huet:** o site passou a usar **E. Huet** em todos os lugares. No verbete INES ficou registrado que as fontes divergem sobre o prenome
  (Eduard, Édouard ou Ernest). O "a convite de Dom Pedro II" virou "com o apoio de Dom Pedro II", em linha com o post `o-que-e-libras`.
- **"Língua oficial":** o FAQ da home, dois verbetes do glossário e `o-papel-da-libras-na-inclusao-do-surdo` agora dizem que a Lei 10.436/2002
  reconhece a Libras como **meio legal de comunicação e expressão**. Regra para textos novos: Libras não é "língua oficial" (ver o pilar
  `libras-nao-e-segunda-lingua-oficial-do-brasil`).

### 4.3 Atualizar e aprofundar (os que têm busca e estão rasos)

Prioridade pela busca do tema (volume relativo do nicho, ver `PESQUISA.md`). A meta é passar de 900 palavras,
com FAQ (`FAQPage`) e com links para sinais e jogos.

1. `entenda-porque-e-errado-o-termo-surdo-mudo` (busca "surdo-mudo" e "termo correto"): incluir a tabela
   de termos certos e errados e o link para `/glossario/surdo/`.
2. `o-papel-do-interprete-de-libras-na-sociedade` ("intérprete de Libras", busca alta): formação,
   Lei 12.319 e Lei 14.704 (revezamento), como contratar. Ponte para `/eventos-ao-vivo/` e `/sejatils/`.
3. `dia-nacional-dos-surdos-conquistas-e-reflexoes` e `dia-internacional-das-linguas-de-sinais`
   (Setembro Azul, sazonal): transformar em um guia do Setembro Azul, atualizado todo agosto.
4. `surdolimpiadas-as-olimpiadas-exclusivas-para-surdos` (está nas mais lidas): Surdolimpíadas 2025 em
   Tóquio, resultados do Brasil.
5. `o-que-e-capacitismo`, `lingua-de-sinais-e-autismo` e `gestuante-entra-para-a-lingua-portuguesa`:
   buscas conceituais estáveis, hoje com cerca de 400 palavras.
6. `documentarios-sobre-surdez-gratis-youtube`: lista que envelhece; revisar os links uma vez por ano.

Ao atualizar um post: na mesma URL, mude `dateModified` (JSON-LD) e rode os geradores (seção 7). O
`sync_blog` propaga a data para `article:modified_time` e para o sitemap.

## 5. Lacunas: pautas novas por palavra-chave

O blog tem notícia de sobra e pouco conteúdo de "como fazer" e "o que é", que é o que mais se busca.

| Busca | Formato | Onde |
|---|---|---|
| cores em Libras; números em Libras | página de aprender com vídeo e PDF | `/aprender-libras/` (números já existe) |
| bom dia em Libras; saudações; frases em Libras | página de aprender e sinais em vídeo (gravar) | `/aprender-libras/` + `/sinal/` |
| como aprender Libras sozinho; curso de Libras grátis | post pilar que leva à trilha do Aprender | blog → `/aprender-libras/` |
| história da Libras; surdos famosos | post pilar | blog → `/cultura-surda/` |
| intérprete de Libras; intérprete de Libras Florianópolis | página comercial (não blog) | `/interprete-de-libras/` (+ local) |
| valor hora de intérprete de Libras | página comercial (**preço não vai no blog**) | idem |
| plano de aula de Libras; atividades | material em PDF + post | `/materiais/`, `/atividades/` |
| janela de Libras: tamanho, posição, norma | post técnico (ABNT NBR 15290) | blog → `/solucoes/` |

Cada pauta nova nasce ligada a um pilar e a um hub (seção 2). Em `home.json`, entra com editoria;
se for pilar, entra também em `links.json → pilares`.

## 6. Calendário editorial (publicar até)

| Data | Gatilho | Pauta |
|---|---|---|
| 20/10/2026 | 10/11 Prevenção e Combate à Surdez; 12/11 Surdocegueira | post sobre surdocegueira e guia-intérprete (Lei 14.704) |
| 10/01/2027 | volta às aulas | cores, saudações, plano de aula, kit de atividades |
| 15/02/2027 | 3/3 Dia Mundial da Audição | dados do IBGE (Censo 2022), prevenção |
| 20/03/2027 | 24/4 Dia Nacional da Libras | atualizar a página anual (seção 4.1) e um kit escolar |
| 01/07/2027 | 26/7 Dia do Tradutor e Intérprete de Libras | intérprete de Libras (pilar) e Seja TILS |
| 01/08/2027 | Setembro Azul (23/9 e 26/9) | guia do Setembro Azul (seção 4.3), kit de cartazes |

Pauta sazonal é **atualizada na mesma URL** todo ano, não publicada de novo.

## 7. Ferramentas e rotina

```bash
python3 tools/blog/home.py         # 1) home do blog, /blog/todos/, /blog/temas/ (fonte dos cards)
python3 tools/seo/links.py         # 2) banners, Continue lendo, ícones, blog nas comerciais e no glossário
python3 tools/sinais/build_pages.py   # (só quando mexer em sinais)
python3 tools/seo/auditoria.py --csv  # 3) relatório: tools/seo/auditoria.json e .csv
```

- **A ordem importa:** `links.py` lê os cards gerados pelo `home.py`.
- **Todos os geradores são idempotentes:** rodar duas vezes não muda nada.
- **Depois de mexer em datas ou na home**, rode também o `audit/sync_blog.py --check`. O script fica no
  clone principal e não é versionado. Ele precisa terminar com "0 derived files".

Rotina:

- **A cada post publicado:**
  - os geradores e a auditoria;
  - o post novo precisa ter pelo menos 2 links de entrada e nenhum problema novo.
- **Todo mês, no Search Console:**
  - consultas com muita impressão e CTR abaixo de 2%: reescrever o title e a description;
  - páginas que caíram de posição: atualizar o conteúdo.
- **A cada trimestre:**
  - revisar o `banner_por_editoria`, para não cansar o leitor com o mesmo banner;
  - revisar os `pilares`.

## 8. Medição

- **Antes e depois:**
  - comparar no Search Console as quatro semanas antes e as quatro depois da publicação desta estrutura;
  - acompanhar impressões, cliques e CTR por cluster, filtrando por `/blog/`, `/glossario/` e `/sinal/`.
- **Banners e correlatas:**
  - no GTM, criar eventos de clique em `.lse-ad a`, `.lse-c` e `.lse-i`;
  - esses eventos mostram qual banner e qual ícone tiram o leitor do post.
- **Metas para 90 dias:**
  - mais 30% de cliques orgânicos no blog;
  - páginas por sessão acima de 1,6 em quem entra por um post;
  - pelo menos 1 clique em "Enviar vídeo" por semana vindo do banner de serviço.

## 9. Pendências técnicas conhecidas

- Os links `api-catalog` e `describedby` da home apontavam para `/.well-known/`, que não existe; foram removidos em 08/10/2026.
- `/produtos/` tem canonical para `/solucoes/`, de propósito, e fica fora do sitemap.
- As páginas de sinal não linkam o blog. Se for desejado, isso entra no gerador `tools/sinais/build_pages.py`,
  e não no `links.py`, porque o gerador de sinais recria a página inteira.
- Os `og:title` antigos ainda usam o sufixo `| Blog LIBRAS.SE`. Não pesa na busca; alinhe quando mexer no post.
