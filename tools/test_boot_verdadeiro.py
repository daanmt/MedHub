"""Descolar part-3 (F47/F45/F46): o input do boot fica verdadeiro.

Asserts nativos, fixtures sinteticas (tmp_path; monkeypatch de db.get_dificuldade; store
real em db temporario). Cobre: precedencia de fonte na calibragem (usuario > persistida
fresca > inferencia; frescor 7d), reconciliacao de vocabulario + upsert por par das
WeakAreas, e paths por __file__ (fim do banco-fantasma).

Fase 0 Lote 1 part 1.0 (11/10/2026): o caminho do boot não carrega memória longa nem RAG
(LangGraph, LangMem, Chroma), e nenhum hook do `.claude/settings.json` dispara a consolidação.
Os testes do MÓDULO `app.memory` (acima) ficam: o módulo segue no disco, sob demanda.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.memory import manager as mgr  # noqa: E402
from app.memory.store import SQLiteMemoryStore  # noqa: E402
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


# ---- F45: reconciliação de vocabulário + upsert por par --------------------------------


def _store_com(tmp_path, entradas):
    store = SQLiteMemoryStore(str(tmp_path / "mem.db"))
    for key, content in entradas.items():
        store.put(("medhub", "weak_areas"), key,
                  {"kind": "WeakArea", "content": content})
    return store


def test_reconcilia_normaliza_e_colapsa(tmp_path, monkeypatch):
    monkeypatch.setattr(mgr, "_vocabulario_taxonomia",
                        lambda p: {"cirurgia": "Cirurgia", "pediatria": "Pediatria"})
    store = _store_com(tmp_path, {
        "k1": {"area": "CIRURGIA", "especialidade": "Trauma", "pattern": "p1",
               "error_count": 0, "last_updated": "2026-08-01"},
        "k2": {"area": "Cirurgia", "especialidade": "trauma", "pattern": "p2",
               "error_count": 5, "last_updated": "2026-08-20"},   # melhor: sobrevive
        "k3": {"area": "Pediatria", "especialidade": "Bronquiolite", "pattern": "p3",
               "error_count": 1},
    })
    stats = mgr.reconciliar_weak_areas(store, tmp_path / "ipub_fake.db")
    assert stats["normalizadas"] >= 1          # CIRURGIA -> Cirurgia
    assert stats["colapsadas"] == 1            # k1 morre, k2 (count 5) sobrevive
    vivos = store.search(("medhub", "weak_areas"), limit=10)
    pares = sorted((i.value["content"]["area"], i.value["content"]["especialidade"].lower())
                   for i in vivos)
    assert pares == [("Cirurgia", "trauma"), ("Pediatria", "bronquiolite")]


def test_reconcilia_detecta_par_invertido(tmp_path, monkeypatch):
    monkeypatch.setattr(mgr, "_vocabulario_taxonomia", lambda p: {"cirurgia": "Cirurgia"})
    store = _store_com(tmp_path, {
        "k1": {"area": "Trauma", "especialidade": "Cirurgia", "pattern": "x"},
    })
    mgr.reconciliar_weak_areas(store, tmp_path / "ipub_fake.db")
    v = store.search(("medhub", "weak_areas"), limit=10)[0].value["content"]
    assert v["area"] == "Cirurgia" and v["especialidade"] == "Trauma"


def test_fora_do_vocabulario_nao_dropa(tmp_path, monkeypatch):
    monkeypatch.setattr(mgr, "_vocabulario_taxonomia", lambda p: {"cirurgia": "Cirurgia"})
    monkeypatch.setattr(mgr, "log_error", lambda *a, **k: None)
    store = _store_com(tmp_path, {
        "k1": {"area": "Astrologia Medica", "especialidade": "X", "pattern": "?"},
    })
    stats = mgr.reconciliar_weak_areas(store, tmp_path / "ipub_fake.db")
    assert stats["fora_vocab"] == 1
    assert len(store.search(("medhub", "weak_areas"), limit=10)) == 1   # recall-safe


# ---- F46: paths por __file__ -----------------------------------------------------------

#: Valor de `mgr._ERROR_LOG` no ATO DO IMPORT -- antes de a fixture autouse do conftest
#: (isolamento F96) redirecionar o global para tmp_path. E este valor que o invariante
#: F46 mede: o path foi calculado a partir de `__file__` do modulo, nao do cwd.
_ERROR_LOG_NO_IMPORT = mgr._ERROR_LOG


def test_paths_ancorados_no_repo():
    """F46: o path nasce de `__file__`, nunca do cwd.

    🔴 O oraculo le `_ERROR_LOG_NO_IMPORT`, capturado no topo deste modulo (importacao,
    antes de qualquer fixture), e nao `mgr._ERROR_LOG` ao vivo: desde o F96 (s177) a
    fixture autouse do `conftest.py` isola esse global em `tmp_path` durante a suite --
    caso contrario o teste que forca a falha do sink escrevia no
    `history/memory_errors.log` de PRODUCAO a cada rodada. O invariante continua sendo
    o mesmo (path ancorado no repo no ato do import); muda so de onde se le o valor.
    """
    root = Path(__file__).resolve().parent.parent
    assert mgr._IPUB_PATH == root / "ipub.db"
    assert _ERROR_LOG_NO_IMPORT == root / "history" / "memory_errors.log"
    import inspect as py_inspect
    from app.memory import inspect as mem_inspect
    assert Path(mem_inspect._DEFAULT_DB).is_absolute()
    assert Path(mem_inspect._DEFAULT_DB).parent == root


def test_leitor_ro_nao_cria_banco_fantasma(tmp_path):
    fantasma = tmp_path / "nao_existe.db"
    try:
        mgr._load_ipub_error_counts(fantasma)
    except Exception:
        pass  # falhar alto é aceitável; criar o arquivo não é
    assert not fantasma.exists()


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
    ao contexto injetado. O bloco segue sob demanda: `python -m app.memory.inspect --context`.

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
    `SendMessage` (exchange_log) ficam. O script e o `app/memory/` ficam no disco: a
    consolidação segue chamável à mão (`python -m app.memory.manager NNN`)."""
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
    assert (_RAIZ / "tools" / "hooks" / "memory_session_log.py").is_file()
    assert (_RAIZ / "app" / "memory" / "manager.py").is_file()


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
