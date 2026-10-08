#!/usr/bin/env python3
"""Gera os materiais em PDF de /materiais/ (assets/materiais/*.pdf) com o Chrome headless.

Cada material é um HTML montado aqui (ou lido de tools/aprender/pdf/<nome>.html) com o CSS
de impressão comum (tools/aprender/pdf/_pdf.css). As imagens e fontes são lidas direto de
assets/, então o PDF fica idêntico ao que o site mostra.

Uso:  python3 tools/aprender/pdf.py              (gera todos)
      python3 tools/aprender/pdf.py flashcards   (só um)
"""
import html
import re
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "assets" / "materiais"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FORA_DA_ESCOLA = {"cerveja"}  # materiais pensados para sala de aula
TMP = None


def esc(s):
    return html.escape(s, quote=True)


def pagina(titulo, corpo):
    css = (HERE / "pdf" / "_pdf.css").read_text().replace("{{ROOT}}", ROOT.as_uri())
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>{esc(titulo)}</title>
<style>{css}</style></head><body>{corpo}</body></html>"""


def rodape(nome, url):
    return (f'<footer class="pf"><span><b>LIBRAS.SE</b> · {esc(nome)} · {esc(url)}</span>'
            f'<span>Material gratuito para uso educativo. Mantenha este crédito.</span></footer>')


def jpeg(slug, largura=720):
    """Ilustração reduzida em JPEG: o Chrome embute o WebP original e o PDF passaria de 10 MB."""
    from PIL import Image
    dest = TMP / f"{slug}.jpg"
    if not dest.exists():
        im = Image.open(ROOT / f"assets/img/sinais/{slug}.webp").convert("RGB")
        im.thumbnail((largura, largura))
        im.save(dest, "JPEG", quality=80, optimize=True, progressive=True)
    return dest.as_uri()


def flashcards():
    data = json.loads((ROOT / "sinal/sinais.json").read_text())
    ss = [s for s in data["sinais"]
          if (ROOT / f"assets/img/sinais/{s['slug']}.webp").exists() and s["slug"] not in FORA_DA_ESCOLA]
    ss.sort(key=lambda s: (s["categoria"], s["palavra"]))
    capa = f"""<section class="page capa">
  <div class="capa-top"><span class="logo">LIBRAS.SE</span><span class="tag">Flashcards · {len(ss)} sinais</span></div>
  <h1>Flashcards <em>de Libras</em></h1>
  <p class="lead">Cartões com sinais do dia a dia, ilustrados a partir de vídeos gravados por intérprete da LIBRAS.SE. Cada cartão traz o endereço do vídeo do sinal.</p>
  <div class="tips">
    <div><b>1</b><h2>Imprima e recorte</h2><p>Use papel mais grosso, se tiver. Recorte nas linhas tracejadas. São 8 cartões por folha.</p></div>
    <div><b>2</b><h2>Veja o sinal em movimento</h2><p>A ilustração mostra a forma e as setas indicam o movimento. Na dúvida, abra o endereço do cartão e assista ao vídeo.</p></div>
    <div><b>3</b><h2>Pratique de várias formas</h2><p>Dobre o cartão para esconder a palavra, faça o sinal e confira. Ou espalhe pela sala e brinque de caça ao sinal.</p></div>
  </div>
  <div class="cats">{''.join(f'<span>{esc(c)}</span>' for c in dict.fromkeys(s["categoria"] for s in ss))}</div>
  <p class="nota">Os sinais seguem a variante usada pela equipe da LIBRAS.SE em Santa Catarina. A Libras tem variações regionais, e algumas palavras podem ter outro sinal na sua região.</p>
  {rodape("Flashcards de Libras", "libras.se/materiais")}
</section>"""
    paginas = []
    for i in range(0, len(ss), 8):
        cards = "".join(f"""<div class="fc"><span class="fc-cat">{esc(s['categoria'])}</span>
<img src="{jpeg(s['slug'])}" alt="">
<b>{esc(s['palavra'])}</b><span class="fc-url">libras.se/sinal/{s['slug']}</span></div>""" for s in ss[i:i + 8])
        paginas.append(f'<section class="page"><div class="fc-grid">{cards}</div>{rodape("Flashcards de Libras", "libras.se/materiais")}</section>')
    return pagina("Flashcards de Libras | LIBRAS.SE", capa + "".join(paginas))



ABC = list("ABCDEFGHIJKLMNOPQRSTUVWXYZÇ")
MOVIMENTO = set("HJKXZÇ")
CORES = ["#b2f5ea", "#c7f0fb", "#e3dcfb", "#fde2cf", "#fdf1b8", "#d4f5d0", "#fbd5e3"]


def soletra(p):
    import unicodedata
    p = p.upper().replace("Ç", "\x01")
    p = "".join(c for c in unicodedata.normalize("NFD", p) if unicodedata.category(c) != "Mn")
    return "".join(c for c in p.replace("\x01", "Ç") if c in ABC)


def palavras():
    return json.loads((HERE / "palavras.json").read_text())


def cab(titulo, sub):
    return (f'<div class="band" style="padding:9mm 14mm 7mm;margin-bottom:6mm"><div class="row" style="margin-bottom:4mm"><span class="logo">LIBRAS.SE</span>'
            f'<span class="tag">{esc(sub)}</span></div><h1 style="font-size:24pt">{titulo}</h1></div>')


def alfabeto_colorido():
    tiles = "".join(
        f'<div class="tile" style="background:{CORES[i % len(CORES)]}">'
        + ('<span class="mv">movimento</span>' if l in MOVIMENTO else "")
        + f'<span class="dat">{l}</span><b>{l}</b></div>' for i, l in enumerate(ABC))
    tiles += ('<div class="tile" style="background:linear-gradient(135deg,#0e3538,#2a6069)"><span class="logo" style="font-size:13pt">LIBRAS.SE</span>'
              '<span style="font-size:7pt;color:rgba(255,255,255,.7);margin-top:1mm">libras.se/aprender-libras</span></div>')
    return pagina("Alfabeto em Libras colorido | LIBRAS.SE",
                  f'<section class="page">{cab("Alfabeto <em>em Libras</em>", "Cartaz · alfabeto manual")}'
                  f'<div class="grade-abc" style="grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(7,1fr)">{tiles}</div>'
                  f'<p class="nota" style="margin-top:4mm">As letras marcadas com "movimento" (H, J, K, X, Z e Ç) não são paradas: siga a seta do desenho. '
                  f'Veja o alfabeto e escreva o seu nome em Libras em libras.se/aprender-libras/alfabeto-em-libras.</p>'
                  f'{rodape("Alfabeto em Libras", "libras.se/aprender-libras/alfabeto-em-libras")}</section>')


def alfabeto_colorir():
    def pag(letras, extra=""):
        tiles = "".join(f'<div class="tile"><span class="dat">{l}</span><b>{l}</b></div>' for l in letras)
        return (f'<section class="page colorir"><div class="mini-head"><h1>Alfabeto em Libras <em>para colorir</em></h1><span class="logo">LIBRAS.SE</span></div>'
                f'<div class="grade-abc" style="grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(5,1fr)">{tiles}{extra}</div>'
                f'{rodape("Alfabeto em Libras para colorir", "libras.se/aprender-libras/alfabeto-em-libras")}</section>')
    nome = ('<div class="tile" style="grid-column:1/-1;border-style:dashed;align-items:flex-start;padding:5mm 7mm;justify-content:flex-start">'
            '<span style="font-size:13pt;font-weight:900">Meu nome é:</span><span style="width:100%;border-bottom:.4mm solid #000;height:14mm"></span>'
            '<span style="font-size:9pt;color:#5d8487;margin-top:3mm">Soletre o seu nome com as mãos olhando o alfabeto.</span></div>')
    return pagina("Alfabeto em Libras para colorir | LIBRAS.SE", pag(ABC[:15]) + pag(ABC[15:], nome))


def alfabeto_tira():
    def tira():
        lin = lambda ls: "".join(f'<span><span class="dat">{l}</span><b>{l}</b></span>' for l in ls)
        return (f'<div class="tira"><div class="tira-top"><b>Meu alfabeto em Libras</b><span>Nome: ______________________</span><span>libras.se</span></div>'
                f'<div class="tira-row">{lin(ABC[:14])}</div><div class="tira-row">{lin(ABC[14:])}<span style="background:none"></span></div></div>')
    return pagina("Alfabeto em Libras: tira de mesa | LIBRAS.SE",
                  '<style>@page{size:A4 landscape}</style>'
                  f'<section class="page paisagem" style="gap:4mm">{tira()}{tira()}{tira()}'
                  f'{rodape("Tira de mesa do alfabeto em Libras", "libras.se/aprender-libras/alfabeto-em-libras")}</section>')


def numeros():
    tiles = "".join(f'<div><span class="dat">{n}</span><b>{n}</b></div>' for n in "0123456789")
    return pagina("Números em Libras | LIBRAS.SE",
                  f'<section class="page">{cab("Números <em>em Libras</em>", "Cartaz · algarismos de 0 a 9")}'
                  f'<div class="num-grid">{tiles}</div>'
                  f'<p class="nota" style="margin-top:4mm">Esta é a forma usada para algarismos, como em telefones, datas e documentos. '
                  f'Quando indicam quantidade, os números de 1 a 4 costumam ser feitos de outro jeito. Saiba mais em libras.se/aprender-libras/numeros-em-libras.</p>'
                  f'{rodape("Números em Libras", "libras.se/aprender-libras/numeros-em-libras")}</section>')


def memoria_alfabeto():
    cartas = []
    for l in ABC:
        cartas.append(f'<div><span class="dat">{l}</span><small>LIBRAS.SE</small></div>')
        cartas.append(f'<div><span class="letra">{l}</span><small>LIBRAS.SE</small></div>')
    pags = []
    for i in range(0, len(cartas), 20):
        bloco = cartas[i:i + 20]
        pags.append(f'<section class="page"><div class="mini-head"><h1 style="font-size:16pt">Jogo da memória <em>do alfabeto em Libras</em></h1>'
                    f'<span style="font-size:8pt;color:#5d8487">Recorte nas linhas · página {i // 20 + 1} de {-(-len(cartas) // 20)}</span></div>'
                    f'<div class="mem">{"".join(bloco)}</div>{rodape("Jogo da memória do alfabeto em Libras", "libras.se/materiais")}</section>')
    instr = ('<section class="page">' + cab("Jogo da memória <em>do alfabeto</em>", "Para imprimir e recortar") +
             '<div class="cols"><div class="box"><h2><i>1</i>Prepare</h2><ul><li>Imprima as próximas páginas, de preferência em papel mais grosso.</li>'
             '<li>Recorte nas linhas tracejadas. São 54 cartas: 27 mãos e 27 letras.</li><li>Para turmas pequenas, use só as letras de A a M no começo.</li></ul></div>'
             '<div class="box"><h2><i>2</i>Jogue</h2><ul><li>Embaralhe e espalhe as cartas viradas para baixo.</li>'
             '<li>Na sua vez, vire duas cartas. Se forem a mão e a letra correspondentes, faça a letra com a sua mão e fique com o par.</li>'
             '<li>Ganha quem juntar mais pares.</li></ul></div>'
             '<div class="box full"><h2><i>3</i>Varie</h2><ul><li><b>Soletre o nome:</b> quem formar um par diz um nome que comece com aquela letra, soletrando em Libras.</li>'
             '<li><b>Online:</b> treine também no jogo da memória com sinais em vídeo, em libras.se/jogos/jogo-da-memoria-libras.</li></ul></div></div>'
             + rodape("Jogo da memória do alfabeto em Libras", "libras.se/materiais") + '</section>')
    return pagina("Jogo da memória do alfabeto em Libras | LIBRAS.SE", instr + "".join(pags))


def caderno():
    import random
    rnd = random.Random(2026)
    dados = palavras()["temas"]
    def sel(tema, n, maxl):
        ps = [p for p in dados[tema]["palavras"] if len(soletra(p)) <= maxl]
        rnd.shuffle(ps)
        return ps[:n]
    def pag(corpo):
        return f'<section class="page">{corpo}{rodape("Caderno de atividades de datilologia", "libras.se/atividades/datilologia")}</section>'
    gab = []

    ref = "".join(f'<div class="tile" style="background:{CORES[i % len(CORES)]}"><span class="dat" style="font-size:30pt">{l}</span><b style="font-size:10pt;min-width:6mm;height:6mm">{l}</b></div>' for i, l in enumerate(ABC))
    capa = pag(cab("Caderno de atividades <em>de datilologia</em>", "Alfabeto manual · com gabarito") +
               '<p class="lead" style="font-size:10.5pt;margin-bottom:5mm">Seis atividades para praticar a leitura do alfabeto manual da Libras. '
               'Use o alfabeto abaixo como consulta nas primeiras vezes e confira as respostas no gabarito, na última página.</p>'
               f'<div class="grade-abc" style="grid-template-columns:repeat(7,1fr);grid-template-rows:repeat(4,1fr)">{ref}</div>')

    ls = ABC[:]; rnd.shuffle(ls); ls = ls[:16]
    def bloco(b):
        d = b[:]; rnd.shuffle(d)
        return '<div class="lig-col">' + "".join(f'<span class="m"><span class="dat">{l}</span><i></i></span><span class="l"><i></i>{d[k]}</span>' for k, l in enumerate(b)) + "</div>"
    a1 = pag('<div class="ex-tit">1. Ligue a mão <span>à letra</span></div><div class="ex-sub">Ligue cada configuração de mão à letra correspondente.</div>'
             f'<div class="lig enche">{bloco(ls[:8])}{bloco(ls[8:])}</div>')
    gab.append(("1. Ligue a mão à letra", "Cada mão corresponde à letra que ela representa: " + ", ".join(ls) + "."))

    def descubra(n, tema, titulo):
        ps = sel(tema, 7, 9)
        linhas = "".join(f'<div class="desc-l"><span class="nr">{k + 1}</span><span class="dat">{soletra(p)}</span><span class="lin"></span></div>' for k, p in enumerate(ps))
        gab.append((f"{n}. {re.sub('<[^>]+>', '', titulo)}", "; ".join(f"{k + 1}. {p}" for k, p in enumerate(ps)) + "."))
        return pag(f'<div class="ex-tit">{n}. {titulo}</div><div class="ex-sub">Leia a palavra soletrada e escreva em português.</div><div class="enche">{linhas}</div>')
    a2 = descubra(2, "animais", 'Descubra o <span>animal</span>')
    a3 = descubra(3, "nomes", 'Descubra o <span>nome</span>')

    T = 9
    g = [["" for _ in range(T)] for _ in range(T)]; pos = set(); ok = []
    for p in sel("frutas", 12, T):
        if len(ok) >= 6: break
        W = soletra(p)
        for _ in range(400):
            d = rnd.choice([(0, 1), (1, 0)]); r0, c0 = rnd.randrange(T), rnd.randrange(T)
            if r0 + d[0] * (len(W) - 1) >= T or c0 + d[1] * (len(W) - 1) >= T: continue
            if any(g[r0 + d[0] * k][c0 + d[1] * k] not in ("", W[k]) for k in range(len(W))): continue
            for k in range(len(W)):
                g[r0 + d[0] * k][c0 + d[1] * k] = W[k]; pos.add((r0 + d[0] * k, c0 + d[1] * k))
            ok.append(p); break
    for r in range(T):
        for c in range(T):
            if not g[r][c]: g[r][c] = rnd.choice(ABC[:26])
    def grade(gab_):
        return (f'<div class="cp{" cp-gab" if gab_ else ""}" style="grid-template-columns:repeat({T},1fr)">' + "".join(
            f'<span class="{"on" if gab_ and (r, c) in pos else ""}"><span class="dat">{g[r][c]}</span><small>{g[r][c] if gab_ else ""}</small></span>'
            for r in range(T) for c in range(T)) + "</div>")
    lista = '<div class="pal">' + "".join(f"<span>{p}</span>" for p in ok) + "</div>"
    a4 = pag('<div class="ex-tit">4. Caça-palavras <span>com mãos</span></div><div class="ex-sub">Encontre as frutas soletradas com o alfabeto manual, na horizontal e na vertical.</div>' + lista + grade(False))

    q = ABC[:]; rnd.shuffle(q); q = q[:18]
    a5 = pag('<div class="ex-tit">5. Que letra <span>é esta?</span></div><div class="ex-sub">Escreva embaixo de cada mão a letra que ela representa.</div>'
             '<div class="qual enche">' + "".join(f'<div><span class="dat">{l}</span><span class="lin"></span></div>' for l in q) + "</div>")
    gab.append(("5. Que letra é esta?", " ".join(q) + "."))

    nomes = sel("libras", 4, 8)
    a6 = pag('<div class="ex-tit">6. Soletre <span>você</span></div><div class="ex-sub">Escreva a palavra e desenhe ou cole embaixo as mãos de cada letra. Depois, soletre em voz alta para a turma com as suas mãos.</div>'
             + "".join(f'<div class="desc-l" style="padding:5mm 0"><span class="nr">{k + 1}</span><span style="font-size:16pt;font-weight:900;flex:1">{p}</span><span class="lin" style="width:110mm;height:20mm"></span></div>' for k, p in enumerate(nomes))
             + '<div class="desc-l" style="padding:5mm 0"><span class="nr">5</span><span style="font-size:16pt;font-weight:900;flex:1">O seu nome</span><span class="lin" style="width:110mm;height:20mm"></span></div>')

    blocos = "".join(f'<div class="gab-bloco"><h3>{esc(t)}</h3><p>{esc(x)}</p></div>' for t, x in gab[:3])
    gab_pag = pag('<div class="ex-tit">Gabarito</div><div class="ex-sub">Respostas das atividades 1, 2, 3 e 5. A atividade 6 é livre.</div>' + blocos +
                  '<div class="gab-bloco"><h3>4. Caça-palavras com mãos</h3>' + lista + grade(True) + "</div>" +
                  "".join(f'<div class="gab-bloco"><h3>{esc(t)}</h3><p>{esc(x)}</p></div>' for t, x in gab[3:]))
    return pagina("Caderno de atividades de datilologia | LIBRAS.SE", capa + a1 + a2 + a3 + a4 + a5 + a6 + gab_pag)


def estatico(nome):
    return lambda: pagina(*(HERE / "pdf" / f"{nome}.html").read_text().split("\n", 1))


MATERIAIS = {
    "flashcards-de-libras": flashcards,
    "guia-como-se-comunicar-com-pessoas-surdas": estatico("guia-comunicacao"),
    "checklist-video-acessivel-em-libras": estatico("checklist-video"),
    "calendario-da-comunidade-surda": estatico("calendario"),
    "alfabeto-em-libras-colorido": alfabeto_colorido,
    "alfabeto-em-libras-para-colorir": alfabeto_colorir,
    "alfabeto-em-libras-tira-de-mesa": alfabeto_tira,
    "numeros-em-libras": numeros,
    "jogo-da-memoria-alfabeto-em-libras": memoria_alfabeto,
    "caderno-de-atividades-de-datilologia": caderno,
}


def gerar(slug, fn):
    global TMP
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        TMP = Path(tmp)
        src = TMP / f"{slug}.html"
        src.write_text(fn())
        dest = OUT / f"{slug}.pdf"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--allow-file-access-from-files", f"--print-to-pdf={dest}", src.as_uri()],
                       check=True, capture_output=True, timeout=120)
    kb = dest.stat().st_size // 1024
    paginas = capa(slug, dest)
    print(f"ok  assets/materiais/{slug}.pdf  ({kb} KB, {paginas} pág.)")


def capa(slug, pdf):
    """Miniatura da primeira página (assets/materiais/capas/<slug>.webp) para a página /materiais/."""
    import re
    from PIL import Image
    (OUT / "capas").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "80", "-f", "1", "-l", "1", "-png", str(pdf), f"{tmp}/c"], check=True)
        im = Image.open(next(Path(tmp).glob("c*.png"))).convert("RGB")
        im.thumbnail((480, 680))
        im.save(OUT / "capas" / f"{slug}.webp", "WEBP", quality=82)
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))


if __name__ == "__main__":
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    for slug, fn in MATERIAIS.items():
        if slug.startswith(filtro):
            try:
                gerar(slug, fn)
            except FileNotFoundError as e:
                print(f"--  {slug}: fonte ausente ({e.filename})")
