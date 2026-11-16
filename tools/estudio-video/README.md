# Vídeo demonstrativo do Libras.se Estúdio (página /estudio/)

Vídeo de 36 s, sem som, que mostra o Estúdio de ponta a ponta:

| Tempo | Passo | O que acontece |
|---|---|---|
| 0 a 3,3 s | Abertura | LIBRAS.SE Estúdio e o título |
| 3,3 a 11,5 s | 1 · Calibra | câmera no fundo verde → máscara → fundo transparente, nota do recorte sobe até 92, "Tudo pronto para gravar" |
| 11,5 a 19,4 s | 2 · Grava | aula com o intérprete recortado, fila do dia, celular aperta Gravar e o REC corre |
| 19,4 a 25 s | 3 · Envia | Finalizar no celular, MP4 Full HD, barra de envio, "Entrega recebida" no WhatsApp |
| 25 a 31,5 s | 4 · Aprova | painel da coordenação: nota técnica 96, clique em Aprovar, contadores sobem |
| 31,5 a 36 s | Encerramento | os quatro diferenciais e libras.se/estudio |

As telas do app são recriadas em HTML a partir dos prints reais do Estúdio (GAMA 1.5.1), com dados
fictícios. A intérprete é uma gravação nossa em fundo verde (`fonte/teste-croma.mp4`, banco de vídeos
LIBRAS.SE, direitos próprios). A aula de fundo é fictícia (`aula.html`).

```bash
cd tools/estudio-video
npm install                    # uma vez (usa o Chrome instalado)
node midia.mjs                 # aulas fictícias, sequências da cena, material com a Bruna
node midia.mjs --so-material   # só as aulas e o material (pula as sequências da cena)
node render.mjs --stills       # revisão: alguns quadros em revisao/folha.jpg
node render.mjs --stills 16.2  # só alguns tempos
node render.mjs                # 1080 quadros + MP4 1080p/720p + cartaz
node render.mjs --encode       # só recodifica a partir de cache/quadros
```

Prévia em tempo real: sirva a raiz do repositório e abra `/tools/estudio-video/cena.html?play`.

## Saída (assets/videos/estudio/)

- `estudio-demo.mp4` (1920×1080) e `estudio-demo-720.mp4` (celular e economia de dados), com cartaz `estudio-demo.webp`
- `aula-bruna.mp4` + `.webp`: a Bruna sinalizando (ola, estudar, aprender, ensinar, livro, dos vídeos do
  vocabulário do site) recortada sobre a aula de Scrum, sem caixa

E em `assets/img/estudio/material/`: as quatro aulas fictícias (Scrum, Estatística, Direito, Fisiologia) com a
Bruna recortada e o bloco seguinte de cada uma sem Libras (`*-original.webp`), para a aba Material do painel.
As aulas vêm de `aula.html?v=dados|direito|saude&k=<rótulo do bloco>`.

A chave do verde é por dominância (G acima de max(R,B)), não `chromakey`: o fundo deste clipe é
claro e a camiseta preta some com a chave em YUV.
