# -*- coding: utf-8 -*-
"""Aplica os acentos restaurados ao ipub.db sob invariante dura.

INVARIANTE: sem_diacriticos(novo) == sem_diacriticos(antigo).
Se falhar em qualquer campo, o registro inteiro e REJEITADO (nao aplicado).
Isso torna impossivel que o agente tenha alterado conteudo clinico.
"""
import sqlite3, json, io, os, sys, glob, unicodedata, html, argparse

SC = os.path.dirname(os.path.abspath(__file__))
DB = r"C:\Users\daanm\medhub\ipub.db"
CAMPOS = ["titulo", "enunciado", "alternativa_correta", "alternativa_marcada", "tipo_erro",
          "habilidades_sequenciais", "o_que_faltou", "explicacao_correta", "armadilha_prova"]


def desac(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if not unicodedata.combining(c))


def limpa(s):
    if s is None:
        return None
    s = html.unescape(s)                       # agentes as vezes escapam &gt;
    s = s.replace("\u2192", "->").replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    atual = {r["id"]: r for r in con.execute(
        f"select id,{','.join(CAMPOS)} from questoes_erros")}

    ok, rej, mudou = [], [], 0
    for f in sorted(glob.glob(os.path.join(SC, "acentos_out", "*.json"))):
        for rec in json.load(io.open(f, encoding="utf-8")):
            eid = int(rec["id"])
            if eid not in atual:
                rej.append((eid, "id inexistente")); continue
            novo, falhou = {}, None
            for c in CAMPOS:
                old = atual[eid][c]
                new = limpa(rec.get(c))
                if old is None and new is None:
                    continue
                if desac(new or "") != desac(old or ""):
                    falhou = c; break
                if new != old:
                    novo[c] = new
            if falhou:
                rej.append((eid, f"invariante quebrada em '{falhou}'"))
            elif novo:
                ok.append((eid, novo)); mudou += len(novo)
    print(f"registros aceitos : {len(ok)}  ({mudou} campos alterados)")
    print(f"registros rejeitados: {len(rej)}")
    for r in rej[:12]:
        print("   ", r)
    if not a.apply:
        print("\n[DRY-RUN] use --apply para gravar")
        return
    cur = con.cursor()
    for eid, campos in ok:
        sets = ", ".join(f"{c}=?" for c in campos)
        cur.execute(f"update questoes_erros set {sets} where id=?",
                    list(campos.values()) + [eid])
    con.commit()
    print(f"\nAPLICADO: {len(ok)} registros atualizados no ipub.db")


if __name__ == "__main__":
    main()
