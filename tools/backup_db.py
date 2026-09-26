"""Backup do ipub.db com integrity_check + rotacao keep-5 EMBUTIDA.

consolidacao part-7 (DoD 2): o destino e `artifacts/backups/` (antes gravava na
raiz do repo, que e o que fazia backup acumular ao lado do banco vivo), e todo
backup bem-sucedido purga o excedente alem dos 5 mais recentes NO PROPRIO
DESTINO -- a rotacao deixa de depender de faxina manual.

REGRA MESTRA: a purga e uma operacao destrutiva; ela calcula o conjunto-alvo,
ASSERTA o tamanho esperado ANTES de deletar e ABORTA (AssertionError) se
divergir. Suporta `dry_run=True` para inspecao sem escrita.
"""
import argparse
import hashlib
import json
import os
import re
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
#: F137 (s201, GO do /ai-eng): backup FIXADO = ponto de retorno com sentido. Prefixo proprio, entao
#: a rotacao (que so enxerga PREFIX) nunca o conta nem o apaga; registro com sha256 em FIXADOS.json.
PREFIX_FIXADO = 'ipub_fixado_'
MANIFESTO_FIXADOS = 'FIXADOS.json'
#: o banco REAL, que nenhum monkeypatch troca: fixa-lo de dentro do pytest e recusa (F137 parte 2).
_DB_REAL = ROOT / 'ipub.db'


class SemPontoDeRetorno(Exception):
    """O ato destrutivo NAO roda: o backup fixado do proprio inicio nao existe ou nao confere."""


class Recusa(Exception):
    """Pedido sobre um fixado recusado (desfixar sem motivo, id ambiguo, arquivo adulterado)."""


def _listar(backup_dir: Path, prefix: str):
    """Backups do prefixo, do mais recente para o mais antigo.

    Ordena pelo CARIMBO DO NOME (`<prefixo>AAAAMMDD_HHMMSS`), nunca pelo mtime (F137, s201):
    `shutil.copy2` preserva o mtime do BANCO de origem, entao o backup feito agora de um banco
    parado ha dias nascia "mais velho" que os de ontem e era o primeiro a ser apagado. Arquivos
    que nao casam o prefixo (ex.: `medhub_memory_pre_purge_*.db`) NAO entram no conjunto-alvo --
    a purga so mexe no que ela mesma produz.
    """
    if not backup_dir.is_dir():
        return []
    itens = [p for p in backup_dir.iterdir()
             if p.is_file() and p.name.startswith(prefix) and p.suffix == '.db']
    return sorted(itens, key=lambda p: p.name, reverse=True)


def purge(backup_dir=BACKUP_DIR, keep=KEEP, prefix=PREFIX, dry_run=False, quiet=False):
    """Remove os backups alem dos `keep` mais recentes. Retorna os purgados.

    COUNT-ASSERT (pre): |manter| + |purgar| == |total|, |manter| <= keep e
    |purgar| == max(0, total - keep). COUNT-ASSERT (pos): sobram exatamente
    |manter| arquivos. Qualquer divergencia levanta AssertionError sem
    completar a operacao.
    """
    assert prefix != PREFIX_FIXADO, "a rotacao nunca purga FIXADO (F137): sair so por --desfixar"
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


def _sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def _mesmo(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def _ler_manifesto(backup_dir):
    arq = Path(backup_dir) / MANIFESTO_FIXADOS
    return json.loads(arq.read_text(encoding='utf-8')) if arq.is_file() else []


def _gravar_manifesto(backup_dir, reg):
    (Path(backup_dir) / MANIFESTO_FIXADOS).write_text(
        json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding='utf-8')


def _fixar(motivo, db, backup_dir, ato=None):
    """Nucleo do FIXADO: copia + sha256 da copia == sha256 do banco no mesmo instante (a prova de
    que e o estado de antes) + integrity_check + linha no manifesto. Qualquer falha levanta
    `SemPontoDeRetorno` e nao deixa copia meia-feita nem linha orfa."""
    db, backup_dir = Path(db), Path(backup_dir)
    if not db.is_file():
        raise SemPontoDeRetorno(f"banco ausente: {db}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = re.sub(r'[^a-z0-9]+', '-', motivo.lower()).strip('-')[:40] or 'sem-motivo'
    dest, n = backup_dir / f'{PREFIX_FIXADO}{ts}_{slug}.db', 1
    while dest.exists():
        dest, n = backup_dir / f'{PREFIX_FIXADO}{ts}_{slug}-{n}.db', n + 1
    try:
        shutil.copy2(db, dest)
        sha = _sha256(dest)
        if sha != _sha256(db):
            raise SemPontoDeRetorno("a copia nao confere com o banco (sha256): o banco mudou durante a copia")
        conn = sqlite3.connect(dest)
        try:
            ok = conn.execute('PRAGMA integrity_check').fetchone()
        finally:
            conn.close()
        if not ok or ok[0] != 'ok':
            raise SemPontoDeRetorno("o backup fixado reprovou no integrity_check")
        reg = _ler_manifesto(backup_dir)
        item = {"arquivo": dest.name, "sha256": sha, "motivo": motivo,
                "criado_em": datetime.now().replace(microsecond=0).isoformat()}
        if ato:
            item["ato"] = ato
        _gravar_manifesto(backup_dir, reg + [item])
    except SemPontoDeRetorno:
        dest.unlink(missing_ok=True)
        raise
    except (OSError, sqlite3.Error, ValueError) as e:
        dest.unlink(missing_ok=True)
        raise SemPontoDeRetorno(f"{type(e).__name__}: {e}") from None
    return dest, item


def backup_fixado(motivo):
    """Backup FIXADO a mao (F137, `--fixar MOTIVO`): fora da rotacao keep-5, linha em `FIXADOS.json`
    com arquivo, sha256, motivo e hora. Devolve o caminho, ou None se abortou."""
    try:
        dest, item = _fixar(motivo, DB, BACKUP_DIR)
    except SemPontoDeRetorno as e:
        print(f"BACKUP FIXADO ABORTADO: {e}")
        return None
    print(f"Backup FIXADO: {dest} (sha256 {item['sha256'][:16]}...)")
    return dest


def fixar_antes_do_ato(ato, db=None, out=print):
    """F137 parte 2 (spec do /ai-eng): o ponto de retorno FIXADO do proprio inicio de um ato
    destrutivo. O writer chama isto ANTES do primeiro write e RECUSA rodar se levantar.

    O fixado do `ipub.db` real vai para `artifacts/backups/`; o de qualquer outro banco, para
    `<pasta do banco>/backups` (o banco temporario de um teste nunca escreve no diretorio real).
    Fixar o banco REAL de dentro do pytest e recusa: a suite nunca mais faz backup real.
    Devolve o item do manifesto + `caminho` -- arquivo e sha256 vao para o ledger no item do ato."""
    db = Path(db) if db else DB
    if os.environ.get("PYTEST_CURRENT_TEST") and _mesmo(db, _DB_REAL):
        raise SemPontoDeRetorno("teste tentou fixar o ipub.db REAL -- aponte o writer para um banco "
                                "temporario (F137: a suite nao faz backup real)")
    pasta = BACKUP_DIR if _mesmo(db, _DB_REAL) else db.parent / "backups"
    dest, item = _fixar(f"antes de {ato}", db, pasta, ato=ato)
    out(f"FIXADO (ponto de retorno do ato): {dest} sha256 {item['sha256']}")
    return {**item, "caminho": str(dest)}


def desfixar(ident, motivo, backup_dir=None):
    """Sai da fixacao SO por decisao com rastro: exige motivo, confere o sha256 do manifesto e
    DEVOLVE o arquivo a rotacao (`ipub_backup_<carimbo>_desfixado.db`) -- quem apaga e a rotacao;
    nenhuma CLI apaga fixado. A linha do manifesto fica, com `desfixado_em` e o motivo."""
    backup_dir = Path(backup_dir) if backup_dir else BACKUP_DIR
    motivo = (motivo or "").strip()
    if not motivo:
        raise Recusa("desfixar exige --motivo (decisao com rastro)")
    ident = (ident or "").strip()
    reg = _ler_manifesto(backup_dir)
    ativos = [i for i, r in enumerate(reg) if not r.get("desfixado_em") and ident and (
        r["arquivo"] == ident or r["arquivo"].startswith(ident)
        or (len(ident) >= 8 and r["sha256"].startswith(ident)))]
    if len(ativos) != 1:
        raise Recusa(f"'{ident}' casa {len(ativos)} fixado(s) ativo(s) -- use o nome do arquivo ou 8+ do sha256")
    item = reg[ativos[0]]
    arq = backup_dir / item["arquivo"]
    if not arq.is_file():
        raise Recusa(f"{item['arquivo']} sumiu do disco -- registrar no ledger, nada mexido")
    if _sha256(arq) != item["sha256"]:
        raise Recusa(f"{item['arquivo']}: sha256 nao confere com o manifesto -- nada mexido; investigar")
    m = re.match(PREFIX_FIXADO + r"(\d{8}_\d{6})", item["arquivo"])
    carimbo = m.group(1) if m else datetime.now().strftime('%Y%m%d_%H%M%S')
    novo = backup_dir / f"{PREFIX}{carimbo}_desfixado.db"
    if novo.exists():
        raise Recusa(f"{novo.name} ja existe -- nada mexido")
    arq.rename(novo)
    item.update({"desfixado_em": datetime.now().replace(microsecond=0).isoformat(),
                 "motivo_desfixar": motivo, "arquivo_na_rotacao": novo.name})
    _gravar_manifesto(backup_dir, reg)
    return item


def _parser():
    ap = argparse.ArgumentParser(
        description="Backup do ipub.db em artifacts/backups/ com integrity_check + rotacao keep-5 "
                    "(ordem pelo carimbo do nome). Sem opcoes: rodar = fazer o backup.")
    ap.add_argument("--fixar", metavar="MOTIVO",
                    help="backup FIXADO (F137): fora da rotacao, sha256 em FIXADOS.json")
    ap.add_argument("--desfixar", metavar="ID",
                    help="devolve um fixado a rotacao (nome do arquivo ou 8+ do sha256); exige --motivo")
    ap.add_argument("--motivo", help="a decisao que desfixa (fica no manifesto e vai para o ledger)")
    return ap


def flags():
    """As opcoes da CLI (para a propriedade 'nenhuma flag apaga fixado')."""
    return [o for a in _parser()._actions for o in a.option_strings]


def main(argv=()):
    """F60 (descolar part-6): o exit code reflete o resultado.

    F137 (s201): `--help` sai 0 SEM fazer backup. A varredura de CLIs da suite roda `--help` em
    todo `tools/*.py`; sem argparse, cada suite fazia um backup real e a rotacao keep-5 apagou os
    pontos de retorno do dia. `argv` explicito (default vazio): chamado de dentro do pytest, ler
    `sys.argv` pegaria os argumentos do pytest.

    Padrao F27 (`insert_questao.py:474`) generalizado. "BACKUP CORROMPIDO --
    abortando" impresso no stdout com exit 0 era a antitese do headless: o
    chamador seguia para a operacao destrutiva achando que tinha rede.
    Qualquer aborto (banco ausente, copia falha, integridade reprovada) = 1.
    """
    ap = _parser()
    args = ap.parse_args(list(argv))
    if args.desfixar:
        if not args.motivo:
            ap.error("--desfixar exige --motivo")
        try:
            item = desfixar(args.desfixar, args.motivo)
        except Recusa as e:
            print(f"RECUSA: {e}")
            return 1
        print(f"DESFIXADO: {item['arquivo']} (sha256 {item['sha256']}) -> rotacao como "
              f"{item['arquivo_na_rotacao']}; motivo: {item['motivo_desfixar']}. Registrar no ledger.")
        return 0
    if args.fixar:
        return 0 if backup_fixado(args.fixar) else 1
    return 0 if backup() else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
