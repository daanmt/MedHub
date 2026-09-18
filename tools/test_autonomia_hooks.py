import os
import sys
import shutil
import tempfile
import unittest
import subprocess
from pathlib import Path

# Garante compatibilidade nativa de encoding em terminais Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR / "tools"))

import audit_resumos
import setup_hooks

try:
    import cronograma
    _CRONOGRAMA_OK = True
except Exception:
    _CRONOGRAMA_OK = False

try:
    import day_plan
    _DAY_PLAN_OK = True
except Exception:
    _DAY_PLAN_OK = False

try:
    import insert_questao
    _INSERT_OK = True
except Exception:
    _INSERT_OK = False

class TestAutonomiaHooks(unittest.TestCase):
    def setUp(self):
        self.test_resumo_ok = ROOT_DIR / "resumos" / "Cirurgia" / "Quadril Pediátrico.md"
        self.test_resumo_fail = ROOT_DIR / "resumos" / "_test_autonomia_fail.md"

    def tearDown(self):
        if self.test_resumo_fail.exists():
            try:
                self.test_resumo_fail.unlink()
            except Exception:
                pass

    def test_01_audit_resumos_pass_on_clean_file(self):
        """Verifica se audit_resumos aprova (exit code 0) um resumo canônico adequado."""
        if not self.test_resumo_ok.exists():
            self.skipTest("Arquivo de teste Quadril Pediátrico.md não encontrado.")
        
        exit_code = audit_resumos.audit_summaries([str(self.test_resumo_ok)])
        self.assertEqual(exit_code, 0, "O linter deveria aprovar o resumo limpo com exit code 0.")

    def test_02_audit_resumos_fail_on_invalid_file(self):
        """Verifica se audit_resumos reprova (exit code 1) um resumo com tabela e sem armadilhas."""
        content_fail = """# Resumo Inválido
| Tabela | Proibida |
| --- | --- |
| Erro | Erro |
Sem marcadores e sem secao de armadilhas.
"""
        with open(self.test_resumo_fail, "w", encoding="utf-8") as f:
            f.write(content_fail)

        exit_code = audit_resumos.audit_summaries([str(self.test_resumo_fail)])
        self.assertEqual(exit_code, 1, "O linter deveria reprovar o arquivo inválido com exit code 1.")

    def test_03_setup_hooks_lifecycle(self):
        """Ciclo de vida do instalador em um .git/hooks ISOLADO (tempdir).

        Hermético por construção: reatribui as constantes de path do módulo
        setup_hooks para um tempdir descartável e as restaura no finally. Nunca
        toca o .git/hooks real do repositório -- evitar isso é crítico porque o
        próprio pre-commit em execução estaria segurando esse arquivo (no Windows,
        um replace/unlink sobre ele dispararia sharing violation) e um teardown
        malfeito deixaria o hook do repo destruído ou armado indevidamente.
        """
        orig_git = setup_hooks.GIT_DIR
        orig_hooks = setup_hooks.HOOKS_DIR
        orig_pc = setup_hooks.PRE_COMMIT_PATH
        tmp = tempfile.mkdtemp(prefix="medhub_hooktest_")
        try:
            fake_hooks = Path(tmp) / ".git" / "hooks"
            fake_hooks.mkdir(parents=True)
            setup_hooks.GIT_DIR = Path(tmp) / ".git"
            setup_hooks.HOOKS_DIR = fake_hooks
            setup_hooks.PRE_COMMIT_PATH = fake_hooks / "pre-commit"

            # Instalar em ambiente limpo (sem hook prévio -> não gera .bak)
            self.assertTrue(setup_hooks.install(), "Falha na instalação do hook.")
            self.assertTrue(setup_hooks.PRE_COMMIT_PATH.exists(),
                            "O hook pre-commit deveria existir após a instalação.")
            content = setup_hooks.PRE_COMMIT_PATH.read_text(encoding="utf-8")
            self.assertIn("tools/auto_check.py --staged", content,
                          "O hook deveria invocar auto_check.py --staged.")

            # Reinstalar sobre hook existente -> gera backup .bak (idempotência)
            self.assertTrue(setup_hooks.install(), "Falha na reinstalação do hook.")
            self.assertTrue((fake_hooks / "pre-commit.bak").exists(),
                            "Reinstalar deveria preservar o anterior em pre-commit.bak.")

            # Uninstall -> restaura o backup por cima
            self.assertTrue(setup_hooks.uninstall(), "Falha no uninstall do hook.")
            self.assertTrue(setup_hooks.PRE_COMMIT_PATH.exists(),
                            "Uninstall deveria restaurar o hook a partir do .bak.")
        finally:
            setup_hooks.GIT_DIR = orig_git
            setup_hooks.HOOKS_DIR = orig_hooks
            setup_hooks.PRE_COMMIT_PATH = orig_pc
            shutil.rmtree(tmp, ignore_errors=True)

    def test_04_auto_check_cli_help(self):
        """Verifica se o orquestrador auto_check responde com sucesso na CLI."""
        cmd = [sys.executable, "-X", "utf8", "tools/auto_check.py", "--help"]
        res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, "auto_check.py --help deveria retornar exit code 0.")
        self.assertIn("--changed", res.stdout)
        self.assertIn("--all", res.stdout)

    def test_05_sync_do_drive_revogado(self):
        """⚰️ **Era `test_05_diff_drive_captura_ordem`** (Part 1 do
        boot-cronograma): `diff_drive` anexava `ordem` (a linha da celula no xlsx)
        a cada task. REMOVIDO em 18/09/2026 (plano-ssot-e-cards-v2 part-8) -- o
        Drive deixou de ser fonte, e a ordem ja era `plano_tarefas.ordem` desde a
        Parte 4.

        Vira GUARDA, como o test_06 ao lado: se a funcao voltar, isto cai."""
        if not _CRONOGRAMA_OK:
            self.skipTest("cronograma indisponivel")
        for morta in ("diff_drive", "sync_drive", "_parse_conclusao_xlsx"):
            self.assertFalse(
                hasattr(cronograma, morta),
                "%s foi revogada no part-8 -- nao reintroduzir. Snapshot do dado "
                "em artifacts/snapshot-cronograma-drive-2026-07-26.json" % morta)

    def test_06_ordem_do_plano_substituiu_a_ordem_do_xlsx(self):
        """⚰️ **Era `test_06_ordenar_por_drive_fallback`** (Part 1 do boot-cronograma):
        `day_plan._ordenar_por_drive` reordenava os temas da semana pela linha da celula
        no xlsx. REMOVIDO em 17/09/2026 (plano-ssot-e-cards-v2 Parte 4) -- a ordem virou
        a coluna `plano_tarefas.ordem`, editavel por `plano.py --mover ID --semana N
        --ordem K`, e quem a le agora e `db.plano_listar` (ORDER BY semana_plano, ordem).

        O teste vira GUARDA da revogacao: se a funcao voltar, ele cai. ⚰️ *A frase
        "o `diff_drive` do `cronograma.py` continua vivo -- o CLI so morre na Parte 8"
        valeu ate 18/09/2026: a Parte 8 chegou e o test_05 ao lado virou guarda.*"""
        if not _DAY_PLAN_OK:
            self.skipTest("day_plan indisponivel")
        self.assertFalse(hasattr(day_plan, "_ordenar_por_drive"),
                         "_ordenar_por_drive foi revogado na Parte 4 -- nao reintroduzir.")
        self.assertFalse(hasattr(day_plan, "_conclusao_drive"),
                         "_conclusao_drive foi revogado na Parte 4 -- nao reintroduzir.")

    def test_07_material_efetivo_rebaixa_sem_md(self):
        """Part 2 (F30): 'resumo' vira 'extensivo' quando o tema nao tem .md;
        rotulo != 'resumo' passa direto; tema real com .md permanece 'resumo'."""
        if not _DAY_PLAN_OK:
            self.skipTest("day_plan indisponivel")
        # tema inexistente + rotulo 'resumo' -> rebaixa (nao promete "so ler o resumo")
        self.assertEqual(
            day_plan._material_efetivo("Tema Inexistente Xyz 999", "resumo"), "extensivo")
        # rotulo != 'resumo' -> passthrough (nao mexe)
        self.assertEqual(
            day_plan._material_efetivo("Tema Inexistente Xyz 999", "extensivo"), "extensivo")
        # tema real com .md -> permanece 'resumo'
        self.assertEqual(
            day_plan._material_efetivo("Quadril Pediátrico", "resumo"), "resumo")

    def test_08_tem_lastro_detecta_ausencia(self):
        """Part 2 (F31): _tem_lastro True p/ tema com .md; False p/ tema sem
        .md nem PDF-fonte par (candidato a Siamese Twins incompleto)."""
        if not _INSERT_OK:
            self.skipTest("insert_questao indisponivel")
        self.assertTrue(insert_questao._tem_lastro("Quadril Pediátrico"))
        self.assertFalse(insert_questao._tem_lastro("Tema Inexistente Xyz 999"))

    def test_09_contador_resumos_bate_com_linter(self):
        """Part 3 (higiene): _contar_resumos() usa o MESMO glob do audit_resumos
        -> numero identico ao do linter (fim do 63x61 digitado a mao no ESTADO)."""
        if not _DAY_PLAN_OK:
            self.skipTest("day_plan indisponivel")
        import glob as _glob
        esperado = len(_glob.glob(str(audit_resumos.TEMAS_DIR / "**" / "*.md"), recursive=True))
        self.assertEqual(day_plan._contar_resumos(), esperado)
        self.assertGreater(day_plan._contar_resumos(), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
