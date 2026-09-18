"""test_status_portador.py -- G14b (s187): cabecalho do achado x o PORTADOR real.

O `check_status_ledger` (G14, s177) compara o cabecalho do achado no
`AUDITORIA_MEDHUB.md` contra a lapide do `§11` do `MEMORIA-AUDITORIA`. Ele so
enxerga achado que **alguem lembrou de por no §11**.

🔴 **F109 e F110 nunca entraram la.** Os dois tiveram os riders de doc pousados
na **s185** -- `fsrs-management-contract` v1.4 (§Politica de fila) e
`revisao-calibrada-contract` v1.5 (Clausula 13) -- e os cabecalhos do ledger
seguiram dizendo `ABERTO`. Foi lido a olho na s187, nao por gate. Consequencia
real: os dois entraram na lista "herdadas e vivas" do `HANDOFF.md`, e a lista
foi usada por DOIS agentes para planejar a janela.

Classe: **gate-miss por escopo de alvo** -- o sensor existe, mede o registro
vizinho, e o painel fica verde. Terceira ocorrencia da serie na mesma janela
(F115 · Invariante A · G14b).

Sinal usado, **derivado e nao digitado**: contrato e skill carimbam o F-id na
propria linha de versao (`**Versao 1.4 | ... (s185, F109: ...)**`). Portador que
declara ter absorvido o achado contradiz cabecalho `ABERTO`.

⚠️ **LIMITE DECLARADO:** so alcanca achado cujo remedio virou **versao de
portador**. Remedio que e so codigo, sem bump de contrato, continua invisivel
aqui. Segunda lente, nao a lente completa (secao 10.8).

🔴 **A base viva e ZERO porque a s187 corrigiu F109/F110 a mao** -- entao o teste
que prova o sensor e o **RETROATIVO**: reconstroi o estado do ledger como estava
em 17/09 e exige que o check acuse os dois. Sem ele, este arquivo seria verde
sem nunca ter visto um positivo -- a licao da s186.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import consistencia_check as cc                                # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _repo(tmp_path, ledger, contratos=None, skills=None):
    (tmp_path / "core" / "contracts").mkdir(parents=True)
    (tmp_path / ".claude" / "commands").mkdir(parents=True)
    (tmp_path / "AUDITORIA_MEDHUB.md").write_text(ledger, encoding="utf-8")
    for nome, txt in (contratos or {}).items():
        (tmp_path / "core" / "contracts" / nome).write_text(txt, encoding="utf-8")
    for nome, txt in (skills or {}).items():
        (tmp_path / ".claude" / "commands" / nome).write_text(txt, encoding="utf-8")
    return str(tmp_path)


# --- o teste que prova o sensor: o caso REAL de 17/09 ----------------------------------

def test_retroativo_o_check_acusaria_F109_e_F110():
    """Estado do repo em 17/09/2026, verbatim nas partes que importam: os dois
    contratos JA carimbavam o F-id na linha de versao e os dois cabecalhos ainda
    diziam ABERTO. Este e o positivo que o sensor existe para pegar."""
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        base = _repo(
            Path(d),
            ledger=(
                "### F109 -- premissa \"revisao em cluster e pedagogicamente superior\" "
                "contradita pela literatura -- **BAIXA/MEDIA** -- **ABERTO (so-dado + 2 riders de doc na fila)**\n"
                "- corpo qualquer\n\n"
                "### F110 -- as friccoes VIRTUOSAS do estudo nao tinham portador -- "
                "**MEDIA** -- **ABERTO (portador criado; gate impossivel, declarado)**\n"
                "- corpo qualquer\n"),
            contratos={
                "fsrs-management-contract.md":
                    "**Versao 1.4 | 2026-09-17 (s185, F109: a ordem intercalada e o default DELIBERADO)**\n",
                "revisao-calibrada-contract.md":
                    "**Versao 1.5 | 2026-09-17 (s185, F110: Clausula 13 -- friccao virtuosa nao se automatiza)**\n",
            })
        achados = cc.check_status_portador(root=base)
        ids = sorted(a["alvo"].split("§")[1] for a in achados)
        assert ids == ["F109", "F110"], achados
        assert "fsrs-management-contract.md" in achados[0]["payload"]["portadores"]


def test_cabecalho_RESOLVIDO_nao_e_achado():
    """Depois do conserto da s187 os dois tem que sair -- senao o check vira ruido
    permanente e ninguem olha mais."""
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        base = _repo(
            Path(d),
            ledger=("### F109 -- premissa contradita -- **BAIXA/MEDIA** -- "
                    "**RESOLVIDO (os 2 riders pousaram na s185)**\n"),
            contratos={"fsrs-management-contract.md":
                       "**Versao 1.4 | 2026-09-17 (s185, F109: ...)**\n"})
        assert cc.check_status_portador(root=base) == []


def test_lapide_no_cabecalho_tambem_isenta():
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        base = _repo(
            Path(d),
            ledger="### F3 -- algo -- **MEDIA** -- **ABERTO** ⚰️ superado pelo F109\n",
            contratos={"c.md": "**Versao 1.1 | 2026-01-01 (s100, F3: ...)**\n"})
        assert cc.check_status_portador(root=base) == []


def test_portador_que_NAO_reivindica_o_id_nao_gera_achado():
    """Guarda de precisao: ABERTO sem portador reivindicando e o estado normal de
    um achado vivo -- 8 dos 97 do ledger real estao assim, legitimamente."""
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        base = _repo(Path(d),
                     ledger="### F104 -- resumo coloquial -- **BAIXA/MEDIA** -- **ABERTO (conteudo)**\n",
                     contratos={"c.md": "**Versao 1.0 | 2026-01-01 (s075)**\n"})
        assert cc.check_status_portador(root=base) == []


def test_so_a_linha_de_VERSAO_conta():
    """Mencao ao F-id no corpo do contrato e comum e NAO significa absorcao --
    contar prosa daria falso-positivo em todo contrato que cita um achado."""
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        base = _repo(Path(d),
                     ledger="### F72 -- algo -- **MEDIA** -- **ABERTO**\n",
                     contratos={"c.md": "**Versao 1.0 | 2026-01-01 (s075)**\n\n"
                                        "Ver o F72 para o contexto historico.\n"})
        assert cc.check_status_portador(root=base) == []


# --- estado do repo real ----------------------------------------------------------------

def test_repo_real_sem_discordancia():
    """O que justifica nascer BLOCK: base ZERO, medida. Se cair, algum portador
    absorveu um achado e o cabecalho nao foi atualizado -- exatamente F109/F110."""
    achados = cc.check_status_portador()
    assert achados == [], "; ".join(
        f"{a['alvo']} reivindicado por {a['payload']['portadores']}" for a in achados)


def test_o_check_esta_no_registro_e_roda_na_varredura():
    """Sem isto o sensor seria construido-e-nunca-conectado (D4) -- e a varredura
    e o unico caminho pelo qual ele chega ao `auto_check`.

    Provado por POSITIVO sintetico, nao por tautologia: monta um repo em que o
    check tem de disparar e exige que `run_checks` -- a porta real -- devolva o
    achado rotulado `portador`."""
    import tempfile
    from pathlib import Path
    assert cc.CHECKS["portador"][1] is cc.check_status_portador
    with tempfile.TemporaryDirectory() as d:
        base = _repo(Path(d),
                     ledger="### F109 -- algo -- **MEDIA** -- **ABERTO**\n",
                     contratos={"c.md": "**Versao 1.4 | 2026-09-17 (s185, F109: ...)**\n"})
        achados = [a for a in cc.run_checks(root=base) if a["check"] == "portador"]
    assert len(achados) == 1, "run_checks nao esta chamando o sub-check novo"
