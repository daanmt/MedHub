"""Backup do ipub.db com integrity_check + rotacao keep-5 EMBUTIDA.

consolidacao part-7 (DoD 2): o destino e `artifacts/backups/` (antes gravava na
raiz do repo, que e o que fazia backup acumular ao lado do banco vivo), e todo
backup bem-sucedido purga o excedente alem dos 5 mais recentes NO PROPRIO
DESTINO -- a rotacao deixa de depender de faxina manual.

REGRA MESTRA: a purga e uma operacao destrutiva; ela calcula o conjunto-alvo,
ASSERTA o tamanho esperado ANTES de deletar e ABORTA (AssertionError) se
divergir. Suporta `dry_run=True` para inspecao sem escrita.
"""
import shutil
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'ipub.db'
BACKUP_DIR = ROOT / 'artifacts' / 'backups'
PREFIX = 'ipub_backup_'
KEEP = 5


def _listar(backup_dir: Path, prefix: str):
    """Backups do prefixo, do mais recente para o mais antigo.

    Ordena por (mtime, nome): o nome carrega o timestamp, entao serve de
    desempate estavel quando dois arquivos tem o mesmo mtime. Arquivos que nao
    casam o prefixo (ex.: `medhub_memory_pre_purge_*.db`) NAO entram no
    conjunto-alvo -- a purga so mexe no que ela mesma produz.
    """
    if not backup_dir.is_dir():
        return []
    itens = [p for p in backup_dir.iterdir()
             if p.is_file() and p.name.startswith(prefix) and p.suffix == '.db']
    return sorted(itens, key=lambda p: (p.stat().st_mtime, p.name), reverse=True)


def purge(backup_dir=BACKUP_DIR, keep=KEEP, prefix=PREFIX, dry_run=False, quiet=False):
    """Remove os backups alem dos `keep` mais recentes. Retorna os purgados.

    COUNT-ASSERT (pre): |manter| + |purgar| == |total|, |manter| <= keep e
    |purgar| == max(0, total - keep). COUNT-ASSERT (pos): sobram exatamente
    |manter| arquivos. Qualquer divergencia levanta AssertionError sem
    completar a operacao.
    """
    backup_dir = Path(backup_dir)
    todos = _listar(backup_dir, prefix)
    manter, purgar = todos[:keep], todos[keep:]

    esperado = max(0, len(todos) - keep)
    assert len(purgar) == esperado, (
        f"COUNT-ASSERT purga: alvo={len(purgar)} != esperado={esperado} "
        f"(total={len(todos)}, keep={keep})")
    assert len(manter) + len(purgar) == len(todos), (
        f"COUNT-ASSERT purga: {len(manter)}+{len(purgar)} != total={len(todos)}")
    assert len(manter) <= keep, (
        f"COUNT-ASSERT purga: manteria {len(manter)} > keep={keep}")

    if dry_run or not purgar:
        return purgar

    removidos = []
    for p in purgar:
        p.unlink()
        removidos.append(p)

    restantes = _listar(backup_dir, prefix)
    assert len(restantes) == len(manter), (
        f"COUNT-ASSERT pos-purga: restaram {len(restantes)}, esperado {len(manter)}")
    if not quiet:
        print(f"Rotacao keep-{keep}: {len(removidos)} backup(s) purgado(s), "
              f"{len(restantes)} mantido(s) em {backup_dir}")
    return removidos


def backup():
    if not DB.exists():
        print("ipub.db nao encontrado.")
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = BACKUP_DIR / f'{PREFIX}{ts}.db'
    try:
        shutil.copy2(DB, dest)
    except OSError as e:
        print(f"BACKUP FALHOU na copia -- abortando: {e}")
        return None

    # Verificar integridade. Um arquivo que nem abre como SQLite (truncado,
    # lixo) levanta sqlite3.DatabaseError aqui -- mesmo desfecho de um
    # integrity_check reprovado: aborta e devolve None.
    try:
        conn = sqlite3.connect(dest)
        try:
            result = conn.execute('PRAGMA integrity_check').fetchone()
        finally:
            conn.close()
    except sqlite3.Error as e:
        result = (f"sqlite: {e}",)
    if not result or result[0] != 'ok':
        dest.unlink(missing_ok=True)
        print("BACKUP CORROMPIDO -- abortando.")
        return None

    print(f"Backup OK: {dest}")
    # Rotacao SO depois do backup validado: nunca purgar apoiado num backup ruim.
    purge()
    assert dest.exists(), "COUNT-ASSERT: a purga removeu o backup recem-criado"
    return dest


def main():
    """F60 (descolar part-6): o exit code reflete o resultado.

    Padrao F27 (`insert_questao.py:474`) generalizado. "BACKUP CORROMPIDO --
    abortando" impresso no stdout com exit 0 era a antitese do headless: o
    chamador seguia para a operacao destrutiva achando que tinha rede.
    Qualquer aborto (banco ausente, copia falha, integridade reprovada) = 1.
    """
    return 0 if backup() else 1


if __name__ == '__main__':
    sys.exit(main())
