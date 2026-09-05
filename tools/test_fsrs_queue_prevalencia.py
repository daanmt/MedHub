"""Teste do opt-in --prevalencia do fsrs_queue (s165): o bucket `novos` e
reordenado por prevalencia ENAMED (alta -> media -> baixa -> sem sinal) com
desempate FIFO e corte em new_limit. Puro: nao toca banco nem FSRS."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.fsrs_queue import load_prevalencia, rank_novos_por_prevalencia  # noqa: E402


class TestPrevalencia(unittest.TestCase):
    def _cards(self):
        return [
            {"card_id": 1, "area": "Cirurgia", "tema": "Sem Sinal"},
            {"card_id": 2, "area": "Pediatria", "tema": "Imunizações"},
            {"card_id": 3, "area": "Endocrino", "tema": "DM2"},
            {"card_id": 4, "area": "Pediatria", "tema": "Imunizações"},
        ]

    def test_ordena_alta_media_sem_sinal_com_desempate_fifo(self):
        prev = {("Pediatria", "Imunizações"): 0, ("Endocrino", "DM2"): 1}
        out = rank_novos_por_prevalencia(self._cards(), prev, new_limit=None)
        self.assertEqual([c["card_id"] for c in out], [2, 4, 3, 1])

    def test_corta_em_new_limit(self):
        prev = {("Pediatria", "Imunizações"): 0}
        out = rank_novos_por_prevalencia(self._cards(), prev, new_limit=2)
        self.assertEqual([c["card_id"] for c in out], [2, 4])

    def test_sem_mapa_vira_fifo(self):
        out = rank_novos_por_prevalencia(self._cards(), {}, new_limit=None)
        self.assertEqual([c["card_id"] for c in out], [1, 2, 3, 4])

    def test_load_prevalencia_arquivo_ausente_retorna_vazio(self):
        self.assertEqual(load_prevalencia("/caminho/inexistente.json"), {})

    def test_load_prevalencia_le_ranks(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"temas": [{"area": "A", "tema": "T1", "prevalencia": "alta"},
                                 {"area": "A", "tema": "T2", "prevalencia": "media"},
                                 {"area": "A", "tema": "T3", "prevalencia": "xpto"}]}, f)
            path = f.name
        try:
            m = load_prevalencia(path)
        finally:
            os.unlink(path)
        self.assertEqual(m, {("A", "T1"): 0, ("A", "T2"): 1, ("A", "T3"): 3})


if __name__ == "__main__":
    unittest.main()
