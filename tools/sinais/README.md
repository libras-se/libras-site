# Vídeos de sinais: do bruto ao site, com aprovação

Os brutos ficam no SSD (`/Volumes/Extreme Pro/LIBRAS.SE/TRABALHOS/VIDEOS GLOSSARIO`) e o trabalho
intermediário em `_processamento/` ao lado deles. **Nada vai para o site sem passar pela aprovação.**

```
brutos .MOV ──► análise (fala + movimento) ──► manifest.csv ──► render de todas as tomadas
                                                                     │
                                         aprovar.py (você e a Bruna) ◄┘
                                                │  aprovacoes.json (versionado)
                                                ▼
                                   publicar.py ──► assets/videos/sinais + /sinal/ + jogo + sitemap
```

## 1. Preparar um lote (uma vez por gravação)

```bash
W="/Volumes/Extreme Pro/LIBRAS.SE/TRABALHOS/VIDEOS GLOSSARIO/_processamento"; R="${W%/_processamento}"
python3 tools/sinais/make_briefing.py                                                # lista ordenada do briefing
uv run --python 3.12 --with numpy tools/sinais/analyze_motion.py "$R" "$W"          # onde ela sinaliza
HF_HUB_OFFLINE=1 uv run --python 3.12 --with mlx-whisper tools/sinais/transcribe.py "$W"  # o que ela fala
uv run --python 3.12 --with numpy tools/sinais/align.py "$W"                        # fala + sinal + briefing
uv run --python 3.12 --with numpy tools/sinais/extent.py "$W" "$R"                  # mão saindo do quadro
python3 tools/sinais/proxies.py "$W" "$R"                                           # brutos leves com áudio
python3 tools/sinais/render.py "$W" "$R"                                            # todas as tomadas
```

O alinhador sugere a **última tomada** de cada palavra. Quando a Bruna diz "ou X", aquilo é uma **variante**
do sinal (outra forma de sinalizar), não uma regravação. Essas tomadas aparecem marcadas para escolha.

## 2. Aprovar

```bash
python3 tools/sinais/aprovar.py        # abre http://localhost:8790
```

Para cada sinal, confira três coisas:
1. **É o sinal certo?** O rótulo bate com o que ela sinaliza.
2. **O corte está bom?** Começa e termina em repouso, sem cortar o início nem o fim do sinal.
3. **O recorte do chroma está limpo?** Use a lupa (`Z`) nas mãos, nos dedos e no cabelo.

O que dá para fazer no app:
- **Aprovar** (`A`): vai para o próximo pendente.
- **Ajustar** (`J`): abre o bruto com som. Marque início e fim (`I`/`O`) e renderize (`Enter`); o item volta
  a pendente para ser aprovado de novo.
- **Regravar** (`R`): o sinal está errado ou faltando e precisa de nova gravação.
- **Escolher a tomada** (`1`–`9`): quando há variantes "ou".
- **Usar como outro sinal…**: transforma uma tomada em um sinal próprio (ex.: o "Oi" gravado junto com "Olá").
- **Itens não encontrados**: aparecem com uma dica de onde procurar no bruto, e o corte é marcado manualmente.

As decisões ficam em `tools/sinais/aprovacoes.json`, junto com a **assinatura** do corte aprovado.
Se o corte mudar depois, a aprovação perde a validade sozinha.

## 2b. Aprovação online (aprovacao.libras.se)

O mesmo app roda na VPS (Dokploy, imagem `tools/sinais/Dockerfile`), com login por pessoa: cada decisão registra
quem aprovou. Lá a revisora aprova, escolhe tomada ou variante, refaz cortes (os brutos ficam no servidor) e
pede ilustração nova com uma nota. O Codex não roda no servidor: o pedido fica na fila e é gerado no Mac.

```bash
python3 tools/sinais/sincronizar.py semear            # 1ª vez: decisões locais -> servidor
python3 tools/sinais/sincronizar.py enviar --brutos   # 1ª vez: brutos, cortes, proxies e ilustrações
# rotina antes de publicar:
python3 tools/sinais/sincronizar.py baixar            # decisões + cortes refeitos online -> Mac
uv run --python 3.12 --with numpy tools/sinais/ilustrar.py --pendentes   # gera as ilustrações pedidas
python3 tools/sinais/sincronizar.py enviar            # sobe as ilustrações novas para aprovação
```

- **Decisões:** depois de semeado, o servidor é a fonte das decisões. O `baixar` sobrescreve o
  `aprovacoes.json` local; não use mais o app local para decidir.
- **Arquivos:** para os demais arquivos, vale o mais novo de cada lado. Uploads vão em partes de 16 MB e
  retomam se a conexão cair.
- **Credencial de admin:** fica em `~/.config/libras-sinais/admin` (fora do git).
- **Usuários:** são definidos na variável `SINAIS_USUARIOS` do Dokploy.
- **Sem o SSD:** aponte `SINAIS_WORK` para uma pasta local e rode o `baixar` (traz cortes, proxies e ilustrações do
  servidor). O `ilustrar.py` usa a mesma variável e, sem a curva de movimento do bruto (`motion/`), mede o movimento no
  próprio corte. No `publicar.py`, passe `--work` com a mesma pasta.
- **Limite do Codex:** a geração de imagem para depois de umas 25 a 30 ilustrações e só volta no horário indicado
  ("try again at…"). O `ilustrar.py` registra cada falha como `ERRO … o Codex não gerou a imagem`; rode de novo depois.

## 3. Publicar

```bash
python3 tools/sinais/publicar.py --simular   # mostra o que entraria/sairia
python3 tools/sinais/publicar.py             # aplica
```

O script faz quatro coisas:
- copia só os aprovados (com assinatura conferida) para `assets/videos/sinais/`;
- remove o que deixou de estar aprovado;
- liga o vídeo nos desafios do jogo;
- regenera `/sinal/` e `sitemap.xml`.

Páginas de sinal vêm de `sinal/sinais.json` (textos). Sem vídeo publicado, a página sai como "vídeo em preparação".

Dois campos opcionais por sinal em `sinal/sinais.json`:
- `publicado_em`: data do lote em que o sinal entrou. Vai para o `uploadDate` do vídeo e para o sitemap; sem ela, vale a data geral.
- `corte`: publica a página com o corte de outro item do app. Serve para sinais criados com "Usar como outro sinal…",
  que ganham o slug da palavra digitada. Exemplo: `{"slug": "letra-r", "corte": "r"}` publica o "R" que a Bruna separou
  de uma tomada da letra S em `/sinal/letra-r/`. Se o item `letra-r` do app for aprovado depois, o `publicar.py` avisa e
  mantém o corte indicado.

Depois de publicar, rode `python3 tools/aprender/build.py`: os jogos (memória, quiz), o bingo, o caça-palavras e a página
do alfabeto leem a lista de sinais com vídeo.

Para o commit, entram:
- `assets/videos/sinais/`
- `sinal/`
- `sitemap.xml`
- `jogo/index.html`
- `tools/sinais/aprovacoes.json`
- as páginas geradas por `tools/aprender/build.py` (jogos, atividades, alfabeto)

## Vídeos provisórios do canal do YouTube (`sinal/canal.json`)

**Todos os vídeos de `assets/videos/sinais-canal/` são provisórios.** São cortes dos shorts do quadro "Sinal novo
todo dia" (youtube.com/@libras-se-yt), verticais e gravados fora do estúdio. Entraram em 2026-11 para as páginas
ganharem busca enquanto a Bruna não regrava esses sinais no padrão do sinalário (chroma, 16:9). A lista do que falta
regravar fica em `producao-conteudo/youtube-sinais/regravar.md`; o pipeline dos cortes, no README da mesma pasta.

- Sinal sem vídeo da intérprete: o corte do canal vai para o topo da página com o selo "Vídeo provisório" e
  "Registro: Canal LIBRAS.SE no YouTube (provisório)".
- Sinal com vídeo da intérprete: o corte do canal aparece em "Outra versão do sinal".
- Em todos os casos, o short completo entra embutido em "Vídeo completo no YouTube", com um `VideoObject` próprio
  (`embedUrl`) no JSON-LD. O `VideoObject` principal continua sendo o vídeo que está no topo.
- Quando a regravação é aprovada e publicada (`publicar.py`), o vídeo da intérprete vira o principal sozinho, o selo
  some e o corte do canal desce para "Outra versão". O embed do short continua.
- Os jogos e as atividades usam só os vídeos da intérprete.
- `canal.json` e a pasta `sinais-canal` são gerados por `producao-conteudo/youtube-sinais/exportar_site.py`: não edite à mão.

## Elementos divertidos: figurinha e ficha de cada sinal

Cada página de sinal pode ter um elemento que ajuda a lembrar da palavra: a **figurinha** (mascote do time, símbolos do
estado, a letra desenhada, o bicho, a comida) e, em três categorias, uma **ficha**.

| Categoria | Ficha (gerada pelo `build_pages.py`, sem IA) |
|---|---|
| Times de futebol | camisa tradicional em SVG, apelido, mascote, cores, estádio, quem torce e link para o sinal do estado |
| Estados | o estado destacado no mapa do Brasil, sigla, capital, região, gentílico, times do estado e quatro símbolos do lugar |
| Alfabeto | a letra de oito jeitos (de forma, cursiva, pontilhada para traçar, com serifa, pixel, bolhas) e os sinais que começam com ela |
| Números | o número de seis jeitos, por extenso, a quantidade no quadro de dez e os vizinhos (antes e depois) |

Os dados ficam em `elementos.json`; o desenho, em `elementos.py`. Os contornos das letras ficam em `letras.json`
(gerado uma vez por `letras.py`). Sem escudo oficial de clube: só cores, camisa e mascote.

```bash
F="uv run --python 3.12 --with numpy --with pillow tools/sinais/figurinhas.py"
$F gerar --pendentes            # pede ao Codex as figurinhas que faltam (descrição em elementos.json), recorta e compõe
$F gerar flamengo --refazer     # versão nova de uma figurinha
$F folha /tmp/figurinhas.jpg    # folha de contato para aprovar de uma vez
$F compor                       # refaz os cartões (ilustração + figurinha)
python3 tools/sinais/build_pages.py
```

- **Figurinha** (`assets/img/sinais/figurinhas/<slug>.webp`): recortada, com transparência. Aparece no cabeçalho da página.
  Sem figurinha, o cabeçalho de time, estado, letra e cor mostra o desenho da ficha (camisa, mapa, letra, mancha de tinta).
- **Cartão** (`assets/img/sinais/cartoes/<slug>.webp`): a ilustração do sinal com a figurinha no canto mais vazio. Vai para a
  página do sinal, os cards do `/sinal/` e o `og:image`. A ilustração limpa continua em `assets/img/sinais/<slug>.webp` e é
  a que os jogos e as atividades usam (a figurinha entregaria a resposta).
- **Originais**: ficam em `<WORK>/figurinhas/<slug>/v<k>.png`, fora do repositório, em fundo magenta (ou verde, com
  `"fundo": "verde"`, quando o desenho precisa de roxo ou rosa).
- **Aprovação**: confira a folha de contato antes de commitar. Procure texto, número ou escudo que o Codex tenha inventado.
- **Limite do Codex**: vale o mesmo das ilustrações. Quando parar, rode `gerar --pendentes` de novo mais tarde.
- **Modelo do Codex**: se o modelo do `~/.codex/config.toml` não for aceito pela conta ("model is not supported"),
  escolha outro só para o script: `CODEX_MODEL=gpt-6.1-sol CODEX_ESFORCO=medium $F gerar --pendentes`.
  O `--pendentes` olha a figurinha publicada no repositório, então funciona sem o SSD (aponte `SINAIS_WORK` para uma pasta local).
- Quando a ilustração de um sinal muda, o `publicar.py` apaga o cartão antigo e avisa para rodar o `compor`.

## Formato

| Item | Valor |
|---|---|
| Quadro | 16:9 inteiro (o espaço de sinalização vai de x≈270 a x≈1550 no bruto) |
| Vídeo | 1280×720, H.264 CRF 26, sem áudio, ~200 KB |
| Poster | WebP |
| Fundo | `#f0fafa` |
| Marca d'água | "LIBRAS.SE" em Museo Sans Rounded 1000 com o gradiente do logo (`make_watermark.py`) |
| Recorte | `chromakey` padrão; perfil `dif` para os sinais listados em `chaves.json` (abaixo) |

## Recorte do chroma: perfis de chave (`chaves.json`)

O `chromakey` padrão compara só a cor e apaga o cabelo escuro que pega reflexo verde (a Bruna anota "recorte, cabelo").
Para esses sinais existe o perfil `dif` (`render.py` → `CHAVES`), que recorta pela diferença entre o verde e o maior dos
outros dois canais:

- o fundo fica em 71 a 77, a mecha de cabelo em 30 a 50, a pele abaixo de 0 e a camiseta perto de 0;
- nas bordas, a cor do verde é descontada do pixel, então o cabelo fino fica escuro e natural, sem halo;
- a máscara perde 1 px e é suavizada, porque o vídeo do celular (H.264 4:2:0) vaza o verde para dentro da pele e
  deixaria um contorno oliva nos dedos;
- as laterais (x < 220 e x > 1700 no bruto) ficam sempre transparentes, porque a tela tem duas marcas fixas ali;
- o recorte é feito já em 1280×720, cerca de 20 s por tomada no Mac.

Os perfis por sinal ficam em `<WORKDIR>/chaves.json`, que o `sincronizar.py enviar` sobe para o servidor:

```json
{"itens": {"lula": "dif", "sao-paulo": "dif"}}
```

- Sinal fora da lista continua no `chromakey` e mantém a assinatura de antes, então as aprovações antigas valem.
- Pôr um sinal **aprovado** na lista muda a assinatura e derruba a aprovação: ele volta a precisar de revisão.
- O app online usa o mesmo `render.py`, então o "Ajustar" lá respeita o perfil. Isso só vale depois que a imagem do
  app for reimplantada no Dokploy com este código.
- Para testar um perfil novo, acrescente outra entrada em `CHAVES` em vez de mudar a `dif`. Mudar a `dif` muda a
  assinatura de todos os sinais que a usam.

## Páginas por categoria (/sinal/categoria/<slug>/)

O `build_pages.py` gera uma página para cada categoria de `categorias.json` com pelo menos `minimo` sinais com vídeo.
A página é montada a partir do `/sinal/` já gerado: head, hero, cards, textos e FAQ próprios, e entra no bloco SINAIS do sitemap.
Os textos (title de até 60 caracteres, description de 70 a 165, dois cards editoriais e FAQ) ficam em `categorias.json`, sem travessão e sem emoji.
Categoria nova em `sinais.json` sem entrada em `categorias.json` continua só como filtro no `/sinal/`.
Em `fora` vai a categoria que já tem página em outra área: Alfabeto aponta para `/aprender-libras/alfabeto-em-libras/` e
Números para `/aprender-libras/numeros-em-libras/` (que lista os vídeos com `{{SINAIS:numero-0,...}}`).
Nas páginas de sinal, a categoria entra no breadcrumb, o selo vira link e aparece "Ver todos: <categoria>".
