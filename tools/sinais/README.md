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

Para o commit, entram:
- `assets/videos/sinais/`
- `sinal/`
- `sitemap.xml`
- `jogo/index.html`
- `tools/sinais/aprovacoes.json`

## Formato

| Item | Valor |
|---|---|
| Quadro | 16:9 inteiro (o espaço de sinalização vai de x≈270 a x≈1550 no bruto) |
| Vídeo | 1280×720, H.264 CRF 26, sem áudio, ~200 KB |
| Poster | WebP |
| Fundo | `#f0fafa` |
| Marca d'água | "LIBRAS.SE" em Museo Sans Rounded 1000 com o gradiente do logo (`make_watermark.py`) |
