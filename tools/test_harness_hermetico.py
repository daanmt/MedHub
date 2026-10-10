"""test_harness_hermetico.py -- Fase 0 · Lote 0 · part-1 (/ai-eng, 10/10/2026).

Hooks e pre-commit não escrevem nem pulam. Três defeitos, um teste (ou mais) para cada:

1. O boot regravava o plano do dia a cada abertura (/clear, sessão do tique): o hook rodava
   `tools/day_plan.py` sem `--no-persist` e o `persistir_plano` fazia DELETE + INSERT com os
   defaults, apagando a intenção declarada de manhã (`--tempo/--energia`). Agora grava só a
   1ª abertura do dia; dúvida (banco/tabela ausente, erro) = não gravar.
2. O pre-commit pulava: o gatilho da suíte era por EXTENSÃO (`.py` em tools/core) e, sem flag
   acesa, um early-return imprimia "Nenhum arquivo crítico... Aprovado!" ANTES dos checks que o
   próprio código chama de "Roda SEMPRE" (CLI_ASSINATURA e cláusulas incluídos, ambos BLOCK).
   Caso real (s216): commit só de `core/hub_quadro.json` + `artifacts/aula-*.html` passou sem
   `test_hub_quadro`. Deleção staged (`--diff-filter=ACMR`) também não acendia nada.
3. O harness sujava a árvore a cada commit: `history/ledger_self.jsonl` e
   `history/card_watermark.json` eram rastreados e gravados DEPOIS do stage.

Rodar o hook real dentro da suíte recursa (o hook roda a suíte, que roda o teste, que
commita) -- por isso `main()` in-process com `run_command` substituído + invariante do git em
subprocess; o commit real é verificado à parte (DoD 5a). Bancos sintéticos em tmp_path; o
ipub.db real e o ledger real nunca são tocados.
"""
import sqlite3
import subprocess
import sys
import types
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import auto_check  # noqa: E402
import consistencia_check  # noqa: E402

_CONSISTENCIA_REAL = consistencia_check.run_checks
_SUITE =[sys.executable, "-m", "pytest", "tools/", "-q"]

_DDL_PLANO_DIA = """
CREATE TABLE plano_dia (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    data               TEXT NOT NULL,
    ordem              INTEGER NOT NULL,
    task_tipo          TEXT NOT NULL,
    alvo_tema          TEXT,
    volume_planejado   INTEGER NOT NULL DEFAULT 0,
    tempo_h            REAL,
    energia            TEXT,
    defaults_assumidos INTEGER NOT NULL DEFAULT 0,
    criado_em          TEXT NOT NULL
)
"""


# --------------------------------------------------------------------------------------
# 1. Boot grava no máximo uma vez por dia
# --------------------------------------------------------------------------------------

def _hook_de_boot(monkeypatch):
    """O hook não é pacote importável: carrega por path (mesmo padrão do F102). O import faz
    `os.chdir(PROJECT_ROOT)`; o `monkeypatch.chdir` devolve o cwd original no teardown."""
    import importlib.util
    monkeypatch.chdir(ROOT)
    spec = importlib.util.spec_from_file_location(
        "memory_boot_hermetico", ROOT / "tools" / "hooks" / "memory_boot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _db_com_plano(caminho, datas):
    con = sqlite3.connect(str(caminho))
    try:
        con.execute(_DDL_PLANO_DIA)
        for i, d in enumerate(datas, 1):
            con.execute("INSERT INTO plano_dia (data, ordem, task_tipo, volume_planejado, criado_em) "
                        "VALUES (?, ?, 'questoes', 0, ?)", (d, i, f"{d}T07:00:00"))
        con.commit()
    finally:
        con.close()
    return caminho


def _argv_do_day_plan(mb, monkeypatch, db_path):
    """argv que o hook entrega ao `subprocess.run` do day_plan, com o banco apontado para
    `db_path`. O subprocess é falso: nada roda, nada grava."""
    chamadas = []

    def falso_run(argv, **_kw):
        chamadas.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    # raising=False: antes do fix o atributo não existe -- o vermelho tem de ser a ASSERÇÃO.
    monkeypatch.setattr(mb, "_IPUB_DB", Path(db_path), raising=False)
    monkeypatch.setattr(mb, "subprocess", types.SimpleNamespace(run=falso_run))
    mb._day_plan_summary()
    do_day_plan = [a for a in chamadas if any("day_plan.py" in str(x) for x in a)]
    assert len(do_day_plan) == 1, chamadas
    return do_day_plan[0]


def test_boot_nao_regrava_plano_do_dia(tmp_path, monkeypatch):
    mb = _hook_de_boot(monkeypatch)
    hoje = date.today().isoformat()          # o mesmo date.today() de day_plan.build()
    ontem = (date.today() - timedelta(days=1)).isoformat()

    com_hoje = _db_com_plano(tmp_path / "com_hoje.db", [ontem, hoje])
    assert "--no-persist" in _argv_do_day_plan(mb, monkeypatch, com_hoje), \
        "o dia já tem plano: a 2ª abertura não pode regravar a intenção declarada"

    sem_hoje = _db_com_plano(tmp_path / "sem_hoje.db", [ontem])
    assert "--no-persist" not in _argv_do_day_plan(mb, monkeypatch, sem_hoje), \
        "1ª abertura do dia grava o planejado -- a série de aderência depende disso"

    ausente = tmp_path / "ausente.db"
    assert "--no-persist" in _argv_do_day_plan(mb, monkeypatch, ausente), \
        "banco ausente = dúvida = não gravar"
    assert not ausente.exists(), "a consulta do boot não pode criar o banco (mode=ro)"

    sem_tabela = tmp_path / "sem_tabela.db"
    con = sqlite3.connect(str(sem_tabela))
    con.execute("CREATE TABLE outra (id INTEGER)")
    con.commit()
    con.close()
    assert "--no-persist" in _argv_do_day_plan(mb, monkeypatch, sem_tabela), \
        "tabela ausente = dúvida = não gravar"


# --------------------------------------------------------------------------------------
# 2. Gatilho da suíte por prefixo, não por extensão
# --------------------------------------------------------------------------------------

def test_gatilho_da_suite_por_prefixo():
    dispara = ["core/hub_quadro.json", "core/templates/hub.html", "artifacts/aula-rd-x.html",
               "app/utils/areas.py", ".claude/commands/revisar.md",
               ".agents/workflows/curar-cards.md", "tools/x.py", "pytest.ini", "conftest.py",
               "requirements.txt"]
    for f in dispara:
        assert auto_check.dispara_suite_por_caminho([f]) is True, f
    nao_dispara = ["history/session_223.md", ".vibeflow/specs/x.md", "docs/x.md",
                   "resumos/GO/X.md", "ROADMAP.md"]
    for f in nao_dispara:
        assert auto_check.dispara_suite_por_caminho([f]) is False, f
    assert auto_check.dispara_suite_por_caminho([]) is False
    assert auto_check.dispara_suite_por_caminho(nao_dispara) is False
    assert auto_check.dispara_suite_por_caminho(nao_dispara + ["core/hub_quadro.json"]) is True
    # Barra invertida (Windows) normaliza, como em dispara_suite_por_selo; prefixo, não substring.
    assert auto_check.dispara_suite_por_caminho(["core\\hub_quadro.json"]) is True
    assert auto_check.dispara_suite_por_caminho(["docs/tools/x.md"]) is False


# --------------------------------------------------------------------------------------
# 3. main() usa o gatilho, conta deleções e nunca pula os "sempre"
# --------------------------------------------------------------------------------------

def _main_staged(monkeypatch, capsys, staged, deletados=(), sempre_real=True):
    """`auto_check.main()` in-process no modo --staged. O que grava (ledger, watermark) e o
    que executa (run_command) ficam substituídos; os sensores "sempre" rodam de verdade sobre
    o repo, em leitura.

    `sempre_real=False` troca SÓ o `consistencia_check.run_checks` (medido: ~17 s por run, quase
    todo o custo dos "sempre") por um vazio -- nos casos cujo assunto é o GATILHO da suíte. O
    caso dos "sempre" roda com ele real."""
    monkeypatch.setattr(consistencia_check, "run_checks",
                        _CONSISTENCIA_REAL if sempre_real else (lambda *a, **k: []))
    chamadas = []

    def falso_run(cmd, desc, capture=False):
        chamadas.append(list(cmd))
        return True, ""

    monkeypatch.setattr(sys, "argv", ["auto_check.py", "--staged"])
    monkeypatch.setattr(auto_check, "get_staged_files", lambda: list(staged))
    # raising=False: antes do fix o leitor de deleções não existe.
    monkeypatch.setattr(auto_check, "_staged_deletados", lambda: list(deletados), raising=False)
    monkeypatch.setattr(auto_check, "run_command", falso_run)
    monkeypatch.setattr(auto_check, "_ledger_record", lambda *a, **k: None)
    monkeypatch.setattr(auto_check, "card_watermark_mudou", lambda *a, **k: (False, None))
    monkeypatch.setattr(auto_check, "card_watermark_selar", lambda *a, **k: None)
    capsys.readouterr()
    auto_check.main()
    return chamadas, capsys.readouterr().out


def test_staged_core_json_roda_a_suite(monkeypatch, capsys):
    chamadas, _ = _main_staged(monkeypatch, capsys, ["core/hub_quadro.json"], sempre_real=False)
    assert _SUITE in chamadas, \
        "core/hub_quadro.json staged tem de rodar a suíte (s216: test_hub_quadro ficou de fora)"

    chamadas, _ = _main_staged(monkeypatch, capsys, [], deletados=["tools/x.py"],
                               sempre_real=False)
    assert _SUITE in chamadas, "só a deleção staged de tools/x.py também roda a suíte"

    chamadas, out = _main_staged(monkeypatch, capsys, ["docs/x.md"])
    assert _SUITE not in chamadas, "docs/ fora do gatilho: a suíte não roda"
    assert "Nenhum arquivo crítico" not in out, "a frase que mentia sobre o que não rodou sai"
    assert "Suíte não exigida para este recorte" in out
    assert "RELATÓRIO FINAL" in out, "sem early-return: o fluxo chega ao relatório"
    relatorio = out.split("RELATÓRIO FINAL", 1)[1]
    for desc in ("Assinatura canonica de CLI (D5)", "Clausula normativa com terminal (1.10)"):
        assert desc in relatorio, f"check 'sempre' pulado: {desc}"


# --------------------------------------------------------------------------------------
# 4. Runtime do harness fora do git
# --------------------------------------------------------------------------------------

def test_runtime_do_harness_fora_do_git():
    """Os 3 arquivos que o harness grava durante o commit (ledger de eventos, estado derivado
    do ledger, watermark de card) não são rastreados e estão no .gitignore -- gravados DEPOIS do
    stage, sujavam a árvore a cada commit.

    Limite declarado: prova os 3 caminhos conhecidos; não prova que não exista um 4º escritor
    -- o DoD 5a (`git status --porcelain` logo depois do commit real) cobre isso empiricamente.
    """
    import ledger_self
    from tools.utils import state_utils

    problemas = []
    for p in [*ledger_self._paths(), state_utils.WATERMARK_PATH]:
        rel = Path(p).resolve().relative_to(ROOT).as_posix()
        rastreado = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", "--", rel],
            capture_output=True, text=True)
        if rastreado.returncode == 0:
            problemas.append(f"{rel}: ainda rastreado (git rm --cached)")
        ignorado = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", "--", rel])
        if ignorado.returncode != 0:
            problemas.append(f"{rel}: git check-ignore não casa (rastreado ou fora do .gitignore)")
    assert not problemas, "\n".join(problemas)
