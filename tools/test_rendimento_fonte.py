"""F37: o ranking de cobertura era guiado por `taxonomia_cronograma.questoes_realizadas`,
um campo inflado 5,4x -- e a prioridade de "qual resumo escrever" saia dele.

Escrito ANTES do fix (AGENTE.md 10.6).

🔴 MEDIDO em 18/09/2026: o campo soma **39.772** contra **7.326** reais em `sessoes_bulk`
(era 3,7x na s127, 5,9x na s159, 5,4x hoje). A causa-raiz foi corrigida na s159 -- o
writer parou de incrementar -- mas o **dado historico** ficou, e `get_taxonomia_rendimento`
derivava `erros = questoes_realizadas - questoes_acertadas` desse numero. O consumidor e
`tools/cobertura_conhecimento.py`, que ordena por rendimento para dizer qual PDF orfao
virar resumo primeiro. Distorcao medida:

    [bulk] Neurologia           erros pelo campo 149   erros REAIS   1
    [bulk] Pediatria                            135                 3
    [bulk] Preventiva                           128                 2
    Trauma - Avaliacao Inicial                  108                 1
    [bulk] Simulado                             270                 0

🔴 POR QUE O REMEDIO NAO E "REPARAR A COLUNA". O ledger propunha recomputar a partir de
`sessoes_bulk`. Nao e executavel: `sessoes_bulk` tem **area, nao tema**, e a coluna e
por `(area, tema)` -- o SSOT nao carrega a dimensao que ela precisa. (A part-6, na mesma
sessao, criou `sessoes_bulk.tarefa_id`, que um dia da essa ponte; hoje o backfill casa
1 de 126 sessoes.) O que existe, correto e per-tema, e a contagem de `questoes_erros`.
Entao o remedio e trocar a FONTE do consumidor, nao consertar o numero: opcao (b) do
ledger -- computar on-the-fly -- aplicada ao leitor em vez da coluna.

A coluna fica: e dado historico, e o que fazer com ele segue sendo decisao do operador.
O que muda e que ela para de dirigir decisao de estudo.
"""

import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.utils import db  # noqa: E402

_DDL = """
CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT,
  questoes_realizadas INTEGER DEFAULT 0, questoes_acertadas INTEGER DEFAULT 0);
CREATE TABLE questoes_erros (id INTEGER PRIMARY KEY AUTOINCREMENT, tema_id INTEGER);
"""


@pytest.fixture()
def conn(tmp_path, monkeypatch):
    caminho = str(tmp_path / "t.db")
    con = sqlite3.connect(caminho)
    con.executescript(_DDL)
    # tema 1: campo diz 149 erros, a realidade e 1 (o caso [bulk] Neurologia)
    con.execute("INSERT INTO taxonomia_cronograma VALUES (1,'Neuro','Cefaleias',667,518)")
    # tema 2: campo diz 5 erros, a realidade e 12 (subnotificado)
    con.execute("INSERT INTO taxonomia_cronograma VALUES (2,'Neuro','AVC',20,15)")
    # tema 3: sem erro nenhum
    con.execute("INSERT INTO taxonomia_cronograma VALUES (3,'Neuro','Epilepsia',0,0)")
    con.execute("INSERT INTO questoes_erros (tema_id) VALUES (1)")
    for _ in range(12):
        con.execute("INSERT INTO questoes_erros (tema_id) VALUES (2)")
    con.commit()
    con.close()
    monkeypatch.setattr(db, "DB_PATH", caminho)
    return caminho


def _por_tema(rows):
    return {r["tema"]: r for r in rows}


# ---- o caso literal do F37 --------------------------------------------------

def test_erros_vem_de_questoes_erros_nao_do_campo_inflado(conn):
    r = _por_tema(db.get_taxonomia_rendimento())
    assert r["Cefaleias"]["erros"] == 1, (
        f"F37: erros vieram do campo inflado (149) em vez da contagem real "
        f"(1) -- {r['Cefaleias']}")


def test_tema_subnotificado_pelo_campo_aparece_com_o_numero_real(conn):
    """A distorcao tem os dois sentidos: o campo tambem SUBESTIMA."""
    r = _por_tema(db.get_taxonomia_rendimento())
    assert r["AVC"]["erros"] == 12


def test_ranking_por_erro_muda_de_ordem(conn):
    """E o ponto do achado: a ordem que decide qual resumo escrever primeiro."""
    ordenado = sorted(db.get_taxonomia_rendimento(), key=lambda x: -x["erros"])
    assert ordenado[0]["tema"] == "AVC", (
        f"ranking ainda liderado pelo campo inflado: {[x['tema'] for x in ordenado]}")


def test_tema_sem_erro_entra_com_zero(conn):
    r = _por_tema(db.get_taxonomia_rendimento())
    assert r["Epilepsia"]["erros"] == 0


# ---- contrato que nao pode quebrar ------------------------------------------

def test_shape_preservado_para_o_consumidor(conn):
    """`cobertura_conhecimento.py:189` consome estas chaves."""
    for r in db.get_taxonomia_rendimento():
        assert set(r) >= {"area", "tema", "volume", "erros"}, f"shape mudou: {r}"


def test_a_coluna_historica_NAO_e_tocada(conn):
    """O remedio troca a FONTE do leitor; o dado historico e decisao do operador."""
    db.get_taxonomia_rendimento()
    con = sqlite3.connect(conn)
    try:
        soma = con.execute("SELECT SUM(questoes_realizadas) FROM taxonomia_cronograma").fetchone()[0]
    finally:
        con.close()
    assert soma == 687, f"o leitor escreveu no banco: soma virou {soma}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
