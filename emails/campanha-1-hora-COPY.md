# Campanha de E-mail — "Entrega em até 1 hora" · Libras.se

Material de copy e direção para a campanha que anuncia a nova fase do Libras.se:
**conteúdo em Libras entregue em até 1 hora — tecnologia que acelera, pessoas que garantem a qualidade.**

Conceito central: **"Automatizamos o que podia. O principal continua sendo feito por pessoas."**

Arquivos HTML prontos para o Brevo:
- `campanha-1-hora-conceitual.html` — versão 1, elegante e conceitual (recomendada como principal).
- `campanha-1-hora-ousado.html` — versão 2, mais ousada e publicitária (ótima para teste A/B).

---

## 1. Assuntos (8 opções)

1. Seu conteúdo em Libras. Agora, em até 1 hora.
2. A acessibilidade não precisa mais esperar
3. Tecnologia para ganhar tempo. Pessoas para garantir qualidade.
4. Libras em até 1 hora — feita por gente de verdade
5. Mais rápido. Sem deixar de ser humano.
6. Automatizamos o processo. As pessoas continuam no centro.
7. O Libras.se acabou de ficar muito mais ágil
8. 1 hora: o novo prazo da acessibilidade audiovisual

> Dica de teste A/B no Brevo: rode o **#1** (benefício direto) contra o **#5** ou **#8** (curiosidade/ousadia).

---

## 2. Preheaders (5 opções)

1. A tecnologia acelera o processo. Os intérpretes garantem o cuidado em cada vídeo.
2. Automatizamos as etapas repetitivas para que pessoas reais cuidem do que importa.
3. Entrega em até 1 hora, com a naturalidade de quem traduz Libras de verdade.
4. Processo automatizado, tradução humana. Veja o que mudou no Libras.se.
5. Mais velocidade, mesma qualidade humana. Conheça a nova fase do Libras.se.

---

## 3. Texto completo do e-mail (versão 1 — conceitual)

**Hero**
- Selo: TECNOLOGIA + PESSOAS REAIS
- Headline: **Seu conteúdo em Libras. Agora, em até 1 hora.**
- Subheadline: Automatizamos as etapas operacionais para acelerar a produção. A tradução, a interpretação e o cuidado continuam nas mãos de intérpretes de verdade.
- Botão: **Enviar meu vídeo →** (https://huet.libras.se/)

**Abertura**
O Libras.se entrou em uma nova fase. Com tecnologia própria e processos automatizados, o que antes levava dias agora pode ser entregue em **até 1 hora**.
O que não mudou: cada tradução continua sendo feita, revisada e validada por intérpretes de Libras de verdade.

**Bloco conceitual (destaque)**
> **Automatizamos o que podia. O principal continua sendo feito por pessoas.**
>
> A automação eliminou as etapas repetitivas do caminho: organização de arquivos, fila de produção, formatação e entrega. Tudo o que tomava tempo sem agregar valor.
>
> Assim, nossos intérpretes concentram a energia onde ela importa de verdade: na expressão, no contexto e na naturalidade que só uma pessoa consegue dar à Libras.

**Benefícios**
- **Entrega em até 1 hora** — Da sua solicitação ao vídeo pronto, sem espera.
- **Processo simples e automatizado** — Você envia, a tecnologia cuida do fluxo de ponta a ponta.
- **Profissionais de verdade** — Intérpretes humanos traduzem e validam cada conteúdo.
- **Acessibilidade com qualidade** — Comunicação natural, fiel e realmente acessível.

**Como funciona (3 passos)**
1. **Você envia** — Mande seu vídeo ou conteúdo pela nossa plataforma.
2. **A tecnologia acelera** — Nosso fluxo organiza e prepara tudo automaticamente.
3. **As pessoas entregam** — Intérpretes realizam, revisam e validam a tradução.

**Chamada final**
- Headline: **Pronto para tornar seu conteúdo acessível?**
- Texto: Envie um vídeo, peça uma demonstração ou converse com a nossa equipe.
- Botões: **Enviar meu vídeo** / **Falar com a equipe** (WhatsApp)

**Rodapé**
Acessibilidade audiovisual mais simples, mais ágil e mais humana. Vídeos para todos.
WhatsApp · contato@libras.se · @libras.se · © 2026 Libras.se · CNPJ 22.943.329/0001-91 · Florianópolis, SC.

---

## 4. Estrutura visual por seções

| # | Seção | Fundo | Função |
|---|-------|-------|--------|
| 1 | Cabeçalho | Branco | Logo LIBRAS.SE + selo "Nova fase" |
| 2 | Hero | Escuro `#0e3538` + **foto** | Foto do intérprete + headline + CTA principal — maior contraste |
| 3 | Abertura | Branco | Contextualiza a novidade em 2 frases |
| 4 | Bloco conceitual | Card teal claro `#f0fafa` c/ borda `#4fd1c5` | Frase-conceito em destaque |
| 5 | Benefícios | Branco | 4 itens com selo teal (lista vertical, à prova de Outlook) |
| 6 | Como funciona | Faixa clara `#f6fcfc` | 3 passos numerados |
| 7 | CTA final | Faixa teal vibrante (gradiente) | Conversão — 2 botões |
| 8 | Rodapé | Escuro `#0e3538` | Marca, contatos, compliance, descadastro |

Ritmo de contraste: claro → **escuro (com foto)** → claro → claro → claro → **teal** → **escuro**.
A versão 2 (ousada) usa o **mesmo layout claro**: muda a copy e acrescenta o número "1h" gigante em destaque logo após o hero.

---

## 5. Imagens da campanha

Cada e-mail já traz **uma foto real** de intérprete (do banco editorial do site), no topo do hero, em `.jpg` — formato que renderiza no Outlook (webp/avif não):

- **Conceitual** → `LIBRAS.SE_4.jpg` — intérprete sorrindo e sinalizando em estúdio (pessoa real + produção).
- **Ousado** → `LIBRAS.SE_7.jpg` — intérprete sorrindo em estúdio (profissionalismo + proximidade).

Ambas confirmadas no ar (`https://libras.se/assets/img/banco-editorial/`, ~150–165 KB). Para **trocar a foto**, mude só o `src` da `<img>` no hero por outra do banco:

| Arquivo | Cena |
|---|---|
| `LIBRAS.SE_4.jpg` | Intérprete sorrindo sinalizando em estúdio (horizontal) |
| `LIBRAS.SE_5.jpg` | Intérprete gravando com celular na ring light |
| `LIBRAS.SE_6.jpg` | Intérprete sinalizando com ring light e softbox |
| `LIBRAS.SE_7.jpg` | Intérprete sorrindo em estúdio |
| `LIBRAS.SE_9.jpg` | Intérprete ao ar livre, árvores ao fundo ("lifestyle"; arquivo pesado ~1,7 MB) |

O restante do e-mail é HTML/CSS — então, **se a imagem for bloqueada, nada quebra**: aparece o texto `alt` (ver seção 8).

**Não usar:** robôs, androides, cérebros de IA ou bancos de imagem genéricos de tecnologia.

---

## 6. Versão curta (mobile / SMS / WhatsApp / push)

> **Seu conteúdo em Libras, agora em até 1 hora.** ⏱
> Automatizamos o processo. A tradução continua sendo feita por intérpretes de verdade.
> Envie seu vídeo: https://huet.libras.se/

Variação 1 linha (notificação):
> Libras em até 1 hora — tecnologia que acelera, pessoas que garantem a qualidade. → huet.libras.se

---

## 7. Versão HTML responsiva (Gmail + Outlook)

Entregue nos arquivos `.html` desta pasta. Características técnicas:

- Layout 100% em **tabelas**, largura máxima **600 px**, CSS **inline**.
- **Fallbacks de cor sólida** (`bgcolor`) em todas as seções escuras/teal — o Outlook ignora gradiente, mas nunca fica texto branco em fundo branco.
- **Botões bulletproof** com VML (`v:roundrect`) para cantos arredondados também no Outlook.
- Fonte da marca **Museo Sans Rounded** via `@font-face` (Apple Mail/iOS); fallback `Nunito → Trebuchet MS → Segoe UI → Arial`. No Outlook força-se Arial via condicional MSO.
- **Preheader oculto** + media queries para mobile.
- Logo em gradiente (`-webkit-background-clip`) com **teal sólido `#1aa8b0`** de fallback.

---

## 8. Texto alternativo (alt) das imagens

A foto do hero já vem com `alt` embutido. Se o cliente bloquear a imagem, esse texto aparece no lugar:

- Conceitual (hero): `Intérprete de Libras sorrindo e sinalizando em estúdio de gravação — a tradução é feita por pessoas de verdade`
- Ousado (hero): `Intérprete de Libras sorrindo em estúdio de gravação — profissionais reais por trás de cada tradução`

> No Brevo, defina também o **texto da pré-visualização** com um dos preheaders da seção 2.

---

## 9. Versão somente texto (plain text — fallback do Brevo)

```
LIBRAS.SE — Nova fase

SEU CONTEÚDO EM LIBRAS. AGORA, EM ATÉ 1 HORA.

Automatizamos as etapas operacionais para acelerar a produção.
A tradução, a interpretação e o cuidado continuam nas mãos de intérpretes de verdade.

> Enviar meu vídeo: https://huet.libras.se/

O Libras.se entrou em uma nova fase. Com tecnologia própria e processos
automatizados, o que antes levava dias agora pode ser entregue em até 1 hora.
O que não mudou: cada tradução continua sendo feita, revisada e validada por
intérpretes de Libras de verdade.

"Automatizamos o que podia. O principal continua sendo feito por pessoas."

O QUE MUDA PARA VOCÊ
- Entrega em até 1 hora — do envio ao vídeo pronto, sem espera.
- Processo simples e automatizado — você envia, a tecnologia cuida do fluxo.
- Profissionais de verdade — intérpretes humanos traduzem e validam cada conteúdo.
- Acessibilidade com qualidade — comunicação natural, fiel e realmente acessível.

COMO FUNCIONA
1. Você envia — mande seu vídeo pela nossa plataforma.
2. A tecnologia acelera — o fluxo organiza e prepara tudo automaticamente.
3. As pessoas entregam — intérpretes realizam, revisam e validam a tradução.

Pronto para tornar seu conteúdo acessível?
Enviar meu vídeo: https://huet.libras.se/
Falar com a equipe: https://wa.me/5548996367511

--
Libras.se — Vídeos para todos.
contato@libras.se · @libras.se
CNPJ 22.943.329/0001-91 · Florianópolis, SC
Cancelar inscrição: {{ unsubscribe }}
```

---

## 10. Versão 2 — abordagem mais ousada e publicitária

Arquivo: `campanha-1-hora-ousado.html`. Diferenças de copy:

- **Hero:** número **"1h"** gigante + headline *"O tempo da acessibilidade acabou de mudar."*
- Subheadline: *Seu conteúdo traduzido para Libras em até 1 hora. Com a velocidade da tecnologia e a alma de quem interpreta de verdade.*
- **Manifesto:** *Automatizamos o que podia. O principal continua sendo feito por pessoas.*
- Bloco **Antes × Agora:** "Dias de espera" → "Até 1 hora".
- Três provas com check: Você envia → Intérpretes traduzem → Você recebe.
- **CTA:** *Mais rápido. Sem deixar de ser humano.* → botão **"Quero meu vídeo acessível"** + WhatsApp.
- **Layout claro**, igual ao conceitual (fundo branco, hero escuro com foto, faixa teal de CTA, rodapé escuro): muda o **tom da copy**, não o esqueleto visual.
- Destaque exclusivo: o número **"1h" gigante** em teal logo abaixo do hero.

Assuntos sugeridos para esta versão: **#5, #7 ou #8**.

---

## Como subir no Brevo

1. **Campanhas → E-mail → Criar** → editor **"Código HTML"** (Paste your code).
2. Cole o conteúdo de um dos arquivos `.html`.
3. Em **Assunto**, use uma opção da seção 1; em **Pré-visualização (preheader)**, uma da seção 2.
4. O `{{ unsubscribe }}` no rodapé é substituído automaticamente pelo link de descadastro do Brevo (obrigatório).
5. Personalização opcional: troque a abertura por `Olá, {{contact.FIRSTNAME}}!` se a sua lista tiver o atributo de nome.
6. Envie um **teste para Gmail e Outlook** antes do disparo; confira CTAs e fontes.

### Checklist de links
- Enviar vídeo / plataforma: `https://huet.libras.se/`
- WhatsApp: `https://wa.me/5548996367511`
- E-mail: `contato@libras.se`
- Instagram: `@libras.se`
