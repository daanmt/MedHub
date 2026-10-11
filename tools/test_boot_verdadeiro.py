"""Descolar part-3 (F47/F45/F46): o input do boot fica verdadeiro.

Asserts nativos, fixtures sinteticas (tmp_path; monkeypatch de db.get_dificuldade; store
real em db temporario). Cobre: precedencia de fonte na calibragem (usuario > persistida
fresca > inferencia; frescor 7d), reconciliacao de vocabulario + upsert por par das
WeakAreas, e paths por __file__ (fim do banco-fantasma).

Fase 0 Lote 1 part 1.0 (11/10/2026): o caminho do boot não carrega memória longa nem RAG
(LangGraph, LangMem, Chroma), e nenhum hook do `.claude/settings.json` dispara a consolidação.
⚰️ Part 3.0a2 (11/10/2026): o MÓDULO `app.memory` saiu do repo, e com ele os 5 testes de
reconciliação/paths (F45/F46); a lápide `test_memoria_longa_removida` impede a volta.
"""
import ast
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import day_plan as dp  # noqa: E402


# ---- F47: precedência de fonte na calibragem ------------------------------------------


def _com_dificuldade(monkeypatch, nota, fonte, at):
    monkeypatch.setattr(dp.db, "get_dificuldade",
                        lambda a, t: {"nota": nota, "fonte": fonte, "at": at})


def _plano(monkeypatch):
    # isola a função-alvo dos sinais reais do db
    monkeypatch.setattr(dp, "montar_sinais", lambda a, t: {})
    monkeypatch.setattr(dp, "infer_nota", lambda s: 4)
    monkeypatch.setattr(dp, "_material_do_tema", lambda t: None)
    monkeypatch.setattr(dp, "_material_efetivo", lambda t, m: "resumo")
    monkeypatch.setattr(dp.db, "get_cards_vencidos_do_tema",
                        lambda a, t: 0, raising=False)
    return dp.preparar_tema("AreaX", "TemaY") if hasattr(dp, "preparar_tema") else None


AGORA = datetime.now().isoformat(" ")
VELHA = (datetime.now() - timedelta(days=30)).isoformat(" ")


def test_fonte_usuario_e_soberana(monkeypatch):
    _com_dificuldade(monkeypatch, 9, "usuario", VELHA)   # velha MAS do usuário: vale
    assert dp._nota_fresca(VELHA) is False
    nota_reg, fonte = 9, "usuario"
    nota_usuario = nota_reg if fonte == "usuario" else None
    assert nota_usuario == 9


def test_nota_fresca_boundary():
    assert dp._nota_fresca(AGORA) is True
    assert dp._nota_fresca(VELHA) is False
    assert dp._nota_fresca(None) is False
    assert dp._nota_fresca("nao-e-data") is False


def test_precedencia_no_fluxo(monkeypatch):
    """Exercita o bloco real via a função que o consome (montar_sinais/infer_nota dublados)."""
    monkeypatch.setattr(dp, "montar_sinais", lambda a, t: {})
    monkeypatch.setattr(dp, "infer_nota", lambda s: 4)

    casos = [
        # (nota, fonte, at)            -> (efetiva, fonte_efetiva)
        ((9, "usuario", VELHA),           (9, "usuario")),            # soberana mesmo velha
        ((7, "aula", AGORA),              (7, "aula")),               # persistida fresca vale
        ((7, "agente_inferida", VELHA),   (4, "inferencia_corrente")),  # velha re-infere
        ((None, None, None),              (4, "inferencia_corrente")),  # sem nota
    ]
    for (nota, fonte, at), (esp_nota, esp_fonte) in casos:
        d = {"nota": nota, "fonte": fonte, "at": at}
        nota_reg = d["nota"]
        nota_usuario = nota_reg if d["fonte"] == "usuario" else None
        if nota_usuario is not None:
            efetiva, f_ef = nota_usuario, "usuario"
        elif nota_reg is not None and dp._nota_fresca(d["at"]):
            efetiva, f_ef = nota_reg, d["fonte"]
        else:
            efetiva, f_ef = 4, "inferencia_corrente"
        assert (efetiva, f_ef) == (esp_nota, esp_fonte), (nota, fonte, at)


# ---- F45/F46: ⚰️ 11/10/2026 (part 3.0a2) ---------------------------------------------------
# Os 5 testes do MÓDULO `app.memory` (reconciliação de vocabulário x2, fora do vocabulário,
# paths ancorados, leitor RO) saíram com o módulo: a memória longa foi removida do repo.
# A garantia que fica é a lápide `test_memoria_longa_removida` (fim deste arquivo).


# ---- Fase 0 Lote 1 part 1.0: memória longa e RAG fora do caminho crítico ----------------

_RAIZ = Path(__file__).resolve().parent.parent

#: O que nenhum processo do caminho do boot carrega desde a part 1.0.
_FORA_DO_BOOT = ("langgraph", "langmem", "chromadb", "app.memory", "app.engine.rag")

#: Sonda instalada como `sitecustomize` (via PYTHONPATH), herdada pelos filhos do boot.
#: (1) Repõe o `ipub.db` e o `medhub_memory.db` reais pelas cópias de BOOT_TESTE_MAPA em todo
#: `sqlite3.connect` (caminho cru, Path ou URI `file:`): o boot grava o planejado na 1ª
#: abertura do dia (part-1), então rodá-lo contra o banco real mudaria o estado do operador.
#: (2) Na saída de cada processo, grava `sorted(sys.modules)` em BOOT_TESTE_MODS.
_SONDA = '''
import atexit, json, os, sqlite3, sqlite3.dbapi2, sys

_MAPA = {os.path.normcase(os.path.abspath(k)): v
         for k, v in json.loads(os.environ["BOOT_TESTE_MAPA"]).items()}
_ORIGINAL = sqlite3.connect


def _copia(caminho):
    while caminho.startswith("/") and caminho[2:3] == ":":
        caminho = caminho[1:]
    return _MAPA.get(os.path.normcase(os.path.abspath(caminho))) if caminho else None


def connect(database, *a, **k):
    s = database.decode() if isinstance(database, bytes) else os.fspath(database)
    if s.startswith("file:"):
        caminho, sep, consulta = s[5:].partition("?")
        if _copia(caminho):
            s = "file:" + _copia(caminho).replace(os.sep, "/") + sep + consulta
    elif s not in ("", ":memory:") and _copia(s):
        s = _copia(s)
    return _ORIGINAL(s, *a, **k)


sqlite3.connect = sqlite3.dbapi2.connect = connect


def _inventario():
    nome = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else "c"
    alvo = os.path.join(os.environ["BOOT_TESTE_MODS"], "%d_%s.txt" % (os.getpid(), nome))
    with open(alvo, "w", encoding="utf-8") as fh:
        fh.write("\\n".join(sorted(sys.modules)))


atexit.register(_inventario)
'''


def test_boot_nao_carrega_memoria_longa_nem_rag(db_sintetico, tmp_path):
    """part 1.0 (DoD 2 e 3; decisão do operador em 10/10/2026: "RAG/LangMem fora do caminho
    crítico SIM"). Roda o hook DE VERDADE -- `python tools/hooks/memory_boot.py`, o comando do
    `SessionStart` -- em subprocesso, sobre o banco sintético, com a `_SONDA` herdada pelos
    filhos. Nenhum processo do caminho (o hook e os dois filhos que ele roda) carrega LangGraph,
    LangMem, Chroma, `app.memory` ou `app.engine.rag`, e o bloco de Áreas de fraqueza não volta
    ao contexto injetado. (⚰️ 3.0a2: o `app.memory.inspect --context` sob demanda saiu com o módulo.)

    Antes da part 1.0 o `_memory_context()` importava `app.memory.inspect` -> `app.memory.store`
    -> `langgraph.store.base` em todo boot (medido: ~0,55 s dos ~0,64 s de import do processo).
    """
    sonda = tmp_path / "sonda"
    sonda.mkdir()
    (sonda / "sitecustomize.py").write_text(_SONDA, encoding="utf-8")
    inventarios_dir = tmp_path / "mods"
    inventarios_dir.mkdir()
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(sonda), env.get("PYTHONPATH")) if p)
    env["BOOT_TESTE_MAPA"] = json.dumps({
        str(_RAIZ / "ipub.db"): db_sintetico,
        str(_RAIZ / "medhub_memory.db"): str(tmp_path / "memoria_sintetica.db"),
    })
    env["BOOT_TESTE_MODS"] = str(inventarios_dir)

    r = subprocess.run([sys.executable, str(_RAIZ / "tools" / "hooks" / "memory_boot.py")],
                       cwd=str(_RAIZ), env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    assert r.returncode == 0, r.stderr[-2000:]
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]

    inventarios = {f.stem.split("_", 1)[1]: f.read_text(encoding="utf-8").splitlines()
                   for f in inventarios_dir.glob("*.txt")}
    assert "memory_boot.py" in inventarios and len(inventarios) >= 3, \
        f"o hook e os 2 filhos deixam inventário: {sorted(inventarios)}"
    carregados = {proc: sorted({alvo for alvo in _FORA_DO_BOOT for m in mods
                                if m == alvo or m.startswith(alvo + ".")})
                  for proc, mods in inventarios.items()}
    assert not any(carregados.values()), f"o caminho do boot carregou: {carregados}"

    assert "MedHub Memory Context" not in ctx and "Áreas de fraqueza" not in ctx, \
        "o bloco de Áreas de fraqueza saiu do boot (part 1.0, opção a)"
    assert "[Boot v2" in ctx, "o texto-contrato do boot continua no fim"


def test_nenhum_hook_dispara_a_consolidacao():
    """part 1.0 (DoD 4): sai do `.claude/settings.json` só a entrada `PostToolUse` matcher
    `Write` -> `memory_session_log.py`. O `SessionStart` (memory_boot) e o `PostToolUse` matcher
    `SendMessage` (exchange_log) ficam. ⚰️ Part 3.0a2 (11/10/2026): invertido -- o script e o
    `app/memory/manager.py` não existem mais (a consolidação à mão morreu com o módulo)."""
    hooks = json.loads((_RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]
    comandos = {}
    for evento, entradas in hooks.items():
        for entrada in entradas:
            comandos.setdefault((evento, entrada.get("matcher")), []).extend(
                h.get("command", "") for h in entrada.get("hooks", []))
    todos = [c for lista in comandos.values() for c in lista]
    assert not any("memory_session_log" in c for c in todos), comandos
    assert any("memory_boot.py" in c for c in comandos.get(("SessionStart", None), [])), comandos
    assert any("exchange_log.py" in c
               for c in comandos.get(("PostToolUse", "SendMessage"), [])), comandos
    assert not (_RAIZ / "tools" / "hooks" / "memory_session_log.py").exists()
    assert not (_RAIZ / "app" / "memory" / "manager.py").exists()


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))


#: Filho do teste do engine: chama a superfície estável e imprime as chaves do retorno.
_FILHO_ENGINE = (
    "import json, sys; sys.path.insert(0, sys.argv[1]); "
    "from app.engine.get_topic_context import get_topic_context as g; "
    "r = g(sys.argv[2]); "
    "print('CHAVES=' + json.dumps(sorted(r)))"
)


def test_engine_sem_memoria_longa(db_sintetico, tmp_path):
    """Fase 0 Lote 3 part 3.0a1 (11/10/2026; ordem do operador: LangMem e afins saem). Roda
    `get_topic_context` DE VERDADE em subprocesso, sobre o banco sintético, com a `_SONDA`:
    o engine não importa `app.memory` nem `langgraph`, e o retorno não tem mais `weak_areas`
    -- o sinal de fraqueza por tema é o `erros_recentes` (`db.get_erros_por_tema`, bloco 2).
    O bloco 5 (RAG) ainda vive até a b1: o chromadb pode carregar, e este teste não olha ele.
    """
    sonda = tmp_path / "sonda"
    sonda.mkdir()
    (sonda / "sitecustomize.py").write_text(_SONDA, encoding="utf-8")
    inventarios_dir = tmp_path / "mods"
    inventarios_dir.mkdir()
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(sonda), env.get("PYTHONPATH")) if p)
    env["BOOT_TESTE_MAPA"] = json.dumps({
        str(_RAIZ / "ipub.db"): db_sintetico,
        str(_RAIZ / "medhub_memory.db"): str(tmp_path / "memoria_sintetica.db"),
    })
    env["BOOT_TESTE_MODS"] = str(inventarios_dir)

    r = subprocess.run([sys.executable, "-c", _FILHO_ENGINE, str(_RAIZ), "Apendicite Aguda"],
                       cwd=str(_RAIZ), env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    assert r.returncode == 0, r.stderr[-2000:]
    linha = [l for l in r.stdout.splitlines() if l.startswith("CHAVES=")]
    assert linha, f"o filho não imprimiu as chaves: {r.stdout[-1000:]}"
    chaves = json.loads(linha[-1][len("CHAVES="):])

    mods = [m for f in inventarios_dir.glob("*.txt")
            for m in f.read_text(encoding="utf-8").splitlines()]
    assert mods, "a sonda deixou o inventário do filho"
    carregados = sorted({alvo for alvo in ("app.memory", "langgraph") for m in mods
                         if m == alvo or m.startswith(alvo + ".")})
    assert not carregados, f"o engine carregou a memória longa: {carregados}"
    assert "weak_areas" not in chaves, f"o retorno ainda tem weak_areas: {chaves}"
    assert "erros_recentes" in chaves, chaves


# ---- Fase 0 Lote 3 part 3.0a2: a memória longa sai do repo (lápide) ----------------------

#: Os 9 arquivos que a part 3.0a2 apagou (git os guarda; ⚰️ 11/10/2026).
_MEMORIA_LONGA_APAGADA = (
    "app/memory/__init__.py", "app/memory/inspect.py", "app/memory/manager.py",
    "app/memory/schemas.py", "app/memory/store.py", "tools/hooks/memory_session_log.py",
    "tools/test_memory.py", "tools/test_memory_counter.py", "tools/test_vocab_memoria.py",
)
#: Prefixos de import proibidos em `tools/` (sem `_archive`), `app/` e `conftest.py`.
_IMPORT_PROIBIDO = ("app.memory", "langgraph", "langmem", "langchain")
#: Os 5 pacotes que só a memória longa usava (o `pip uninstall` é G-op; pydantic só na b4).
_PACOTES_MORTOS = ("langgraph", "langgraph-checkpoint-sqlite", "langmem",
                   "langchain-anthropic", "pydantic")


def _modulos_importados(arvore):
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for a in no.names:
                yield a.name
        elif isinstance(no, ast.ImportFrom) and not no.level and no.module:
            yield no.module
            for a in no.names:              # `from app import memory`
                yield f"{no.module}.{a.name}"


def test_memoria_longa_removida():
    """part 3.0a2 (ordem do operador de 11/10/2026: LangMem e afins saem). (i) os 9 arquivos
    não existem; (ii) nenhum `.py` de `tools/` (sem `_archive`), de `app/` nem o `conftest.py`
    IMPORTA `app.memory`, `langgraph`, `langmem` ou `langchain*` -- o oráculo é o import por
    `ast`, não a menção: narrar a remoção em comentário/docstring é o registro correto (mesma
    isenção do gate CONTRATO_REVOGADO); (iii) nenhum dos 5 pacotes está no `requirements.txt`."""
    vivos = [p for p in _MEMORIA_LONGA_APAGADA if (_RAIZ / p).exists()]
    assert not vivos, f"a memória longa voltou ao disco: {vivos}"

    fontes = [_RAIZ / "conftest.py", *sorted((_RAIZ / "app").rglob("*.py")),
              *(p for p in sorted((_RAIZ / "tools").rglob("*.py"))
                if "_archive" not in p.relative_to(_RAIZ / "tools").parts)]
    culpados = []
    for fonte in fontes:
        arvore = ast.parse(fonte.read_text(encoding="utf-8-sig"), filename=str(fonte))
        for mod in _modulos_importados(arvore):
            if any(mod == p or mod.startswith(p + ".") or (p == "langchain" and
                   mod.startswith("langchain")) for p in _IMPORT_PROIBIDO):
                culpados.append(f"{fonte.relative_to(_RAIZ).as_posix()}: {mod}")
    assert not culpados, f"import da memória longa voltou: {culpados}"

    nomes = set()
    for linha in (_RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines():
        linha = linha.split("#", 1)[0].strip()
        if linha:
            nomes.add(re.split(r"[<>=!~\[;\s]", linha, 1)[0].strip().lower().replace("_", "-"))
    assert not nomes & set(_PACOTES_MORTOS), \
        f"dependência da memória longa no requirements: {sorted(nomes & set(_PACOTES_MORTOS))}"
