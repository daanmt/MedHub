import os
import shutil
from pathlib import Path

# Raiz do repositório (2 níveis acima de app/utils/)
ROOT_DIR = Path(__file__).parent.parent.parent

def get_abs_path(relative_path: str) -> Path:
    """Retorna o caminho absoluto baseado na raiz do projeto considerando .md etc."""
    return ROOT_DIR / relative_path

def read_md(rel_path: str) -> str:
    """Lê um arquivo markdown de forma segura e retorna o conteúdo em string."""
    path = get_abs_path(rel_path)
    if not path.exists():
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_md(rel_path: str, content: str) -> None:
    """Escreve conteúdo num arquivo, criando um backup .bak automático antes."""
    path = get_abs_path(rel_path)
    if path.exists():
        backup_path = path.with_suffix('.bak')
        shutil.copy2(path, backup_path)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def append_md(rel_path: str, content: str) -> None:
    """Faz um append num arquivo, criando backup .bak."""
    path = get_abs_path(rel_path)
    if path.exists():
        backup_path = path.with_suffix('.bak')
        shutil.copy2(path, backup_path)
    
    with open(path, 'a', encoding='utf-8') as f:
        if not content.startswith('\n'):
            f.write('\n')
        f.write(content)
