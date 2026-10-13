"""Procura sinais de texto escrito por IA no texto visível de uma apresentação.

Uso: python checar_copy.py apresentacao-<produto>.html
Sai com código 1 se encontrar algo, para servir de trava antes da entrega.

Não substitui a leitura humana nem a reescrita (ver references/humanizer-ptbr.md):
ele pega o que é mecânico de achar. Trio forçado e frase de efeito em sequência
continuam sendo trabalho de quem revisa.
"""
import re
import sys
from html.parser import HTMLParser


class _Texto(HTMLParser):
    """Coleta o texto que o leitor vê, mais data-text (texto que "digita" na tela)."""

    PULAR = {"script", "style", "svg", "title"}

    def __init__(self):
        super().__init__()
        self.pilha = []
        self.trechos = []

    def handle_starttag(self, tag, attrs):
        self.pilha.append(tag)
        for nome, valor in attrs:
            if nome in ("data-text", "alt", "aria-label") and valor:
                self.trechos.append(valor)

    def handle_endtag(self, tag):
        while self.pilha and self.pilha.pop() != tag:
            pass

    def handle_data(self, data):
        if not any(t in self.PULAR for t in self.pilha) and data.strip():
            self.trechos.append(data.strip())


REGRAS = [
    ("travessão", r"[—–]| -- "),
    ("aspas curvas", r"[“”‘’]"),
    # ✓ e ✕ ficam de fora: são marcação de interface nos mockups, não enfeite.
    ("emoji decorativo", "[\U0001F300-\U0001FAFF☀-⛿✀-✒✖✙-➿]"),
    ("'não é X, é Y'", r"\bnão (?:é|são) (?:só |apenas )?[^.;:]{1,40}, (?:é|são)\b"),
    ("'não só/apenas X, mas Y'", r"\bnão (?:só|apenas|somente)\b[^.]{1,60}\bmas\b"),
    ("'X, não Y' de efeito", r", não (?:um|uma|o|a|só|apenas)\b"),
    ("fragmento 'sem X' no fim", r"\b[Ss]em (?:complicação|esforço|dor de cabeça|surpresas?|adivinhação)\b"),
    (
        "vocabulário de IA",
        r"\b(?:crucial|fundamental|essencial|potencializ\w+|alavanc\w+|impulsion\w+|"
        r"jornada|ecossistema|robust[oa]s?|sinergia|revolucion\w+|disruptiv\w+|"
        r"de ponta|inovador\w*|transformador\w*|incrível|perfeit[oa]|sem igual|"
        r"no mundo de hoje|cenário atual|desbloque\w+|elev(?:a|e|ar) (?:o|a) (?:nível|patamar))\b",
    ),
    ("anúncio/sinalização", r"\b(?:vamos explorar|vamos mergulhar|confira a seguir|saiba mais abaixo|é importante (?:notar|destacar|ressaltar))\b"),
    ("encerramento genérico", r"\b(?:o futuro é agora|o céu é o limite|leve (?:sua|seu) \w+ ao próximo nível)\b"),
]


def checar(caminho: str) -> int:
    p = _Texto()
    p.feed(open(caminho, encoding="utf-8").read())
    achados = 0
    for trecho in p.trechos:
        for nome, padrao in REGRAS:
            for m in re.finditer(padrao, trecho, flags=re.IGNORECASE):
                achados += 1
                ini = max(0, m.start() - 40)
                print(f"[{nome}] ...{trecho[ini:m.end() + 40]}...")
    if achados:
        print(f"\n{achados} sinal(is). Reescreva seguindo references/humanizer-ptbr.md e rode de novo.")
        return 1
    print("Nenhum sinal mecânico encontrado. Falta a leitura humana: trios forçados e frases de efeito em sequência.")
    return 0


if __name__ == "__main__":
    sys.exit(checar(sys.argv[1]))
