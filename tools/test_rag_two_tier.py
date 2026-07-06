#!/usr/bin/env python3
"""test_rag_two_tier.py -- testes do RAG two-tier / tier bruto pdf_raw (F17, part-2).

Estrutura:
  - Logica pura (sem Chroma/Ollama): _chunk_plain, _norm_tema, _tema_norm_de_hit,
    _aplica_sombreamento (sombreamento), index_pdf incremental (fake collection).
  - Live guardado (Chroma + Ollama): index_pdf real + search_two_tier ponta-a-ponta
    (orfao -> pdf_raw marcado; tema com gold -> sombreado). SKIP gracioso se offline.

Uso: python tools/test_rag_two_tier.py  OU  pytest tools/test_rag_two_tier.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import app.engine.rag as rag  # noqa: E402


class FakeCollection:
    """Collection ChromaDB fake (duck-typed) para testar index_pdf sem Ollama."""

    def __init__(self):
        self.store = {}  # id -> (doc, meta)

    def get(self, where=None, limit=None, include=None):
        origem = (where or {}).get("origem")
        metas = [m for (_d, m) in self.store.values() if m.get("origem") == origem]
        if limit:
            metas = metas[:limit]
        return {"metadatas": metas}

    def delete(self, where=None):
        origem = (where or {}).get("origem")
        for k in [k for k, (_d, m) in self.store.items() if m.get("origem") == origem]:
            del self.store[k]

    def upsert(self, ids, documents, metadatas):
        for i, d, m in zip(ids, documents, metadatas):
            self.store[i] = (d, m)


# ------------------------- logica pura -------------------------

def test_chunk_plain():
    txt = ("A" * 2000) + "\n\n" + ("B" * 10) + "\n\n" + ("C" * 200)
    chunks = rag._chunk_plain(txt, max_chars=1500)
    assert chunks, "esperava chunks"
    assert all(len(c) <= 1500 for c in chunks), "paragrafo gigante nao foi fatiado"
    assert all(len(c) >= 50 for c in chunks), "chunk curto nao foi descartado"
    assert not any(c.strip() == "B" * 10 for c in chunks), "curto virou chunk isolado"


def test_norm_tema():
    # prefixo EMED + acento + case colapsam
    assert rag._norm_tema("12 - Apendicite Aguda") == rag._norm_tema("Apendicite Aguda")
    assert rag._norm_tema("Cirrose Hep" + chr(0x00e1) + "tica") == rag._norm_tema("Cirrose Hepatica")
    assert rag._norm_tema("Meckel") != rag._norm_tema("Apendicite")


def test_tema_norm_de_hit_alinha_gold_e_pdf():
    # a chave de sombreamento do gold (stem do path) casa com a do pdf_raw (tema)
    gold_hit = {"metadata": {"source": "resumos/Cirurgia/Apendicite Aguda.md", "section": "x"}}
    pdf_hit = {"metadata": {"source": "pdf_raw", "tema": "12 - Apendicite Aguda"}}
    assert rag._tema_norm_de_hit(gold_hit) == rag._tema_norm_de_hit(pdf_hit)


def test_aplica_sombreamento():
    temas_gold = {rag._norm_tema("Apendicite Aguda")}
    hits = [
        {"text": "a", "distance": 0.10, "metadata": {"source": "pdf_raw", "tema": "12 - Apendicite Aguda"}},  # sombreado
        {"text": "b", "distance": 0.20, "metadata": {"source": "pdf_raw", "tema": "Meckel"}},                  # passa
        {"text": "b", "distance": 0.25, "metadata": {"source": "pdf_raw", "tema": "Meckel"}},                  # dup texto
        {"text": "c", "distance": 0.90, "metadata": {"source": "pdf_raw", "tema": "Hernia"}},                  # > max_distance
    ]
    out = rag._aplica_sombreamento(hits, temas_gold, max_distance=0.35, faltam=5)
    assert [h["text"] for h in out] == ["b"], out


def test_index_pdf_incremental_skip(tmp_path):
    pdf = tmp_path / "Tema X.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    fake = FakeCollection()

    n1 = rag.index_pdf(pdf, collection=fake, extractor=lambda p: "paragrafo de teste " * 30)
    assert n1 > 0, "primeira indexacao deveria inserir chunks"
    total = len(fake.store)

    # segunda chamada, mesmo mtime -> pula (custo zero), nao re-embedda
    n2 = rag.index_pdf(pdf, collection=fake, extractor=lambda p: "conteudo diferente " * 30)
    assert n2 == 0, "mtime inalterado deveria pular"
    assert len(fake.store) == total, "nada deveria mudar no skip"


def test_index_pdf_reindex_on_mtime_change(tmp_path):
    pdf = tmp_path / "Tema Y.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    fake = FakeCollection()
    # chunk antigo com mtime "0" (forcado)
    fake.upsert(ids=["old::0"], documents=["velho " * 30],
                metadatas=[{"source": "pdf_raw", "origem": str(pdf), "tema": "Tema Y", "mtime": "0"}])

    n = rag.index_pdf(pdf, collection=fake, extractor=lambda p: "novo conteudo " * 40)
    assert n > 0, "mtime mudou -> deveria reindexar"
    assert "old::0" not in fake.store, "chunk antigo deveria ter sido removido"
    assert all(m.get("mtime") != "0" for (_d, m) in fake.store.values()), "restou chunk stale"


# ------------------------- live (guardado) -------------------------

def _ollama_vivo():
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def test_two_tier_live(tmp_path):
    if not rag._CHROMA_AVAILABLE or not _ollama_vivo():
        print("  SKIP test_two_tier_live (ChromaDB/Ollama offline)")
        return

    orig_path = rag.CHROMA_PATH
    rag.CHROMA_PATH = str(tmp_path / "chroma")
    try:
        # gold com UM tema
        resumos = tmp_path / "resumos" / "Cirurgia"
        resumos.mkdir(parents=True)
        # Corpo >= _MIN_CHUNK_CHARS (100): secao curta demais e descartada no
        # chunking do gold e nao produziria hit (o gold precisa existir para
        # o sombreamento ter o que sombrear).
        (resumos / "Apendicite Aguda.md").write_text(
            "---\narea: Cirurgia\n---\n## Quadro clinico\n"
            "Dor em fossa iliaca direita com sinal de Blumberg positivo. Apendicite "
            "aguda e o diagnostico mais provavel em jovem com dor migratoria "
            "periumbilical para a FID, anorexia, febre baixa e leucocitose. "
            "Conduta padrao: apendicectomia apos hidratacao e antibiotico.\n",
            encoding="utf-8")
        rag.index_all(resumos_dir=str(tmp_path / "resumos"), clear=True)

        # pdf_raw com dois temas: Apendicite (sombreavel) + Meckel (orfao)
        coll = rag.get_pdf_collection()
        pdf_ap = tmp_path / "Apendicite Aguda.pdf"
        pdf_ap.write_bytes(b"%PDF")
        pdf_me = tmp_path / "Diverticulo de Meckel.pdf"
        pdf_me.write_bytes(b"%PDF")
        rag.index_pdf(pdf_ap, collection=coll,
                      extractor=lambda p: "Apendicite aguda: dor em fossa iliaca direita, Blumberg. " * 20)
        rag.index_pdf(pdf_me, collection=coll,
                      extractor=lambda p: "Diverticulo de Meckel: regra dos 2, sangramento indolor no lactente. " * 20)

        # (a) tema orfao (Meckel) -> retorna hit marcado pdf_raw
        res_me = rag.search_two_tier("diverticulo de Meckel regra dos 2 sangramento",
                                     n_results=5, use_hyde=False, max_distance=0.5)
        assert any(h["metadata"].get("source") == "pdf_raw" for h in res_me), \
            f"esperava hit pdf_raw para tema orfao; veio {[h['metadata'] for h in res_me]}"

        # (b) tema com gold (Apendicite) -> sem pdf_raw do MESMO tema (sombreado)
        res_ap = rag.search_two_tier("apendicite aguda dor FID Blumberg conduta",
                                     n_results=5, use_hyde=False, max_distance=0.5)
        ap = rag._norm_tema("Apendicite Aguda")
        vazou = [h for h in res_ap if h["metadata"].get("source") == "pdf_raw"
                 and rag._norm_tema(h["metadata"].get("tema", "")) == ap]
        assert not vazou, f"pdf_raw do tema com gold vazou (sombreamento falhou): {vazou}"
    finally:
        rag.CHROMA_PATH = orig_path


if __name__ == "__main__":
    import tempfile

    falhas = []

    def _run(fn, precisa_tmp):
        try:
            if precisa_tmp:
                # ignore_cleanup_errors: ChromaDB mantem handles abertos no
                # Windows (WinError 32 no rmtree); a limpeza nao deve falhar o teste.
                with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
                    fn(Path(d))
            else:
                fn()
            print(f"  OK  {fn.__name__}")
        except AssertionError as e:
            falhas.append(fn.__name__)
            print(f"FALHOU {fn.__name__}: {e}")
        except Exception as e:
            falhas.append(fn.__name__)
            print(f"ERRO  {fn.__name__}: {e}")

    _run(test_chunk_plain, False)
    _run(test_norm_tema, False)
    _run(test_tema_norm_de_hit_alinha_gold_e_pdf, False)
    _run(test_aplica_sombreamento, False)
    _run(test_index_pdf_incremental_skip, True)
    _run(test_index_pdf_reindex_on_mtime_change, True)
    _run(test_two_tier_live, True)

    print()
    if falhas:
        print(f"FALHOU: {len(falhas)} check(s)")
        sys.exit(1)
    print("TODOS OS CHECKS PASSARAM (part-2 RAG two-tier)")
