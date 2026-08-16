# -*- coding: utf-8 -*-
"""Consolida os lotes de reforja, aplica acentuacao e emite o JSON do recurate_cards."""
import json, io, os, re, glob, html, unicodedata, sys

SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
MAPA = json.load(io.open(os.path.join(SC, "acentos.json"), encoding="utf-8"))
WORD = re.compile(r"[A-Za-zÀ-ÿ]+")
VERBO = [
    (re.compile(r"\b(qual|quais|o que|como|quando|onde|quem|isso|isto|este|esta|esse|essa|"
                r"aquele|aquela|ele|ela|que)\s+e\b", re.I), lambda m: m.group(1) + " é"),
    (re.compile(r"\bnao\s+e\b(?!\s+sim\b)", re.I), lambda m: "não é"),
    (re.compile(r"\be\s+(correto|incorreto|verdadeiro|falso)\s+afirmar\b", re.I),
     lambda m: "é " + m.group(1) + " afirmar"),
]
CAMPOS = ["contexto", "pergunta", "resposta", "regra", "armadilha"]


def acentua(t):
    if not t:
        return t
    t = html.unescape(t)
    t = t.replace("→", "->").replace("‘", "'").replace("’", "'")
    t = t.replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "--")

    def sub(m):
        w = m.group(0)
        r = MAPA.get(w.lower())
        if not r:
            return w
        if w.isupper() and len(w) > 1:
            return r.upper()
        if w[0].isupper():
            return r[0].upper() + r[1:]
        return r
    t = WORD.sub(sub, t)
    for rx, rep in VERBO:
        t = rx.sub(rep, t)
    return t


def main():
    itens, vistos = [], set()
    for f in sorted(glob.glob(os.path.join(SC, "reforja_out", "*.json"))):
        for c in json.load(io.open(f, encoding="utf-8")):
            cid = int(c["card_id"])
            if cid in vistos:
                continue
            vistos.add(cid)
            if c.get("aposentar"):
                itens.append({"card_id": cid, "aposentar": True}); continue
            novo = {"card_id": cid}
            if c.get("tipo"):
                novo["tipo"] = c["tipo"]
            for k in CAMPOS:
                if c.get(k) is not None:
                    novo[k] = acentua(c[k])
            itens.append(novo)
    dest = os.path.join(SC, "reforja_final.json")
    json.dump(itens, io.open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    apos = sum(1 for i in itens if i.get("aposentar"))
    print(f"cards no lote: {len(itens)}  (reforjar {len(itens)-apos}, aposentar {apos})")
    print("->", dest)


if __name__ == "__main__":
    main()
