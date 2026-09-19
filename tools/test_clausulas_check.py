"""test_clausulas_check.py -- item 1.10 (s187): clausula normativa tem terminal nomeado.

O defeito de fundo: **nao havia como saber quais regras o harness impoe e quais sao
prosa de honra.** F90 e F97 sao a forma aguda (clausula revogada seguiu prescrevendo, o
painel imprimiu PASSED); a cronica e 283 prescricoes em 23 portadores sem resposta para
"esta e verificada?".

O teste central e `test_anotacao_que_nomeia_gate_inexistente_e_BLOCK`: anotacao mentirosa
e PIOR que anotacao nenhuma, porque fabrica aparencia de cobertura. E o F90 um nivel
acima -- la o registro de portadores era manual e tinha buraco; aqui o registro de gates
e DERIVADO do auto_check e das suites, e toda anotacao e conferida contra ele.

Nasce BLOCK (nao WARN) pela mesma condicao que promoveu F79b e D5: o passivo e zero por
construcao -- nao existe anotacao nenhuma hoje, entao a primeira que mentir sera nova.

LIMITE DECLARADO: o gate confere que o nome do CHECK existe, nunca que aquele gate testa
MESMO aquela clausula. A metade semantica (a anotacao e honesta?) nao tem sensor e fica
com a leitura humana. O detector tambem e lexical (~86% de precisao amostrada): clausula
escrita sem marcador deontico e invisivel para o inventario inteiro.
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import clausulas_check as cn                                   # noqa: E402


def _portador(tmp_path, corpo, nome="contrato-sintetico.md"):
    p = tmp_path / nome
    p.write_text(corpo, encoding="utf-8")
    return str(p)


def _com(monkeypatch, path):
    monkeypatch.setattr(cn, "portadores", lambda: [path])


# --- o guarda central: anotacao que mente --------------------------------------------

def test_anotacao_que_nomeia_gate_inexistente_e_BLOCK(tmp_path, monkeypatch):
    """Anotacao mentirosa e pior que anotacao nenhuma -- fabrica aparencia de cobertura."""
    p = _portador(tmp_path, "- O agente **nunca** escreve FSRS no ensino. "
                            "<!-- CHECK: GATE_QUE_NAO_EXISTE -->\n")
    _com(monkeypatch, p)
    achados, resumo = cn.run_checks()
    assert resumo["com_check"] == 0, "gate inexistente NAO pode contar como cobertura"
    assert [a["tipo"] for a in achados] == ["gate_inexistente"]
    assert achados[0]["severidade"] == "BLOCK"


def test_anotacao_com_gate_REAL_conta_como_coberta(tmp_path, monkeypatch):
    """O nome tem que existir no registro DERIVADO -- aqui, uma suite real do repo."""
    assert "test_comprimento_total" in cn.registro_de_gates()
    p = _portador(tmp_path, "- O card **nunca** nasce acima do corte. "
                            "<!-- CHECK: test_comprimento_total -->\n")
    _com(monkeypatch, p)
    achados, resumo = cn.run_checks()
    assert resumo["com_check"] == 1 and achados == []


def test_registro_de_gates_e_DERIVADO_nao_enumerado(tmp_path):
    """Licao do F90/F95: registro mantido a mao tem buraco. Este sai do auto_check
    (slugs das descricoes) e das suites (modulo + funcao), por AST."""
    g = cn.registro_de_gates()
    assert "CONTRATO_REVOGADO" in g, "slug de gate do auto_check tem que entrar"
    assert "test_clausulas_check" in g, "o proprio modulo de teste tem que entrar"
    assert any(n.startswith("test_anotacao_que_nomeia") for n in g), \
        "funcao de teste tem que entrar -- inclusive as escritas nesta sessao"
    assert len(g) > 300


# --- o terminal DECLARADO -------------------------------------------------------------

def test_nao_verificavel_com_data_futura_e_terminal_valido(tmp_path, monkeypatch):
    p = _portador(tmp_path, "- O tom **deve** ser caloroso e motivacional. "
                            "<!-- NAO-VERIFICAVEL: julgamento de estilo (revisar: 2027-06-01) -->\n")
    _com(monkeypatch, p)
    achados, resumo = cn.run_checks(hoje=dt.date(2026, 9, 18))
    assert resumo["nao_verificaveis"] == 1 and achados == []


def test_nao_verificavel_SEM_data_e_BLOCK(tmp_path, monkeypatch):
    """Marca sem data nunca e revisitada -- vira isencao permanente por esquecimento.
    A data e o que torna a declaracao uma divida, e nao uma anistia."""
    p = _portador(tmp_path, "- O tom **deve** ser caloroso. "
                            "<!-- NAO-VERIFICAVEL: julgamento de estilo -->\n")
    _com(monkeypatch, p)
    achados, resumo = cn.run_checks()
    assert [a["tipo"] for a in achados] == ["nv_sem_data"]
    assert achados[0]["severidade"] == "BLOCK"
    assert resumo["nao_verificaveis"] == 0


def test_nao_verificavel_vencida_vira_WARN(tmp_path, monkeypatch):
    p = _portador(tmp_path, "- O tom **deve** ser caloroso. "
                            "<!-- NAO-VERIFICAVEL: estilo (revisar: 2026-01-01) -->\n")
    _com(monkeypatch, p)
    achados, _ = cn.run_checks(hoje=dt.date(2026, 9, 18))
    assert [a["tipo"] for a in achados] == ["nv_vencida"]
    assert achados[0]["severidade"] == "WARN"


# --- colocacao e escopo do detector ---------------------------------------------------

def test_anotacao_na_linha_ANTERIOR_vale():
    """Clausula longa fica ilegivel com a anotacao no fim -- a linha de cima e valida."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("<!-- CHECK: CONTRATO_REVOGADO -->\n"
                     "- A clausula revogada **nunca** segue prescrevendo.\n")
        cl = cn.extrair(p)
        assert len(cl) == 1 and cl[0]["check"] == "CONTRATO_REVOGADO"


def test_bloco_de_codigo_nao_e_clausula():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("```python\n# sempre valida antes de gravar\nx = 1\n```\n")
        assert cn.extrair(p) == []


def test_linha_de_tabela_e_heading_ficam_de_fora():
    """Exclusao MEDIDA, nao por gosto: 64 dos 347 hits crus eram doc de flag de CLI
    (que o argparse ja impoe) ou titulo de secao."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("## Clausula 4 -- o derivador\n"
                     "| `--sessao ID` | **Exige** o id. |\n"
                     "- O derivador **nunca** escreve no ipub.db.\n")
        cl = cn.extrair(p)
        assert len(cl) == 1 and "derivador **nunca** escreve" in cl[0]["texto"]


# --- estado do repo REAL ---------------------------------------------------------------

def test_repo_real_sem_anotacao_mentirosa():
    """O que justifica nascer BLOCK: a base e ZERO por construcao. Se esta cair, alguem
    anotou uma clausula com um gate que nao existe -- e e exatamente o caso a pegar."""
    achados, resumo = cn.run_checks()
    graves = [a for a in achados if a["severidade"] == "BLOCK"]
    assert graves == [], "; ".join(f"{a['tipo']}@{a['portador']}:{a['linha']}" for a in graves)
    print(f"  repo: {resumo['clausulas']} clausulas, {resumo['com_check']} com check, "
          f"{resumo['nao_verificaveis']} declaradas, {resumo['orfas']} orfas "
          f"({resumo['cobertura_pct']}% cobertas)")


def test_inventario_do_repo_tem_a_forma_esperada():
    """Ratchet frouxo: o inventario nao pode SUMIR (detector quebrado passando por
    limpo) nem explodir. Nao asserta numero exato -- os portadores sao editados."""
    _, resumo = cn.run_checks()
    assert 150 <= resumo["clausulas"] <= 600, resumo
    assert resumo["gates_conhecidos"] > 300, resumo


def test_catraca_de_orfas_so_avisa_quando_a_contagem_sobe():
    """s189 (pedido do /ai-eng): a contagem de orfas do 1.10 nao sobe sem DECLARACAO. Subir
    exige editar `BASE_ORFAS` no mesmo commit (o diff e a declaracao); descer e livre. WARN,
    nunca BLOCK -- por isso nenhuma assercao sobre o repo real aqui."""
    from clausulas_check import BASE_ORFAS, catraca
    assert catraca(BASE_ORFAS) is None and catraca(BASE_ORFAS - 3) is None
    msg = catraca(BASE_ORFAS + 2)
    assert msg and "2 clausula(s) nova(s)" in msg and "BASE_ORFAS" in msg
