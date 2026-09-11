"""test_deixis_sem_contexto.py -- F79b: deixis sobre contexto VAZIO e BLOCK (s176, item 1.1).

O achado (s169) veio do USUARIO no drill, nao do harness: o card **#367** perguntava
"que elementos DO CASO ... classificam ESSA morte como suspeita?" com
`frente_contexto = ''` -- literalmente inrespondivel como posto. O
`card_self_sufficiency` rodou e **nao o pegou**: ele procurava auto-suficiencia por
outros criterios e nunca cruzava deixis com contexto vazio.

🔴 **O fixture original NAO reproduz mais.** Medido em 10/09/2026: o #367 foi
reforjado -- hoje tem vinheta completa e outra pergunta. Entao os fixtures aqui sao
(a) o TEXTO do achado da s169, preservado como caso sintetico, e (b) cards VIVOS do
banco, medidos hoje, para os controles. Fixture que cicatriza e dado, nao motivo para
parar: a CLASSE do defeito continua real e o gate e prospectivo.

Populacao medida com o predicado real, 1419 cards ativos: **passivo 0, falso-positivo
0, 95 controles** (mesma deixis COM vinheta) corretamente fora.
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import card_checks as cc                    # noqa: E402
import card_self_sufficiency as css         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _card(pergunta, contexto="", resposta="Resposta qualquer que serve."):
    return {"frente_contexto": contexto, "frente_pergunta": pergunta,
            "verso_resposta": resposta}


# --- positivos: a conjuncao que produz card inrespondivel ---------------------------

def test_o_card_do_achado_original_dispara():
    """Texto da s169 (#367 antes da reforja), preservado como fixture sintetico."""
    c = _card("Que elementos do caso (historico do paciente e circunstancia do achado) "
              "classificam essa morte como suspeita?")
    msg = cc.checar_deixis_sem_contexto(c)
    assert msg, "o card que originou o F79b tem que disparar"
    assert "inrespondivel" in msg and "vinheta" in msg, \
        "a mensagem tem que dizer o que fazer, nao so que ha defeito"


def test_variantes_de_deixis_disparam_com_contexto_vazio():
    for pergunta in (
        "Qual a conduta neste paciente?",
        "Por que esse medico nao pode preencher a Declaracao de Obito?",
        "Qual achado descrito acima fecha o diagnostico?",
        "O que na vinheta contraindica a trombolise?",
        "Qual o proximo passo para esta gestante?",
    ):
        assert cc.checar_deixis_sem_contexto(_card(pergunta)), f"deveria disparar: {pergunta}"


def test_dispara_como_BLOCK_e_nao_como_aviso():
    """A condicao da politica warning-first ja esta satisfeita: passivo MEDIDO = 0."""
    r = cc.validar_card(_card("Qual a conduta neste paciente?"))
    assert any("deixis sem contexto" in e for e in r["erros"]), "tem que entrar em `erros`"
    assert not any("deixis sem contexto" in a for a in r["avisos"]), "nao pode estar nos dois"


# --- negativos: por que o predicado e ESTREITO --------------------------------------

def test_a_mesma_deixis_COM_vinheta_e_legitima():
    """95 cards do corpus fazem exatamente isto. Se um dia virarem achado, o defeito
    e do predicado, nao deles."""
    c = _card("Qual e a conduta mais apropriada para esta crianca com PTI pos-viral?",
              contexto="Crianca de 7 anos com peteguias e equimoses apos infeccao viral "
                       "das vias aereas superiores; plaquetas 18.000.")
    assert cc.checar_deixis_sem_contexto(c) is None


def test_classe_generica_nao_e_deixis():
    """O candidato AMPLO (`do paciente`, `na crianca`, `no lactente`) deu 26 achados,
    TODOS falsos -- sao classe clinica, nao referencia a uma vinheta. Fixtures vivos."""
    for pergunta in (
        "Na intubacao orotraqueal do paciente asmatico em crise, qual o agente de inducao?",
        "Qual a causa mais comum de abdome obstrutivo no LACTENTE (29 dias a 2 anos)?",
        "Como a IDADE ajuda a discriminar tumor de Wilms de neuroblastoma na crianca?",
        "Qual a conduta na hernia umbilical da crianca?",
        "Em pacientes acima de 65 anos, o limiar de TSH sobe ou desce?",
    ):
        assert cc.checar_deixis_sem_contexto(_card(pergunta)) is None, \
            f"classe generica virou achado (falso-positivo): {pergunta}"


def test_caso_epidemiologico_nao_e_vinheta():
    """#620, o unico falso-positivo que a medicao encontrou antes da guarda:
    'confirmacao do caso' e caso-INDICE, nao a vinheta do card."""
    for pergunta in (
        "O bloqueio vacinal do sarampo so e feito apos confirmacao do caso? E quem e o alvo?",
        "Em quanto tempo a notificacao do caso suspeito de sarampo deve ocorrer?",
        "Qual a definicao de caso confirmado de dengue grave?",
    ):
        assert cc.checar_deixis_sem_contexto(_card(pergunta)) is None, \
            f"caso epidemiologico virou achado: {pergunta}"


def test_contexto_curto_demais_conta_como_vazio_e_longo_nao():
    pergunta = "Qual a conduta neste paciente?"
    assert cc.checar_deixis_sem_contexto(_card(pergunta, contexto="Homem 40a")), \
        "contexto de 9 chars nao sustenta deixis"
    assert cc.checar_deixis_sem_contexto(
        _card(pergunta, contexto="Homem de 40 anos, dor toracica em aperto ha 2h.")) is None


def test_corte_e_parametrizado_com_proveniencia():
    assert cc.CORTE_CONTEXTO_MINIMO == 15
    with open(os.path.join(ROOT, "tools", "card_checks.py"), encoding="utf-8") as fh:
        fonte = fh.read()
    assert "PASSIVO 0 e ZERO falso-positivo" in fonte, \
        "o corte e o nascimento em BLOCK precisam carregar a medicao que os justifica"


# --- populacao: a varredura que autoriza o BLOCK ------------------------------------

def test_passivo_no_banco_real_continua_zero():
    """Se esta cair, ou o predicado ficou largo ou entrou card defeituoso -- as duas
    leituras exigem acao, e nenhuma delas e 'afrouxar o corte'. Pula sem banco."""
    dbp = os.path.join(ROOT, "ipub.db")
    if not os.path.exists(dbp):
        return
    con = sqlite3.connect(f"file:{dbp}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        cards = [dict(r) for r in con.execute(
            "SELECT id, frente_contexto, frente_pergunta FROM flashcards "
            "WHERE COALESCE(needs_qualitative,0) < 2")]
    finally:
        con.close()
    achados = [c["id"] for c in cards if cc.checar_deixis_sem_contexto(c)]
    assert achados == [], f"passivo deixou de ser zero: {achados}"


def test_a_varredura_do_corpus_enxerga_o_predicado():
    """O gate de escrita e a varredura do banco olham pelo MESMO predicado -- uma
    copia da regex em `card_self_sufficiency` seria a 2a fonte (defeito do F89)."""
    assert css._deixis_sem_contexto is cc.checar_deixis_sem_contexto
    achados = css.run_checks(cards=[
        {"id": 1, "frente_contexto": "", "frente_pergunta": "Qual a conduta neste paciente?"},
        {"id": 2, "frente_contexto": "Homem de 60 anos com dor toracica tipica ha 1h.",
         "frente_pergunta": "Qual a conduta neste paciente?"},
    ])
    ids = {(a["id"], a["padrao"]) for a in achados}
    assert (1, "deixis-sem-contexto") in ids, "a varredura tem que ver o card sem vinheta"
    assert (2, "deixis-sem-contexto") not in ids, "o card COM vinheta nao e achado"


if __name__ == "__main__":
    falhas = 0
    for nome, fn in sorted(list(globals().items())):
        if nome.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  OK   {nome}")
            except AssertionError as e:
                falhas += 1
                print(f"  FALHA {nome}: {e}")
    print(f"\n{'FALHOU' if falhas else 'PASSOU'} -- {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
