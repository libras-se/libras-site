#!/usr/bin/env python3
"""Monta um post de baixa complexidade do blog a partir de um JSON de entrada (Agent Control).

O Agent Control (agentes.libras.se), depois que uma pessoa aprova o texto, cria a branch
agentes/blog-<slug>, commita UM arquivo blog/_entrada/<slug>.json e abre um PR. O workflow
.github/workflows/publicar-post.yml roda este script nessa branch e commita o resultado.

    python3 tools/blog/novo_post.py                         # processa todos os blog/_entrada/*.json
    python3 tools/blog/novo_post.py caminho/entrada.json    # um ou mais arquivos
    python3 tools/blog/novo_post.py --validar entrada.json  # só valida; não escreve nada

Opções: --sem-geradores (monta o post sem rodar os geradores do §8) e --manter-entrada (não
apaga o JSON de blog/_entrada/ no fim). Formato do JSON e fluxo: blog/CLAUDE.md, seção
"Publicação pelo Agent Control". Exemplo: tools/blog/exemplo-entrada.json.

Para cada entrada:
  1. valida o JSON (versão 1) e converte o markdown. Com qualquer erro, nada é escrito e a saída é 1;
  2. gera a capa em assets/img/blog/<slug>/<slug>.{jpg,webp,avif} (1200x675; o JPG fica abaixo de
     300 KB e é a og:image): a imagem do campo "capa" ou, se ele vier null, uma foto do banco
     editorial escolhida pelo tema (§7);
  3. escreve blog/<slug>/index.html a partir do molde tools/blog/post-simples.html: markdown sem
     HTML bruto, só links http(s) e caminhos /... que existem no site, e a primeira ocorrência de
     cada termo do glossário linkada (§6);
  4. registra a editoria em tools/blog/home.json (classificacao).
Depois roda os geradores do §8 que se aplicam a post novo (og.py, home.py, autores.py, links.py,
llms.py e auditoria.py; videos.py só se o post tiver vídeo, o que o markdown não permite), confere
o resultado e apaga os JSON de blog/_entrada/.

O post leva o carimbo <!-- agentes:origem aprovacao=<id> artefato=<id> versao=<n> -->. Um slug que
já existe em blog/ é erro, a menos que o post tenha esse carimbo com os mesmos três valores: aí é
uma re-execução, e o post é refeito igual (a capa já gerada é mantida).

Saída: 0 = ok (ou nada a publicar), 1 = entrada inválida, 2 = falha nos geradores ou na conferência.
Dependências: Python 3.10+, markdown-it-py e Pillow (tools/blog/requirements-publicador.txt).
"""
import argparse
import csv
import hashlib
import html
import io
import json
import math
import os
import re
import subprocess
import sys
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SITE = "https://libras.se"
ENTRADA = RAIZ / "blog/_entrada"
MOLDE = AQUI / "post-simples.html"
REFERENCIA = RAIZ / "blog/tradutor-de-libras-se-destaca-no-rock-in-rio/index.html"
HOME_JSON = AQUI / "home.json"
TZ = ZoneInfo("America/Sao_Paulo")
EDITORIAS = ("lingua", "educacao", "direitos", "inclusao", "cultura", "esporte")
MESES = "jan. fev. mar. abr. mai. jun. jul. ago. set. out. nov. dez.".split()
W, H = 1200, 675
LIMITE_OG = 300 * 1024
CARIMBO = "<!-- agentes:origem aprovacao={} artefato={} versao={} -->"
CARIMBO_RE = re.compile(r"<!-- agentes:origem aprovacao=(\S+) artefato=(\S+) versao=(\d+) -->")
NA_ACTION = os.environ.get("GITHUB_ACTIONS") == "true"

ORGANIZACAO = {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "LIBRAS.SE", "url": f"{SITE}/",
               "sameAs": ["https://instagram.com/libras.se", "https://youtube.com/@librasse", "https://linkedin.com/company/librasse",
                          "https://facebook.com/librasse", "https://tiktok.com/@libras.se"]}
PUBLISHER = {
    "@type": "Organization", "@id": f"{SITE}/#organization", "name": "LIBRAS.SE", "url": f"{SITE}/",
    "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/img/favicon/cropped-FAVICONpng-1-512x512.png", "width": 512, "height": 512},
    "sameAs": ["https://instagram.com/libras.se", "https://youtube.com/@librasse", "https://linkedin.com/company/librasse",
               "https://facebook.com/librasse", "https://tiktok.com/@libras.se"],
}
NOMES_DA_ORGANIZACAO = {"libras.se", "libras se", "librasse", "equipe libras.se", "equipe libras se", "equipe da libras.se"}

CAMPOS = {"versao", "tipo", "slug", "titulo", "subtitulo", "descricao", "palavras_chave", "editoria", "tags", "autor",
          "publicado_em", "markdown", "fontes", "capa", "cta", "origem"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._:-]{0,98}[A-Za-z0-9])?$")
PRECO_RE = re.compile(r"R\$|US\$|€|\d\s*(?:reais|real)\b", re.I)
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B50\U00002B55\U0000FE0F\U0000200D]")
CONTROLE_RE = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\U00002028\U00002029]")
NAO_PUBLICADO = ("tools/", "scripts/", "og/", "emails/", "audit/", "crm/", "CLIENTES/", "node_modules/")

# Glossário (§6): variações de cada termo que viram link. Termo novo no termos.csv sem entrada aqui
# usa o próprio nome (sem o parêntese) e a sigla entre parênteses, se tiver 3 letras ou mais.
# Uma palavra só com maiúscula (Libras, LBI, TILs) casa exatamente; o resto casa sem diferenciar
# maiúsculas. Assim "libras" minúsculo (a moeda) não casa, e LIBRAS.SE nunca casa.
APELIDOS = {
    "libras": ["Língua Brasileira de Sinais", "Libras", "LIBRAS"],
    "surdo": ["pessoas surdas", "pessoa surda", "surdos", "surdas", "surdo", "surda", "surdez"],
    "til-tils": ["tradutores e intérpretes de Libras", "tradutoras e intérpretes de Libras", "tradutor e intérprete de Libras",
                 "tradutora e intérprete de Libras", "tradutores-intérpretes de Libras", "tradutor-intérprete de Libras",
                 "intérpretes de Libras", "intérprete de Libras", "TILS", "TILs", "TIL"],
    "lei-10436": ["Lei nº 10.436/2002", "Lei n° 10.436/2002", "Lei n.º 10.436/2002", "Lei 10.436/2002", "Lei nº 10.436",
                  "Lei 10.436", "Lei de Libras"],
    "decreto-5626": ["Decreto nº 5.626/2005", "Decreto n° 5.626/2005", "Decreto 5.626/2005", "Decreto nº 5.626", "Decreto 5.626"],
    "lbi": ["Lei Brasileira de Inclusão", "LBI"],
    "ines": ["Instituto Nacional de Educação de Surdos", "INES"],
    "feneis": ["Federação Nacional de Educação e Integração dos Surdos", "FENEIS", "Feneis"],
    "janela-de-libras": ["janelas de Libras", "janela de Libras"],
    "comunidade-surda": ["comunidades surdas", "comunidade surda"],
    "populacao-surda": ["população surda"],
    "acessibilidade-audiovisual": ["acessibilidade audiovisual"],
    "audiodescricao": ["audiodescrições", "audiodescrição"],
    "lse": ["Legenda para Surdos e Ensurdecidos", "legendas para surdos", "legenda para surdos", "LSE"],
    "bilinguismo": ["bilinguismo", "educação bilíngue", "escolas bilíngues", "escola bilíngue"],
    "interpretacao-simultanea": ["interpretação simultânea"],
    "interpretacao-remota": ["interpretação remota"],
    "datilologia": ["datilologia"],
    "configuracao-de-mao": ["configurações de mão", "configuração de mão", "configuração da mão"],
    "espaco-de-sinalizacao": ["espaço de sinalização"],
    "expressao-nao-manual": ["expressões não manuais", "expressões não-manuais", "expressão não manual", "expressão não-manual"],
    "sinal-soletrado": ["sinais soletrados", "sinal soletrado"],
    "ponto-de-articulacao": ["pontos de articulação", "ponto de articulação"],
    "movimento": ["parâmetro movimento", "parâmetro de movimento"],
    "orientacao-de-mao": ["orientação de mão", "orientação da mão", "orientação da palma"],
    "glosa": ["glosas", "glosa"],
}
NAO_DERIVAR = {"movimento", "legenda", "comunidade", "interprete"}

# Banco editorial (§7): o CSV vem sem acento; o alt da capa sai acentuado para o leitor de tela.
ACENTOS_BANCO = {"Interprete": "Intérprete", "interprete": "intérprete", "estudio": "estúdio", "atraves": "através",
                 "gravacao": "gravação", "area": "área", "arvores": "árvores", "edicao": "edição", "video": "vídeo",
                 "traducao": "tradução", "acessivel": "acessível", "camera": "câmera"}
PARADAS = set("""para pela pelo pelas pelos como sobre entre mais menos muito muita muitos muitas seus suas nosso nossa
este esta estes estas esse essa esses essas isso isto aquilo eles elas voce voces nao tambem quando onde porque qual quais
quem cada todo toda todos todas outro outra outros outras mesmo mesma desde ainda apos antes depois sera foram pode podem
deve devem fazer feito feita sendo serem estao libras""".split())


# ------------------------------------------------------------------ utilidades

class Relatorio:
    """Erros e avisos de uma entrada; imprime cada um uma vez (e anota no GitHub Actions)."""

    def __init__(self, arquivo):
        self.arquivo = arquivo
        self.erros, self.avisos = [], []
        self._impressos = (0, 0)

    def erro(self, msg):
        self.erros.append(msg)

    def aviso(self, msg):
        self.avisos.append(msg)

    def imprime(self):
        nome = rel(self.arquivo)
        e0, a0 = self._impressos
        for m in self.erros[e0:]:
            erro_na_tela(f"ERRO  {nome}: {m}")
            anota("error", nome, m)
        for m in self.avisos[a0:]:
            print(f"aviso {nome}: {m}", flush=True)
            anota("warning", nome, m)
        self._impressos = (len(self.erros), len(self.avisos))


def erro_na_tela(msg):
    """Erro no stderr, sem trocar a ordem com o que já foi para o stdout (o log do Action junta os dois)."""
    sys.stdout.flush()
    print(msg, file=sys.stderr, flush=True)


def anota(nivel, arquivo, msg):
    """Anotação do GitHub Actions: aparece no resumo do run e na API de check-runs."""
    if NA_ACTION:
        e = lambda s: s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::{nivel} title=novo_post.py ({e(arquivo).replace(',', '%2C').replace(':', '%3A')})::{e(msg)}", flush=True)


def falha(msg, codigo=2):
    erro_na_tela(f"ERRO  {msg}")
    anota("error", "tools/blog/novo_post.py", msg)
    raise SystemExit(codigo)


def rel(p):
    try:
        return Path(p).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return str(p)


def esc(s, quote=True):
    return html.escape(s, quote=quote)


def norm(s):
    """Para comparar: sem acento, minúsculo, hífen vira espaço."""
    s = unicodedata.normalize("NFD", s.casefold())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.replace("-", " ").split())


def hoje_sp():
    return datetime.now(TZ).date()


def dia_sp(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.astimezone(TZ).date() if dt.tzinfo else dt.date()


def data_txt(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def limpa(s, linha_unica=True, campo="", r=None):
    """Texto vindo de IA: sem caracteres de controle, emoji ou travessão (o blog não usa e a
    checagem_blog.py trata como erro). O travessão vira vírgula; numa fala com travessão no começo
    da linha, o traço sai."""
    s = unicodedata.normalize("NFC", s).replace("\r\n", "\n").replace("\r", "\n")
    s = CONTROLE_RE.sub(" ", s)
    if EMOJI_RE.search(s):
        s = EMOJI_RE.sub("", s)
        if r:
            r.aviso(f"{campo}: emoji removido (o blog não usa emoji)")
    if "—" in s:
        s = re.sub(r"(?m)^([ \t>*+-]*)—[ \t]*", r"\1", s)
        s = re.sub(r"[ \t]*—[ \t]*", ", ", s)
        s = re.sub(r",(\s*[,.;:!?])", r"\1", s)
        if r:
            r.aviso(f"{campo}: travessão (—) trocado por vírgula (o blog não usa travessão)")
    s = s.replace("LIBRAS-SE", "LIBRAS.SE")
    return " ".join(s.split()) if linha_unica else s.strip("\n")


# ------------------------------------------------------------------ links

def caminho_publico(caminho):
    """Arquivo do repositório que responde por um caminho do site, ou None se ele não existe ou
    não vai para o ar (ferramentas, rascunhos, pastas com _ ou .)."""
    p = unquote(caminho.split("#", 1)[0].split("?", 1)[0])
    if not p.startswith("/") or p.startswith("//") or "\\" in p or "\x00" in p:
        return None
    partes = [x for x in p.split("/") if x]
    if any(x in (".", "..") or x.startswith((".", "_")) for x in partes):
        return None
    relp = "/".join(partes)
    if relp.startswith(NAO_PUBLICADO) or relp.endswith(".md"):
        return None
    alvo = (RAIZ / relp).resolve()
    try:
        alvo.relative_to(RAIZ)
    except ValueError:
        return None
    if alvo.is_dir():
        alvo = alvo / "index.html"
    return alvo if alvo.is_file() else None


def confere_link(href, slug_do_post=None):
    """('interno'|'externo', href normalizado) ou (None, motivo). Só passam http(s):// e /caminho
    que existe no site; https://libras.se/... vira caminho relativo e http:// vira https://."""
    h = (href or "").strip()
    if not h:
        return None, "link vazio"
    if CONTROLE_RE.search(h) or re.search(r"\s", h):
        return None, "link com espaço ou caractere de controle"
    partes = urlsplit(h)
    esquema = partes.scheme.lower()
    if esquema in ("http", "https"):
        host = (partes.hostname or "").lower()
        if not host or "@" in partes.netloc or "\\" in h:
            return None, "endereço inválido"
        if host not in ("libras.se", "www.libras.se"):
            return "externo", ("https" + h[len(partes.scheme):] if esquema == "http" else h)
        h = urlunsplit(("", "", partes.path or "/", partes.query, partes.fragment))
        partes = urlsplit(h)
    elif esquema:
        return None, f"esquema não permitido ({esquema})"
    elif partes.netloc:
        return None, "endereço começando com // não é aceito; use https://"
    if not h.startswith("/") or h.startswith("//") or h.startswith("/\\"):
        return None, "só são aceitos links http(s):// e caminhos que começam com /"
    caminho = partes.path or "/"
    if slug_do_post and caminho.rstrip("/") == f"/blog/{slug_do_post}":
        caminho = f"/blog/{slug_do_post}/"
    elif not caminho_publico(caminho):
        return None, f"a página {caminho} não existe no site"
    elif not caminho.endswith("/") and "." not in caminho.rsplit("/", 1)[-1]:
        caminho += "/"
    return "interno", urlunsplit(("", "", caminho, partes.query, partes.fragment))


# ------------------------------------------------------------------ glossário

def derivar(termo):
    out = []
    for parte in re.split(r"\s+/\s+|:\s+", termo):
        sigla = re.search(r"\(([^)]+)\)", parte)
        base = re.sub(r"\s*\([^)]*\)", "", parte).strip()
        for a in (base, sigla.group(1).strip() if sigla else ""):
            if len(a) < 3 or norm(a) in NAO_DERIVAR:
                continue
            out.append(a if " " in a or a.isupper() else a.lower())
    return out


def exato(apelido):
    """Palavra única com maiúscula (Libras, LBI, TILs) casa exatamente; o resto, sem diferenciar maiúsculas."""
    return " " not in apelido and any(c.isupper() for c in apelido)


class Glossario:
    """Termos publicados de glossario/termos.csv que têm página, com as variações que viram link."""

    def __init__(self):
        self.termos = []
        with open(RAIZ / "glossario/termos.csv", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                slug = (row.get("slug") or "").strip()
                if (row.get("status") or "").strip() == "publicado" and (RAIZ / "glossario" / slug / "index.html").exists():
                    self.termos.append((slug, APELIDOS.get(slug) or derivar(row.get("termo") or "")))
        self.exatos, self.livres, alternativas = {}, {}, []
        for slug, apelidos in self.termos:
            for a in apelidos:
                corpo = r"\s+".join(re.escape(p) for p in a.split())
                if exato(a):
                    self.exatos.setdefault(a, slug)
                    alternativas.append((len(a), corpo))
                else:
                    self.livres.setdefault(a.casefold(), slug)
                    alternativas.append((len(a), f"(?i:{corpo})"))
        alternativas.sort(key=lambda x: -x[0])  # a variação mais longa primeiro: "janela de Libras" antes de "Libras"
        self.re = (re.compile(r"(?<![\w@/.-])(?:" + "|".join(c for _, c in alternativas) + r")(?![\w-]|\.\w)")
                   if alternativas else None)

    def slug(self, achado):
        t = " ".join(achado.split())
        return self.exatos.get(t) or self.livres.get(t.casefold())

    def da_tag(self, tag):
        n = norm(tag)
        for slug, apelidos in self.termos:
            if n == norm(slug) or any(n == norm(a) for a in apelidos):
                return slug
        return None


# ------------------------------------------------------------------ markdown

def markdown_seguro():
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        falha("falta o markdown-it-py: pip install -r tools/blog/requirements-publicador.txt")
    md = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False, "xhtmlOut": False, "breaks": False})
    # Sem HTML bruto (o texto vem de IA) e sem bloco de código por recuo (um parágrafo recuado por
    # engano viraria <pre>). Todo link, inclusive <autolink>, passa por confere_link() nos tokens.
    md.disable(["code", "html_block", "html_inline"])
    md.validateLink = lambda url: True
    return md


def renderiza(texto, slug, titulo, glossario, r):
    """(HTML do corpo, palavras, blocos de primeiro nível, termos do glossário linkados)."""
    from markdown_it.token import Token
    md = markdown_seguro()
    tokens = md.parse(texto, {})

    if len(tokens) >= 3 and tokens[0].type == "heading_open" and norm(tokens[1].content) == norm(titulo):
        r.aviso("markdown: o primeiro subtítulo repetia o título do post e foi retirado")
        tokens = tokens[3:]

    rebaixou = False
    for t in tokens:
        if t.type in ("heading_open", "heading_close"):
            n = int(t.tag[1])
            novo = 2 if n == 1 else min(n, 4)
            if novo != n:
                rebaixou = rebaixou or n == 1
                t.tag = f"h{novo}"
    if rebaixou:
        r.aviso("markdown: título de nível 1 (#) virou ## (o único H1 da página é o título do post)")

    ja_linkados = set()
    for t in tokens:
        if t.type != "inline" or not t.children:
            continue
        filhos, pula_fecha, abre = [], False, None
        for i, c in enumerate(t.children):
            if c.type == "image":
                r.aviso(f"markdown: imagem removida ({c.attrs.get('src', '')}); a capa vem do campo capa ou do banco editorial")
                continue
            if c.type == "link_open":
                tipo, valor = confere_link(str(c.attrs.get("href", "")), slug)
                if not tipo:
                    resto = t.children[i + 1:]
                    fim = next((k for k, x in enumerate(resto) if x.type == "link_close"), len(resto))
                    ancora = "".join(x.content for x in resto[:fim])
                    r.aviso(f"markdown: link removido ({valor}): {c.attrs.get('href', '')!r}; o texto {ancora!r} ficou sem link")
                    pula_fecha = True
                    continue
                c.attrs = {"href": valor}
                if tipo == "externo":
                    c.attrs.update({"target": "_blank", "rel": "noopener noreferrer"})
                abre = len(filhos)
            elif c.type == "link_close" and pula_fecha:
                pula_fecha = False
                continue
            elif c.type == "link_close" and abre is not None:
                if not "".join(x.content for x in filhos[abre + 1:]).strip():
                    del filhos[abre:]  # link que ficou sem texto (era só a imagem)
                    abre = None
                    continue
                m = re.match(r"^/glossario/([a-z0-9-]+)/$", str(filhos[abre].attrs["href"]))
                if m:
                    ja_linkados.add(m.group(1))
                abre = None
            filhos.append(c)
        # sem espaço sobrando onde uma imagem foi tirada da ponta do parágrafo
        if filhos and filhos[0].type == "text":
            filhos[0].content = filhos[0].content.lstrip()
        if filhos and filhos[-1].type == "text":
            filhos[-1].content = filhos[-1].content.rstrip()
        t.children = filhos

    # glossário: a primeira ocorrência de cada termo vira link, fora de links e de subtítulos
    if glossario.re:
        for i, t in enumerate(tokens):
            if t.type != "inline" or not t.children or (i and tokens[i - 1].type == "heading_open"):
                continue
            novos, dentro = [], 0
            for c in t.children:
                if c.type in ("link_open", "link_close"):
                    dentro += 1 if c.type == "link_open" else -1
                if c.type != "text" or dentro:
                    novos.append(c)
                    continue
                pos, pedacos = 0, []
                for m in glossario.re.finditer(c.content):
                    s = glossario.slug(m.group(0))
                    if not s or s in ja_linkados:
                        continue
                    ja_linkados.add(s)
                    if m.start() > pos:
                        pedacos.append(Token("text", "", 0, content=c.content[pos:m.start()]))
                    pedacos += [Token("link_open", "a", 1, attrs={"href": f"/glossario/{s}/"}),
                                Token("text", "", 0, content=m.group(0)), Token("link_close", "a", -1)]
                    pos = m.end()
                if not pedacos:
                    novos.append(c)
                    continue
                if pos < len(c.content):
                    pedacos.append(Token("text", "", 0, content=c.content[pos:]))
                novos += pedacos
            t.children = novos

    corpo = md.renderer.render(tokens, md.options, {}).strip("\n")
    palavras = len(html.unescape(re.sub(r"<[^>]+>", " ", corpo)).split())
    blocos = sum(1 for t in tokens if t.level == 0 and t.nesting >= 0 and t.type != "inline")
    return corpo, palavras, blocos, sorted(ja_linkados)


# ------------------------------------------------------------------ capa

def pil():
    try:
        from PIL import Image, ImageOps, features
    except ImportError:
        falha("falta o Pillow: pip install -r tools/blog/requirements-publicador.txt")
    return Image, ImageOps, features


def tamanho(caminho):
    Image, _, _ = pil()
    with Image.open(caminho) as im:
        return im.size


def maior_versao(arquivo):
    """A maior versão da mesma imagem (png, jpg ou webp com o mesmo nome), como no og.py."""
    cands = [arquivo] + [arquivo.with_suffix(e) for e in (".png", ".jpg", ".jpeg", ".JPG", ".JPEG", ".webp")]
    cands = [c for c in dict.fromkeys(cands) if c.exists() and c.suffix.lower() != ".avif"] or [arquivo]
    return max(cands, key=lambda c: (tamanho(c)[0], {".png": 2, ".jpg": 1, ".jpeg": 1}.get(c.suffix.lower(), 0)))


def raizes(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {p[:6] for p in re.findall(r"[a-z0-9]+", t) if len(p) >= 4 and p not in PARADAS}


def escolhe_do_banco(slug, titulo, tags, palavras_chave):
    """Foto do banco editorial pelo tema: palavras do título, das tags e das palavras-chave contra
    uso, alt, meta_descricao e motivo (peso dobrado no uso; palavra que aparece em todas as fotos
    não conta). Só fotos horizontais, porque o recorte 16:9 de uma foto vertical perde quase tudo.
    No empate, ou sem palavra em comum, a escolha é fixa por post (hash do slug)."""
    with open(RAIZ / "assets/img/banco-editorial/imagens.csv", encoding="utf-8", newline="") as fh:
        linhas = [x for x in csv.DictReader(fh) if caminho_publico(x["arquivo"])]
    if not linhas:
        return None
    for x in linhas:
        w, h = tamanho(RAIZ / x["arquivo"].lstrip("/"))
        x["_horizontal"] = w >= h
        x["_uso"] = raizes(x["uso"])
        x["_tudo"] = x["_uso"] | raizes(" ".join(x[k] for k in ("alt", "meta_descricao", "motivo")))
    horizontais = [x for x in linhas if x["_horizontal"]] or linhas
    df = {}
    for x in linhas:
        for p in x["_tudo"]:
            df[p] = df.get(p, 0) + 1
    post = raizes(" ".join([titulo] + tags + palavras_chave))

    def nota(x):
        return round(sum(math.log((len(linhas) + 1) / (df[p] + 1)) * (2 if p in x["_uso"] else 1) for p in post & x["_tudo"]), 6)
    melhor = max(nota(x) for x in horizontais)
    if melhor > 0:
        empate = [x for x in horizontais if nota(x) == melhor]
    else:
        empate = [x for x in horizontais if not x["meta_descricao"].lower().startswith("captura de tela")] or horizontais
    return empate[int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(empate)]


def acentua_alt(alt):
    return re.sub(r"\b(" + "|".join(ACENTOS_BANCO) + r")\b", lambda m: ACENTOS_BANCO[m.group(1)], alt)


def gera_capa(fonte, slug, foco, reexecucao, r):
    """assets/img/blog/<slug>/<slug>.{jpg,webp,avif} em 1200x675, recortados em 16:9 no ponto de
    foco. O JPG fica abaixo de 300 KB (é a og:image). Devolve True se há AVIF."""
    Image, ImageOps, features = pil()
    pasta = RAIZ / "assets/img/blog" / slug
    jpg, webp, avif = (pasta / f"{slug}.{e}" for e in ("jpg", "webp", "avif"))
    if reexecucao and jpg.exists() and webp.exists():
        print(f"  = capa mantida: {rel(jpg)} (re-execução)")
        return avif.exists()
    with Image.open(fonte) as im0:
        im = ImageOps.exif_transpose(im0)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            fundo = Image.new("RGB", im.size, "white")
            fundo.paste(im, mask=im.split()[3])
            im = fundo
        im = im.convert("RGB")
    if im.width < W:
        r.aviso(f"capa: a imagem tem {im.width}px de largura e foi ampliada para {W}px")
    escala = max(W / im.width, H / im.height)
    im = im.resize((max(W, round(im.width * escala)), max(H, round(im.height * escala))), Image.LANCZOS)
    x, y = round((im.width - W) * foco[0]), round((im.height - H) * foco[1])
    im = im.crop((x, y, x + W, y + H))
    pasta.mkdir(parents=True, exist_ok=True)
    pronto = fonte.resolve() == jpg.resolve() and fonte.stat().st_size < LIMITE_OG and tamanho(fonte) == (W, H)
    if not pronto:
        for q in (86, 82, 78, 74, 70, 65, 60):
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
            if buf.tell() < LIMITE_OG:
                break
        jpg.write_bytes(buf.getvalue())
    im.save(webp, "WEBP", quality=80, method=6)
    tem_avif = bool(features.check("avif"))
    if tem_avif:
        im.save(avif, "AVIF", quality=60)
    else:
        r.aviso("capa: este Pillow não grava AVIF; o post sai só com WebP e JPG")
        if avif.exists():
            avif.unlink()
    print(f"  + capa em {rel(pasta)}/ (jpg {jpg.stat().st_size // 1024} KB, webp {webp.stat().st_size // 1024} KB"
          + (f", avif {avif.stat().st_size // 1024} KB" if tem_avif else "") + f") a partir de {rel(fonte)}")
    return tem_avif


# ------------------------------------------------------------------ validação

def le_json(arquivo, r):
    def sem_repetir(pares):
        visto = {}
        for k, v in pares:
            if k in visto:
                r.erro(f"chave repetida no JSON: {k!r}")
            visto[k] = v
        return visto
    try:
        if arquivo.stat().st_size > 1_000_000:
            r.erro("o arquivo passa de 1 MB")
            return None
        return json.loads(arquivo.read_text(encoding="utf-8"), object_pairs_hook=sem_repetir)
    except UnicodeDecodeError:
        r.erro("o arquivo não está em UTF-8")
    except json.JSONDecodeError as e:
        r.erro(f"JSON inválido (linha {e.lineno}, coluna {e.colno}): {e.msg}")
    except OSError as e:
        r.erro(f"não consegui ler o arquivo: {e}")
    return None


def texto(d, campo, r, minimo, maximo):
    if campo not in d:  # a falta já foi apontada
        return None
    v = d[campo]
    if not isinstance(v, str):
        r.erro(f"{campo}: precisa ser texto")
        return None
    v = limpa(v, True, campo, r)
    if re.search(r"[<>]", v):
        r.erro(f"{campo}: não pode ter < ou > (é texto simples, sem HTML)")
    if not minimo <= len(v) <= maximo:
        r.erro(f"{campo}: precisa ter de {minimo} a {maximo} caracteres (tem {len(v)})")
    return v


def lista_de_textos(d, campo, r, minimo, maximo, tam_min, tam_max):
    if campo not in d:  # a falta já foi apontada
        return []
    v = d[campo]
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        r.erro(f"{campo}: precisa ser uma lista de textos")
        return []
    out, vistos = [], set()
    for x in v:
        x = limpa(x, True, campo, r).lstrip("#").strip()
        if re.search(r"[<>]", x):
            r.erro(f"{campo}: {x!r} não pode ter < ou >")
        elif not tam_min <= len(x) <= tam_max:
            r.erro(f"{campo}: {x!r} precisa ter de {tam_min} a {tam_max} caracteres")
        elif norm(x) not in vistos:
            vistos.add(norm(x))
            out.append(x)
    if not minimo <= len(out) <= maximo:
        r.erro(f"{campo}: precisa ter de {minimo} a {maximo} itens (tem {len(out)})")
    return out


def autores_cadastrados():
    return json.loads((AQUI / "autores.json").read_text(encoding="utf-8"))["autores"]


def autor_do_post(nome):
    """(author do JSON-LD, nome exibido, link da página do autor ou None), ou None se desconhecido."""
    n = norm(nome)
    if n in NOMES_DA_ORGANIZACAO:
        return dict(ORGANIZACAO), "Equipe LIBRAS.SE", None
    for a in autores_cadastrados():
        if norm(a["nome"]) == n:
            url = f"{SITE}/{a['pasta']}/{a['slug']}/"
            return {"@type": "Person", "@id": url + "#person", "name": a["nome"], "url": url}, a["nome"], f"/{a['pasta']}/{a['slug']}/"
    return None


def valida(arquivo, glossario):
    """Lê, valida e converte um JSON de entrada. Devolve (entrada pronta ou None, Relatorio)."""
    r = Relatorio(arquivo)
    d = le_json(arquivo, r)
    if d is None or r.erros:
        return None, r
    if not isinstance(d, dict):
        r.erro("o JSON precisa ser um objeto { ... }")
        return None, r
    for k in sorted(set(d) - CAMPOS):
        r.aviso(f"campo desconhecido ignorado: {k!r}")
    for k in sorted(CAMPOS - set(d)):
        r.erro(f"falta o campo {k!r}")
    # segue validando o resto, para apontar todos os problemas de uma vez

    e = {}
    if "versao" in d and (d["versao"] != 1 or isinstance(d["versao"], bool)):
        r.erro(f"versao: só a versão 1 do formato é aceita (veio {d['versao']!r})")
    if "tipo" in d and d["tipo"] != "post_simples":
        r.erro(f"tipo: só \"post_simples\" é aceito (veio {d['tipo']!r})")

    slug = d.get("slug")
    if "slug" in d and (not isinstance(slug, str) or not SLUG_RE.match(slug) or not 3 <= len(slug) <= 90):
        r.erro(f"slug: use só letras minúsculas sem acento, números e hífens, de 3 a 90 caracteres (veio {slug!r})")
        slug = None
    elif slug and arquivo.stem != slug:
        r.aviso(f"o arquivo se chama {arquivo.name}, mas o slug é {slug!r}")
    e["slug"] = slug

    e["titulo"] = texto(d, "titulo", r, 5, 140)
    e["subtitulo"] = texto(d, "subtitulo", r, 10, 400)
    e["descricao"] = texto(d, "descricao", r, 70, 165)
    if e["descricao"] and 70 <= len(e["descricao"]) <= 165 and not 120 <= len(e["descricao"]) <= 160:
        r.aviso(f"descricao: o ideal é de 120 a 160 caracteres (tem {len(e['descricao'])})")
    e["palavras_chave"] = lista_de_textos(d, "palavras_chave", r, 1, 15, 2, 80)
    e["tags"] = [t.lower() for t in lista_de_textos(d, "tags", r, 1, 10, 2, 40)]
    if e["tags"] and not 3 <= len(e["tags"]) <= 6:
        r.aviso(f"tags: o blog usa de 3 a 6 tags (vieram {len(e['tags'])})")
    if "editoria" in d and d["editoria"] not in EDITORIAS:
        r.erro(f"editoria: precisa ser uma de {', '.join(EDITORIAS)} (veio {d['editoria']!r})")
    e["editoria"] = d.get("editoria")

    autor = texto(d, "autor", r, 2, 80)
    e["autor"] = autor_do_post(autor) if autor else None
    if autor and not e["autor"]:
        nomes = ", ".join(a["nome"] for a in autores_cadastrados())
        r.erro(f"autor: {autor!r} não é a LIBRAS.SE nem um autor de tools/blog/autores.json ({nomes}); "
               "use \"Libras.se\" ou cadastre a pessoa antes (o blog não cria página de autor sozinho)")

    pub = d.get("publicado_em")
    try:
        pub = date.fromisoformat(pub) if isinstance(pub, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", pub) else None
    except ValueError:
        pub = None
    if "publicado_em" in d and not pub:
        r.erro(f"publicado_em: use uma data no formato AAAA-MM-DD (veio {d['publicado_em']!r})")
    elif pub and pub > hoje_sp() + timedelta(days=1):
        r.erro(f"publicado_em: {pub.isoformat()} está no futuro; o site é estático e o post iria ao ar já com essa data")
    e["publicado_em"] = pub

    e["fontes"] = []
    fontes = d.get("fontes")
    if "fontes" in d and not isinstance(fontes, list):
        r.erro("fontes: precisa ser uma lista (pode ser vazia)")
    elif "fontes" in d:
        if not fontes:
            r.aviso("fontes: nenhuma fonte; o bloco Créditos e referências fica só com o crédito da imagem")
        if len(fontes) > 30:
            r.erro(f"fontes: no máximo 30 (vieram {len(fontes)})")
        vistas = set()
        for i, f in enumerate(fontes[:30], 1):
            if not isinstance(f, dict) or not isinstance(f.get("url"), str) or not isinstance(f.get("titulo"), str):
                r.erro(f"fontes[{i}]: precisa ser um objeto com url e titulo (textos)")
                continue
            for k in sorted(set(f) - {"url", "titulo"}):
                r.aviso(f"fontes[{i}]: campo desconhecido ignorado: {k!r}")
            tipo, url = confere_link(f["url"])
            if not tipo:
                r.erro(f"fontes[{i}].url: {f['url']!r} não serve ({url}); use um endereço http(s)://")
                continue
            if tipo == "externo" and url != f["url"].strip():
                r.aviso(f"fontes[{i}].url: http:// trocado por https://")
            tit = limpa(f["titulo"], True, f"fontes[{i}].titulo", r)
            if re.search(r"[<>]", tit) or not 2 <= len(tit) <= 300:
                r.erro(f"fontes[{i}].titulo: texto simples de 2 a 300 caracteres, sem < ou >")
                continue
            if url not in vistas:
                vistas.add(url)
                e["fontes"].append({"url": url, "titulo": tit, "interno": tipo == "interno"})

    e["capa"] = None
    capa = d.get("capa")
    if capa is not None:
        if not isinstance(capa, dict) or not all(isinstance(capa.get(k), str) for k in ("arquivo", "alt", "credito")):
            r.erro("capa: precisa ser null ou um objeto com arquivo, alt e credito (textos)")
        else:
            for k in sorted(set(capa) - {"arquivo", "alt", "credito"}):
                r.aviso(f"capa: campo desconhecido ignorado: {k!r}")
            arq = caminho_publico(capa["arquivo"].strip()) if capa["arquivo"].strip().startswith("/assets/img/") else None
            if not arq:
                r.erro(f"capa.arquivo: {capa['arquivo']!r} precisa ser uma imagem que já existe no site, em /assets/img/...")
            elif arq.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".avif"):
                r.erro("capa.arquivo: use uma imagem .jpg, .jpeg, .png, .webp ou .avif")
            else:
                try:
                    if tamanho(arq)[0] < 600:
                        r.aviso(f"capa.arquivo: a imagem tem só {tamanho(arq)[0]}px de largura")
                except Exception:
                    r.erro("capa.arquivo: não consegui abrir a imagem")
            alt = limpa(capa["alt"], True, "capa.alt", r)
            cred = limpa(capa["credito"], True, "capa.credito", r)
            if re.search(r"[<>]", alt + cred) or not 5 <= len(alt) <= 250 or not 2 <= len(cred) <= 200:
                r.erro("capa: alt (5 a 250 caracteres) e credito (2 a 200) são texto simples, sem < ou >")
            e["capa"] = {"arquivo": arq, "alt": alt, "credito": cred}

    e["cta"] = texto(d, "cta", r, 10, 300)
    if e["cta"] and PRECO_RE.search(e["cta"]):
        r.erro("cta: o blog não mostra preço (nada de R$ ou valores); os preços ficam na home do site e no Huet")

    o = d.get("origem")
    if "origem" in d and not isinstance(o, dict):
        r.erro("origem: precisa ser um objeto com sistema, aprovacao, artefato e versao")
    elif "origem" in d:
        for k in ("aprovacao", "artefato"):
            v = o.get(k)
            if not isinstance(v, str) or not ID_RE.match(v) or "--" in v:
                r.erro(f"origem.{k}: precisa ser um identificador (letras, números, ponto, dois-pontos e hífen; ex.: um UUID)")
        v = o.get("versao")
        if not isinstance(v, int) or isinstance(v, bool) or v < 1:
            r.erro("origem.versao: precisa ser um número inteiro a partir de 1")
        if not isinstance(o.get("sistema"), str) or not o.get("sistema").strip():
            r.erro("origem.sistema: precisa ser texto (ex.: \"agentes.libras.se\")")
    e["origem"] = o

    md = d.get("markdown")
    if "markdown" not in d:
        pass
    elif not isinstance(md, str) or not md.strip():
        r.erro("markdown: precisa ser um texto não vazio")
    elif len(md) > 60_000:
        r.erro(f"markdown: passa de 60 mil caracteres ({len(md)})")
    elif slug and e["titulo"]:
        corpo, palavras, blocos, linkados = renderiza(limpa(md, False, "markdown", r), slug, e["titulo"], glossario, r)
        if palavras < 150 or blocos < 3:
            r.erro(f"markdown: texto curto demais para um post ({palavras} palavras em {blocos} blocos; o mínimo é 150 "
                   "palavras em 3 blocos, para o banner do serviço caber entre dois parágrafos)")
        e.update(corpo=corpo, palavras=palavras, linkados=linkados)

    if r.erros:
        return None, r

    # o slug já existe?
    e["reexecucao"], e["publicado_iso"] = False, None
    pasta = RAIZ / "blog" / slug
    origem = (o["aprovacao"], o["artefato"], str(o["versao"]))
    if (pasta / "index.html").exists():
        atual = (pasta / "index.html").read_text(encoding="utf-8")
        m = CARIMBO_RE.search(atual)
        if m and m.groups() == origem:
            e["reexecucao"] = True
            r.aviso(f"blog/{slug}/ já foi gerado a partir deste mesmo JSON (mesma aprovação, artefato e versão): re-execução")
            bp = next((x for x in schemas(atual) if x.get("@type") == "BlogPosting"), None)
            if bp and isinstance(bp.get("datePublished"), str) and dia_sp(bp["datePublished"]) == pub:
                e["publicado_iso"] = bp["datePublished"]
        elif m:
            r.erro(f"slug: blog/{slug}/ já existe e foi gerado de outra aprovação ou versão (carimbo do post: aprovacao={m.group(1)}, "
                   f"artefato={m.group(2)}, versao={m.group(3)}); use outro slug ou apague o post antigo antes")
        else:
            r.erro(f"slug: já existe um post em blog/{slug}/ (publicado fora do Agent Control); use outro slug")
    elif pasta.exists():
        r.erro(f"slug: a pasta blog/{slug}/ já existe e não é um post; use outro slug")
    redirs = RAIZ / "tools/seo/redirects.json"
    if redirs.exists() and f"/blog/{slug}/" in json.loads(redirs.read_text(encoding="utf-8")).get("redirects", {}):
        r.erro(f"slug: /blog/{slug}/ é um endereço antigo que redireciona (tools/seo/redirects.json); use outro slug")
    return (None if r.erros else e), r


def schemas(src):
    out = []
    for m in re.finditer(r'<script type="application/ld\+json">([\s\S]*?)</script>', src):
        try:
            o = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        out += [n for n in (o.get("@graph", [o]) if isinstance(o, dict) else o) if isinstance(n, dict)]
    return out


# ------------------------------------------------------------------ montagem

def ld_script(obj):
    # "<" e ">" escapados: nenhum texto consegue fechar o <script> antes da hora
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=2).replace("<", "\\u003c").replace(">", "\\u003e")
            + "\n</script>")


def legenda(credito, rotulo):
    c = credito.rstrip(".")
    if not re.match(r"(?i)(fotos?|imagens?|ilustra[cç][aã]o|reprodu[cç][aã]o|cr[eé]dito|arte|frame)\b", c):
        c = f"{rotulo}: {c}"
    return c + "."


def dominio(url):
    h = (urlsplit(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def monta(e, glossario, molde, r):
    slug = e["slug"]
    url = f"{SITE}/blog/{slug}/"
    base_img = f"/assets/img/blog/{slug}/{slug}"

    if e["capa"]:
        fonte, alt, credito, rotulo, foco = e["capa"]["arquivo"], e["capa"]["alt"], e["capa"]["credito"], "Imagem", (0.5, 0.5)
    else:
        foto = escolhe_do_banco(slug, e["titulo"], e["tags"], e["palavras_chave"])
        if not foto:
            falha("capa: veio null e o banco editorial não tem imagem disponível", 1)
        fonte = maior_versao(RAIZ / foto["arquivo"].lstrip("/"))
        alt, credito, rotulo, foco = acentua_alt(foto["alt"]).rstrip("."), "Banco editorial LIBRAS.SE", "Foto", (0.5, 0.4)
        print(f"  + capa do banco editorial: {foto['arquivo']}")
    tem_avif = gera_capa(fonte, slug, foco, e["reexecucao"], r)

    # datas: hoje = agora; outro dia = meio-dia em São Paulo; re-execução = a data já gravada no post
    pub = e["publicado_em"]
    if e["publicado_iso"]:
        publicado = e["publicado_iso"]
    elif pub == hoje_sp():
        publicado = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:00.000Z")
    else:
        publicado = f"{pub.isoformat()}T15:00:00.000Z"
    if dia_sp(publicado) != pub:
        publicado = f"{pub.isoformat()}T15:00:00.000Z"

    autor_ld, autor_nome, autor_link = e["autor"]
    autor_html = f"<strong>{esc(autor_nome, False)}</strong>"
    if autor_link:
        autor_html = f'<a href="{autor_link}">{autor_html}</a>'
    leitura = max(1, math.ceil(e["palavras"] / 220))

    img_url = f"{SITE}{base_img}.jpg"
    rotulo_editoria = json.loads(HOME_JSON.read_text(encoding="utf-8"))["temas"][e["editoria"]]["rotulo"]
    blog_posting = {
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": e["titulo"], "description": e["descricao"],
        "image": {"@type": "ImageObject", "url": img_url, "width": W, "height": H},
        "author": autor_ld, "publisher": PUBLISHER,
        "datePublished": publicado, "dateModified": publicado, "inLanguage": "pt-BR",
        "articleSection": rotulo_editoria, "keywords": e["palavras_chave"],
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    trilha = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
        {"@type": "ListItem", "position": 3, "name": e["titulo"], "item": url}]}

    figura = ('<figure class="pa-fig"><picture>'
              + (f'<source srcset="{base_img}.avif" type="image/avif">' if tem_avif else "")
              + f'<source srcset="{base_img}.webp" type="image/webp">'
              f'<img src="{base_img}.jpg" alt="{esc(alt)}" width="{W}" height="{H}" fetchpriority="high" decoding="async">'
              f"</picture><figcaption>{esc(legenda(credito, rotulo), False)}</figcaption></figure>")

    refs = []
    for f in e["fontes"]:
        alvo = "" if f["interno"] else ' target="_blank" rel="noopener noreferrer"'
        refs.append(f'        <li>{esc("LIBRAS.SE" if f["interno"] else dominio(f["url"]), False)}. '
                    f'“<a href="{esc(f["url"])}"{alvo}>{esc(f["titulo"], False)}</a>”.</li>')
    refs.append(f"        <li>Imagem de capa: {esc(credito.rstrip('.'), False)}.</li>")
    quem = autor_nome if autor_link else "Equipe LIBRAS.SE"
    credito_texto = f"Texto: {quem}, com informações das fontes listadas abaixo." if e["fontes"] else f"Texto: {quem}."

    tags = []
    for t in e["tags"]:
        s = glossario.da_tag(t)
        tags.append(f'<a class="pa-tag" href="/glossario/{s}/">#{esc(t, False)}</a>' if s else f'<span class="pa-tag">#{esc(t, False)}</span>')

    chaves, vistas = [], set()
    for k in e["palavras_chave"] + e["tags"] + ["blog LIBRAS.SE"]:
        if norm(k) not in vistas:
            vistas.add(norm(k))
            chaves.append(k)
    titulo_seo = f"{e['titulo']} | LIBRAS.SE" if len(e["titulo"]) + 12 <= 60 else e["titulo"]
    if len(titulo_seo) > 65:
        r.aviso(f"titulo: o <title> fica com {len(titulo_seo)} caracteres (a auditoria aponta acima de 65)")

    o = e["origem"]
    valores = {
        "ORIGEM": CARIMBO.format(o["aprovacao"], o["artefato"], o["versao"]),
        "TITLE": esc(titulo_seo, False), "DESCRICAO": esc(e["descricao"]), "KEYWORDS": esc(", ".join(chaves)), "URL": url,
        "TITULO_ATTR": esc(e["titulo"]), "IMAGEM": img_url, "IMAGEM_ALT": esc(alt), "PUBLICADO": publicado,
        "JSONLD": ld_script(blog_posting) + "\n" + ld_script(trilha),
        "TITULO": esc(e["titulo"], False), "SUBTITULO": esc(e["subtitulo"], False), "AUTOR_HTML": autor_html,
        "DATA_ISO": pub.isoformat(), "DATA_TXT": data_txt(pub), "LEITURA": str(leitura), "FIGURA": figura, "CORPO": e["corpo"],
        "CREDITO_TEXTO": esc(credito_texto, False), "REFERENCIAS": "\n".join(refs), "TAGS": "".join(tags), "CTA": esc(e["cta"], False),
    }
    # uma passada só: o que entra no molde nunca é lido de novo como placeholder
    pagina = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: valores[m.group(1)], molde)
    destino = RAIZ / "blog" / slug / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(pagina, encoding="utf-8")
    print(f"  + {rel(destino)} ({e['palavras']} palavras, {leitura} min; glossário: {', '.join(e['linkados']) or 'nenhum termo'})")

    cfg = json.loads(HOME_JSON.read_text(encoding="utf-8"))
    if cfg["classificacao"].get(slug) != e["editoria"]:
        cfg["classificacao"][slug] = e["editoria"]
        HOME_JSON.write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"  + tools/blog/home.json: {slug} na editoria {e['editoria']}")
    return {"slug": slug, "titulo": e["titulo"], "url": url, "pagina": destino}


def le_molde():
    molde = MOLDE.read_text(encoding="utf-8")
    faltam = {"ORIGEM", "TITLE", "DESCRICAO", "KEYWORDS", "URL", "TITULO_ATTR", "IMAGEM", "IMAGEM_ALT", "PUBLICADO", "JSONLD", "TITULO",
              "SUBTITULO", "AUTOR_HTML", "DATA_ISO", "DATA_TXT", "LEITURA", "FIGURA", "CORPO", "CREDITO_TEXTO", "REFERENCIAS", "TAGS",
              "CTA"} - set(re.findall(r"\{\{([A-Z_]+)\}\}", molde))
    if faltam:
        falha(f"o molde {rel(MOLDE)} está sem os placeholders {sorted(faltam)}")
    return molde


def confere_molde(molde):
    """Avisa se o cabeçalho ou o rodapé do molde ficaram diferentes dos do post de referência:
    sinal de que o site mudou (menu, rodapé) e o molde precisa ser atualizado."""
    if not REFERENCIA.exists():
        return

    def partes(t):
        try:
            return t[t.index("<body>"):t.index('<main id="main-content">')], t[t.index('<footer id="foot"'):]
        except ValueError:
            return None
    pm, pr = partes(molde), partes(REFERENCIA.read_text(encoding="utf-8"))
    if pm and pr and pm != pr:
        qual = " e o ".join(n for n, a, b in (("cabeçalho", pm[0], pr[0]), ("rodapé", pm[1], pr[1])) if a != b)
        msg = (f"o {qual} do molde {rel(MOLDE)} está diferente do post de referência {rel(REFERENCIA)}; "
               "se o site mudou, atualize o molde")
        print(f"aviso {msg}")
        anota("warning", rel(MOLDE), msg)


# ------------------------------------------------------------------ geradores e conferência

GERADORES = [
    ("tools/seo/og.py", []),
    ("tools/blog/home.py", []),
    ("tools/blog/autores.py", []),
    ("tools/seo/videos.py", ["--offline"]),
    ("tools/seo/links.py", []),
    ("tools/seo/llms.py", []),
]


def roda_geradores(posts):
    """A sequência do blog/CLAUDE.md §8 que se aplica a post novo (redirects.py não: o post não
    muda redirecionamento; videos.py só se houver vídeo)."""
    tem_video = any(re.search(r"<video\b|yt-lite", p["pagina"].read_text(encoding="utf-8")) for p in posts)
    for script, args in GERADORES:
        if script.endswith("videos.py") and not tem_video:
            print(f"\n== {script}: não se aplica (o post não tem vídeo)")
            continue
        print(f"\n== {' '.join([script] + args)}", flush=True)
        res = subprocess.run([sys.executable, str(RAIZ / script)] + args, cwd=RAIZ)
        if res.returncode != 0:
            falha(f"o gerador {script} falhou (código {res.returncode}); veja a saída acima")
    print("\n== tools/seo/auditoria.py", flush=True)
    res = subprocess.run([sys.executable, str(RAIZ / "tools/seo/auditoria.py")], cwd=RAIZ, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout + res.stderr)
        falha("a auditoria (tools/seo/auditoria.py) falhou")
    paginas = {p["url"]: p for p in json.loads((RAIZ / "tools/seo/auditoria.json").read_text(encoding="utf-8"))["paginas"]}
    avisos = []
    for p in posts:
        probs = paginas.get(f"/blog/{p['slug']}/", {}).get("problemas", [])
        for x in probs:
            print(f"aviso auditoria /blog/{p['slug']}/: {x}")
            anota("warning", f"blog/{p['slug']}/index.html", f"auditoria: {x}")
            avisos.append(f"auditoria /blog/{p['slug']}/: {x}")
        if not probs:
            print(f"ok  auditoria sem problemas em /blog/{p['slug']}/")
    return avisos


def confere(posts, com_geradores):
    """O post entrou em tudo o que o site espera? Devolve os avisos; falha se faltar o essencial."""
    falhas, avisos = [], []
    home = (RAIZ / "blog/index.html").read_text(encoding="utf-8")
    sitemap = (RAIZ / "sitemap.xml").read_text(encoding="utf-8")
    for p in posts:
        t = p["pagina"].read_text(encoding="utf-8")
        s = p["slug"]
        if not CARIMBO_RE.search(t):
            falhas.append(f"blog/{s}/: sem o carimbo agentes:origem")
        og = re.search(r'<meta property="og:image" content="([^"]+)"', t)
        if not og or not (RAIZ / unquote(og.group(1).replace(SITE + "/", "", 1))).is_file():
            falhas.append(f"blog/{s}/: a og:image não existe")
        if not com_geradores:
            continue
        if "<!-- LSE:MAIS" not in t:
            falhas.append(f"blog/{s}/: o links.py não pôs o 'Continue lendo' (LSE:MAIS)")
        if "<!-- LSE:BANNER" not in t:
            avisos.append(f"blog/{s}/: o links.py não achou lugar para o banner do serviço (LSE:BANNER)")
        if f'href="/blog/{s}/"' not in home:
            falhas.append(f"blog/index.html: sem o card de {s}")
        if f"<loc>{SITE}/blog/{s}/</loc>" not in sitemap:
            falhas.append(f"sitemap.xml: sem {SITE}/blog/{s}/")
    for a in avisos:
        print(f"aviso {a}")
        anota("warning", "tools/blog/novo_post.py", a)
    if falhas:
        for f in falhas[:-1]:
            print(f"ERRO  {f}", file=sys.stderr)
            anota("error", "tools/blog/novo_post.py", f)
        falha(falhas[-1])
    return avisos


# ------------------------------------------------------------------ principal

def saida_action(posts, avisos):
    """Saídas do passo (slugs, titulo, urls) e resumo do run, quando roda no GitHub Actions."""
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write(f"slugs={' '.join(p['slug'] for p in posts)}\n")
            fh.write(f"titulo={'; '.join(p['titulo'] for p in posts)}\n")
            fh.write(f"urls={' '.join(p['url'] for p in posts)}\n")
    if os.environ.get("GITHUB_STEP_SUMMARY") and posts:
        linhas = ["### Post montado pelo tools/blog/novo_post.py", ""]
        linhas += [f"- {p['titulo']}: {p['url']} (`blog/{p['slug']}/index.html`)" for p in posts]
        if avisos:
            linhas += ["", "Avisos:", ""] + [f"- {a}" for a in avisos]
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write("\n".join(linhas) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Monta posts do blog a partir de blog/_entrada/*.json (Agent Control).")
    ap.add_argument("arquivos", nargs="*", type=Path, help="JSON de entrada (padrão: todos os blog/_entrada/*.json)")
    ap.add_argument("--validar", action="store_true", help="só valida; não escreve nada")
    ap.add_argument("--sem-geradores", action="store_true", help="não roda os geradores do §8 depois de montar o post")
    ap.add_argument("--manter-entrada", action="store_true", help="não apaga o JSON de blog/_entrada/ no fim")
    args = ap.parse_args(argv)

    arquivos = [a.resolve() for a in args.arquivos] or sorted(ENTRADA.glob("*.json"))
    if not arquivos:
        print("nada a publicar: blog/_entrada/ não tem JSON")
        saida_action([], [])
        return 0

    glossario = Glossario()
    entradas, relatorios = [], []
    for a in arquivos:
        print(f"-> {rel(a)}")
        r = Relatorio(a)
        if a.is_file():
            e, r = valida(a, glossario)
        else:
            r.erro("arquivo não encontrado")
            e = None
        r.imprime()
        relatorios.append(r)
        if e:
            entradas.append((a, e, r))
    slugs = [e["slug"] for _, e, _ in entradas]
    for s in sorted({s for s in slugs if slugs.count(s) > 1}):
        falha(f"o slug {s!r} aparece em mais de um JSON de entrada", 1)
    if any(r.erros for r in relatorios):
        print(f"\nentrada inválida: nada foi escrito ({sum(len(r.erros) for r in relatorios)} erro(s))", file=sys.stderr)
        return 1
    if args.validar:
        print(f"ok  {len(entradas)} entrada(s) válida(s); nada foi escrito (--validar)")
        return 0

    molde = le_molde()
    confere_molde(molde)
    posts = []
    for a, e, r in entradas:
        print(f"\n== montando blog/{e['slug']}/", flush=True)
        posts.append(monta(e, glossario, molde, r))
        r.imprime()

    extras = []
    if not args.sem_geradores:
        extras += roda_geradores(posts)
    extras += confere(posts, not args.sem_geradores)

    if not args.manter_entrada:
        for a, _, _ in entradas:
            try:
                a.relative_to(ENTRADA.resolve())
            except ValueError:
                continue
            a.unlink()
            print(f"  - {rel(a)} apagado")
    saida_action(posts, [f"{rel(r.arquivo)}: {m}" for r in relatorios for m in r.avisos] + extras)
    print(f"\nok  {len(posts)} post(s): " + ", ".join(p["url"] for p in posts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
