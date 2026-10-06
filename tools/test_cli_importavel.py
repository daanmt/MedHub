"""test_cli_importavel.py -- F118 (s187): todo CLI de `tools/` roda COMO CLI.

🔴 **O defeito, e ele e meu.** A refatoracao **1.9(a)** (s186) moveu `card_checks` de
`tools/` para `app/utils/`. Dois CLIs ancoravam o `sys.path` no **proprio diretorio**:

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -> tools/
    from app.utils import card_checks                                 # precisa da RAIZ

Antes do 1.9a isso funcionava, porque `card_checks` morava em `tools/`. Depois, nao.
Medido em 18/09/2026: **`tools/insert_card_extra.py` e `tools/calibrate_card_checks.py`
morrem com `ModuleNotFoundError: No module named 'app'` ao serem invocados**. O
`insert_card_extra` e o writer canonico de card adicional sobre um `questao_id`
existente -- ou seja, um caminho de escrita do baralho ficou inalcancavel por 1 dia.

🔴 **Por que a suite inteira era CEGA a isso, e este e o ponto:** o pytest insere a raiz
do repo no `sys.path` antes de importar os modulos de teste. Entao
`test_writer_gates.py` importa `insert_card_extra` **com o path que o proprio CLI
deveria ter fornecido** e passa. O gate alcanca o MODULO; nao alcanca o PONTO DE
ENTRADA. Nenhum dos checks existentes olha para isso: o `IMPORT_DANGLING` resolve
imports estaticamente, o `D5` le assinatura de flag, o `reachability_check` conta
referenciadores.

Classe: a familia da janela s187 numa superficie nova -- *o sensor alcanca o modulo e
nao o executavel*. Irma do F116 (escopo maior que o declarado) pelo avesso: aqui o
escopo do teste e **menor que o uso real**, e a diferenca e exatamente o que o harness
fornece de graca e o usuario nao.

Nasce BLOCK: a base zerou no mesmo commit (2 -> 0), a mesma condicao do F79b e do D5.

⚠️ **LIMITE DECLARADO:** este gate prova que o CLI **carrega** (import + parser de
argumentos). Ele nao prova que o CLI FUNCIONA -- nao executa nenhum caminho real, nao
toca banco e nao valida saida. E o piso, nao o teto: um CLI pode passar aqui e falhar
na primeira invocacao de verdade.

E02 (s216) -- a corrida. Ate a s214 o assert do F137 FOTOGRAFAVA o estado real (mtime +
tamanho de `ipub.db`, `medhub_memory.db` e `artifacts/backups/`) antes e depois de cada
`--help`. A foto nao sabe QUEM gravou: com outro agente gravando no `ipub.db` durante a
varredura (~60 CLIs), o CLI da vez levava a culpa e a suite barrava o commit (s214). Agora
o efeito e medido DENTRO do processo do CLI, por uma sonda (`_SONDA`, carregada como
`sitecustomize` so no subprocesso): ganchos de auditoria do Python para escrita de arquivo
e um `sqlite3.connect` vigiado (`total_changes` + `schema_version` da PROPRIA conexao). O
teste nao le nem fotografa o estado real; writer concorrente fica fora da conta
(`test_writer_concorrente_nao_suja_o_cli_inocente`). Limite da sonda: so ve o que passa
pelo Python do proprio CLI -- subprocesso filho (ex.: `sqlite3.exe`) fica fora.
"""
import os
import sqlite3
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")

# CLIs que nao expoem `--help` por desenho (script-style, sem argparse). Ficam de fora
# do teste de PARSER, mas continuam no teste de IMPORT -- a lista e explicita para que
# a isencao seja visivel, nunca inferida por heuristica.
SEM_ARGPARSE = set()


def _clis():
    for nome in sorted(os.listdir(TOOLS)):
        if not nome.endswith(".py"):
            continue
        if nome.startswith("test_") or nome == "__init__.py":
            continue
        yield nome


#: estado real que um `--help` jamais pode tocar (F137). Caminhos ABSOLUTOS: viram a lista
#: de alvos da sonda; o teste nunca os le nem fotografa (E02).
_ESTADO_REAL = tuple(os.path.join(ROOT, a) for a in (
    "ipub.db", "medhub_memory.db", os.path.join("artifacts", "backups")))

#: Sonda E02 (s216), gravada como `sitecustomize.py` num diretorio temporario que e o UNICO
#: item do PYTHONPATH do subprocesso -- a raiz do repo NAO entra, senao mascararia o F118.
_SONDA = r'''"""Sonda do test_cli_importavel (E02, s216): efeito do PROPRIO processo no estado guardado."""
import atexit
import os
import sqlite3
import sqlite3.dbapi2
import sys

_SAIDA = os.environ.get("MEDHUB_SONDA_SAIDA")
_ALVOS = tuple(os.path.normcase(os.path.abspath(p))
               for p in os.environ.get("MEDHUB_SONDA_ALVOS", "").split(os.pathsep) if p)
_ESCRITA = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
#: evento de auditoria -> indices dos argumentos que sao caminho ALTERADO
_DESTINO = {
    "os.remove": (0,), "os.rmdir": (0,), "os.mkdir": (0,), "os.truncate": (0,),
    "os.utime": (0,), "os.chmod": (0,), "shutil.rmtree": (0,),
    "os.rename": (0, 1), "os.link": (1,), "os.symlink": (1,), "shutil.move": (0, 1),
    "shutil.copyfile": (1,), "shutil.copymode": (1,), "shutil.copystat": (1,),
    "shutil.copytree": (1,), "_winapi.CopyFile2": (1,),
}


def _norm(p):
    try:
        return os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(p))))
    except (TypeError, ValueError):
        return None  # descritor inteiro: nao ha caminho a julgar


def _guardado(p):
    p = _norm(p)
    return bool(p) and any(p == a or p.startswith(a + os.sep) for a in _ALVOS)


def _registrar(linha):
    with open(_SAIDA, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def _gancho(evento, args):
    if evento == "open":
        caminho, modo, flags = (tuple(args) + (None, None, None))[:3]
        escreve = (bool(flags & _ESCRITA) if isinstance(flags, int)
                   else isinstance(modo, str) and any(c in modo for c in "wax+"))
        if escreve and _guardado(caminho):
            _registrar(f"EFEITO open {_norm(caminho)}")
    elif evento in _DESTINO:
        for i in _DESTINO[evento]:
            if i < len(args) and _guardado(args[i]):
                _registrar(f"EFEITO {evento} {_norm(args[i])}")


_connect_original = sqlite3.connect
_vigiadas = []


def _arquivo_do_banco(database, uri):
    try:
        s = os.fsdecode(os.fspath(database))
    except TypeError:
        return None
    if uri and s.startswith("file:"):
        s = s[5:].split("?", 1)[0]
        if len(s.lstrip("/")) > 1 and s.lstrip("/")[1] == ":":
            s = s.lstrip("/")
    return _norm(s) if _guardado(s) else None


def _versao(conn):
    try:
        cur = conn.cursor()
        cur.row_factory = None
        return cur.execute("PRAGMA schema_version").fetchone()[0]
    except Exception:
        return None


def _avaliar(conn):
    if conn.__dict__.get("_sonda_avaliada", True):
        return
    conn._sonda_avaliada = True
    try:
        linhas = conn.total_changes
    except Exception:
        return
    v0, v1 = conn._sonda_versao, _versao(conn)
    if linhas or (v0 is not None and v1 is not None and v0 != v1):
        _registrar(f"EFEITO sqlite {conn._sonda_db} total_changes={linhas} "
                   f"schema_version={v0}->{v1}")


def _connect_vigiado(database, *args, **kwargs):
    uri = kwargs.get("uri", args[6] if len(args) > 6 else False)
    alvo = _arquivo_do_banco(database, uri)
    if alvo is None:
        return _connect_original(database, *args, **kwargs)
    args = list(args)
    base = (args[4] if len(args) > 4 else kwargs.get("factory")) or sqlite3.Connection

    def _fechar(self):
        _avaliar(self)
        base.close(self)

    classe = type("ConexaoVigiada", (base,), {"close": _fechar})
    if len(args) > 4:
        args[4] = classe
    else:
        kwargs["factory"] = classe
    novo = not os.path.exists(alvo)
    conn = _connect_original(database, *args, **kwargs)
    if novo and "mode=ro" not in str(database):
        _registrar(f"EFEITO sqlite cria {alvo}")
    conn._sonda_db, conn._sonda_versao, conn._sonda_avaliada = alvo, _versao(conn), False
    _vigiadas.append(conn)
    return conn


if _SAIDA:
    _registrar("SONDA_ATIVA")
    sys.addaudithook(_gancho)
    sqlite3.connect = sqlite3.dbapi2.connect = _connect_vigiado
    atexit.register(lambda: [_avaliar(c) for c in _vigiadas])
'''


@pytest.fixture(scope="module")
def dir_sonda(tmp_path_factory):
    d = tmp_path_factory.mktemp("sonda")
    (d / "sitecustomize.py").write_text(_SONDA, encoding="utf-8")
    return d


def _ambiente_sonda(dir_sonda, saida, alvos):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(dir_sonda)
    env["MEDHUB_SONDA_SAIDA"] = str(saida)
    env["MEDHUB_SONDA_ALVOS"] = os.pathsep.join(str(a) for a in alvos)
    return env


def _ler_sonda(saida):
    """-> (sonda carregou?, linhas de EFEITO)."""
    try:
        with open(saida, encoding="utf-8") as f:
            linhas = f.read().splitlines()
    except FileNotFoundError:
        return False, []
    return "SONDA_ATIVA" in linhas, [x for x in linhas if x.startswith("EFEITO")]


def _rodar(script, args, cwd=ROOT, env=None):
    return subprocess.run([sys.executable, "-X", "utf8", str(script), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=str(cwd), env=env, timeout=90)


def test_nenhum_cli_morre_por_import_ao_ser_invocado(dir_sonda, tmp_path):
    """O caso do defeito: `python tools/insert_card_extra.py --help` ->
    ModuleNotFoundError. O CLI tem de ancorar o proprio `sys.path`, porque em uso real
    NAO ha pytest para faze-lo por ele."""
    quebrados, com_efeito, sem_sonda = [], [], []
    for nome in _clis():
        saida = tmp_path / f"{nome}.sonda"
        r = _rodar(os.path.join(TOOLS, nome), ["--help"],
                   env=_ambiente_sonda(dir_sonda, saida, _ESTADO_REAL))
        ativa, efeitos = _ler_sonda(saida)
        if not ativa:
            sem_sonda.append(nome)
        if efeitos:
            com_efeito.append(f"{nome} ({efeitos[0]})")
        erro = (r.stderr or "")
        if "ModuleNotFoundError" in erro or "ImportError" in erro:
            linha = next((x for x in erro.splitlines()
                          if "ModuleNotFoundError" in x or "ImportError" in x), erro[:120])
            quebrados.append(f"{nome}: {linha.strip()}")
    assert quebrados == [], (
        "CLI que nao carrega quando invocado como CLI -- o pytest fornece o sys.path "
        "que o proprio arquivo deveria fornecer, entao a suite passa e o uso real morre: "
        + "; ".join(quebrados))
    # Anti-vacuidade E02: sem a sonda carregada o assert de efeito abaixo seria verde sem olhar.
    assert sem_sonda == [], "a sonda nao carregou no subprocesso: " + ", ".join(sem_sonda)
    # F137 (s201): `--help` nao pode ter efeito no estado REAL. `backup_db.py` nao tinha argparse:
    # cada suite fazia um backup de verdade e a rotacao keep-5 apagava os pontos de retorno.
    assert com_efeito == [], ("`--help` mudou o banco ou os backups REAIS: " + ", ".join(com_efeito))


# --- E02 (s216): a sonda atribui o efeito ao processo; o writer concorrente nao conta ---

def _semear(db):
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE t (x BLOB)")
    conn.execute("CREATE VIEW v AS SELECT * FROM t")
    conn.commit()
    conn.close()


def _foto(caminho):
    st = os.stat(caminho)
    return st.st_mtime_ns, st.st_size


#: outro agente gravando no banco: transacao ABERTA (BEGIN IMMEDIATE) + commit em laco
_WRITER = (
    "import sqlite3, sys, time\n"
    "conn = sqlite3.connect(sys.argv[1], isolation_level=None, timeout=30)\n"
    "primeira = True\n"
    "while True:\n"
    "    conn.execute('BEGIN IMMEDIATE')\n"
    "    conn.execute('INSERT INTO t VALUES (randomblob(8192))')\n"
    "    time.sleep(0.02)\n"
    "    conn.execute('COMMIT')\n"
    "    if primeira:\n"
    "        open(sys.argv[2], 'w').close()\n"
    "        primeira = False\n"
    "    time.sleep(0.01)\n")

#: o CLI inocente imita o `audit_fsrs.py` real: sem argparse, `--help` RODA o corpo -- le o
#: banco via conexao que faz o DDL idempotente do `get_connection` (CREATE VIEW IF NOT EXISTS)
_CLI_INOCENTE = (
    "import sqlite3, time\n"
    "conn = sqlite3.connect({db!r})\n"
    "conn.execute('CREATE VIEW IF NOT EXISTS v AS SELECT * FROM t')\n"
    "n = conn.execute('SELECT COUNT(*) FROM t').fetchone()[0]\n"
    "time.sleep(0.3)\n"
    "conn.close()\n"
    "print(n)\n")


def test_writer_concorrente_nao_suja_o_cli_inocente(dir_sonda, tmp_path):
    """E02, a corrida reproduzida num banco de TESTE: um writer em paralelo grava durante o
    `--help` (a foto do banco MUDA -- era o que barrava o commit), e a sonda nao culpa o CLI."""
    db = tmp_path / "estado.db"
    _semear(db)
    cli = tmp_path / "inocente.py"
    cli.write_text(_CLI_INOCENTE.format(db=str(db)), encoding="utf-8")
    pronto, saida = tmp_path / "writer.pronto", tmp_path / "inocente.sonda"
    writer = subprocess.Popen([sys.executable, "-X", "utf8", "-c", _WRITER, str(db), str(pronto)])
    try:
        limite = time.monotonic() + 60
        while not pronto.exists():
            assert writer.poll() is None, "o writer concorrente morreu antes de gravar"
            assert time.monotonic() < limite, "o writer concorrente nao gravou em 60 s"
            time.sleep(0.05)
        antes = _foto(db)
        r = _rodar(cli, ["--help"], cwd=tmp_path, env=_ambiente_sonda(dir_sonda, saida, [db]))
        depois = _foto(db)
    finally:
        writer.terminate()
        writer.wait(timeout=30)
    ativa, efeitos = _ler_sonda(saida)
    assert r.returncode == 0, r.stderr
    assert ativa, "a sonda nao carregou"
    assert antes != depois, "o writer nao gravou durante o --help: a corrida nao foi reproduzida"
    assert efeitos == [], efeitos


@pytest.mark.parametrize("corpo, esperado", [
    ("import sqlite3\nc = sqlite3.connect({db!r})\n"
     "c.execute('INSERT INTO t VALUES (1)')\nc.commit()\nc.close()\n", "EFEITO sqlite"),
    ("import sqlite3\nc = sqlite3.connect({db!r})\n"
     "c.execute('ALTER TABLE t ADD COLUMN y')\nc.close()\n", "total_changes=0 schema_version=2->3"),
    ("import shutil\nshutil.copy2({db!r}, {bkp!r})\n", "EFEITO"),
    ("import pathlib\npathlib.Path({bkp!r}).write_text('x')\n", "EFEITO open"),
])
def test_sonda_pega_efeito_plantado(dir_sonda, tmp_path, corpo, esperado):
    """Um gate que nunca viu um positivo nao foi testado: linha, DDL, copia para o diretorio
    de backups e escrita de arquivo -- cada um tem de aparecer como EFEITO."""
    db, backups = tmp_path / "estado.db", tmp_path / "backups"
    _semear(db)
    backups.mkdir()
    cli = tmp_path / "malicioso.py"
    cli.write_text(corpo.format(db=str(db), bkp=str(backups / "x.db")), encoding="utf-8")
    saida = tmp_path / "malicioso.sonda"
    r = _rodar(cli, ["--help"], cwd=tmp_path, env=_ambiente_sonda(dir_sonda, saida, [db, backups]))
    assert r.returncode == 0, r.stderr
    ativa, efeitos = _ler_sonda(saida)
    assert ativa and any(esperado in e for e in efeitos), efeitos


def test_o_gate_pega_uma_ancora_errada_plantada(tmp_path):
    """Um gate que nunca viu um positivo nao foi testado. Reproduz o caso real: ancora
    no PROPRIO diretorio em vez da raiz, com um import que exige a raiz."""
    sub = tmp_path / "tools"
    sub.mkdir()
    (sub / "quebrado.py").write_text(
        "import os, sys\n"
        "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
        "from app.utils import card_checks\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "-X", "utf8", str(sub / "quebrado.py")],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(tmp_path), timeout=60)
    assert "ModuleNotFoundError" in (r.stderr or ""), \
        "o fixture tinha que reproduzir o defeito; se nao reproduz, o teste acima nao prova nada"


def test_a_lista_de_clis_nao_esta_vazia():
    """Guarda anti-vacuidade: lista vazia deixaria o teste acima verde sem olhar nada."""
    nomes = list(_clis())
    assert len(nomes) > 40, f"so {len(nomes)} CLIs encontrados -- o glob quebrou?"
    assert "insert_card_extra.py" in nomes, "o CLI do defeito original tem que estar no escopo"


def test_escopo_do_gate_esta_declarado():
    doc = sys.modules[__name__].__doc__.replace("*", "").lower()
    assert "limite declarado" in doc
    assert "nao prova que o cli funciona" in doc
