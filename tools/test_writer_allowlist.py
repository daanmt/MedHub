"""Descolar part-2 (F49): escopo de escrita do ipub.db vira TESTE — allowlist tabela->writers.

O writer-gate era prosa (AGENTE.md) violada por 5 arquivos, com um teste homônimo que testava
OUTRA coisa. Este teste trava o PERÍMETRO REAL (verificado por varredura em 2026-09-01):
arquivo novo que escreva numa tabela fora da lista FALHA nomeando (arquivo, tabela).
Encolher o perímetro = editar a allowlist CONSCIENTEMENTE (o diff denuncia).

Padrão replicado de test_revisao_calibrada.py::test_craftsmanship_sqlite (allowlist + varredura).
Leitura com utf-8-sig (lição do BOM que escondia o F51 do ast.parse).

Sabotagem verificada (2026-09-01): arquivo sintético com `INSERT INTO flashcards` fora da
lista -> o scanner o acusa (test_scanner_detecta_writer_novo prova o mecanismo sem tocar o repo).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Par (arquivo -> tabelas em que ELE escreve), estado real medido em 2026-09-01.
# app/memory/store.py escreve em medhub_memory.db (backend separado, AGENTE §8) — está aqui
# porque o scanner vê SQL de escrita, não qual arquivo .db a conexão abre.
ALLOWLIST = {
    "app/memory/store.py": {"memory_store"},
    "app/utils/db.py": {"cronograma_progresso", "flashcards", "fsrs_cards", "fsrs_revlog",
                        "habilidades", "preparacao_estado", "questao_habilidades", "review_log"},
    "tools/backfill_review_log.py": {"review_log"},
    "tools/day_plan.py": {"plano_dia"},
    "tools/dedup_taxonomia.py": {"flashcards", "questoes_erros", "taxonomia_cronograma"},
    "tools/habilidades.py": {"habilidades", "questao_habilidades"},
    "tools/insert_card_base.py": {"flashcards", "fsrs_cards", "taxonomia_cronograma"},
    "tools/insert_card_extra.py": {"flashcards", "fsrs_cards"},
    "tools/insert_questao.py": {"cronograma_progresso", "flashcards", "fsrs_cards",
                                "questoes_erros", "taxonomia_cronograma"},
    "tools/normalize_taxonomia.py": {"flashcards", "questoes_erros", "taxonomia_cronograma"},
    "tools/recurate_cards.py": {"flashcards"},
    "tools/registrar_sessao_bulk.py": {"preparacao_estado", "sessoes_bulk",
                                       "taxonomia_cronograma"},
}

_KW = re.compile(
    r"\b(?:INSERT(?:\s+OR\s+\w+)?\s+INTO|DELETE\s+FROM)\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"|\bUPDATE\s+([A-Za-z_][A-Za-z0-9_]*)\s+SET\b", re.I)


def tabelas_escritas(texto: str) -> set:
    """Tabelas-alvo de INSERT/UPDATE/DELETE num fonte Python (regex sobre o texto — mesmo
    trade-off do padrão provado: docstring pode gerar falso-positivo raro, allowlist-ável;
    falso-negativo é o que custa)."""
    out = set()
    for m in _KW.finditer(texto):
        out.add((m.group(1) or m.group(2)).lower())
    return out


def varrer_repo() -> dict:
    achados = {}
    for base in ("tools", "app"):
        for f in (ROOT / base).rglob("*.py"):
            rel = f.relative_to(ROOT).as_posix()
            if ("_archive" in rel or "__pycache__" in rel
                    or f.name.startswith("test_")):
                continue
            tabelas = tabelas_escritas(f.read_text(encoding="utf-8-sig", errors="replace"))
            if tabelas:
                achados[rel] = tabelas
    return achados


def test_nenhum_writer_fora_da_allowlist():
    achados = varrer_repo()
    violacoes = []
    for rel, tabelas in sorted(achados.items()):
        extras = tabelas - ALLOWLIST.get(rel, set())
        if extras:
            violacoes.append(f"{rel} escreve em {sorted(extras)} FORA da allowlist")
    assert not violacoes, (
        "Escrita fora do perímetro declarado (F49). Ou o writer passa pelo caminho "
        "canônico, ou a allowlist é editada CONSCIENTEMENTE:\n  " + "\n  ".join(violacoes))


def test_allowlist_sem_entrada_morta():
    """Entrada da allowlist cujo arquivo sumiu/parou de escrever = lista mentindo — remove."""
    achados = varrer_repo()
    mortas = [rel for rel in ALLOWLIST
              if rel not in achados or not (ALLOWLIST[rel] & achados.get(rel, set()))]
    assert not mortas, f"Entradas mortas na allowlist (arquivo não escreve mais): {mortas}"


def test_scanner_detecta_writer_novo():
    """O mecanismo, provado sem tocar o repo: a sabotagem viraria exatamente isto."""
    fonte = 'def go(c):\n    c.execute("INSERT INTO flashcards (a) VALUES (?)", (1,))\n'
    assert tabelas_escritas(fonte) == {"flashcards"}
    fonte2 = 'c.execute("UPDATE taxonomia_cronograma SET x=1 WHERE id=?")'
    assert tabelas_escritas(fonte2) == {"taxonomia_cronograma"}
    fonte3 = 'c.execute("DELETE FROM questoes_erros WHERE id=?")'
    assert tabelas_escritas(fonte3) == {"questoes_erros"}
    assert tabelas_escritas("x = 1  # nada de sql") == set()


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
