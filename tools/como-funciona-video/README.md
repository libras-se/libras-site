# Animação 3D "Simples, rápido e fácil" (home, seção #how)

Vídeo em loop de 12 s com fundo transparente que resume o serviço: a janela do huet flutua em 3D
e as peças saltam da tela.

| Tempo | Passo | O que acontece |
|---|---|---|
| 0 a 3,9 s | Você envia | o arquivo voa até a zona de upload, barra de envio, prazo "1 hora", selo **Simples** |
| 3,9 a 8 s | Nós traduzimos | a intérprete sai da tela e grava na frente da câmera; o fundo do estúdio vira xadrez ("Fundo transparente"), ela pousa no vídeo e uma varredura remove o xadrez, deixando só ela recortada sobre a cena; status até "Pronto"; selo **Rápido** |
| 8 a 12 s | Você baixa | aviso "Seu vídeo com Libras está pronto", formato "Fundo transparente" selecionado, clique em Baixar, o .MOV sai da tela; selo **Fácil** |

A cena é HTML/CSS (`cena.html` + `stage.js`) capturada quadro a quadro pelo Chrome (Playwright),
com a mesma timeline determinística dos stories (`instagram/stories`).

```bash
cd tools/como-funciona-video
npm install                         # uma vez (usa o Chrome instalado)
npm run midia                       # intérprete recortada (sinal "obrigado") em cache/interprete
npm run stills                      # revisão: quadros sobre a cor da seção em revisao/folha.jpg
node render.mjs --stills 5.6 9.3    # só alguns tempos
npm run render                      # quadros + vídeos + imagens em assets/videos/como-funciona/
node render.mjs --encode            # só recodifica a partir de cache/quadros
```

Prévia em tempo real no navegador: sirva a raiz do repositório e abra
`/tools/como-funciona-video/cena.html?play&fundo`.

## Saída (assets/videos/como-funciona/)

- `como-funciona.webm`: VP9 com alfa (Chrome, Edge, Firefox, Android), ~770 KB
- `como-funciona.mov`: HEVC com alfa (Safari e qualquer navegador de iPhone/iPad), ~1,1 MB
- `como-funciona.webp`: primeiro quadro, aparece enquanto o vídeo carrega
- `como-funciona-resumo.webp`: quadro do passo 3, para movimento reduzido e economia de dados

Na home nada disso é baixado no carregamento: o vídeo só recebe `src` a 600 px da seção, toca
quando visível e pausa fora da tela. O trilho de passos abaixo dele é texto real, sincronizado
pelo `currentTime` (clicar num passo pula para ele).

## Cuidados

- **Ao re-renderizar, suba o `?v=` em `index.html`** (vídeo e imagens): o nginx serve esses arquivos
  com cache imutável de 1 ano.
- **Nada pode encostar nas bordas do palco.** Na página o vídeo fica no meio da seção e qualquer corte
  vira uma linha reta. O render roda `bordas.py` (Pillow, `python3.12`) e falha se houver alfa nas bordas.
- **HEVC precisa de `premultiply`**: o Safari lê a cor como pré-multiplicada; sem isso as sombras
  viram halo claro. O VP9 vai com alfa "reto" mesmo.
- Tempos dos passos: se mudar a timeline, atualize os `data-t` do trilho em `index.html` (0, 3.9, 8).
