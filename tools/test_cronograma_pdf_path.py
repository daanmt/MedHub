"""Regressao (hotfix 2026-09-06, s166): o derivador do cronograma tem que achar o
`Cronograma.pdf` tambem em `data/` e degradar sem traceback quando nao existe.

`cronograma.py --check` (instrumento W5 do reconcile) abortava com
FileNotFoundError porque `PDF_PATH` era fixo na raiz e o PDF real vive em
`data/`. Fixtures sinteticas em tmp_path; nada toca o ipub.db.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cronograma  # noqa: E402


def test_resolve_prefere_raiz_e_cai_para_data(tmp_path):
    raiz = tmp_path / "Cronograma.pdf"
    data = tmp_path / "data" / "Cronograma.pdf"
    data.parent.mkdir()
    data.write_bytes(b"%PDF-fake-data")
    assert cronograma.resolve_pdf_path(str(tmp_path)) == str(data)
    raiz.write_bytes(b"%PDF-fake-root")
    assert cronograma.resolve_pdf_path(str(tmp_path)) == str(raiz)


def test_check_sem_pdf_degrada_sem_traceback(tmp_path):
    grade = tmp_path / "grade.json"
    grade.write_text('{"_meta": {"fonte_sha256": "abc"}, "semanas": []}', encoding="utf-8")
    r = cronograma.check(pdf_path=str(tmp_path / "nao_existe.pdf"), grade_path=str(grade))
    assert r["status"] == "missing_pdf"
    assert "Cronograma.pdf" in r["msg"]
