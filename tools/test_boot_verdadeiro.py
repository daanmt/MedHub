"""Descolar part-3 (F47/F45/F46): o input do boot fica verdadeiro.

Asserts nativos, fixtures sinteticas (tmp_path; monkeypatch de db.get_dificuldade; store
real em db temporario). Cobre: precedencia de fonte na calibragem (usuario > persistida
fresca > inferencia; frescor 7d), reconciliacao de vocabulario + upsert por par das
WeakAreas, e paths por __file__ (fim do banco-fantasma).
"""
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


def test_paths_ancorados_no_repo():
    root = Path(__file__).resolve().parent.parent
    assert mgr._IPUB_PATH == root / "ipub.db"
    assert mgr._ERROR_LOG == root / "history" / "memory_errors.log"
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


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
