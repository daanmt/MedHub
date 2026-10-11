"""Cópia OFF-MACHINE do ipub.db e dos fixados que a 0.4b devolve à rotação (Fase 0, Lote 1, part 1.4).

Por que existe (M-129): não havia cópia fora desta máquina. O apply da 0.4b devolve os fixados
antigos à rotação keep-5, que apaga dezenas de pontos de retorno de uma vez. Antes dele, o
`ipub.db` e esses fixados ganham uma cópia carimbada, com md5 conferido de volta no destino, numa
pasta FORA do repo público. Subir a cópia para o git privado e para o Drive é ato do operador.

Uso (dry-run por padrão, como o `backup_db.py --desfixar-lote`):

    python tools/backup_offmachine.py --dest DIR                     # lista N, MB e o carimbo
    python tools/backup_offmachine.py --dest DIR --apply --expect N  # copia para DIR/<carimbo>/
    python tools/backup_offmachine.py --conferir DIR/<carimbo>       # relê contra o MD5SUMS dela

O que vai: o snapshot `ipub_<carimbo>.db` (a receita do `backup_db._fixar`: `shutil.copy2`,
sha256 da cópia == sha256 do banco, `PRAGMA integrity_check`) e os K de
`backup_db.plano_desfixar_lote(5)["sair"]`, os mesmos que o apply da 0.4b soltaria, cada um com o
sha256 conferido contra o `FIXADOS.json`. Junto vão o `MD5SUMS` (formato do `md5sum`, com o md5
lido da ORIGEM) e o `manifest.json` (origem, bytes, sha256, md5, motivo do fixado e o sha256 do
próprio `FIXADOS.json`).

Travas, todas ANTES de escrever:
  - destino dentro do repo público (`REPO_PUBLICO`, com subpasta e variação de caixa) ou numa
    árvore git com QUALQUER remote igual ao público (`REMOTE_PUBLICO`, normalizado) ou apontando
    para a pasta dele. O script só roda git de LEITURA (`rev-parse`, `remote -v`);
  - banco em uso: `-journal` ao lado, ou `-wal`/`-shm` com bytes. O ipub.db está em
    `journal_mode=delete`, e hot journal = transação em curso ou queda;
  - `--expect N` diferente do N medido, fixado sumido ou com sha256 divergente, e
    `DIR/<carimbo>/` já existente (nunca sobrescreve).
Depois de copiar, o script RELÊ cada arquivo no destino contra o md5 da origem, pelo mesmo
`conferir()` do `--conferir`. Divergência = exit 1 com o nome.

O que NÃO faz (anti-scope da part 1.4): não cria repo, não autentica, não roda `git add`,
`commit` nem `push`, não fala com o Drive e não apaga nada, nem na origem nem no destino. A única
remoção é a do próprio snapshot que acabou de reprovar, como no `_fixar` (nenhuma cópia
meia-feita). Não chama `desfixar`, `purge` nem `backup()`: a F137 fica intacta.

A regra pura do gate `[BLOCK] BANCO_NO_RECORTE` do `auto_check` também mora aqui
(`bancos_no_recorte`): este módulo é a fronteira do que pode sair da máquina.
"""
import argparse
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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
import backup_db  # noqa: E402

#: o repo PÚBLICO (este checkout) e o remote dele; o destino nunca é nenhum dos dois.
REPO_PUBLICO = ROOT
REMOTE_PUBLICO = "https://github.com/daanmt/MedHub.git"
#: o `--manter` do desfixar-lote da 0.4b: a cópia leva exatamente os K que ele soltaria.
MANTER = 5
#: arquivo de banco, com os satélites do SQLite. Caixa não conta: `IPUB.DB` é o mesmo arquivo no NTFS.
RE_BANCO = re.compile(r"\.(db|sqlite3?)(-wal|-shm|-journal)?$", re.I)
MD5SUMS = "MD5SUMS"
MANIFESTO = "manifest.json"
_RE_LINHA_MD5 = re.compile(r"([0-9a-fA-F]{32}) [ *](.+)")
_BACKUPS_REAL = backup_db.ROOT / "artifacts" / "backups"
#: o relógio do carimbo, trocável no teste (o carimbo do nome segue o formato do `backup_db`).
_agora = datetime.now

Recusa = backup_db.Recusa


class Falha(Exception):
    """A cópia começou e não fechou: a pasta fica como está (nada apagado) e NÃO passa no
    `--conferir`, então não sobe."""


# ---------------------------------------------------------------- regra pura do gate do auto_check

def bancos_no_recorte(caminhos):
    """Os caminhos do recorte que são arquivo de banco (`.db`, `.sqlite`, `.sqlite3` e os
    `-wal`/`-shm`/`-journal` deles), em ordem. PURA.

    É a regra do `[BLOCK] BANCO_NO_RECORTE` do `auto_check`: banco não vai para o repo público, nem
    com `git add -f` (o gitignore não segura o `-f`, e um nome novo escaparia de um padrão por
    nome). O ipub.db tem conteúdo do EMED, IP de terceiro."""
    return sorted({str(c) for c in (caminhos or []) if RE_BANCO.search(str(c))})


# ---------------------------------------------------------------- o destino nunca é o repo público

def normalizar_remote(url):
    """Forma canônica de uma URL de remote, para comparar com a do público. PURA.

    Não contam a caixa, a barra final e o `.git` final (o que a spec pede), nem o esquema
    (`https://`, `ssh://`), o usuário (`usuario@`), a porta e a forma scp do ssh
    (`git@host:dono/repo`)."""
    u = (url or "").strip().lower()
    u = re.sub(r"^[a-z][a-z0-9+.-]*://", "", u)          # esquema
    u = re.sub(r"^[^/@]+@", "", u)                         # usuario[:senha]@
    u = re.sub(r"^([^/:]+):\d+/", r"\1/", u)               # porta
    u = re.sub(r"^([^/:]{2,}):", r"\1/", u)                # scp: host:dono/repo
    u = u.rstrip("/")
    if u.endswith(".git"):
        u = u[:-4]
    return u.rstrip("/")


def _dentro(caminho, raiz):
    """`caminho` é `raiz` ou fica abaixo dela (links resolvidos; caixa não conta no Windows)."""
    a = os.path.normcase(os.path.realpath(caminho))
    b = os.path.normcase(os.path.realpath(raiz)).rstrip("\\/")
    return a == b or a.startswith(b + os.sep)


def _sem_credencial(url):
    return re.sub(r"//[^/@]+@", "//***@", url)


def _env_git():
    """Ambiente sem o git herdado de um hook (`GIT_DIR`, `GIT_INDEX_FILE`...): quem manda é o `-C`."""
    return {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}


def _git(cwd, *args):
    """Git de LEITURA, e só ele: `rev-parse` e `remote -v` são os únicos subcomandos chamados."""
    try:
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=_env_git())
    except OSError as e:
        return subprocess.CompletedProcess(["git", *args], 127, "", f"git indisponível: {e}")


def _existente(caminho):
    p = Path(os.path.abspath(caminho))
    while not p.exists() and p.parent != p:
        p = p.parent
    return p if p.is_dir() else p.parent


def _arvore_git(dest):
    """Raiz da árvore git que contém `dest` (o ancestral mais próximo que existe), ou None.
    Git ilegível com `.git` no caminho = `Recusa`: sem ler o remote, o destino não é conferido."""
    base = _existente(dest)
    r = _git(base, "rev-parse", "--show-toplevel")
    if r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip())
    if any((p / ".git").exists() for p in (base, *base.parents)):
        raise Recusa(f"o git não leu a árvore de {base} ({(r.stderr or '').strip()[:200]}); sem o "
                     "remote, o destino não é conferido -- nada escrito")
    return None


def _remotes(arvore):
    r = _git(arvore, "remote", "-v")
    if r.returncode != 0:
        raise Recusa(f"`git remote -v` falhou em {arvore} ({(r.stderr or '').strip()[:200]}) -- nada escrito")
    vistos = []
    for linha in r.stdout.splitlines():
        if "\t" in linha:
            nome, resto = linha.split("\t", 1)
            vistos.append((nome, re.sub(r"\s+\((fetch|push)\)$", "", resto)))
    return vistos


def _caminho_local(url, base):
    """O caminho de um remote LOCAL (pasta ou `file://`), ou None se for URL de rede ou scp."""
    u = url.strip()
    if u.lower().startswith("file://"):
        u = u[7:]
        if re.match(r"^/[a-zA-Z]:", u):
            u = u[1:]
    elif "://" in u or re.match(r"^[^/\\]{2,}:", u):
        return None
    p = Path(u)
    return p if p.is_absolute() else Path(base) / p


def _remote_e_publico(url, arvore, repo_publico):
    if normalizar_remote(url) == normalizar_remote(REMOTE_PUBLICO):
        return True
    local = _caminho_local(url, arvore)
    return local is not None and _dentro(local, repo_publico)


def conferir_destino(dest, repo_publico=None):
    """`Recusa` se `dest` for o repo público: dentro da pasta dele (subpasta e caixa incluídas) ou
    numa árvore git com QUALQUER remote igual ao público ou apontando para a pasta dele. Só lê
    (caminho, `git rev-parse --show-toplevel`, `git remote -v`). Devolve a raiz da árvore git do
    destino, ou None."""
    repo_publico = Path(repo_publico if repo_publico is not None else REPO_PUBLICO)
    if _dentro(dest, repo_publico):
        raise Recusa(f"--dest {dest} fica dentro do repo público ({repo_publico}). O ipub.db tem "
                     "conteúdo do EMED e só vai ao destino privado -- nada escrito")
    arvore = _arvore_git(dest)
    if arvore is None:
        return None
    for nome, url in _remotes(arvore):
        if _remote_e_publico(url, arvore, repo_publico):
            raise Recusa(f"--dest {dest} fica na árvore git {arvore}, cujo remote '{nome}' "
                         f"({_sem_credencial(url)}) é o repo público -- nada escrito; o destino é o "
                         "clone do repo PRIVADO")
    return arvore


# ---------------------------------------------------------------- origem: o banco quieto e o lote

def banco_em_uso(db):
    """O que impede o snapshot consistente: `-journal` ao lado do banco (hot journal) ou
    `-wal`/`-shm` com bytes. Lista vazia = banco quieto. Só lê o diretório."""
    db = Path(db)
    achados = []
    journal = Path(f"{db}-journal")
    if journal.exists():
        achados.append(f"{journal.name} presente ({journal.stat().st_size} bytes; hot journal = "
                       "transação em curso ou queda)")
    for suf in ("-wal", "-shm"):
        p = Path(f"{db}{suf}")
        if p.exists() and p.stat().st_size > 0:
            achados.append(f"{p.name} com {p.stat().st_size} bytes")
    return achados


def _guarda_pytest(db, backup_dir):
    """Como o `fixar_antes_do_ato`: dentro do pytest, o ipub.db e o artifacts/backups REAIS são
    recusa antes de qualquer leitura (a suíte nunca roda a cópia real)."""
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        return
    reais = [str(x) for x, real in ((db, backup_db._DB_REAL), (backup_dir, _BACKUPS_REAL))
             if backup_db._mesmo(x, real)]
    if reais:
        raise Recusa(f"teste tentou copiar o estado REAL ({', '.join(reais)}): aponte para um "
                     "diretório sintético (F137: a suíte não lê nem copia o real)")


def plano(dest, db=None, backup_dir=None, manter=MANTER):
    """Dry-run: o que o `--apply` copiaria e por que recusaria. NÃO escreve nada.

    Ordem: guarda do pytest, destino (antes de ler a origem), o lote de
    `backup_db.plano_desfixar_lote(manter)` (que confere o sha256 de cada alvo contra o
    `FIXADOS.json`), banco em uso e a pasta do carimbo. Devolve {carimbo, dest, pasta, db,
    backup_dir, manter, ativos, k, n, bytes, itens: [{arquivo, origem, bytes, tipo}], problemas,
    em_uso}; `itens[0]` é o snapshot, e os demais seguem a ordem de `sair` (do mais antigo ao mais
    recente)."""
    db = Path(db if db is not None else backup_db.DB)
    backup_dir = Path(backup_dir if backup_dir is not None else backup_db.BACKUP_DIR)
    _guarda_pytest(db, backup_dir)
    dest = Path(os.path.abspath(dest))
    conferir_destino(dest)
    lote = backup_db.plano_desfixar_lote(manter, backup_dir)
    carimbo = _agora().strftime("%Y%m%d_%H%M%S")
    pasta = dest / carimbo
    problemas = list(lote["problemas"])
    if not db.is_file():
        problemas.append(f"banco ausente: {db}")
    if dest.exists() and not dest.is_dir():
        problemas.append(f"--dest {dest} existe e não é pasta")
    if pasta.exists():
        problemas.append(f"{pasta} já existe: duas cópias nunca se misturam (rode de novo, o carimbo muda)")
    itens = [{"arquivo": f"ipub_{carimbo}.db", "origem": db, "tipo": "banco",
              "bytes": db.stat().st_size if db.is_file() else 0}]
    itens += [{"arquivo": a["arquivo"], "origem": backup_dir / a["arquivo"], "tipo": "fixado",
               "bytes": a["bytes"]} for a in lote["sair"]]
    return {"carimbo": carimbo, "dest": dest, "pasta": pasta, "db": db, "backup_dir": backup_dir,
            "manter": manter, "ativos": lote["ativos"], "k": lote["k"], "n": len(itens),
            "bytes": sum(i["bytes"] for i in itens), "itens": itens, "problemas": problemas,
            "em_uso": banco_em_uso(db) if db.is_file() else []}


# ---------------------------------------------------------------- o apply

def _md5(caminho):
    h = hashlib.md5()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _integridade(arquivo):
    """`PRAGMA integrity_check` da cópia, aberta só para leitura (nenhum arquivo satélite nasce
    no destino). Banco ilegível vira a mensagem do sqlite, nunca exceção."""
    try:
        con = sqlite3.connect(f"{Path(arquivo).resolve().as_uri()}?mode=ro", uri=True)
        try:
            linha = con.execute("PRAGMA integrity_check").fetchone()
        finally:
            con.close()
    except sqlite3.Error as e:
        return f"sqlite: {e}"
    return linha[0] if linha else "sem resposta"


def _snapshot(db, dest):
    """A receita do `backup_db._fixar`: `copy2`, sha256 da cópia == sha256 do banco agora,
    `integrity_check` ok. Qualquer falha remove a cópia recém-feita e levanta `Recusa`."""
    try:
        shutil.copy2(db, dest)
        sha = backup_db._sha256(dest)
        if sha != backup_db._sha256(db):
            raise Recusa("o snapshot não confere com o banco (sha256): o banco mudou durante a cópia "
                         "-- pare o tique e repita")
        ok = _integridade(dest)
        if ok != "ok":
            raise Recusa(f"o snapshot reprovou no integrity_check ({ok})")
    except Recusa:
        Path(dest).unlink(missing_ok=True)
        raise
    except OSError as e:
        Path(dest).unlink(missing_ok=True)
        raise Recusa(f"snapshot falhou ({type(e).__name__}: {e})") from None
    return sha


def _gravar(caminho, texto):
    with open(caminho, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto)


def copiar(dest, expect, db=None, backup_dir=None, manter=MANTER):
    """O `--apply`. Antes de escrever: banco quieto, zero problema no plano e COUNT-ASSERT
    (`expect` == N medido); senão `Recusa`, nada escrito. Depois: `DIR/<carimbo>/` com o snapshot,
    os K fixados (sha256 da cópia == `FIXADOS.json`), o `manifest.json` e o `MD5SUMS` (md5 da
    ORIGEM), e então RELÊ tudo pelo `conferir()`. Falha depois de começar = `Falha` (a pasta fica,
    sem passar no `--conferir`). Devolve o resultado do `conferir` + carimbo, n e bytes."""
    if expect is None:
        raise Recusa("--apply exige --expect N (o N que o dry-run mediu)")
    p = plano(dest, db, backup_dir, manter)
    if p["em_uso"]:
        raise Recusa("banco em uso: pare o tique e feche conexões (" + "; ".join(p["em_uso"])
                     + ") -- nada escrito")
    if p["problemas"]:
        raise Recusa(f"{len(p['problemas'])} problema(s) -- nada escrito: " + "; ".join(p["problemas"]))
    if expect != p["n"]:
        raise Recusa(f"COUNT-ASSERT: --expect {expect} != N medido {p['n']} (1 snapshot + K={p['k']}) "
                     "-- nada escrito")
    pasta, db, backup_dir = p["pasta"], p["db"], p["backup_dir"]
    ativos = {r["arquivo"]: r for r in backup_db._ler_manifesto(backup_dir) if not r.get("desfixado_em")}
    fixados_json = backup_dir / backup_db.MANIFESTO_FIXADOS
    sha_fixados_json = backup_db._sha256(fixados_json) if fixados_json.is_file() else None
    try:
        pasta.mkdir(parents=True, exist_ok=False)
    except OSError as e:
        raise Recusa(f"não criei {pasta} ({type(e).__name__}: {e}) -- nada escrito") from None
    snap = pasta / p["itens"][0]["arquivo"]
    try:
        sha_banco = _snapshot(db, snap)
    except Recusa:
        try:
            pasta.rmdir()                   # vazia: o snapshot reprovado já saiu
        except OSError:
            pass
        raise
    copiados = [{"arquivo": snap.name, "tipo": "banco", "origem": str(db), "bytes": snap.stat().st_size,
                 "sha256": sha_banco, "integrity_check": "ok"}]
    incompleta = (f"{pasta} ficou incompleta, sem {MD5SUMS}, e não passa no --conferir: não suba. "
                  "Nada apagado")
    for it in p["itens"][1:]:
        reg, alvo = ativos[it["arquivo"]], pasta / it["arquivo"]
        try:
            shutil.copy2(it["origem"], alvo)
            sha = backup_db._sha256(alvo)
        except OSError as e:
            raise Falha(f"cópia de {it['arquivo']} falhou ({type(e).__name__}: {e}); {incompleta}") from None
        if sha != reg["sha256"]:
            raise Falha(f"a cópia de {it['arquivo']} não confere com o FIXADOS.json (sha256); {incompleta}")
        item = {"arquivo": it["arquivo"], "tipo": "fixado", "origem": str(it["origem"]),
                "bytes": alvo.stat().st_size, "sha256": sha, "motivo": reg.get("motivo"),
                "criado_em": reg.get("criado_em")}
        if reg.get("ato"):
            item["ato"] = reg["ato"]
        copiados.append(item)
    total = sum(c["bytes"] for c in copiados)
    try:
        for c in copiados:                  # md5 lido da ORIGEM: a releitura no destino compara com ele
            c["md5"] = _md5(c["origem"])
        manifesto = {"gerado_por": "tools/backup_offmachine.py", "carimbo": p["carimbo"],
                     "criado_em": _agora().replace(microsecond=0).isoformat(),
                     "origem": {"banco": str(db), "backups": str(backup_dir)},
                     "fixados_json": {"arquivo": backup_db.MANIFESTO_FIXADOS, "sha256": sha_fixados_json},
                     "manter": manter, "k": p["k"], "n": len(copiados), "bytes": total,
                     "arquivos": copiados}
        _gravar(pasta / MANIFESTO, json.dumps(manifesto, ensure_ascii=False, indent=1) + "\n")
        _gravar(pasta / MD5SUMS, "".join(f"{c['md5']}  {c['arquivo']}\n" for c in copiados))
    except OSError as e:
        raise Falha(f"md5 da origem ou gravação do {MANIFESTO}/{MD5SUMS} falhou ({type(e).__name__}: {e}); "
                    f"{pasta} não passa no --conferir: não suba. Nada apagado") from None
    res = conferir(pasta)
    if not res["ok"]:
        ruins = res["divergentes"] + res["ausentes"] + res["problemas"]
        raise Falha(f"md5 relido no destino diverge da origem: {', '.join(ruins)}. {pasta} não passa no "
                    "--conferir: não suba. Nada apagado; repita com o tique parado")
    return {**res, "carimbo": p["carimbo"], "n": len(copiados), "bytes": total}


# ---------------------------------------------------------------- a conferência de volta

def _nome_seguro(nome):
    return nome not in (".", "..") and not re.search(r"[\\/:]", nome)


def conferir(pasta):
    """Relê cada arquivo de `pasta` contra o `MD5SUMS` DELA, e o `MD5SUMS` contra o
    `manifest.json` (uma linha apagada do `MD5SUMS` não passa calada). Só lê. CRLF de um checkout
    com `core.autocrlf` não conta. Devolve {pasta, ok, total, batem, divergentes, ausentes,
    problemas, fora}; `fora` = arquivos da pasta que nenhum dos dois lista (informativo)."""
    pasta = Path(pasta)
    res = {"pasta": pasta, "ok": False, "total": 0, "batem": [], "divergentes": [], "ausentes": [],
           "problemas": [], "fora": []}
    arq = pasta / MD5SUMS
    if not arq.is_file():
        res["problemas"].append(f"{MD5SUMS} ausente em {pasta}: pasta incompleta ou não é cópia "
                                "do backup_offmachine")
        return res
    esperado = {}
    for i, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip():
            continue
        m = _RE_LINHA_MD5.fullmatch(linha.rstrip("\r"))
        if not m or not _nome_seguro(m.group(2)):
            res["problemas"].append(f"{MD5SUMS}:{i} ilegível: {linha[:80]!r}")
            continue
        esperado[m.group(2)] = m.group(1).lower()
    try:
        itens = json.loads((pasta / MANIFESTO).read_text(encoding="utf-8"))["arquivos"]
        listados = {i["arquivo"]: i.get("md5") for i in itens}
    except (OSError, ValueError, KeyError, TypeError) as e:
        res["problemas"].append(f"{MANIFESTO} ilegível ({type(e).__name__}): sem a lista do que "
                                "devia estar aqui")
        listados = {}
    for nome in sorted(set(listados) - set(esperado)):
        res["problemas"].append(f"{nome}: está no {MANIFESTO} e falta no {MD5SUMS}")
    for nome in sorted(set(esperado) - set(listados)):
        res["problemas"].append(f"{nome}: está no {MD5SUMS} e falta no {MANIFESTO}")
    for nome in sorted(set(esperado) & set(listados)):
        if listados[nome] != esperado[nome]:
            res["problemas"].append(f"{nome}: o md5 do {MD5SUMS} difere do {MANIFESTO}")
    for nome, md5 in esperado.items():
        alvo = pasta / nome
        if not alvo.is_file():
            res["ausentes"].append(nome)
        elif _md5(alvo) != md5:
            res["divergentes"].append(nome)
        else:
            res["batem"].append(nome)
    res["total"] = len(esperado)
    res["fora"] = sorted(p.name for p in pasta.iterdir() if p.is_file()
                         and p.name not in esperado and p.name not in (MD5SUMS, MANIFESTO))
    res["ok"] = bool(esperado) and not (res["divergentes"] or res["ausentes"] or res["problemas"])
    return res


# ---------------------------------------------------------------- CLI

def _main_dry(args):
    try:
        p = plano(args.dest)
    except Recusa as e:
        print(f"RECUSA: {e}")
        return 1
    print("CÓPIA OFF-MACHINE (dry-run, nada escrito)")
    print(f"  origem: banco {p['db']} + fixados de {p['backup_dir']}")
    print(f"  destino: {p['pasta']}  (carimbo de agora; o --apply carimba na hora dele)")
    print(f"  N={p['n']} arquivo(s), {backup_db._mb(p['bytes'])}: 1 snapshot do banco + K={p['k']} "
          f"fixado(s) que o desfixar-lote --manter {p['manter']} soltaria (de {p['ativos']} ativos)")
    for it in p["itens"]:
        nota = f"  (snapshot de {Path(it['origem']).name})" if it["tipo"] == "banco" else ""
        print(f"    {it['arquivo']}  {backup_db._mb(it['bytes'])}{nota}")
    if p["em_uso"]:
        print("  RECUSA no --apply: banco em uso: pare o tique e feche conexões ("
              + "; ".join(p["em_uso"]) + ")")
    if p["problemas"]:
        print(f"  RECUSA no --apply: {len(p['problemas'])} problema(s) -- " + "; ".join(p["problemas"]))
    if p["em_uso"] or p["problemas"]:
        return 1
    print(f'  Para aplicar: python tools/backup_offmachine.py --dest "{p["dest"]}" --apply --expect {p["n"]}')
    return 0


def _main_apply(args):
    try:
        res = copiar(args.dest, args.expect)
    except Recusa as e:
        print(f"RECUSA: {e}")
        return 1
    except Falha as e:
        print(f"FALHA: {e}")
        return 1
    print(f"CÓPIA OFF-MACHINE: N={res['n']} arquivo(s), {backup_db._mb(res['bytes'])}, copiados para "
          f"{res['pasta']} e conferidos (md5 relido no destino contra o da origem)")
    print(f"  {MD5SUMS} + {MANIFESTO} gravados. Nada apagado; git só de leitura.")
    print("  G-op (operador): commit + push no repo privado; o upload ao Drive é manual.")
    print(f"  Depois do clone fresco: python tools/backup_offmachine.py --conferir <clone>/{res['carimbo']}")
    return 0


def _main_conferir(pasta):
    res = conferir(pasta)
    if res["ok"]:
        print(f"CONFERIR {res['pasta']}: {len(res['batem'])} de {res['total']} arquivo(s) batem com o "
              f"{MD5SUMS} (md5 relido agora)")
        if res["fora"]:
            print(f"  fora do {MD5SUMS}, não conferidos: {', '.join(res['fora'])}")
        return 0
    print(f"CONFERIR {res['pasta']}: FALHA -- {len(res['batem'])} de {res['total']} batem")
    for nome in res["divergentes"]:
        print(f"  diverge (md5): {nome}")
    for nome in res["ausentes"]:
        print(f"  ausente: {nome}")
    for prob in res["problemas"]:
        print(f"  {prob}")
    return 1


def _parser():
    ap = argparse.ArgumentParser(
        description="Cópia OFF-MACHINE do ipub.db + os fixados que o desfixar-lote --manter 5 soltaria, "
                    "para uma pasta FORA do repo público, com md5 relido no destino. Dry-run por padrão; "
                    "nunca roda git de escrita e não apaga nada.")
    ap.add_argument("--dest", metavar="DIR",
                    help="pasta de destino, fora do repo público (ex.: o clone do repo PRIVADO); a cópia "
                         "vai para DIR/<carimbo>/")
    ap.add_argument("--apply", action="store_true",
                    help="copia (default: dry-run, nada escrito); exige --expect N")
    ap.add_argument("--expect", type=int, metavar="N",
                    help="com --apply: COUNT-ASSERT, o N (1 snapshot + K fixados) que o dry-run mediu")
    ap.add_argument("--conferir", metavar="PASTA",
                    help="relê DIR/<carimbo> contra o MD5SUMS da própria pasta (exit 0 = tudo bate)")
    return ap


def main(argv=()):
    """`argv` explícito (default vazio), como no `backup_db`: chamado de dentro do pytest, ler
    `sys.argv` pegaria os argumentos do pytest. Exit 0 = feito/confere; 1 = recusa ou falha;
    2 = uso errado (argparse)."""
    ap = _parser()
    args = ap.parse_args(list(argv))
    if args.conferir is not None:
        if args.dest is not None or args.apply or args.expect is not None:
            ap.error("--conferir não combina com --dest/--apply/--expect")
        return _main_conferir(args.conferir)
    if args.dest is None:
        ap.error("informe --dest DIR (dry-run ou --apply) ou --conferir PASTA")
    if args.expect is not None and not args.apply:
        ap.error("--expect só com --apply")
    if args.apply and args.expect is None:
        ap.error("--apply exige --expect N (o N que o dry-run mediu)")
    return _main_apply(args) if args.apply else _main_dry(args)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
    sys.exit(main(sys.argv[1:]))
