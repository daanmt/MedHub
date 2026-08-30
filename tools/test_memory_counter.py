"""Testes do contador de erros das WeakAreas (consolidacao-part-3).

Asserts nativos -- coletado direto pelo pytest (allowlist em pytest.ini).

O bug corrigido: `GROUP BY area` (sem tema) + match por substring
bidirecional com `break` no primeiro hit. Efeito: todo sub-tema de uma
area herdava o MESMO total da area (ex.: 25 WeakAreas de sub-temas de
Cirurgia, todas com error_count=1250).

Contrato novo: GROUP BY (area, tema) + match EXATO do par
(WeakArea.area, WeakArea.especialidade) contra (taxonomia.area, .tema).
Sem match => 0. Multiplos matches (rotulos que normalizam para o mesmo
par) => soma.

Fixtures 100% sinteticas: rotulos e textos dummy, sem conteudo clinico.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.memory.manager import (  # noqa: E402
    _load_ipub_error_counts,
    _norm,
    _sync_error_counts,
)
from app.memory.store import SQLiteMemoryStore  # noqa: E402

_NS = ("medhub", "weak_areas")


def _make_ipub(tmpdir: str, rows: list[tuple[str, str, int, int]]) -> str:
    """Cria um ipub.db sintetico com taxonomia_cronograma + questoes_erros.

    rows: (area, tema, questoes_realizadas, questoes_acertadas)

    s159/F37: a assinatura do fixture nao mudou -- o que mudou e ONDE o erro
    passa a morar. `questoes_realizadas - questoes_acertadas` continua sendo o
    numero de erros que cada teste espera, mas agora ele e MATERIALIZADO como
    N linhas reais em `questoes_erros` com `tema_id` resolvido, porque essa
    passou a ser a fonte de `_load_ipub_error_counts`. As colunas de volume
    seguem populadas de proposito: servem de armadilha para o teste estrutural
    `test_contador_nao_le_o_campo_inflado`, que falharia se alguem voltasse a
    somar `questoes_realizadas - questoes_acertadas`.
    """
    path = os.path.join(tmpdir, "ipub_fake.db")
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE taxonomia_cronograma (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               area TEXT NOT NULL,
               tema TEXT NOT NULL,
               questoes_realizadas INTEGER DEFAULT 0,
               questoes_acertadas INTEGER DEFAULT 0
           )"""
    )
    conn.execute(
        """CREATE TABLE questoes_erros (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               tema_id INTEGER,
               data_registro TEXT
           )"""
    )
    conn.executemany(
        "INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas) VALUES (?,?,?,?)",
        rows,
    )
    for area, tema, feitas, acertos in rows:
        tema_id = conn.execute(
            "SELECT id FROM taxonomia_cronograma WHERE area=? AND tema=?", (area, tema)
        ).fetchone()[0]
        for _ in range(max(0, feitas - acertos)):
            conn.execute(
                "INSERT INTO questoes_erros (tema_id, data_registro) VALUES (?, '2026-08-30')",
                (tema_id,))
    conn.commit()
    conn.close()
    return path


def _put_weak(store: SQLiteMemoryStore, key: str, area: str, especialidade: str, error_count: int = 0) -> None:
    store.put(
        _NS,
        key,
        {
            "kind": "WeakArea",
            "content": {
                "area": area,
                "especialidade": especialidade,
                "pattern": "padrao dummy de teste",
                "error_count": error_count,
                "last_updated": "2026-08-14",
            },
        },
    )


def _counts(store: SQLiteMemoryStore) -> dict[str, int]:
    return {
        item.key: item.value["content"]["error_count"]
        for item in store.search(_NS, limit=100)
    }


def test_subtemas_da_mesma_area_recebem_counts_diferentes():
    """O coracao do bug: 2 sub-temas da MESMA area nao podem colidir."""
    with tempfile.TemporaryDirectory() as tmp:
        ipub = _make_ipub(
            tmp,
            [
                ("AreaAlfa", "TemaUm", 100, 40),    # 60 erros
                ("AreaAlfa", "TemaDois", 100, 95),  # 5 erros
            ],
        )
        store = SQLiteMemoryStore(os.path.join(tmp, "mem.db"))
        _put_weak(store, "w1", "AreaAlfa", "TemaUm")
        _put_weak(store, "w2", "AreaAlfa", "TemaDois")

        _sync_error_counts(store, ipub_path=ipub)
        got = _counts(store)

        assert got["w1"] == 60, got
        assert got["w2"] == 5, got
        assert got["w1"] != got["w2"], "sub-temas da mesma area colidiram (bug do GROUP BY area)"
        # Nenhum dos dois herdou o total da area (60 + 5 = 65)
        assert 65 not in got.values(), got


def test_sem_match_recebe_zero_e_nao_herda_total_da_area():
    """Sub-tema inexistente na taxonomia => 0, nunca o total da area."""
    with tempfile.TemporaryDirectory() as tmp:
        ipub = _make_ipub(tmp, [("AreaAlfa", "TemaUm", 100, 40)])  # 60 erros
        store = SQLiteMemoryStore(os.path.join(tmp, "mem.db"))
        # error_count=999 simula o valor corrompido ja persistido
        _put_weak(store, "orfa", "AreaAlfa", "TemaInexistente", error_count=999)

        _sync_error_counts(store, ipub_path=ipub)

        assert _counts(store)["orfa"] == 0, _counts(store)


def test_substring_nao_casa_mais():
    """'Cardio' nao pode mais casar com 'Cardiologia' (match bidirecional morto)."""
    with tempfile.TemporaryDirectory() as tmp:
        ipub = _make_ipub(tmp, [("AreaAlfa", "TemaCompleto", 100, 20)])  # 80 erros
        store = SQLiteMemoryStore(os.path.join(tmp, "mem.db"))
        _put_weak(store, "prefixo", "AreaAlfa", "TemaComp")           # substring do tema
        _put_weak(store, "superstring", "AreaAlfa", "TemaCompletoXY")  # tema e substring dela
        _put_weak(store, "area_so", "AreaAlfa", "")                    # so a area

        _sync_error_counts(store, ipub_path=ipub)
        got = _counts(store)

        assert got == {"prefixo": 0, "superstring": 0, "area_so": 0}, got


def test_multiplos_matches_somam():
    """Rotulos que normalizam para o mesmo par (acento/caixa/espaco) somam."""
    with tempfile.TemporaryDirectory() as tmp:
        ipub = _make_ipub(
            tmp,
            [
                ("AreaBeta", "Tema Unico", 50, 20),   # 30 erros
                ("AREABETA", "TEMA  UNICO", 50, 10),  # 40 erros, mesmo par normalizado
                ("AreaBetá", "Têma Único", 50, 50),   # 0 erros: nao entra (so pares com erro)
            ],
        )
        store = SQLiteMemoryStore(os.path.join(tmp, "mem.db"))
        _put_weak(store, "soma", "AreaBeta", "Tema Unico")

        _sync_error_counts(store, ipub_path=ipub)

        assert _counts(store)["soma"] == 70, _counts(store)


def test_norm_e_exato_nao_substring():
    """_norm normaliza caixa/acento/espaco, mas nao aproxima rotulos distintos."""
    assert _norm("Obstetrícia") == _norm("obstetricia")
    assert _norm("  Clínica   Médica ") == _norm("Clinica Medica")
    assert _norm("Cardio") != _norm("Cardiologia")
    assert _norm(None) == ""


def test_ipub_ausente_nao_altera_nada():
    """Sem ipub.db o sync e no-op (nao zera counts existentes)."""
    with tempfile.TemporaryDirectory() as tmp:
        store = SQLiteMemoryStore(os.path.join(tmp, "mem.db"))
        _put_weak(store, "w1", "AreaAlfa", "TemaUm", error_count=42)

        updated = _sync_error_counts(store, ipub_path=os.path.join(tmp, "nao_existe.db"))

        assert updated == 0
        assert _counts(store)["w1"] == 42


def test_registro_legado_sem_envelope_tambem_e_contado():
    """Dict plano (pre-LangMem) continua sendo atualizado."""
    with tempfile.TemporaryDirectory() as tmp:
        ipub = _make_ipub(tmp, [("AreaAlfa", "TemaUm", 100, 40)])  # 60 erros
        store = SQLiteMemoryStore(os.path.join(tmp, "mem.db"))
        store.put(_NS, "legado", {"area": "AreaAlfa", "especialidade": "TemaUm", "error_count": 0})

        _sync_error_counts(store, ipub_path=ipub)

        item = store.get(_NS, "legado")
        assert item is not None and item.value["error_count"] == 60, item.value


def test_contador_nao_le_o_campo_inflado():
    """F37 (s159): a fonte do contador e `questoes_erros`, NUNCA a subtracao de
    `taxonomia_cronograma`. O campo de volume e alimentado por sessoes bulk que
    sao atribuidas a AREA -- ate a s159 espalhadas por todos os temas dela --,
    entao usa-lo como proxy de erro por tema mede quanto a area foi estudada, e
    nao quao fraco o tema e. Teste ESTRUTURAL: falha se alguem reintroduzir o
    campo na query, mesmo que os numeros por acaso batam nas fixtures.
    """
    import inspect

    src = inspect.getsource(_load_ipub_error_counts)
    # Remove SO a docstring (que cita o campo de proposito, para explicar o
    # defeito). Split por aspas triplas nao serve: a propria query e uma string
    # tripla, entao o split comeria o SQL junto e o teste passaria vazio.
    corpo = src.replace(_load_ipub_error_counts.__doc__ or "", "")
    assert "questoes_realizadas" not in corpo,         "contador voltou a ler o campo inflado (F37)"
    assert "questoes_erros" in corpo, "contador deixou de ler a fonte atribuida"


def test_tema_sem_erro_atribuido_nao_entra_no_dict():
    """Volume alto e zero erro atribuido => o tema nao aparece. Foi exatamente o
    caso de `Ginecologia / Gravidez ectopica`, que figurava como fraqueza
    persistente com '61 erros' e tinha zero linhas em `questoes_erros`."""
    with tempfile.TemporaryDirectory() as tmp:
        ipub = _make_ipub(tmp, [("AreaAlfa", "TemaSemErro", 335, 335)])
        counts = _load_ipub_error_counts(Path(ipub))
        assert counts == {}
