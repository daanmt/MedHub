import shutil, sqlite3
from pathlib import Path
from datetime import datetime

DB = Path(__file__).resolve().parents[1] / 'ipub.db'

def backup():
    if not DB.exists():
        print("ipub.db nao encontrado."); return None
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = DB.parent / f'ipub_backup_{ts}.db'
    shutil.copy2(DB, dest)
    # Verificar integridade
    with sqlite3.connect(dest) as c:
        result = c.execute('PRAGMA integrity_check').fetchone()
    if result[0] != 'ok':
        dest.unlink(); print("BACKUP CORROMPIDO — abortando."); return None
    print(f"Backup OK: {dest}")
    return dest

if __name__ == '__main__':
    backup()
