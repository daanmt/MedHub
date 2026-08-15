"""Rotacao keep-5 embutida no backup_db (consolidacao part-7, DoD 2).

Fixture sintetica em tmp_path: 6 backups fake -> sobram 5. Nada toca o
`artifacts/backups/` real nem o `ipub.db`. Asserts nativos.
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.backup_db import purge, PREFIX, KEEP  # noqa: E402


def _semear(dirpath: Path, n: int, prefix: str = PREFIX):
    """Cria n backups fake com mtime crescente (o mais novo por ultimo)."""
    criados = []
    for i in range(n):
        p = dirpath / f"{prefix}2026010{i}_120000.db"
        p.write_bytes(b"fake-sqlite-" + str(i).encode())
        os.utime(p, (1_700_000_000 + i * 60, 1_700_000_000 + i * 60))
        criados.append(p)
    return criados


def test_seis_backups_sobram_cinco(tmp_path):
    criados = _semear(tmp_path, 6)
    assert len(list(tmp_path.glob(f"{PREFIX}*.db"))) == 6

    removidos = purge(backup_dir=tmp_path, keep=5, quiet=True)

    restantes = sorted(p.name for p in tmp_path.glob(f"{PREFIX}*.db"))
    assert len(removidos) == 1, f"esperado 1 purgado, veio {len(removidos)}"
    assert len(restantes) == 5, f"esperado 5 mantidos, veio {len(restantes)}"
    # o purgado e o MAIS ANTIGO
    assert removidos[0].name == criados[0].name
    assert criados[0].name not in restantes
    assert criados[-1].name in restantes, "o mais recente nunca pode ser purgado"


def test_keep_default_e_cinco():
    assert KEEP == 5


def test_abaixo_do_teto_nao_purga(tmp_path):
    _semear(tmp_path, 5)
    removidos = purge(backup_dir=tmp_path, keep=5, quiet=True)
    assert removidos == []
    assert len(list(tmp_path.glob(f"{PREFIX}*.db"))) == 5


def test_dry_run_nao_deleta(tmp_path):
    _semear(tmp_path, 8)
    alvo = purge(backup_dir=tmp_path, keep=5, dry_run=True, quiet=True)
    assert len(alvo) == 3, "dry-run deve reportar 3 alvos"
    assert len(list(tmp_path.glob(f"{PREFIX}*.db"))) == 8, "dry-run nao pode deletar"


def test_purga_ignora_arquivos_de_outro_prefixo(tmp_path):
    _semear(tmp_path, 6)
    estranho = tmp_path / "medhub_memory_pre_purge_20260814.db"
    estranho.write_bytes(b"nao-e-alvo")
    outro = tmp_path / "notas.txt"
    outro.write_text("nao-e-alvo", encoding="utf-8")

    purge(backup_dir=tmp_path, keep=5, quiet=True)

    assert estranho.exists(), "purga nao pode tocar backup de outro prefixo"
    assert outro.exists(), "purga nao pode tocar arquivo nao-.db"
    assert len(list(tmp_path.glob(f"{PREFIX}*.db"))) == 5


def test_diretorio_inexistente_e_no_op(tmp_path):
    assert purge(backup_dir=tmp_path / "nao-existe", keep=5, quiet=True) == []


def test_count_assert_barra_teto_negativo(tmp_path):
    """keep negativo torna |manter| incoerente -> o assert deve barrar."""
    _semear(tmp_path, 3)
    with pytest.raises(AssertionError):
        purge(backup_dir=tmp_path, keep=-1, quiet=True)
    assert len(list(tmp_path.glob(f"{PREFIX}*.db"))) == 3, "nada pode ter sido deletado"
