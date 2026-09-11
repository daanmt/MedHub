"""Regressao F91 (hotfix 2026-09-10, s176): o leitor de evidencia nao pode devolver `[]`
quando a busca NAO ACONTECEU.

Caso real (s175): com o Ollama fora do ar (`WinError 10061`), `rag.search()` devolveu `[]` sem
excecao e sem WARN. Um subagente `evidence-researcher` leu esse `[]` como fato e escreveu num
relatorio que "nao ha resumo indexado sobre HPB/LUTS" -- falso: `resumos/Cirurgia/Urologia.md`
tem 39 chunks indexados. O leitor produziu um fato falso, e o agente o publicou.

Viola `core/contracts/evidence-governance.md §7` (honest-negative) na camada `local`: ausencia de
evidencia so pode ser declarada quando a busca de fato rodou.

🔴 O QUE ESTA SUITE FIXA -- a desambiguacao do `[]`. Antes, tres mundos colapsavam no mesmo
valor: (a) procurei e nao ha; (b) o motor caiu e o fallback nao achou; (c) o motor caiu e o
proprio fallback quebrou. Depois, `[]` significa SO o (a); (b) e (c) levantam `RagIndisponivel`
nomeando o backend, e o meio-termo (motor caido + fallback com hits) volta marcado
`source='fallback_textual'`.

A negativa honesta e testada explicitamente (`test_motor_vivo_sem_hit_...`): fail-loud que vira
fail-sempre destruiria a unica resposta legitimamente vazia.

Fixtures: monkeypatch sobre `rag.get_collection` / `_find_resumo`; zero dependencia de o Ollama
estar realmente no ar (o CI nao tem Ollama, e e exatamente la que o defeito seria invisivel).
"""
import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.engine import rag  # noqa: E402

# `app.engine.get_topic_context` como ATRIBUTO do pacote e a funcao (o __init__ a
# reexporta); o modulo so vem por import_module.
gtc = importlib.import_module("app.engine.get_topic_context")  # noqa: E402


class _MotorCaido:
    """Substitui get_collection(): o erro exato do caso real."""

    def __call__(self, *a, **k):
        raise ConnectionError("[WinError 10061] conexao recusada em localhost:11434")


@pytest.fixture
def motor_caido(monkeypatch):
    monkeypatch.setattr(rag, "get_collection", _MotorCaido())
    monkeypatch.setattr(rag, "_CHROMA_AVAILABLE", True)
    # HyDE tambem depende do Ollama: se o motor caiu, ele cai junto.
    monkeypatch.setattr(rag, "_generate_hypothetical_document",
                        lambda q: (_ for _ in ()).throw(ConnectionError("10061")))
    return True


@pytest.fixture
def resumo_real(tmp_path, monkeypatch):
    """Um resumo de verdade no disco, para o fallback lexico ter o que achar."""
    p = tmp_path / "Urologia.md"
    # Secoes com corpo REAL: `_chunk_by_headers` descarta chunk < 50 chars, entao um
    # fixture de brinquedo produz zero chunks e o teste mediria a coisa errada.
    p.write_text(
        "---\narea: Cirurgia\nespecialidade: Urologia\n---\n\n"
        "## Indicacoes cirurgicas na HPB\n\n"
        "- Retencao urinaria aguda refrataria ao teste de retirada da sonda vesical.\n"
        "- Litiase vesical de repeticao atribuivel a obstrucao infravesical cronica.\n"
        "- Infeccao urinaria de repeticao com residuo pos-miccional elevado.\n"
        "- Insuficiencia renal pos-renal por obstrucao prostatica documentada.\n\n"
        "## Armadilhas de Prova\n\n"
        "- Nao atribuir LUTS ao adenocarcinoma de prostata: o CaP inicial e tipicamente\n"
        "  assintomatico, e sintoma obstrutivo aponta para a zona de transicao.\n"
        "- I-PSS 8 e 20 separam leve de moderado e moderado de grave.\n",
        encoding="utf-8")
    monkeypatch.setattr(gtc, "_find_resumo", lambda q: p)
    return p


# --------------------------------------------------------------------------
# 1. Motor caido + tema QUE EXISTE -> degradado marcado, nunca []
# --------------------------------------------------------------------------
def test_motor_caido_com_tema_existente_devolve_fallback_marcado(motor_caido, resumo_real):
    hits = rag.search("hiperplasia prostatica benigna indicacao cirurgica", n_results=3)

    assert hits, ("motor caido + tema existente devolveu vazio -- e o caso exato que fez um "
                  "subagente escrever 'nao ha resumo indexado sobre HPB/LUTS'")
    assert all(h["metadata"]["source"] == "fallback_textual" for h in hits), \
        "resultado degradado sem a marca de proveniencia: %r" % [h["metadata"] for h in hits]


def test_motor_caido_avisa_em_stderr_nomeando_o_backend(motor_caido, resumo_real, capsys):
    rag.search("hiperplasia prostatica benigna", n_results=3)
    err = capsys.readouterr().err.lower()
    assert "warn" in err, "degradacao silenciosa: nada foi para stderr"
    assert "rag" in err or "ollama" in err or "chroma" in err, \
        "o WARN nao nomeia o backend que caiu: %r" % err


# --------------------------------------------------------------------------
# 2. Motor caido + fallback sem resultado -> EXCECAO, nunca []
# --------------------------------------------------------------------------
def test_motor_caido_sem_fallback_levanta_em_vez_de_mentir(motor_caido, monkeypatch):
    monkeypatch.setattr(gtc, "_find_resumo", lambda q: None)

    with pytest.raises(rag.RagIndisponivel) as exc:
        rag.search("tema qualquer sem resumo casado", n_results=3)

    assert "10061" in str(exc.value) or "ollama" in str(exc.value).lower() \
        or "chroma" in str(exc.value).lower() or "rag" in str(exc.value).lower(), \
        "a excecao nao nomeia o backend nem a causa: %r" % str(exc.value)


def test_fallback_que_quebra_por_dentro_acusa_a_propria_falha(motor_caido, resumo_real, monkeypatch):
    """O `except Exception: return []` do fim do fallback era o pior dos silencios:
    colapsava 'a salvaguarda quebrou' em 'nao ha nada'."""
    monkeypatch.setattr(rag, "_chunk_by_headers",
                        lambda *a, **k: (_ for _ in ()).throw(ValueError("chunker quebrado")))

    with pytest.raises(rag.RagIndisponivel):
        rag.search("hiperplasia prostatica benigna", n_results=3)


# --------------------------------------------------------------------------
# 3. A NEGATIVA HONESTA sobrevive -- fail-loud nao pode virar fail-sempre
# --------------------------------------------------------------------------
class _ColecaoVazia:
    def query(self, *a, **k):
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}


def test_motor_vivo_sem_hit_continua_devolvendo_lista_vazia(monkeypatch):
    monkeypatch.setattr(rag, "_CHROMA_AVAILABLE", True)
    monkeypatch.setattr(rag, "get_collection", lambda *a, **k: _ColecaoVazia())
    monkeypatch.setattr(rag, "_generate_hypothetical_document", lambda q: q)

    assert rag.search("tema inexistente no corpus", n_results=3) == [], \
        "a negativa honesta virou excecao -- fail-loud nao pode virar fail-sempre"


def test_motor_vivo_com_hits_e_caminho_inalterado(monkeypatch):
    class _ColecaoComHit:
        def query(self, *a, **k):
            return {"documents": [["texto do chunk"]],
                    "metadatas": [[{"source": "resumo", "section": "H2"}]],
                    "distances": [[0.10]]}

    monkeypatch.setattr(rag, "_CHROMA_AVAILABLE", True)
    monkeypatch.setattr(rag, "get_collection", lambda *a, **k: _ColecaoComHit())
    monkeypatch.setattr(rag, "_generate_hypothetical_document", lambda q: q)

    hits = rag.search("qualquer", n_results=3)
    assert len(hits) == 1 and hits[0]["distance"] == 0.10
    assert hits[0]["metadata"]["source"] == "resumo", "o caminho semantico feliz foi alterado"


# --------------------------------------------------------------------------
# 4. O consumidor para de mascarar (2o silenciador, em serie)
# --------------------------------------------------------------------------
def test_get_topic_context_declara_a_degradacao_em_vez_de_engoli_la(motor_caido, monkeypatch):
    monkeypatch.setattr(gtc, "_find_resumo", lambda q: None)

    ctx = gtc.get_topic_context("Urologia")

    assert ctx.get("rag_degradado"), (
        "get_topic_context:175-179 tinha `except Exception: pass` -- mesmo uma excecao do RAG "
        "virava `relevant_chunks: []`, como se o corpus estivesse vazio")
    assert not ctx.get("relevant_chunks"), \
        "nao pode entregar chunks E declarar degradacao total"
