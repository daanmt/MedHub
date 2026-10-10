"""Testes da telemetria de fila FSRS (spec Part 2): pool x divida.

Valida a rotulacao canonica (telemetria_fila) e que os renderizadores nao
apresentam mais o pool como 'backlog' agregado. Roda standalone (exit != 0
em falha) e e invocado pelo auto_check (check 3, quando day_plan muda).

HERMÉTICO x VIVO (Fase 0 Lote 0 part-2c, 10/10/2026):
  - Hermético: os 3 testes. `test_header_distingue_pool_divida` monta o plano
    (`day_plan.build()`) sobre um banco SINTÉTICO -- schema canônico do `init_db`
    em diretório temporário, semeado com 2 cards novos (pool) e 2 devidos (1
    atrasado + 1 de hoje) -- com `db.DB_PATH`, `review_radar.DB_PATH` e
    `variancia.DB_PATH` apontados para ele. Os outros dois usam fixture em memória.
  - Vivo: nenhum. Um sentinela em `sqlite3.connect` recusa e registra conexão ao
    ipub.db real, e o teste exige registro vazio. O `build()` ainda lê arquivos do
    checkout (core/provas.json, ESTADO.md, snapshot da planilha), mas nenhuma
    asserção depende deles: o que se asserta é a linha FSRS, que sai só do banco.
"""
import contextlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR / "tools"))

import day_plan

# O banco do operador: o teste NÃO o lê (Lote 0 part-2c); só o sentinela o reconhece.
REAL_DB = ROOT_DIR / "ipub.db"


def _mesmo_arquivo(a, b):
    return os.path.normcase(os.path.abspath(os.fspath(a))) == os.path.normcase(os.path.abspath(os.fspath(b)))


@contextlib.contextmanager
def _sentinela_banco_real():
    """Toda conexão SQLite do bloco passa por aqui: conexão ao ipub.db real é registrada e
    RECUSADA (RuntimeError). Devolve a lista de registros para o teste exigir que fique vazia
    -- módulo com `DB_PATH` próprio que escape do redirecionamento e engula o erro num
    `try` de degradação ainda deixa rastro aqui."""
    registro = []
    original = sqlite3.connect

    def vigiado(database, *args, **kwargs):
        alvo = database
        if isinstance(alvo, str) and alvo.startswith("file:"):
            alvo = alvo[len("file:"):].split("?", 1)[0]
        if isinstance(alvo, (str, os.PathLike)) and _mesmo_arquivo(alvo, REAL_DB):
            registro.append(os.fspath(database))
            raise RuntimeError(f"VIVO proibido neste teste: conexão ao ipub.db real ({database})")
        return original(database, *args, **kwargs)

    with mock.patch.object(sqlite3, "connect", vigiado):
        yield registro


# Seed do banco sintético: o que a linha FSRS do cabeçalho tem de contar.
POOL = 2          # state 0: nunca introduzidos
ATRASADOS = 1     # state > 0, due antes de hoje
DE_HOJE = 1       # state > 0, due hoje


@contextlib.contextmanager
def _banco_sintetico(pasta):
    """Schema CANÔNICO (`tools/init_db.py`, sem copiar DDL; padrão de
    `tools/test_fuso_unico_leitores.py::banco`) em `pasta`, semeado com POOL cards
    novos e ATRASADOS + DE_HOJE devidos. Aponta para ele os três `DB_PATH` que o
    `build()` alcança: `db` (fila FSRS, volume, plano), `review_radar` (via
    `dormant_refresh.pick`, sem `try` -- sem o patch o build lia o banco real) e
    `variancia` (via `_diagnostico`, que degradaria em silêncio). Devolve o caminho."""
    import init_db
    import review_radar
    import variancia
    from app.utils import db

    caminho = str(Path(pasta) / "ipub.db")
    with mock.patch.object(init_db, "DB_PATH", caminho), \
            contextlib.redirect_stdout(io.StringIO()):
        init_db.init_db()
    agora = datetime.now()
    fmt = "%Y-%m-%d %H:%M:%S"
    revisado_em = (agora - timedelta(days=7)).strftime(fmt)
    cards = ([(0, agora.strftime(fmt))] * POOL
             + [(2, (agora - timedelta(days=2)).strftime(fmt))] * ATRASADOS
             + [(2, agora.replace(hour=12, minute=0, second=0, microsecond=0).strftime(fmt))] * DE_HOJE)
    con = sqlite3.connect(caminho)
    try:
        con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) "
                    "VALUES (1, 'Cirurgia', 'Apendicite Aguda')")
        for card_id, (state, due) in enumerate(cards, start=1):
            con.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_pergunta, verso_resposta, "
                        "quality_source) VALUES (?, 1, 'conteudo', 'P?', 'R.', 'qualitative')", (card_id,))
            con.execute("INSERT INTO fsrs_cards (card_id, state, due, stability, reps, last_review) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (card_id, state, due, 5.0 if state else 0.0, 1 if state else 0,
                         revisado_em if state else None))
        con.commit()
    finally:
        con.close()
    with mock.patch.object(db, "DB_PATH", caminho), \
            mock.patch.object(review_radar, "DB_PATH", caminho), \
            mock.patch.object(variancia, "DB_PATH", caminho):
        yield caminho


def _p_fixture():
    """p minimo suficiente para render_handoff_block (nao toca o db)."""
    return {
        "volume": {"total": 5026, "acertos": 3976, "hoje": 18,
                   "alvo_enamed": 10000, "ritmo_alvo": 82.9, "dias_ate_marco": 60},
        "fsrs": {"atrasados": 22, "hoje": 4, "backlog_novos": 425},
        "divida": {"teto_efetivo": 30, "regime_divida": False, "teto_base": 30},
        "cronograma": None,
    }


class TestTelemetriaFila(unittest.TestCase):
    def test_separa_divida_hoje_pool(self):
        """telemetria_fila mapeia atrasados->divida, backlog_novos->pool, teto."""
        t = day_plan.telemetria_fila(
            {"atrasados": 22, "hoje": 4, "backlog_novos": 425},
            {"teto_efetivo": 30, "regime_divida": False})
        self.assertEqual(t["divida"], 22)
        self.assertEqual(t["hoje"], 4)
        self.assertEqual(t["pool"], 425)
        self.assertEqual(t["teto"], 30)
        self.assertFalse(t["regime_divida"])

    def test_handoff_block_sem_backlog_agregado(self):
        """O bloco do handoff separa pool e divida, sem o termo 'backlog'."""
        bloco = day_plan.render_handoff_block(_p_fixture()).lower()
        self.assertIn("pool", bloco)
        self.assertIn("divida", bloco)
        self.assertIn("425", bloco)   # pool
        self.assertIn("22", bloco)    # divida
        self.assertNotIn("backlog", bloco)

    def test_header_distingue_pool_divida(self):
        """O cabecalho do plano distingue pool x divida (build sobre banco SINTÉTICO, part-2c)."""
        from app.utils import db
        with tempfile.TemporaryDirectory(prefix="dp_telemetria_", ignore_cleanup_errors=True) as pasta, \
                _banco_sintetico(pasta) as caminho, \
                _sentinela_banco_real() as conexoes_no_real:
            self.assertEqual(db.DB_PATH, caminho, "db.DB_PATH tem de apontar para o banco sintético")
            self.assertFalse(_mesmo_arquivo(db.DB_PATH, REAL_DB))
            header = day_plan.render(day_plan.build()).lower()
        self.assertEqual(conexoes_no_real, [], "build() conectou no ipub.db real")
        # os números do SEED, não os do operador: prova que a linha saiu do banco sintético
        self.assertIn(f"dívida {ATRASADOS} atrasados + {DE_HOJE} p/ hoje", header)
        self.assertIn(f"pool {POOL} nunca introduzidos", header)
        self.assertIn("pool", header)
        self.assertIn("nunca introduzidos", header)
        # o antigo rotulo enganoso 'novos (backlog)' nao pode reaparecer
        self.assertNotIn("(backlog)", header)


if __name__ == "__main__":
    unittest.main()
