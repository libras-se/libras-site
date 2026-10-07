"""Gera briefing.json: lista ordenada de sinais do briefing da intérprete (jun/2026)."""
import json
import re
import unicodedata
from pathlib import Path


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


BLOCOS = [
    ("jogo", "Educação", "Livro|Escola"),
    ("jogo", "Relações", "Amigo|Família"),
    ("jogo", "Cotidiano", "Comer"),
    ("jogo", "Sentimentos", "Feliz"),
    ("jogo", "Cotidiano", "Trabalho"),
    ("jogo", "Expressões", "Obrigado"),
    ("jogo", "Cultura", "Música"),
    ("jogo", "Família", "Criança"),
    ("jogo", "Sentimentos", "Sonhar"),
    ("jogo", "Cotidiano", "Janela"),
    ("desafios", "Cotidiano", "Água|Casa|Porta|Mesa|Cama|Roupa|Sapato|Carro|Ônibus|Telefone|Banheiro|Dinheiro"),
    ("desafios", "Sentimentos", "Amor|Raiva|Medo|Triste|Alegre|Calmo|Orgulho|Saudade|Ansioso|Cansado|Surpresa|Vergonha"),
    ("desafios", "Alimentos", "Arroz|Feijão|Frango|Peixe|Fruta|Banana|Queijo|Leite|Café|Sorvete|Cerveja|Suco"),
    ("desafios", "Verbos", "Falar|Ouvir|Olhar|Gostar|Ajudar|Aprender|Ensinar|Estudar|Correr|Dormir|Viajar|Morar"),
    ("desafios", "Família", "Mãe|Pai|Irmão|Irmã|Filho|Filha|Avô|Bebê|Surdo|Ouvinte|Professor|Médico"),
    ("desafios", "Animais", "Cachorro|Gato|Pássaro|Cavalo|Leão|Macaco|Cobra|Elefante|Abelha|Tartaruga|Borboleta|Pato"),
    ("desafios", "Cores", "Vermelho|Azul|Verde|Amarelo|Laranja|Roxo|Rosa|Marrom|Branco|Preto|Cinza"),
    ("desafios", "Lugares", "Praia|Cidade|Campo|Floresta|Parque|Hospital|Mercado|Teatro|Museu|Igreja|Montanha"),
    ("saudacoes", "Saudações", "Olá|Bom dia|Boa tarde|Boa noite|Tchau|Eu te amo|Por favor|Desculpa|Sim|Não|Ajuda|Parabéns|Feliz Natal|Feliz Ano Novo|Feliz aniversário|Eu|Você|Ele/Ela"),
    ("alfabeto", "Alfabeto", "|".join("ABCDEFGHIJKLMNOPQRSTUVWXYZ")),
    ("numeros", "Números", "|".join(str(i) for i in range(21))),
    ("estados", "Estados", "Acre|Alagoas|Amapá|Amazonas|Bahia|Ceará|Distrito Federal|Espírito Santo|Goiás|Maranhão|Mato Grosso|Mato Grosso do Sul|Minas Gerais|Pará|Paraíba|Paraná|Pernambuco|Piauí|Rio de Janeiro|Rio Grande do Norte|Rio Grande do Sul|Rondônia|Roraima|Santa Catarina|São Paulo|Sergipe|Tocantins"),
    ("presidentes", "Presidentes", "Lula|Dilma Rousseff|Getúlio Vargas|JK|Fernando Henrique Cardoso|Fernando Collor|Michel Temer|Jair Bolsonaro|João Goulart|José Sarney|Itamar Franco|Deodoro da Fonseca"),
    ("times", "Times", "Flamengo|Fluminense|Botafogo|Vasco|Corinthians|Palmeiras|São Paulo FC|Santos|Grêmio|Internacional|Athletico Paranaense|Avaí|Figueirense|Chapecoense|Atlético Mineiro|Cruzeiro|Bahia (time)|Fortaleza|Sport Recife|Ceará SC"),
]

items, seen = [], set()
for bloco, cat, words in BLOCOS:
    for w in words.split("|"):
        palavra = w.strip()
        slug = slugify(palavra.replace("/", " "))
        if bloco == "alfabeto":
            slug = f"letra-{slug}"
        elif bloco == "numeros":
            slug = f"numero-{slug}"
        elif bloco == "times" and slug in seen | {"bahia-time", "ceara-sc", "sao-paulo-fc"}:
            slug = {"bahia-time": "esporte-clube-bahia", "ceara-sc": "ceara-sporting-club", "sao-paulo-fc": "sao-paulo-futebol-clube"}.get(slug, slug)
        if slug in seen:
            continue
        seen.add(slug)
        items.append({"slug": slug, "palavra": palavra.replace(" (time)", ""), "categoria": cat, "bloco": bloco})

Path(__file__).with_name("briefing.json").write_text(json.dumps(items, ensure_ascii=False, indent=1))
print(len(items), "itens")
