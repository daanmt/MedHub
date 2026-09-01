"""Exit codes que nao mentem + integridade do session log novo (descolar part-6, F60/F58).

Escrito ANTES do patch (2026-09-01) e SABOTAGEM EXECUTADA de verdade contra o
codigo pre-patch (fontes de HEAD carregadas por `importlib` num scratch), com
o resultado abaixo colado do run:

  - `test_backup_db_*`: `1) backup_db.main existe? False` -- nao havia exit
    code nenhum (o `__main__` chamava `backup()` e o processo saia 0 sempre,
    inclusive imprimindo "BACKUP CORROMPIDO"). E com db corrompido sintetico o
    pre-patch nem chegava la: `backup() levantou: DatabaseError file is not a
    database` (traceback cru, sem mensagem).
  - `test_importar_100pct_rejeitado_sai_nao_zero`:
    `2) importar_sessoes.main() com 100% rejeitado devolveu: None` -- exit 0
    com zero linhas importadas.
  - `test_history_*`: `3) auto_check.check_history_integrity existe? False` --
    nenhum gate olhava `history/` (a importacao do teste nem resolvia).
  - Bonus medido: coletar este arquivo contra o pre-patch estourava
    `ValueError: I/O operation on closed file` no proprio pytest, porque
    `importar_sessoes` sequestrava `sys.stdout` no import. Corrigido junto.

Nada aqui toca o `ipub.db` real, o `artifacts/backups/` real nem o
`history/` real: tudo roda em `tmp_path` com constantes monkeypatchadas.
"""
import sqlite3
import sys
from pathlib import Path

import pytest  # noqa: F401  -- tmp_path/monkeypatch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import backup_db as bkp  # noqa: E402
from tools import importar_sessoes as imp  # noqa: E402
from tools.auto_check import check_history_integrity  # noqa: E402


# ---------------------------------------------------------------- backup_db

def _db_valido(path: Path):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE t (a INTEGER)")
    con.execute("INSERT INTO t VALUES (1)")
    con.commit()
    con.close()
    return path


def test_backup_db_ok_sai_zero(tmp_path, monkeypatch):
    """Simetria: o caminho feliz continua saindo 0 (nao viramos tudo em erro)."""
    db = _db_valido(tmp_path / "ipub.db")
    monkeypatch.setattr(bkp, "DB", db)
    monkeypatch.setattr(bkp, "BACKUP_DIR", tmp_path / "backups")
    assert bkp.main() == 0
    assert list((tmp_path / "backups").glob(f"{bkp.PREFIX}*.db"))


def test_backup_db_corrompido_sai_nao_zero(tmp_path, monkeypatch):
    """F60: 'BACKUP CORROMPIDO' no stdout com exit 0 e a antitese do headless."""
    db = tmp_path / "ipub.db"
    # db sintetico corrompido: header SQLite plausivel + lixo (integrity_check
    # nao consegue nem abrir -- e o mesmo desfecho de um arquivo truncado).
    db.write_bytes(b"SQLite format 3\x00" + b"\x00" * 64 + b"LIXO" * 32)
    monkeypatch.setattr(bkp, "DB", db)
    monkeypatch.setattr(bkp, "BACKUP_DIR", tmp_path / "backups")

    rc = bkp.main()

    assert rc != 0, "aborto de backup precisa sair != 0 (F60)"
    # e o backup ruim NAO fica no disco
    assert not list((tmp_path / "backups").glob(f"{bkp.PREFIX}*.db"))


def test_backup_db_sem_banco_sai_nao_zero(tmp_path, monkeypatch):
    """Aborto por ausencia do banco tambem e falha -- nao 'sucesso vazio'."""
    monkeypatch.setattr(bkp, "DB", tmp_path / "nao_existe.db")
    monkeypatch.setattr(bkp, "BACKUP_DIR", tmp_path / "backups")
    assert bkp.main() != 0


# ------------------------------------------------------------ importar_sessoes

def _rows_file(tmp_path: Path, rows):
    import json
    p = tmp_path / "linhas.json"
    p.write_text(json.dumps(rows), encoding="utf-8")
    return p


def test_importar_100pct_rejeitado_sai_nao_zero(tmp_path, monkeypatch, capsys):
    """F60: lote 100% rejeitado saia != 0 -- nada entrou, nada de exit 0."""
    chamadas = []
    monkeypatch.setattr(imp, "registrar",
                        lambda **kw: chamadas.append(kw) or True)
    rows = [
        {"sessao": 1, "area": "AREA QUE NAO EXISTE", "feitas": 10, "acertos": 5},
        {"sessao": 2, "area": "Clinica Medica", "feitas": 3, "acertos": 9},
    ]
    monkeypatch.setattr(sys, "argv",
                        ["importar_sessoes.py", "--rows-file",
                         str(_rows_file(tmp_path, rows))])

    rc = imp.main()

    assert chamadas == [], "nenhuma linha invalida podia ter sido registrada"
    assert rc != 0, "100% rejeitado tem que sair != 0 (F60)"


def test_importar_parcial_sai_zero_com_contagem(tmp_path, monkeypatch, capsys):
    """Parcial segue exit 0 -- mas o resumo CONTA as rejeitadas (nao emudece)."""
    monkeypatch.setattr(imp, "registrar", lambda **kw: True)
    area_ok = sorted(imp.AREAS_VALIDAS)[0]
    rows = [
        {"sessao": 1, "area": area_ok, "feitas": 10, "acertos": 5},
        {"sessao": 2, "area": "AREA QUE NAO EXISTE", "feitas": 10, "acertos": 5},
    ]
    monkeypatch.setattr(sys, "argv",
                        ["importar_sessoes.py", "--rows-file",
                         str(_rows_file(tmp_path, rows))])

    rc = imp.main()
    saida = capsys.readouterr().out

    assert rc == 0, "lote parcial nao e falha"
    assert "1 invalidas" in saida or "1 invalida" in saida


# --------------------------------------------------------- history_integrity

CABECALHO = (
    "# Session 999 -- Sessao sintetica\n"
    "**Data:** 2026-09-01\n"
    "**Ferramenta:** Claude Code (Fable 5)\n"
    "**Continuidade:** Sessao 998\n\n"
    "Corpo.\n"
)


def _repo_history(tmp_path: Path, nome: str, conteudo: bytes, max_index=998):
    hist = tmp_path / "history"
    hist.mkdir(parents=True, exist_ok=True)
    (hist / "INDEX.md").write_text(
        f"# Chronicle\n\n**session_{max_index:03d}.md (2026-08-30):** ultima indexada.\n",
        encoding="utf-8")
    (hist / nome).write_bytes(conteudo)
    return tmp_path


def test_history_novo_integro_fica_em_silencio(tmp_path):
    root = _repo_history(tmp_path, "session_999.md", CABECALHO.encode("utf-8"))
    assert check_history_integrity(root=root) == []


def test_history_bom_e_acusado(tmp_path):
    """A metade exata do defeito F58 real da s156 (BOM UTF-8 no SSOT)."""
    root = _repo_history(tmp_path, "session_999.md",
                         b"\xef\xbb\xbf" + CABECALHO.encode("utf-8"))
    achados = check_history_integrity(root=root)
    assert len(achados) == 1
    assert "session_999.md" == achados[0][0]
    assert "BOM" in achados[0][1]


def test_history_byte_de_controle_e_acusado(tmp_path):
    """A outra metade da s156: escapes comidos viraram 0x07/0x0c crus."""
    corpo = CABECALHO.replace("Corpo.", "\ttools/\x07pp/\x0cuto_check")
    root = _repo_history(tmp_path, "session_999.md", corpo.encode("utf-8"))
    achados = check_history_integrity(root=root)
    assert len(achados) == 1
    assert "controle" in achados[0][1]
    # o \t legitimo NAO pode ser acusado
    assert "0x09" not in achados[0][1]


def test_history_header_fora_do_template_e_acusado(tmp_path):
    root = _repo_history(tmp_path, "session_999.md",
                         b"anotacao solta sem header\n")
    achados = check_history_integrity(root=root)
    assert len(achados) == 1
    assert "header" in achados[0][1]


def test_history_ferramenta_ausente_e_acusado(tmp_path):
    """`Ferramenta:` e o campo que torna o swap test possivel -- preservar."""
    corpo = "\n".join(l for l in CABECALHO.splitlines()
                      if not l.startswith("**Ferramenta:")) + "\n"
    root = _repo_history(tmp_path, "session_999.md", corpo.encode("utf-8"))
    achados = check_history_integrity(root=root)
    assert len(achados) == 1
    assert "Ferramenta" in achados[0][1]


def test_history_antigo_corrompido_nao_e_reaberto(tmp_path):
    """Anti-scope: a historia ja indexada e lapide, nao alarme recorrente."""
    root = _repo_history(tmp_path, "session_500.md",
                         b"\xef\xbb\xbflixo sem header\n", max_index=998)
    assert check_history_integrity(root=root) == []
    # ...mas volta a ser candidato se o commit corrente MEXER nele
    achados = check_history_integrity(root=root, extras={"session_500.md"})
    assert len(achados) == 1


def test_history_ausente_e_silencio_honesto(tmp_path):
    """Sensor que nao pode julgar fica calado (convencao WARN-first)."""
    assert check_history_integrity(root=tmp_path) == []
