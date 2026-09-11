"""Item 1.8 (s177): varredura unica de consistencia entre REGISTROS -- G5, G10, G14,
mais as duas derivacoes que aposentam enumeracao a mao (F95 e o (ii') do F90).

O que os tres achados tem em comum: **nao tinham gate**. Alguem notava a instancia,
corrigia, e a classe voltava na sessao seguinte. A regra que o `/ai-eng` deu para esta
varredura foi explicita -- *"cada um vira CHECK de ALCANCE: 'alguem chega aqui?', nao
presenca de string"*.

🔴 **Dois vieses foram MEDIDOS e viraram regra de precisao, nao suposicao:**

1. **G10 sem isencao de lapide nasce ruidoso.** O `ROADMAP.md` e historico: ele narra o
   que foi deletado (*"o player foi removido como codigo morto"*). Uma linha que AFIRMA a
   ausencia e lapide, nao ponteiro morto -- convencao ja escrita em
   `.vibeflow/conventions.md`. Sem a isencao, 3 dos 5 achados iniciais eram falsos.
2. **G14 com mencao larga nasce 100% falso.** A 1a versao coletava todo `**F<id>**` de
   qualquer linha com `⚰️` + `FEITO` e devolveu **2 achados, os 2 falsos** -- lapide cita
   F-id vizinho o tempo todo. E `PARCIAL` **nao** e contradicao: e o meio-termo declarado
   (F16, F39: mecanismo fechado, divida de conteudo aberta). Punir isso seria punir quem
   escreveu honestamente o meio-termo. Sobrou: linha de inventario **riscada**, sujeito =
   1o F-id depois do `FEITO`, e so `ABERTO` x `FEITO` conta.

Fixtures hermeticas em tmp_path + testes de repo real (ratchet).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import consistencia_check as cc  # noqa: E402


def _repo(tmp_path, arquivos):
    for rel, conteudo in arquivos.items():
        alvo = tmp_path / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")
    return tmp_path


# --- G10: ponteiro morto x lapide --------------------------------------------

def test_path_inexistente_em_doc_de_raiz_e_achado(tmp_path):
    r = _repo(tmp_path, {"ESTADO.md": "O modelo canonico e `tools/nao_existe.py`.\n"})
    a = cc.check_paths_mortos(root=r, docs=("ESTADO.md",))
    assert len(a) == 1
    assert a[0]["payload"]["paths"] == ["tools/nao_existe.py"]


def test_path_que_existe_nao_e_achado(tmp_path):
    r = _repo(tmp_path, {"ESTADO.md": "Rode `tools/vivo.py`.\n", "tools/vivo.py": "x = 1\n"})
    assert cc.check_paths_mortos(root=r, docs=("ESTADO.md",)) == []


def test_linha_que_AFIRMA_a_ausencia_e_lapide(tmp_path):
    """`ROADMAP.md` narra o que morreu -- isso e registro, nao ponteiro quebrado."""
    r = _repo(tmp_path, {"ROADMAP.md":
                         "O player `app/pages/2_estudo.py` foi removido como codigo morto.\n"})
    assert cc.check_paths_mortos(root=r, docs=("ROADMAP.md",)) == []


def test_riscado_tambem_conta_como_lapide(tmp_path):
    r = _repo(tmp_path, {"ROADMAP.md": "~~aposentar `tools/regenerate_cards.py`~~\n"})
    assert cc.check_paths_mortos(root=r, docs=("ROADMAP.md",)) == []


# --- G14: status do ledger x lapide do inventario -----------------------------

LEDGER_ABERTO = "### F42 -- defeito qualquer -- **MEDIA** -- **ABERTO**\ntexto\n"
INV_FEITO = "| ~~1.17~~ | ⚰️ **FEITO em 10/09/2026** -- **F42** fechado com (a)+(b). | x | y |\n"


def test_cabecalho_ABERTO_com_lapide_no_inventario_e_achado(tmp_path):
    r = _repo(tmp_path, {"AUDITORIA_MEDHUB.md": LEDGER_ABERTO,
                         "docs/MEMORIA-AUDITORIA.md": INV_FEITO})
    a = cc.check_status_ledger(root=r)
    assert len(a) == 1 and a[0]["payload"]["cabecalho"] == "ABERTO"


def test_cabecalho_RESOLVIDO_nao_e_achado(tmp_path):
    r = _repo(tmp_path, {
        "AUDITORIA_MEDHUB.md": "### F42 -- defeito -- **MEDIA** -- **RESOLVIDO (s176)**\n",
        "docs/MEMORIA-AUDITORIA.md": INV_FEITO})
    assert cc.check_status_ledger(root=r) == []


def test_PARCIAL_nao_e_contradicao(tmp_path):
    """Meio-termo declarado (mecanismo fechado, conteudo aberto) e honestidade."""
    r = _repo(tmp_path, {
        "AUDITORIA_MEDHUB.md": "### F42 -- defeito -- **ALTA** -- **PARCIAL: mecanismo pronto**\n",
        "docs/MEMORIA-AUDITORIA.md": INV_FEITO})
    assert cc.check_status_ledger(root=r) == []


def test_mencao_a_F_id_VIZINHO_numa_lapide_nao_conta(tmp_path):
    """O falso-positivo que a 1a versao produziu: a lapide do F35 citava o F36."""
    inv = ("| ~~0.5~~ | ⚰️ **FEITO em 10/09** -- **F35** fechado; a familia **F36**/F63 "
           "segue aberta. | x | y |\n")
    r = _repo(tmp_path, {
        "AUDITORIA_MEDHUB.md": "### F36 -- outro defeito -- **ALTA** -- **ABERTO**\n",
        "docs/MEMORIA-AUDITORIA.md": inv})
    assert cc.check_status_ledger(root=r) == [], \
        "citar um F-id vizinho dentro de uma lapide nao o declara fechado"


def test_linha_de_prosa_nao_vira_lapide_de_inventario(tmp_path):
    """So linha de tabela RISCADA conta -- prosa com ⚰️ e FEITO nao e inventario."""
    r = _repo(tmp_path, {
        "AUDITORIA_MEDHUB.md": "### F42 -- defeito -- **MEDIA** -- **ABERTO**\n",
        "docs/MEMORIA-AUDITORIA.md": "⚰️ O **F42** foi FEITO na s176, conforme narrado.\n"})
    assert cc.check_status_ledger(root=r) == []


# --- G5: tabela gerada --------------------------------------------------------

def test_tabela_ausente_nao_inventa_achado(tmp_path):
    """Repo sem AGENTE.md: o check cala, nao acusa."""
    assert cc.check_tabela_gerada(root=tmp_path) == []


# --- derivacoes (F95 e ii') ---------------------------------------------------

def test_portadores_derivados_pegam_contrato_skill_e_codigo():
    p = cc.portadores_derivados()
    assert any(x.startswith("core/contracts/") for x in p)
    assert any(x.startswith(".claude/commands/") for x in p)
    assert "AGENTE.md" in p
    assert "tools/day_plan.py" in p, "F97: portador de CODIGO tem que entrar"
    assert len(p) > 20, f"lista derivada suspeitamente curta: {len(p)}"


def test_termos_saem_dos_marcadores_do_inventario(tmp_path):
    doc = ("prosa\n"
           "<!-- TERMO-REVOGADO: FULANO | contrato-fixture v9.9 -->\n"
           "<!-- TERMO-REVOGADO: outro termo | outro lugar -->\n")
    r = _repo(tmp_path, {"docs/MEMORIA-AUDITORIA.md": doc})
    t = cc.termos_revogados_do_ledger(root=r)
    assert t == {"FULANO": "contrato-fixture v9.9", "outro termo": "outro lugar"}


def test_sem_doc_devolve_vazio_e_quem_chama_decide(tmp_path):
    assert cc.termos_revogados_do_ledger(root=tmp_path) == {}


def test_gate_nunca_fica_sem_vocabulario():
    """O fallback e a parte que importa: derivacao que falha nao pode ESVAZIAR o
    gate -- gate vazio passa por estar vazio, que e pior que enumerar a mao."""
    from auto_check import _TERMOS_REVOGADOS, _TERMOS_SEMENTE, _PORTADORES_NORMA
    assert set(_TERMOS_SEMENTE).issubset(set(_TERMOS_REVOGADOS))
    assert len(_PORTADORES_NORMA) >= 10


# --- ratchet sobre o repo real ------------------------------------------------

def test_repo_real_consistente():
    achados = cc.run_checks()
    assert achados == [], "; ".join(f"{a['check']}:{a['alvo']}" for a in achados)


def test_todo_termo_do_codigo_tem_marcador_no_inventario():
    """(ii'): cadastrar so no codigo e a regressao que este teste impede."""
    from auto_check import _TERMOS_SEMENTE
    faltando = sorted(set(_TERMOS_SEMENTE) - set(cc.termos_revogados_do_ledger()))
    assert not faltando, (
        f"termo revogado sem marcador no §12 de docs/MEMORIA-AUDITORIA.md: {faltando}")
