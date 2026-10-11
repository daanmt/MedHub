"""F137 parte 2 (spec do /ai-eng, GO com 3 ALTERA na s201): o backup FIXADO amarrado ao ATO destrutivo.

(1) O writer destrutivo (reforja in-place, `--ingerir/--registrar --apply` que SOBRESCREVE, poda,
    saneamento da taxonomia) RECUSA rodar sem o backup fixado do proprio inicio -- e esse backup
    prova que e o estado de antes: sha256 da copia == sha256 do banco no mesmo instante.
(2) Sair da fixacao so por decisao com rastro: `--desfixar ID --motivo`; nenhuma CLI apaga fixado --
    o desfixado volta para a ROTACAO, que e quem apaga.
(2b) Desfixar em LOTE (part-4b): `--desfixar-lote --manter N --motivo` e dry-run por padrao; o
    `--apply` exige `--expect K` e passa cada item pelo mesmo `desfixar()`. Diretorio sintetico.
(3) Propriedade: rotacao com 20 backups falsos nunca remove fixado (e a purga recusa o prefixo).
(4) Copia OFF-MACHINE (Fase 0, Lote 1, part 1.4): `tools/backup_offmachine.py` copia o banco e os
    fixados que o desfixar-lote soltaria para uma pasta FORA do repo publico, com md5 relido no
    destino; e o gate `BANCO_NO_RECORTE` barra arquivo de banco no commit. Diretorio sintetico
    (a fixture `lote` + banco sintetico) e repos git sinteticos com o ambiente `GIT_*` limpo.

Nada aqui toca o `ipub.db` nem o `artifacts/backups/` reais: todo banco e temporario, o fixado de
um banco temporario mora em `<pasta do banco>/backups`, e fixar o banco REAL dentro do pytest e
recusa (a suite nunca mais faz backup real -- a causa do F137).
"""
import ast
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

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


def test_desfixar_dois_fixados_do_mesmo_carimbo_nao_colidem_na_rotacao(tmp_path):
    """No `FIXADOS.json` real ha 6 carimbos repetidos (ex.: 3 fixados em `20260929_184526`): o 2o
    `desfixar` do mesmo carimbo recusava (`..._desfixado.db ja existe`) e o lote parava no meio.
    Agora desambigua com `-N`, o mesmo padrao do `_fixar`, sem sobrescrever nada."""
    pasta = _fixados_sinteticos(tmp_path / "backups", ["20260929_184526", "20260929_184526", "20261001_120000"])
    a, b, _ = _manifesto(pasta)
    ra = backup_db.desfixar(a["arquivo"], "lote de teste", backup_dir=pasta)
    rb = backup_db.desfixar(b["arquivo"], "lote de teste", backup_dir=pasta)
    assert ra["arquivo_na_rotacao"] != rb["arquivo_na_rotacao"]
    for r, orig in ((ra, a), (rb, b)):
        novo = pasta / r["arquivo_na_rotacao"]
        assert novo.name.startswith(backup_db.PREFIX + "20260929_184526") and novo.suffix == ".db"
        assert _sha(novo) == orig["sha256"]
    assert len(backup_db._listar(pasta, backup_db.PREFIX)) == 2      # a rotacao enxerga os dois


# ---------------------------------------------------------------- (2b) desfixar em lote (part-4b)
#: carimbos fora de ordem no manifesto; o mtime sai INVERTIDO (o mais antigo no carimbo e o mais
#: novo no disco): "mais recente" e o carimbo do nome, como no `purge` (DT2 da part-4b)
_OITO = ["20260905_120000", "20260901_120000", "20260908_090000", "20260903_235959",
         "20260902_000001", "20260907_120000", "20260904_120000", "20260906_120000"]
_TRES_MAIS_ANTIGOS = ["20260901_120000", "20260902_000001", "20260903_235959"]


def _fixados_sinteticos(pasta, carimbos):
    pasta.mkdir(parents=True, exist_ok=True)
    reg = []
    for i, c in enumerate(carimbos):
        nome = f"{backup_db.PREFIX_FIXADO}{c}_ato-{i}.db"
        conteudo = f"fixado {i} {c}\n".encode() * 500
        (pasta / nome).write_bytes(conteudo)
        reg.append({"arquivo": nome, "sha256": hashlib.sha256(conteudo).hexdigest(),
                    "motivo": f"ato {i}", "criado_em": "2026-09-01T12:00:00"})
    for nome in sorted(r["arquivo"] for r in reg):                  # mtime invertido em relacao ao carimbo
        t = 2_000_000_000 - int(nome[len(backup_db.PREFIX_FIXADO):][:8])
        os.utime(pasta / nome, (t, t))
    (pasta / backup_db.MANIFESTO_FIXADOS).write_text(json.dumps(reg, indent=1) + "\n", encoding="utf-8")
    return pasta


def _foto_pasta(pasta):
    return {p.name: _sha(p) for p in sorted(Path(pasta).iterdir())}


@pytest.fixture
def lote(tmp_path, monkeypatch):
    """8 fixados sinteticos + manifesto + 1 backup da rotacao; o BACKUP_DIR da CLI aponta para ca."""
    pasta = _fixados_sinteticos(tmp_path / "backups", _OITO)
    (pasta / f"{backup_db.PREFIX}20260910_120000.db").write_bytes(b"rotacao")
    monkeypatch.setattr(backup_db, "BACKUP_DIR", pasta)
    return pasta


def _cli(*args):
    return backup_db.main(["--desfixar-lote", "--manter", "5", "--motivo", "poda dos antigos", *args])


def test_desfixar_lote_dry_run_lista_k_e_mb_e_nao_altera_nada(lote, capsys):
    antes = _foto_pasta(lote)
    assert _cli() == 0
    saida = capsys.readouterr().out
    assert "K=3" in saida and "MB" in saida and "--apply --expect 3" in saida
    assert all(c in saida for c in _TRES_MAIS_ANTIGOS)
    assert _foto_pasta(lote) == antes                                # arquivos E FIXADOS.json, mesmo sha256
    plano = backup_db.plano_desfixar_lote(5, backup_dir=lote)
    assert [r["arquivo"][len(backup_db.PREFIX_FIXADO):][:15] for r in plano["sair"]] == _TRES_MAIS_ANTIGOS
    assert plano["k"] == 3 and len(plano["manter"]) == 5 and plano["problemas"] == []
    assert _foto_pasta(lote) == antes


def test_desfixar_lote_apply_sem_expect_recusa(lote, capsys):
    antes = _foto_pasta(lote)
    casos = [(["--desfixar-lote", "--manter", "5", "--motivo", "x", "--apply"], "--expect"),
             (["--desfixar-lote", "--manter", "5"], "--motivo"),
             (["--desfixar-lote", "--motivo", "x"], "--manter"),
             (["--manter", "5", "--motivo", "x", "--apply", "--expect", "3"], "--desfixar-lote")]
    for argv, exigido in casos:                   # a recusa nomeia o que falta (nao e "flag desconhecida")
        with pytest.raises(SystemExit):
            backup_db.main(argv)
        err = capsys.readouterr().err
        assert "exige" in err and exigido in err.split("error:")[-1], (argv, err)
    assert _foto_pasta(lote) == antes


def test_desfixar_lote_expect_errado_recusa_e_nada_muda(lote, capsys):
    antes = _foto_pasta(lote)
    for k in ("2", "4", "0"):
        assert _cli("--apply", "--expect", k) == 1
        assert "RECUSA" in capsys.readouterr().out
    assert _foto_pasta(lote) == antes


def test_desfixar_lote_com_k_certo_desfixa_so_os_mais_antigos_pelo_carimbo(lote, capsys):
    antes = _foto_pasta(lote)
    reg_antes = {r["arquivo"]: r for r in _manifesto(lote)}
    assert _cli("--apply", "--expect", "3") == 0
    capsys.readouterr()
    reg = {r["arquivo"]: r for r in _manifesto(lote)}
    assert reg.keys() == reg_antes.keys()                            # o rastro fica: nenhuma linha sai
    sairam = sorted(n for n, r in reg.items() if r.get("desfixado_em"))
    assert [n[len(backup_db.PREFIX_FIXADO):][:15] for n in sairam] == _TRES_MAIS_ANTIGOS
    for n in sairam:
        r = reg[n]
        assert r["motivo_desfixar"] == "poda dos antigos" and r["desfixado_em"]
        assert not (lote / n).exists()
        assert _sha(lote / r["arquivo_na_rotacao"]) == r["sha256"]   # devolvido a rotacao, intacto
    ficam = [n for n, r in reg.items() if not r.get("desfixado_em")]
    assert len(ficam) == 5 and all(_sha(lote / n) == reg[n]["sha256"] for n in ficam)
    # nenhum arquivo apagado (a flag nao apaga: quem apaga e a rotacao, que o lote nao chama)
    assert sorted(v for k, v in _foto_pasta(lote).items() if k.endswith(".db")) == \
        sorted(v for k, v in antes.items() if k.endswith(".db"))
    assert (lote / f"{backup_db.PREFIX}20260910_120000.db").is_file()


def test_desfixar_lote_sha_divergente_recusa_o_lote_inteiro(lote, capsys):
    (alvo,) = [r for r in _manifesto(lote) if "20260902_000001" in r["arquivo"]]
    (lote / alvo["arquivo"]).write_bytes(b"adulterado")
    antes = _foto_pasta(lote)
    assert _cli() == 1                                               # o dry-run ja denuncia
    assert _cli("--apply", "--expect", "3") == 1
    assert "sha256" in capsys.readouterr().out
    assert _foto_pasta(lote) == antes                                # nenhum dos 3 saiu: nada pela metade


def test_desfixar_lote_sem_carimbo_legivel_recusa_sem_inventar_ordem(lote, capsys):
    reg = _manifesto(lote)
    (lote / f"{backup_db.PREFIX_FIXADO}manual.db").write_bytes(b"sem carimbo")
    reg.append({"arquivo": f"{backup_db.PREFIX_FIXADO}manual.db",
                "sha256": _sha(lote / f"{backup_db.PREFIX_FIXADO}manual.db"), "motivo": "m", "criado_em": "x"})
    (lote / backup_db.MANIFESTO_FIXADOS).write_text(json.dumps(reg, indent=1) + "\n", encoding="utf-8")
    antes = _foto_pasta(lote)
    assert _cli() == 1
    assert _cli("--apply", "--expect", "4") == 1
    saida = capsys.readouterr().out
    assert "carimbo" in saida and f"{backup_db.PREFIX_FIXADO}manual.db" in saida
    assert _foto_pasta(lote) == antes


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


# ---------------------------------------------------------------- (4) cópia off-machine (Lote 1, part 1.4)
# O `lote` tem 8 fixados ativos: `plano_desfixar_lote(5)` solta os 3 mais antigos, e a cópia leva
# esses 3 + o snapshot do banco (N = 4). O banco sintético entra no lugar do ipub.db (`backup_db.DB`).
_N_SINTETICO = 1 + len(_TRES_MAIS_ANTIGOS)
_REMOTE_PRIVADO = "https://github.com/daanmt/medhub-backup-privado.git"
_PADROES_BANCO = [f"*.{ext}{suf}" for ext in ("db", "sqlite", "sqlite3")
                  for suf in ("", "-wal", "-shm", "-journal")]


def _bom():
    """Import tardio: com o módulo ainda inexistente, só os testes desta seção ficam vermelhos."""
    import backup_offmachine
    return backup_offmachine


def _md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


@pytest.fixture
def git_isolado(monkeypatch):
    """O mesmo da `test_clausulas_check.py`: a suíte roda dentro do pre-commit e herdaria o
    `GIT_INDEX_FILE` do commit em curso; com o ambiente `GIT_*` limpo, o repo sintético fica
    sintético."""
    for chave in [k for k in os.environ if k.upper().startswith("GIT_")]:
        monkeypatch.delenv(chave, raising=False)


def _repo_git(pasta, *remotes):
    pasta.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(pasta)], check=True, capture_output=True)
    for nome, url in remotes:
        subprocess.run(["git", "-C", str(pasta), "remote", "add", nome, url],
                       check=True, capture_output=True)
    return pasta


def _subcomando_git(cmd):
    """O subcomando de `git [-C dir] [-c k=v] <sub> ...`; chamada que não é git volta inteira."""
    if isinstance(cmd, (str, bytes)) or Path(str(cmd[0])).stem.lower() != "git":
        return f"<nao-git: {cmd}>"
    resto = [str(c) for c in cmd[1:]]
    while resto and resto[0].startswith("-"):
        resto = resto[2:] if resto[0] in ("-C", "-c") else resto[1:]
    return resto[0] if resto else "<vazio>"


@pytest.fixture
def offm(lote, tmp_path, monkeypatch):
    """O `lote` (8 fixados + manifesto + 1 da rotação) + um banco sintético no lugar do ipub.db;
    o destino fica em `tmp_path`, fora do repo."""
    banco = _banco(tmp_path / "ipub.db")
    monkeypatch.setattr(backup_db, "DB", banco)
    return SimpleNamespace(backups=lote, banco=banco, raiz=tmp_path, dest=tmp_path / "destino")


def _foto_origem(o):
    """sha256 de cada arquivo da pasta de backups (fixados, rotação, FIXADOS.json) e do banco, mais
    o que mora ao lado do banco (um -journal deixado para trás apareceria aqui)."""
    return {**_foto_pasta(o.backups), "<banco>": _sha(o.banco),
            "<ao lado>": sorted(p.name for p in o.raiz.iterdir() if p.name != o.dest.name)}


def _apply(bom, o, expect=_N_SINTETICO):
    return bom.main(["--dest", str(o.dest), "--apply", "--expect", str(expect)])


def test_offmachine_dry_run_lista_n_mb_e_carimbo_sem_escrever(offm, capsys):
    """DoD 1: o dry-run é o default. Lista o snapshot + os K de `plano_desfixar_lote(5)["sair"]`,
    com MB e o carimbo da pasta que seria criada; não cria `--dest` e não toca a origem."""
    bom = _bom()
    antes = _foto_origem(offm)
    assert bom.main(["--dest", str(offm.dest)]) == 0
    saida = capsys.readouterr().out
    carimbo = re.search(r"ipub_(\d{8}_\d{6})\.db", saida).group(1)
    assert str(offm.dest / carimbo) in saida
    assert f"N={_N_SINTETICO}" in saida and "K=3" in saida and "MB" in saida
    assert all(c in saida for c in _TRES_MAIS_ANTIGOS)
    assert [c for c in _OITO if c not in _TRES_MAIS_ANTIGOS and c in saida] == []   # os 5 que ficam
    assert f"{backup_db.PREFIX}20260910_120000" not in saida                         # a rotação não entra
    assert f"--apply --expect {_N_SINTETICO}" in saida
    plano = bom.plano(offm.dest)
    sair = backup_db.plano_desfixar_lote(5, backup_dir=offm.backups)["sair"]
    assert plano["n"] == _N_SINTETICO == 1 + len(sair)
    assert [i["arquivo"] for i in plano["itens"][1:]] == [a["arquivo"] for a in sair]   # reuso, não recálculo
    assert plano["itens"][0]["arquivo"] == f"ipub_{plano['carimbo']}.db"
    assert plano["bytes"] == offm.banco.stat().st_size + sum(a["bytes"] for a in sair)
    assert not offm.dest.exists() and _foto_origem(offm) == antes


def test_offmachine_apply_sem_expect_ou_com_n_errado_recusa(offm, capsys):
    """DoD 2: `--apply` exige `--expect N`; N diferente do medido = recusa, nada escrito."""
    bom = _bom()
    antes = _foto_origem(offm)
    casos = [(["--dest", str(offm.dest), "--apply"], "--expect"),
             (["--dest", str(offm.dest), "--expect", "4"], "--apply"),
             (["--apply", "--expect", "4"], "--dest"),
             (["--conferir", str(offm.dest), "--dest", str(offm.dest)], "--conferir")]
    for argv, exigido in casos:                   # a recusa nomeia o que falta
        with pytest.raises(SystemExit):
            bom.main(argv)
        assert exigido in capsys.readouterr().err.split("error:")[-1], argv
    for n in ("3", "5", "0", "49"):
        assert _apply(bom, offm, n) == 1
        assert "RECUSA" in capsys.readouterr().out
    assert not offm.dest.exists() and _foto_origem(offm) == antes


@pytest.mark.parametrize("sufixo, conteudo", [("-journal", b""), ("-journal", b"j" * 512),
                                              ("-wal", b"w" * 64), ("-shm", b"s" * 64)],
                         ids=["journal-vazio", "journal-com-bytes", "wal-com-bytes", "shm-com-bytes"])
def test_offmachine_banco_em_uso_recusa_antes_de_copiar(offm, capsys, sufixo, conteudo):
    """DoD 2, adição (A) do ai-eng: o banco está em `journal_mode=delete`. Um `-journal` ao lado
    (hot journal: transação em curso ou queda) ou `-wal`/`-shm` com bytes = recusa ANTES de copiar,
    e `--dest` nem é criado."""
    bom = _bom()
    Path(f"{offm.banco}{sufixo}").write_bytes(conteudo)
    antes = _foto_origem(offm)
    assert _apply(bom, offm) == 1
    saida = capsys.readouterr().out
    assert "banco em uso: pare o tique e feche conexões" in saida and f"ipub.db{sufixo}" in saida
    assert not offm.dest.exists() and _foto_origem(offm) == antes


def test_offmachine_wal_e_shm_vazios_nao_contam_como_uso(offm):
    bom = _bom()
    for suf in ("-wal", "-shm"):
        Path(f"{offm.banco}{suf}").write_bytes(b"")
    assert bom.banco_em_uso(offm.banco) == []
    Path(f"{offm.banco}-journal").write_bytes(b"")
    assert [p for p in bom.banco_em_uso(offm.banco) if "-journal" in p]


def test_offmachine_apply_copia_confere_md5_e_nada_sai_da_origem(offm, capsys):
    """DoD 2: com o N certo e o banco quieto, `DIR/<carimbo>/` recebe o snapshot (sha256 == banco,
    integrity_check ok), os K fixados (sha256 == FIXADOS.json), o `MD5SUMS` no formato do `md5sum`
    com o md5 da ORIGEM e o `manifest.json`. Nada é apagado nem mexido na origem."""
    bom = _bom()
    antes = _foto_origem(offm)
    alvos = [a["arquivo"] for a in backup_db.plano_desfixar_lote(5, backup_dir=offm.backups)["sair"]]
    assert _apply(bom, offm) == 0
    saida = capsys.readouterr().out
    (pasta,) = list(offm.dest.iterdir())                       # só a pasta do carimbo
    assert re.fullmatch(r"\d{8}_\d{6}", pasta.name)
    snap = f"ipub_{pasta.name}.db"
    assert sorted(p.name for p in pasta.iterdir()) == sorted([snap, *alvos, "MD5SUMS", "manifest.json"])
    bruto = (pasta / "MD5SUMS").read_bytes()
    assert b"\r" not in bruto                                  # LF, como o md5sum escreve
    md5s = {}
    for linha in bruto.decode("utf-8").splitlines():
        m = re.fullmatch(r"([0-9a-f]{32})  (\S+)", linha)
        assert m, linha
        md5s[m.group(2)] = m.group(1)
    assert md5s == {snap: _md5(offm.banco), **{a: _md5(offm.backups / a) for a in alvos}}
    reg = {r["arquivo"]: r for r in _manifesto(offm.backups)}
    assert _sha(pasta / snap) == _sha(offm.banco)
    assert all(_sha(pasta / a) == reg[a]["sha256"] for a in alvos)
    con = sqlite3.connect(f"file:{(pasta / snap).as_posix()}?mode=ro", uri=True)
    try:
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        con.close()
    man = json.loads((pasta / "manifest.json").read_text(encoding="utf-8"))
    assert man["fixados_json"]["sha256"] == _sha(offm.backups / backup_db.MANIFESTO_FIXADOS)
    assert man["n"] == _N_SINTETICO and man["bytes"] == sum((pasta / n).stat().st_size for n in md5s)
    itens = {i["arquivo"]: i for i in man["arquivos"]}
    assert set(itens) == set(md5s)
    assert (itens[snap]["tipo"], itens[snap]["origem"]) == ("banco", str(offm.banco))
    for a in alvos:
        assert (itens[a]["tipo"], itens[a]["origem"]) == ("fixado", str(offm.backups / a))
        assert (itens[a]["sha256"], itens[a]["motivo"]) == (reg[a]["sha256"], reg[a]["motivo"])
    assert all(itens[n]["md5"] == md5s[n] and itens[n]["bytes"] == (pasta / n).stat().st_size
               for n in md5s)
    assert f"N={_N_SINTETICO}" in saida and "--conferir" in saida
    assert _foto_origem(offm) == antes          # os 8 fixados, a rotação, o FIXADOS.json e o banco
    assert bom.main(["--conferir", str(pasta)]) == 0     # a conferência de volta (o comando do G-op)


def test_offmachine_pasta_do_carimbo_existente_recusa_sem_sobrescrever(offm, monkeypatch, capsys):
    """DoD 2: `DIR/<carimbo>/` já existente = recusa; nunca sobrescreve."""
    bom = _bom()
    monkeypatch.setattr(bom, "_agora", lambda: datetime(2026, 10, 11, 0, 15, 0))
    ja = offm.dest / "20261011_001500"
    ja.mkdir(parents=True)
    (ja / "MD5SUMS").write_bytes(b"de outra copia\n")
    antes = {**_foto_origem(offm), "<ja>": _foto_pasta(ja)}
    assert bom.main(["--dest", str(offm.dest)]) == 1            # o dry-run já avisa
    assert _apply(bom, offm) == 1
    assert "já existe" in capsys.readouterr().out
    assert {**_foto_origem(offm), "<ja>": _foto_pasta(ja)} == antes
    assert [p.name for p in offm.dest.iterdir()] == [ja.name]


@pytest.mark.parametrize("estrago", ["adulterado", "sumido"])
def test_offmachine_fixado_divergente_ou_sumido_recusa_o_lote_inteiro(offm, capsys, estrago):
    """DoD 2: o sha256 de cada fixado é conferido contra o FIXADOS.json ANTES de copiar; um
    divergente ou sumido recusa o lote inteiro (nada copiado, `--dest` nem nasce)."""
    bom = _bom()
    (alvo,) = [r for r in _manifesto(offm.backups) if "20260902_000001" in r["arquivo"]]
    arq = offm.backups / alvo["arquivo"]
    if estrago == "adulterado":
        arq.write_bytes(b"adulterado")
    else:
        arq.unlink()
    antes = _foto_origem(offm)
    assert bom.main(["--dest", str(offm.dest)]) == 1            # o dry-run já denuncia
    assert _apply(bom, offm) == 1
    saida = capsys.readouterr().out
    assert "RECUSA" in saida and alvo["arquivo"] in saida
    assert not offm.dest.exists() and _foto_origem(offm) == antes


def test_offmachine_snapshot_que_nao_confere_nao_deixa_copia(offm, monkeypatch, capsys):
    """DoD 2: o snapshot segue a receita do `_fixar` (sha256 da cópia == do banco). Aqui o banco
    "muda durante a cópia": recusa, e nenhuma cópia meia-feita fica no destino."""
    bom = _bom()
    real = shutil.copy2

    def copia_que_diverge(src, dst, *a, **k):
        feito = real(src, dst, *a, **k)
        if Path(src) == offm.banco:
            with open(dst, "ab") as fh:
                fh.write(b"\0")
        return feito

    monkeypatch.setattr(bom.shutil, "copy2", copia_que_diverge)
    antes = _foto_origem(offm)
    assert _apply(bom, offm) == 1
    assert "sha256" in capsys.readouterr().out
    assert not offm.dest.exists() or list(offm.dest.iterdir()) == []
    assert _foto_origem(offm) == antes


def test_offmachine_snapshot_corrompido_reprova_no_integrity_check(offm, capsys):
    bom = _bom()
    offm.banco.write_bytes(b"isto nao e sqlite" * 200)
    antes = _foto_origem(offm)
    assert _apply(bom, offm) == 1
    assert "integrity_check" in capsys.readouterr().out
    assert not offm.dest.exists() or list(offm.dest.iterdir()) == []
    assert _foto_origem(offm) == antes


def test_offmachine_copia_de_fixado_que_nao_confere_para_e_diz_qual(offm, monkeypatch, capsys):
    """A cópia de cada fixado tem o sha256 do FIXADOS.json; se não tiver, para, diz qual e não
    grava o MD5SUMS (a pasta não passa no `--conferir`, então não sobe)."""
    bom = _bom()
    real = shutil.copy2
    estragar = f"{backup_db.PREFIX_FIXADO}20260903_235959"

    def copia_que_estraga(src, dst, *a, **k):
        feito = real(src, dst, *a, **k)
        if Path(src).name.startswith(estragar):
            with open(dst, "ab") as fh:
                fh.write(b"x")
        return feito

    monkeypatch.setattr(bom.shutil, "copy2", copia_que_estraga)
    antes = _foto_origem(offm)
    assert _apply(bom, offm) == 1
    assert estragar in capsys.readouterr().out
    (pasta,) = list(offm.dest.iterdir())
    assert not (pasta / "MD5SUMS").exists()
    assert bom.main(["--conferir", str(pasta)]) == 1
    assert _foto_origem(offm) == antes


def test_offmachine_md5_relido_que_diverge_sai_1_e_diz_qual(offm, monkeypatch, capsys):
    """DoD 2: depois de copiar, o script RELÊ cada arquivo no destino contra o md5 da ORIGEM. Aqui
    o banco "muda" entre o snapshot e o md5 da origem: sai 1 e nomeia o arquivo; nada é apagado,
    e a pasta não passa no `--conferir`."""
    bom = _bom()
    real = bom._md5
    monkeypatch.setattr(bom, "_md5", lambda p: "0" * 32 if Path(p) == offm.banco else real(p))
    antes = _foto_origem(offm)
    assert _apply(bom, offm) == 1
    saida = capsys.readouterr().out
    assert re.search(r"ipub_\d{8}_\d{6}\.db", saida) and "diverge" in saida
    (pasta,) = list(offm.dest.iterdir())
    assert bom.main(["--conferir", str(pasta)]) == 1
    assert _foto_origem(offm) == antes


def test_offmachine_banco_real_dentro_do_pytest_e_recusa(lote, tmp_path):
    """Como o `fixar_antes_do_ato`: copiar o ipub.db ou ler o artifacts/backups REAIS de dentro do
    pytest é recusa, antes de qualquer leitura (a suíte nunca roda a cópia real)."""
    bom = _bom()
    dest = tmp_path / "destino"
    for kw in ({"db": backup_db._DB_REAL, "backup_dir": lote},
               {"db": _banco(tmp_path / "x.db"), "backup_dir": backup_db.ROOT / "artifacts" / "backups"}):
        with pytest.raises(backup_db.Recusa) as e:
            bom.plano(dest, **kw)
        assert "REAL" in str(e.value)
    assert not dest.exists()


def test_offmachine_destino_dentro_do_repo_publico_recusa(offm, monkeypatch, capsys):
    """DoD 3: `--dest` dentro do repo público (a raiz, subpasta, variação de caixa) = recusa antes
    de qualquer escrita. (a) a regra sobre a raiz REAL: só caminho, nenhuma escrita; (b) o CLI com
    um "repo público" sintético: dry-run e apply recusam."""
    bom = _bom()
    for dest in (ROOT, ROOT / "tmp" / "copia", ROOT / "artifacts" / "backups" / "fora"):
        with pytest.raises(backup_db.Recusa) as e:
            bom.conferir_destino(dest)
        assert "repo público" in str(e.value)
    if os.name == "nt":                                          # NTFS não distingue caixa
        with pytest.raises(backup_db.Recusa):
            bom.conferir_destino(Path(str(ROOT).upper()) / "Tmp" / "Copia")
    pub = offm.raiz / "RepoPublico"
    pub.mkdir()
    monkeypatch.setattr(bom, "REPO_PUBLICO", pub)
    antes = _foto_origem(offm)
    alvo = (Path(str(pub).swapcase()) if os.name == "nt" else pub) / "sub" / "copia"
    for argv in (["--dest", str(alvo)], ["--dest", str(alvo), "--apply", "--expect", str(_N_SINTETICO)]):
        assert bom.main(argv) == 1
        assert "repo público" in capsys.readouterr().out
    assert list(pub.iterdir()) == [] and _foto_origem(offm) == antes


@pytest.mark.parametrize("url", [
    "https://github.com/daanmt/MedHub.git", "https://github.com/DAANMT/medhub/",
    "https://github.com/daanmt/MedHub", "git@github.com:daanmt/MedHub.git",
    "ssh://git@github.com/daanmt/medhub.git/", "https://usuario@github.com/daanmt/MedHub.git"])
def test_offmachine_arvore_git_com_remote_publico_recusa(offm, git_isolado, capsys, url):
    """DoD 3: `--dest` numa árvore git com QUALQUER remote igual ao público (normalizados `.git`
    final, barra final e caixa; ssh e usuário na URL também) = recusa, sem escrever no clone."""
    bom = _bom()
    clone = _repo_git(offm.raiz / "clone", ("origin", _REMOTE_PRIVADO), ("espelho", url))
    antes = _foto_origem(offm)
    dest = clone / "backups"
    for argv in (["--dest", str(dest)], ["--dest", str(dest), "--apply", "--expect", str(_N_SINTETICO)]):
        assert bom.main(argv) == 1
        assert "remote" in capsys.readouterr().out
    assert sorted(p.name for p in clone.iterdir()) == [".git"] and _foto_origem(offm) == antes


def test_offmachine_remote_que_aponta_para_a_pasta_do_repo_publico_recusa(offm, git_isolado,
                                                                         monkeypatch, capsys):
    """Um clone LOCAL do repo público (remote = a pasta dele) empurraria para lá: recusa."""
    bom = _bom()
    pub = offm.raiz / "RepoPublico"
    pub.mkdir()
    monkeypatch.setattr(bom, "REPO_PUBLICO", pub)
    clone = _repo_git(offm.raiz / "clone", ("origin", str(pub)))
    assert bom.main(["--dest", str(clone / "x")]) == 1
    assert "remote" in capsys.readouterr().out
    assert sorted(p.name for p in clone.iterdir()) == [".git"]


def test_normalizar_remote_iguala_as_grafias_e_separa_os_outros():
    bom = _bom()
    pub = bom.normalizar_remote(bom.REMOTE_PUBLICO)
    assert pub == bom.normalizar_remote("HTTPS://GitHub.com/daanmt/medhub.GIT/")
    for outro in (_REMOTE_PRIVADO, "https://github.com/outro/MedHub.git",
                  "https://gitlab.com/daanmt/MedHub.git", "https://github.com/daanmt/MedHub2.git"):
        assert bom.normalizar_remote(outro) != pub, outro


def test_offmachine_apply_so_roda_git_de_leitura(offm, git_isolado, monkeypatch, capsys):
    """DoD 3: o apply num clone de repo privado só roda git de LEITURA. Um `subprocess.run`
    gravador registra cada chamada: só `rev-parse` e `remote` aparecem (nenhum init/add/commit/
    push, nenhum processo que não seja git), e o clone segue sem nada no índice nem no HEAD."""
    bom = _bom()
    clone = _repo_git(offm.raiz / "privado", ("origin", _REMOTE_PRIVADO))
    real = subprocess.run
    chamadas = []

    def gravador(cmd, *a, **k):
        chamadas.append(cmd)
        return real(cmd, *a, **k)

    monkeypatch.setattr(bom.subprocess, "run", gravador)
    assert bom.main(["--dest", str(clone), "--apply", "--expect", str(_N_SINTETICO)]) == 0
    monkeypatch.setattr(bom.subprocess, "run", real)
    subs = [_subcomando_git(c) for c in chamadas]
    assert {"rev-parse", "remote"} <= set(subs) and set(subs) <= {"rev-parse", "remote"}, subs
    assert real(["git", "-C", str(clone), "ls-files"], capture_output=True, text=True,
                check=True).stdout == ""
    assert real(["git", "-C", str(clone), "rev-parse", "--verify", "-q", "HEAD"],
                capture_output=True).returncode != 0
    (pasta,) = [p for p in clone.iterdir() if p.name != ".git"]
    assert bom.main(["--conferir", str(pasta)]) == 0


def test_offmachine_conferir_acusa_byte_alterado_ausente_e_md5sums_mexido(offm, capsys):
    """DoD 4: `--conferir DIR/<carimbo>` relê contra o MD5SUMS da própria pasta: tudo bate = 0; um
    byte alterado ou um arquivo ausente = 1 com o nome. O MD5SUMS sem uma linha também é acusado
    (o manifest.json lista o que devia estar lá), e o CRLF de um checkout com `core.autocrlf` não
    quebra a conferência."""
    bom = _bom()
    assert _apply(bom, offm) == 0
    (pasta,) = list(offm.dest.iterdir())
    capsys.readouterr()
    assert bom.main(["--conferir", str(pasta)]) == 0
    assert f"{_N_SINTETICO} de {_N_SINTETICO}" in capsys.readouterr().out
    alvo = sorted(pasta.glob(f"{backup_db.PREFIX_FIXADO}*.db"))[0]
    original = alvo.read_bytes()
    alvo.write_bytes(original[:100] + bytes([original[100] ^ 1]) + original[101:])   # um byte
    assert bom.main(["--conferir", str(pasta)]) == 1
    saida = capsys.readouterr().out
    assert alvo.name in saida and "diverge" in saida
    alvo.unlink()
    assert bom.main(["--conferir", str(pasta)]) == 1
    saida = capsys.readouterr().out
    assert alvo.name in saida and "ausente" in saida
    alvo.write_bytes(original)
    md5sums = pasta / "MD5SUMS"
    bruto = md5sums.read_bytes()
    for arq in (md5sums, pasta / "manifest.json"):                  # checkout com core.autocrlf=true
        arq.write_bytes(arq.read_bytes().replace(b"\n", b"\r\n"))
    assert bom.main(["--conferir", str(pasta)]) == 0
    capsys.readouterr()
    md5sums.write_bytes(b"".join(l for l in bruto.splitlines(keepends=True)
                                 if alvo.name.encode() not in l))
    assert bom.main(["--conferir", str(pasta)]) == 1
    assert alvo.name in capsys.readouterr().out
    md5sums.unlink()
    assert bom.main(["--conferir", str(pasta)]) == 1
    assert "MD5SUMS" in capsys.readouterr().out


def test_bancos_no_recorte_regra_pura():
    """DoD 5: a regra do gate é PURA e mora no módulo; o `auto_check` só orquestra."""
    bom = _bom()
    assert bom.RE_BANCO.pattern == r"\.(db|sqlite3?)(-wal|-shm|-journal)?$"
    sim = ["ipub.db", "artifacts/backups/ipub_fixado_20261010_120000_x.db", "outra/ipub_fixado_y.db",
           "data/chroma/chroma.sqlite3", "a.sqlite", "x.db-wal", "x.db-shm", "x.db-journal",
           "c.sqlite3-wal", "c.sqlite-journal", "artifacts\\backups\\b.db", "MAIUSCULO.DB"]
    nao = ["tools/db.py", "app/utils/db.py", "x.dbx", "x.db.bak", "notas.md", "x.sqlite4",
           "x.db-walx", "db", "sqlite3", "x.db/leia.md"]
    assert bom.bancos_no_recorte(nao + sim) == sorted(sim)
    assert bom.bancos_no_recorte([]) == [] and bom.bancos_no_recorte(None) == []


def test_gitignore_cobre_todo_arquivo_de_banco(tmp_path, git_isolado):
    """DoD 5 + adição (B) do ai-eng: `*.db`, `*.sqlite` e `*.sqlite3`, cada um com `-wal`, `-shm` e
    `-journal`. Prova dupla: as 12 linhas estão no `.gitignore` e o git as aplica (repo sintético
    com o mesmo `.gitignore`, config global vazia)."""
    texto = (ROOT / ".gitignore").read_text(encoding="utf-8")
    linhas = {linha.strip() for linha in texto.splitlines()}
    assert [p for p in _PADROES_BANCO if p not in linhas] == []
    repo = _repo_git(tmp_path / "repo")
    (repo / ".gitignore").write_text(texto, encoding="utf-8")
    vazio = tmp_path / "gitconfig_vazio"
    vazio.write_text("", encoding="utf-8")
    env = {**os.environ, "GIT_CONFIG_GLOBAL": str(vazio), "GIT_CONFIG_NOSYSTEM": "1"}
    sim = ["fora/ipub_fixado_20261010_120000_x.db", "data/chroma/chroma.sqlite3", "a.sqlite",
           *[f"b.{ext}{suf}" for ext in ("db", "sqlite", "sqlite3") for suf in ("-wal", "-shm", "-journal")]]
    nao = ["tools/db.py", "docs/notas.md"]
    r = subprocess.run(["git", "-C", str(repo), "check-ignore", *sim, *nao],
                       capture_output=True, text=True, env=env)
    assert sorted(r.stdout.split()) == sorted(sim), r.stderr


def _main_auto_check(monkeypatch, capsys, modo, recorte):
    """`auto_check.main()` in-process com tudo que não é o gate neutralizado (o molde é o
    `_main_do_check29` da test_clausulas_check): o exit code depende só do BANCO_NO_RECORTE."""
    import auto_check
    import clausulas_check
    import cli_signature_check
    import consistencia_check
    resumo = {"orfas": 0, "normativas": 0, "cobertura_pct": 100.0, "nao_normativas": 0}
    monkeypatch.setattr(clausulas_check, "registro_de_gates", lambda: set())
    monkeypatch.setattr(clausulas_check, "run_checks", lambda hoje=None, gates=None: ([], resumo))
    monkeypatch.setattr(clausulas_check, "catraca_contra_head", lambda modo, root=None, gates=None: {
        "severidade": "WARN", "mensagem": None, "aviso": None, "head": 0, "atual": 0,
        "recorte": "indice"})
    monkeypatch.setattr(consistencia_check, "run_checks", lambda *a, **k: [])
    monkeypatch.setattr(cli_signature_check, "run_checks", lambda *a, **k: [])
    monkeypatch.setattr(sys, "argv", ["auto_check.py", modo])
    monkeypatch.setattr(auto_check, "get_staged_files", lambda: list(recorte))
    monkeypatch.setattr(auto_check, "get_changed_files", lambda: list(recorte))
    monkeypatch.setattr(auto_check, "_staged_deletados", lambda: [])
    monkeypatch.setattr(auto_check, "run_command", lambda *a, **k: (True, ""))
    monkeypatch.setattr(auto_check, "_ledger_record", lambda *a, **k: None)
    monkeypatch.setattr(auto_check, "card_watermark_mudou", lambda *a, **k: (False, None))
    monkeypatch.setattr(auto_check, "card_watermark_selar", lambda *a, **k: None)
    monkeypatch.setattr(auto_check, "check_erros_orfaos", lambda *a, **k: [])
    monkeypatch.setattr(auto_check, "check_areas_fora_vocabulario", lambda *a, **k: [])
    capsys.readouterr()
    codigo = auto_check.main()
    return codigo, capsys.readouterr().out


def test_auto_check_banco_no_recorte_barra_o_commit_e_passa_sem_banco(monkeypatch, capsys):
    """DoD 5: o gate roda no conjunto "sempre" (o recorte não tem código, a suíte nem é exigida) e
    o BLOCK muda o exit code, inclusive para o `.db` que só entrou por `git add -f` (o pre-commit
    vê o índice, não o .gitignore). Sem banco no recorte, passa e aparece no relatório."""
    staged = ["docs/nota.md", "fora/ipub_fixado_20261010_120000_x.db", "data/chroma/chroma.sqlite3-wal"]
    codigo, out = _main_auto_check(monkeypatch, capsys, "--staged", staged)
    assert codigo == 1 and "[BLOCK] BANCO_NO_RECORTE" in out, out[-1500:]
    assert "fora/ipub_fixado_20261010_120000_x.db" in out and "chroma.sqlite3-wal" in out
    assert "Suíte não exigida para este recorte" in out
    for modo in ("--staged", "--changed"):
        codigo, out = _main_auto_check(monkeypatch, capsys, modo, ["docs/nota.md", "notas/db.md"])
        assert codigo == 0, out[-1500:]
        assert "[BLOCK]" not in out
        assert "BANCO_NO_RECORTE" in out.split("RELATÓRIO FINAL", 1)[1]


def test_auto_check_banco_no_recorte_mora_no_conjunto_sempre():
    """DoD 5, lente estática declarada: o BLOCK mora num `if` direto no corpo do `main()` (fora de
    `else`, `except` ou `try` que o engulam, e sem gatilho por modo ou extensão), zera o
    `all_passed`, e a regra vem do módulo (`from backup_offmachine import bancos_no_recorte`)."""
    arvore = ast.parse((ROOT / "tools" / "auto_check.py").read_text(encoding="utf-8"))
    main = next(n for n in arvore.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    assert [n for n in ast.walk(main) if isinstance(n, ast.ImportFrom) and n.module == "backup_offmachine"
            and any(a.name == "bancos_no_recorte" for a in n.names)], "a regra não vem do módulo"

    def tem_block(no):
        return any(isinstance(c, ast.Constant) and isinstance(c.value, str)
                   and "[BLOCK] BANCO_NO_RECORTE" in c.value for c in ast.walk(no))

    gates = [s for s in main.body if isinstance(s, ast.If) and tem_block(s)]
    assert len(gates) == 1, "o BLOCK tem de ser um `if` direto no corpo do main"
    assert sum(tem_block(s) for s in main.body) == 1
    (gate,) = gates
    assert not gate.orelse
    assert "mode" not in {n.id for n in ast.walk(gate.test) if isinstance(n, ast.Name)}
    assert any(isinstance(s, ast.Assign) and any(getattr(t, "id", None) == "all_passed" for t in s.targets)
               and isinstance(s.value, ast.Constant) and s.value.value is False for s in gate.body)
