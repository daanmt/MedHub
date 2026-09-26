"""F137 parte 2 (spec do /ai-eng, GO com 3 ALTERA na s201): o backup FIXADO amarrado ao ATO destrutivo.

(1) O writer destrutivo (reforja in-place, `--ingerir/--registrar --apply` que SOBRESCREVE, poda,
    saneamento da taxonomia) RECUSA rodar sem o backup fixado do proprio inicio -- e esse backup
    prova que e o estado de antes: sha256 da copia == sha256 do banco no mesmo instante.
(2) Sair da fixacao so por decisao com rastro: `--desfixar ID --motivo`; nenhuma CLI apaga fixado --
    o desfixado volta para a ROTACAO, que e quem apaga.
(3) Propriedade: rotacao com 20 backups falsos nunca remove fixado (e a purga recusa o prefixo).

Nada aqui toca o `ipub.db` nem o `artifacts/backups/` reais: todo banco e temporario, o fixado de
um banco temporario mora em `<pasta do banco>/backups`, e fixar o banco REAL dentro do pytest e
recusa (a suite nunca mais faz backup real -- a causa do F137).
"""
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import backup_db  # noqa: E402
import cards_prune  # noqa: E402
import dedup_taxonomia  # noqa: E402
import emed_banco  # noqa: E402
import normalize_taxonomia  # noqa: E402
import recurate_cards  # noqa: E402
from app.utils import db  # noqa: E402


def _banco(caminho):
    con = sqlite3.connect(caminho)
    con.execute("CREATE TABLE t (a INTEGER)")
    con.execute("INSERT INTO t VALUES (1)")
    con.commit()
    con.close()
    return Path(caminho)


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _manifesto(pasta):
    arq = Path(pasta) / backup_db.MANIFESTO_FIXADOS
    return json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else []


# ---------------------------------------------------------------- (1) o fixado do proprio inicio

def test_fixar_antes_do_ato_prova_o_estado_de_antes(tmp_path):
    banco = _banco(tmp_path / "x.db")
    antes = _sha(banco)
    rec = backup_db.fixar_antes_do_ato("poda de teste", db=banco, out=lambda *_: None)
    copia = tmp_path / "backups" / rec["arquivo"]
    assert copia.is_file() and rec["arquivo"].startswith(backup_db.PREFIX_FIXADO)
    assert rec["sha256"] == antes == _sha(copia)
    (item,) = _manifesto(tmp_path / "backups")
    assert (item["arquivo"], item["sha256"], item["ato"]) == (rec["arquivo"], antes, "poda de teste")


def test_fixar_o_banco_real_dentro_do_pytest_e_recusa():
    reais = sorted(os.listdir(backup_db.BACKUP_DIR)) if backup_db.BACKUP_DIR.is_dir() else []
    with pytest.raises(backup_db.SemPontoDeRetorno) as e:
        backup_db.fixar_antes_do_ato("qualquer", db=backup_db.DB, out=lambda *_: None)
    assert "REAL" in str(e.value)
    assert (sorted(os.listdir(backup_db.BACKUP_DIR)) if backup_db.BACKUP_DIR.is_dir() else []) == reais


def test_banco_corrompido_nao_deixa_fixado_nem_linha_no_manifesto(tmp_path):
    ruim = tmp_path / "ruim.db"
    ruim.write_bytes(b"isto nao e sqlite" * 200)
    with pytest.raises(backup_db.SemPontoDeRetorno):
        backup_db.fixar_antes_do_ato("x", db=ruim, out=lambda *_: None)
    assert not list((tmp_path / "backups").glob(f"{backup_db.PREFIX_FIXADO}*")) if (tmp_path / "backups").exists() else True
    assert _manifesto(tmp_path / "backups") == []


def test_banco_ausente_e_recusa(tmp_path):
    with pytest.raises(backup_db.SemPontoDeRetorno):
        backup_db.fixar_antes_do_ato("x", db=tmp_path / "nao.db", out=lambda *_: None)


# ---------------------------------------------------------------- (2) desfixar: so com motivo, volta a rotacao

def test_desfixar_exige_motivo_e_devolve_o_arquivo_a_rotacao(tmp_path):
    banco = _banco(tmp_path / "x.db")
    rec = backup_db.fixar_antes_do_ato("reforja", db=banco, out=lambda *_: None)
    pasta = tmp_path / "backups"
    for motivo in ("", "   ", None):
        with pytest.raises(backup_db.Recusa):
            backup_db.desfixar(rec["arquivo"], motivo, backup_dir=pasta)
    assert (pasta / rec["arquivo"]).is_file()
    r = backup_db.desfixar(rec["arquivo"][:30], "ato conferido, estado novo fixado", backup_dir=pasta)
    assert not (pasta / rec["arquivo"]).exists()
    na_rotacao = pasta / r["arquivo_na_rotacao"]
    assert na_rotacao.name.startswith(backup_db.PREFIX) and _sha(na_rotacao) == rec["sha256"]
    (item,) = _manifesto(pasta)                           # o rastro fica: a linha nao sai do manifesto
    assert item["motivo_desfixar"] == "ato conferido, estado novo fixado" and item["desfixado_em"]
    for i in range(5):                                    # 5 mais novos: a rotacao e quem apaga
        (pasta / f"{backup_db.PREFIX}2099010{i}_120000.db").write_bytes(b"fake")
    backup_db.purge(backup_dir=pasta, keep=5, quiet=True)
    assert not na_rotacao.exists()


def test_desfixar_ambiguo_inexistente_ou_adulterado_e_recusa(tmp_path):
    banco = _banco(tmp_path / "x.db")
    a = backup_db.fixar_antes_do_ato("a", db=banco, out=lambda *_: None)
    backup_db.fixar_antes_do_ato("b", db=banco, out=lambda *_: None)
    pasta = tmp_path / "backups"
    with pytest.raises(backup_db.Recusa):
        backup_db.desfixar(backup_db.PREFIX_FIXADO, "motivo", backup_dir=pasta)     # casa os dois
    with pytest.raises(backup_db.Recusa):
        backup_db.desfixar("ipub_fixado_19990101", "motivo", backup_dir=pasta)
    (pasta / a["arquivo"]).write_bytes(b"adulterado")
    with pytest.raises(backup_db.Recusa) as e:
        backup_db.desfixar(a["arquivo"], "motivo", backup_dir=pasta)
    assert "sha256" in str(e.value) and (pasta / a["arquivo"]).exists()


def test_cli_desfixar_exige_motivo_e_nao_existe_flag_de_apagar(tmp_path, capsys):
    with pytest.raises(SystemExit):
        backup_db.main(["--desfixar", "qualquer"])
    capsys.readouterr()
    ap_flags = backup_db.flags()
    assert not [f for f in ap_flags if any(p in f for p in ("apagar", "deletar", "remover", "purgar"))]


# ---------------------------------------------------------------- (3) propriedade da rotacao

def test_rotacao_com_20_falsos_nunca_remove_fixado_e_recusa_o_prefixo(tmp_path):
    banco = _banco(tmp_path / "x.db")
    fixados = [backup_db.fixar_antes_do_ato(f"ato {i}", db=banco, out=lambda *_: None) for i in range(3)]
    pasta = tmp_path / "backups"
    for i in range(20):
        (pasta / f"{backup_db.PREFIX}202601{i:02d}_120000.db").write_bytes(b"fake")
    backup_db.purge(backup_dir=pasta, keep=5, quiet=True)
    assert all((pasta / f["arquivo"]).is_file() for f in fixados)
    assert len(list(pasta.glob(f"{backup_db.PREFIX}*.db"))) == 5
    with pytest.raises(AssertionError):
        backup_db.purge(backup_dir=pasta, keep=0, prefix=backup_db.PREFIX_FIXADO, quiet=True)
    assert all((pasta / f["arquivo"]).is_file() for f in fixados)


# ---------------------------------------------------------------- os writers destrutivos

def _falha(*a, **k):
    raise backup_db.SemPontoDeRetorno("disco cheio (simulado)")


def _docs_emed(pasta, enunciado):
    q = pasta / "questoes"
    q.mkdir(parents=True, exist_ok=True)
    for n in (1, 2):
        (q / f"t9_{n}.json").write_text(json.dumps(
            {"lista": "t9", "tarefa": 9, "num": n, "banca": "X, 2020", "gabarito": "A", "emed_id": f"e{n}",
             "enunciado": f"{enunciado} {n}", "alternativas": "A) a\nB) b\nC) c\nD) d", "tags": "T",
             "capturado_em": "2026-09-26T10:00:00", "executor": "teste"}, ensure_ascii=False), encoding="utf-8")
    return pasta


def test_emed_ingerir_que_sobrescreve_fixa_antes_e_so_novas_nao(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "emed.db"))
    assert emed_banco.main(["--ingerir", str(_docs_emed(tmp_path / "v1", "original")), "--apply"]) == 0
    assert _manifesto(tmp_path / "backups") == []                 # so novas: nada destrutivo, nada fixado
    antes = _sha(tmp_path / "emed.db")
    capsys.readouterr()
    assert emed_banco.main(["--ingerir", str(_docs_emed(tmp_path / "v2", "mudado")), "--apply", "--json"]) == 0
    saida = json.loads(capsys.readouterr().out)
    (item,) = _manifesto(tmp_path / "backups")
    assert item["sha256"] == antes and saida["fixado"]["sha256"] == antes
    assert "2 atualizada" in item["ato"]


def test_emed_sem_ponto_de_retorno_nao_sobrescreve(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "emed.db"))
    assert emed_banco.main(["--ingerir", str(_docs_emed(tmp_path / "v1", "original")), "--apply"]) == 0
    monkeypatch.setattr(backup_db, "fixar_antes_do_ato", _falha)
    assert emed_banco.main(["--ingerir", str(_docs_emed(tmp_path / "v2", "mudado")), "--apply"]) == 1
    assert "sem ponto de retorno" in capsys.readouterr().out
    assert {r["enunciado"] for r in db.emed_listar_questoes("t9")} == {"original 1", "original 2"}


def _banco_cards(caminho):
    con = sqlite3.connect(caminho)
    con.executescript("""
        CREATE TABLE flashcards (id INTEGER PRIMARY KEY, needs_qualitative INTEGER, tema_id INTEGER);
        CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY);
        CREATE TABLE fsrs_revlog (id INTEGER PRIMARY KEY, card_id INTEGER);
        CREATE TABLE reforja_marks (id INTEGER PRIMARY KEY, card_id INTEGER);
        INSERT INTO flashcards VALUES (1, 2, 1), (2, 0, 1);
        INSERT INTO fsrs_cards VALUES (1), (2);
    """)
    con.commit()
    con.close()


def test_cards_prune_fixa_antes_e_sem_fixado_nao_apaga(tmp_path, monkeypatch, capsys):
    banco = tmp_path / "cards.db"
    _banco_cards(banco)
    antes = _sha(banco)
    monkeypatch.setattr(cards_prune, "EXPORT_DIR_DEFAULT", tmp_path / "exp")
    real = backup_db.fixar_antes_do_ato
    monkeypatch.setattr(backup_db, "fixar_antes_do_ato", _falha)
    assert cards_prune.main(["--ids", "1", "--apply", "--expect", "1", "--db", str(banco)]) != 0
    assert _sha(banco) == antes
    monkeypatch.setattr(backup_db, "fixar_antes_do_ato", real)
    assert cards_prune.main(["--ids", "1", "--apply", "--expect", "1", "--db", str(banco)]) == 0
    (item,) = _manifesto(tmp_path / "backups")
    assert item["sha256"] == antes and item["ato"].startswith("cards_prune")


def test_recurate_sem_fixado_nao_aplica(tmp_path, monkeypatch, capsys):
    plano = tmp_path / "plano.json"
    plano.write_text(json.dumps([{"card_id": 1, "acao": "aposentar"}]), encoding="utf-8")
    monkeypatch.setattr(recurate_cards, "DB_PATH", str(_banco(tmp_path / "r.db")))
    monkeypatch.setattr(recurate_cards, "validar", lambda e, c, p: ([], [], [("aposentar", 1, {}, 1, "x")]))
    aplicados = []
    monkeypatch.setattr(recurate_cards, "aplicar", lambda plano, conn: aplicados.append(plano) or (0, 1))
    monkeypatch.setattr(sys, "argv", ["recurate_cards.py", "--from", str(plano), "--apply"])
    monkeypatch.setattr(backup_db, "fixar_antes_do_ato", _falha)
    assert recurate_cards.main() == 1 and aplicados == []
    assert "sem ponto de retorno" in capsys.readouterr().out


def test_recurate_fixa_antes_de_aplicar(tmp_path, monkeypatch, capsys):
    plano = tmp_path / "plano.json"
    plano.write_text(json.dumps([{"card_id": 1, "acao": "aposentar"}]), encoding="utf-8")
    banco = _banco(tmp_path / "r.db")
    antes = _sha(banco)
    monkeypatch.setattr(recurate_cards, "DB_PATH", str(banco))
    monkeypatch.setattr(recurate_cards, "validar", lambda e, c, p: ([], [], [("aposentar", 1, {}, 1, "x")]))
    ordem = []
    monkeypatch.setattr(recurate_cards, "aplicar", lambda plano, conn: ordem.append("aplicar") or (0, 1))
    real = backup_db.fixar_antes_do_ato
    monkeypatch.setattr(backup_db, "fixar_antes_do_ato",
                        lambda *a, **k: ordem.append("fixar") or real(*a, **k))
    monkeypatch.setattr(sys, "argv", ["recurate_cards.py", "--from", str(plano), "--apply"])
    assert recurate_cards.main() == 0 and ordem == ["fixar", "aplicar"]
    assert _manifesto(tmp_path / "backups")[0]["sha256"] == antes


def _banco_taxonomia(caminho):
    con = sqlite3.connect(caminho)
    con.executescript("""
        CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT,
            questoes_realizadas INTEGER, questoes_acertadas INTEGER, percentual_acertos REAL,
            ultima_revisao TEXT);
        CREATE TABLE questoes_erros (id INTEGER PRIMARY KEY, tema_id INTEGER);
        CREATE TABLE flashcards (id INTEGER PRIMARY KEY, tema_id INTEGER);
        INSERT INTO taxonomia_cronograma VALUES (1, 'Pediatria', 'Kawasaki', 10, 5, 50, NULL),
                                                (2, 'Pediatria', 'Kawasaki', 4, 4, 100, NULL);
    """)
    con.commit()
    con.close()
    return Path(caminho)


def test_dedup_taxonomia_sem_fixado_nao_grava(tmp_path, monkeypatch, capsys):
    banco = _banco_taxonomia(tmp_path / "tx.db")
    antes = _sha(banco)
    monkeypatch.setattr(dedup_taxonomia, "DB_PATH", str(banco))
    monkeypatch.setattr(backup_db, "fixar_antes_do_ato", _falha)
    monkeypatch.setattr(sys, "argv", ["dedup_taxonomia.py", "--apply"])
    with pytest.raises(SystemExit) as e:
        dedup_taxonomia.main()
    assert e.value.code == 1 and _sha(banco) == antes
    assert "sem ponto de retorno" in capsys.readouterr().out


def test_dedup_taxonomia_fixa_o_estado_de_antes(tmp_path, monkeypatch, capsys):
    banco = _banco_taxonomia(tmp_path / "tx.db")
    antes = _sha(banco)
    monkeypatch.setattr(dedup_taxonomia, "DB_PATH", str(banco))
    monkeypatch.setattr(sys, "argv", ["dedup_taxonomia.py", "--apply"])
    dedup_taxonomia.main()
    assert _manifesto(tmp_path / "backups")[0]["sha256"] == antes
    con = sqlite3.connect(banco)
    assert con.execute("SELECT COUNT(*) FROM taxonomia_cronograma").fetchone()[0] == 1
    con.close()


def test_normalize_taxonomia_chama_o_fixado_antes_da_transacao():
    """normalize_taxonomia e migracao one-shot (s097) com operacoes fixas sobre ids do banco real;
    reproduzir o banco dela aqui seria copiar o banco. Lente estatica declarada: o `--apply` passa
    pelo fixado ANTES do `with con:` que grava."""
    src = Path(normalize_taxonomia.__file__).read_text(encoding="utf-8")
    corpo = src[src.index("def main("):]
    assert "backup_db.fixar_antes_do_ato" in src
    assert "_fixar_antes(" in corpo and corpo.index("_fixar_antes(") < corpo.index("with con:")
