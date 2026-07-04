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

if __name__ == "__main__":
    unittest.main(verbosity=2)
