"""Descolar part-5 (F48): sensores do RAG — chunker, cauda órfã, staleness.

Asserts nativos, zero rede/Chroma/Ollama (funções puras + tmp_path). Os testes do chunker
seguem o CONTRATO real (`_chunk_by_headers`): split H2/H3, merge de chunk curto no anterior,
preamble curto descartado — por isso as fixtures têm corpo longo (> _MIN_CHUNK_CHARS).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.engine.rag import _chunk_by_headers, caudas_orfas  # noqa: E402
from tools.utils.state_utils import check_rag_staleness  # noqa: E402

_LONGO_A = "Asma e uma doenca inflamatoria cronica das vias aereas. " * 8
_LONGO_B = "O tratamento de manutencao usa corticoide inalatorio como base. " * 8


def test_chunker_header_simples():
    md = f"# Titulo\n\n## Fisiopatologia\n{_LONGO_A}\n\n## Tratamento\n{_LONGO_B}\n"
    chunks = _chunk_by_headers(md)
    assert len(chunks) == 2
    assert chunks[0]["header"] == "Fisiopatologia" and "inflamatoria" in chunks[0]["text"]
    assert chunks[1]["header"] == "Tratamento" and "corticoide" in chunks[1]["text"]


def test_chunker_h3_e_merge_de_curto():
    md = (f"## A\n{_LONGO_A}\n\n### A1\ncurto.\n\n### A2\n{_LONGO_B}\n")
    chunks = _chunk_by_headers(md)
    headers = [c["header"] for c in chunks]
    assert "A" in headers and "A2" in headers
    # o chunk curto (A1) foi FUNDIDO no anterior — contrato do passo 2
    assert any("curto." in c["text"] for c in chunks)
    assert "A1" not in headers


def test_chunker_preamble_longo_vira_chunk():
    md = f"{_LONGO_A}\n\n## B\n{_LONGO_B}\n"
    chunks = _chunk_by_headers(md)
    assert chunks[0]["header"] == "preamble"
    assert "inflamatoria" in chunks[0]["text"]


def test_caudas_orfas():
    atuais = ["Asma::0", "Asma::1"]
    existentes = ["Asma::0", "Asma::1", "Asma::2", "Asma::3"]
    assert caudas_orfas(atuais, existentes) == ["Asma::2", "Asma::3"]
    assert caudas_orfas(atuais, atuais) == []


def _repo(tmp_path):
    (tmp_path / "resumos").mkdir()
    (tmp_path / "resumos" / "Asma.md").write_text("## A\nx\n", encoding="utf-8")
    return tmp_path


def test_staleness_sem_carimbo(tmp_path):
    root = _repo(tmp_path)
    n, carimbo = check_rag_staleness(root)
    assert n == 1 and carimbo is None


def test_staleness_resumo_mais_novo_que_carimbo(tmp_path):
    root = _repo(tmp_path)
    meta = root / "data" / "chroma" / "index_meta.json"
    meta.parent.mkdir(parents=True)
    meta.write_text(json.dumps({"indexed_at": "2020-01-01T00:00:00"}), encoding="utf-8")
    n, carimbo = check_rag_staleness(root)
    assert n == 1 and carimbo == "2020-01-01T00:00:00"


def test_staleness_em_dia(tmp_path):
    root = _repo(tmp_path)
    meta = root / "data" / "chroma" / "index_meta.json"
    meta.parent.mkdir(parents=True)
    from datetime import datetime
    meta.write_text(json.dumps({"indexed_at": datetime.now().isoformat(timespec="seconds")}),
                    encoding="utf-8")
    assert check_rag_staleness(root) is None   # tolerância de 2s cobre a resolução do carimbo


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
