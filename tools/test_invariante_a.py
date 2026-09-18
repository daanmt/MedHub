"""test_invariante_a.py -- o ENSINO nunca escreve FSRS (s187).

O Invariante A e uma das fronteiras duras do MedHub (`forgetting-curve-contract.md`,
`revisao-calibrada-contract.md`, `refrescar.md`): o re-ensino de tema -- refresh dormente
e Revisao Direcionada de fechamento -- **nao toca o FSRS**. Nao chama `record_review`, nao
cunha card, nao grava rating. So carimba `review_log`.

🔴 **Ele nao tinha gate, e isso foi achado pelo inventario do item 1.10 (s187), nao por
leitura.** A allowlist do F49 (`test_writer_allowlist`) cobre *escrita SQL DIRETA por
arquivo* -- ela nunca veria `dormant_refresh` chamando `db.record_review()`, porque a
escrita aconteceria dentro de `db.py`, que esta legitimamente na allowlist. Gate-miss por
**escopo de alvo**, a mesma forma do F115: o sensor existe, mede a coisa vizinha, e o
painel fica verde.

Por que importa mais que um smell: se o ensino gravasse FSRS, o agendamento passaria a
refletir *ter sido re-ensinado* em vez de *ter sido lembrado a frio*. O sinal que governa
toda a repeticao espacada viraria outro -- e ninguem notaria, porque o numero continuaria
existindo. E o mesmo modo de falha do F112, um nivel acima.

Nasce BLOCK (nao WARN) pela condicao ja usada em F79b, D5 e 1.10: **o passivo e ZERO,
medido** -- `dormant_refresh.py` usa exclusivamente `db.log_review`. Gate PROSPECTIVO.

⚠️ **ESCOPO DECLARADO, nunca maquiado.** Este gate cobre o CODIGO do caminho de ensino.
Ele **nao** cobre o agente: nada impede que, numa sessao, o agente rode
`fsrs_queue.py --record` enquanto ensina. Essa metade e comportamental e segue
nao-verificavel por gate (secao 10.8, verification-stack) -- quem a sustenta e o
Invariante A escrito nos contratos e a Clausula 11.
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# O caminho de ENSINO: quem serve refresh de tema dormente e Revisao Direcionada.
# Lista curta e explicita de proposito -- um glob varreria o repo e o gate viraria
# ruido. Modulo novo de ensino entra aqui no mesmo commit que o cria.
CAMINHO_DE_ENSINO = ["tools/dormant_refresh.py"]

# Escritores de FSRS que o ensino nao pode alcancar (verbatim do contrato).
PROIBIDOS = {"record_review", "insert_questao", "insert_card_base",
             "marcar_reforja", "update_flashcard_fields"}

TABELAS_FSRS = ("fsrs_cards", "fsrs_revlog", "flashcards")


def _chamadas(arvore):
    """Nomes chamados no modulo: `f()` e `obj.f()`, com a linha."""
    saida = []
    for n in ast.walk(arvore):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Attribute):
            saida.append((f.attr, n.lineno))
        elif isinstance(f, ast.Name):
            saida.append((f.id, n.lineno))
    return saida


def _sql_literais(arvore):
    return [(n.value, n.lineno) for n in ast.walk(arvore)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _arvore(rel):
    caminho = os.path.join(ROOT, rel)
    with open(caminho, encoding="utf-8") as fh:
        return ast.parse(fh.read()), caminho


# --- o invariante, sobre o codigo real -------------------------------------------------

def test_caminho_de_ensino_nao_chama_escritor_de_fsrs():
    achados = []
    for rel in CAMINHO_DE_ENSINO:
        arvore, _ = _arvore(rel)
        for nome, linha in _chamadas(arvore):
            if nome in PROIBIDOS:
                achados.append(f"{rel}:{linha} chama {nome}()")
    assert achados == [], (
        "Invariante A violado -- o ensino alcancou um escritor de FSRS: "
        + "; ".join(achados)
        + ". Se o re-ensino gravar FSRS, o agendamento passa a refletir 'foi re-ensinado' "
          "em vez de 'foi lembrado a frio', e o sinal que governa a repeticao espacada "
          "vira outro sem ninguem notar.")


def test_caminho_de_ensino_nao_escreve_tabela_de_fsrs_por_sql():
    """A segunda porta: SQL cru dentro do proprio modulo de ensino, que passaria
    por baixo do teste de chamadas."""
    achados = []
    for rel in CAMINHO_DE_ENSINO:
        arvore, _ = _arvore(rel)
        for txt, linha in _sql_literais(arvore):
            alto = txt.upper()
            if not any(v in alto for v in ("INSERT", "UPDATE", "DELETE")):
                continue
            if any(t in txt for t in TABELAS_FSRS):
                achados.append(f"{rel}:{linha} -> {txt[:70]}")
    assert achados == [], "SQL de escrita em tabela FSRS no ensino: " + "; ".join(achados)


def test_o_ensino_carimba_review_log_e_so():
    """O lado positivo do invariante: o refresh EXISTE para carimbar `review_log`.
    Um gate so negativo passaria verde num modulo que nao faz mais nada."""
    arvore, _ = _arvore("tools/dormant_refresh.py")
    nomes = {n for n, _ in _chamadas(arvore)}
    assert "log_review" in nomes, \
        "o refresh tem que carimbar review_log -- se parou, o Invariante B quebrou"


# --- o gate pega de verdade? (defeito plantado, nao confianca) --------------------------

def test_o_gate_pega_uma_violacao_plantada():
    """Um gate que nunca viu um positivo e um gate nao testado -- a licao da s186
    (um teste estava verde sem testar nada)."""
    fonte = ("import app.utils.db as db\n"
             "def refrescar(t):\n"
             "    db.log_review(tema_id=t)\n"
             "    db.record_review(card_id=1, rating=3)\n")
    achados = [n for n, _ in _chamadas(ast.parse(fonte)) if n in PROIBIDOS]
    assert achados == ["record_review"], achados

    sql = ("def f(c):\n"
           "    c.execute('UPDATE fsrs_cards SET due = ? WHERE card_id = ?', (1, 2))\n")
    viola = [t for t, _ in _sql_literais(ast.parse(sql))
             if "UPDATE" in t.upper() and any(x in t for x in TABELAS_FSRS)]
    assert len(viola) == 1


def test_escopo_do_gate_esta_declarado():
    """Contra o verde decorativo: a lista de modulos cobertos e curta e explicita, e
    o limite (o gate nao cobre o AGENTE, so o codigo) tem de estar escrito."""
    assert CAMINHO_DE_ENSINO, "lista vazia tornaria os testes acima verdes por vacuidade"
    for rel in CAMINHO_DE_ENSINO:
        assert os.path.exists(os.path.join(ROOT, rel)), f"{rel} nao existe mais"
    doc = sys.modules[__name__].__doc__.replace("*", "").lower()
    assert "escopo declarado" in doc and "nao cobre o agente" in doc, \
        "o limite do gate (cobre o CODIGO, nao o agente) tem de estar escrito no portador"
