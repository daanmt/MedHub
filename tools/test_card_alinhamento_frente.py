"""B1 / F81 (s176): alinhamento interno da FRENTE do card -- contexto x pergunta.

Todo predicado de `card_checks.py` compara frente x VERSO ou olha a pergunta isolada. A relacao
interna da FRENTE estava inteiramente fora de cobertura, e foi de la que sairam os tres ultimos
defeitos achados por LEITURA HUMANA e nao por gate (familia F79 / F79b / F81).

Spec: `.vibeflow/specs/alinhamento-frente-do-card.md`.

🔴 POR QUE TRES PREDICADOS E NAO UM. A ordem original mandava usar #1568 e #1574 como fixtures do
predicado de containment. A medicao desmentiu: eles pontuam 0.056 e 0.091 -- o CHAO da
distribuicao (951 cards: >=0.7 -> 26, >=0.8 -> 12, >=0.9 -> 4, ==1.0 -> 3). Force-los ali exigiria
afrouxar o corte ate ~0.05, varrendo metade do baralho: inventar a metrica para o painel ficar
verde. Cada fixture passa a viver sob a metrica que de fato o descreve.

🔴 CADA PREDICADO TEM FIXTURE NEGATIVO. Populacoes de 12 / 4 / 1 sao pequenas o bastante para um
predicado DECORAR o positivo. O negativo e o que prova que ele discrimina em vez de memorizar --
e os melhores negativos aqui sao os que um regex ingenuo pegaria:
  - #284 tem o MESMO shape `A x B` do #1574, mas a pergunta manda APLICAR ao caso -> vinheta
    load-bearing, card bom.
  - #1184 tem a palavra "ausencia" na pergunta -- so que ali "ausencia" e o NOME da epilepsia.
  - #792 tem o mesmo desenho contrafactual do #1568 e E BEM-FORMADO: traz o "se presente" que o
    #1568 nao tem. O par #792 x #1568 e o contraste que define o predicado 3.

Textos dos fixtures sao VERBATIM do `ipub.db` (minimizados apenas por corte de espaco em branco),
para o oraculo nao depender do banco local. O teste de POPULACAO le o banco e faz skip se ausente.
"""
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import card_checks as cc  # noqa: E402

DB = ROOT / "ipub.db"


def _c(ctx, perg):
    return {"frente_contexto": ctx, "frente_pergunta": perg}


# ---------------------------------------------------------------------------
# Fixtures verbatim (id real -> (contexto, pergunta))
# ---------------------------------------------------------------------------
C673 = _c("Qual a vantagem da imunizacao passiva sobre a ativa?",
          "Qual a principal vantagem da imunizacao passiva sobre a ativa?")
C525 = _c("Na enterocolite necrosante, qual achado tem indicacao ABSOLUTA de laparotomia?",
          "Na enterocolite necrosante, qual achado radiologico e indicacao ABSOLUTA de laparotomia?")
C664 = _c("Gestante convulsionando por eclampsia; pergunta a PRIMEIRA medida.",
          "Qual a PRIMEIRA medida diante de uma gestante convulsionando por eclampsia?")
C284 = _c("RN de 16 horas com vomitos biliosos, sem eliminacao de meconio e RX com dupla bolha.",
          "Atresia duodenal x pancreas anular: qual a hipotese mais provavel?")
C1574 = _c("Adolescente atleta com dor anterior no joelho ha semanas, sem trauma.",
           "Dor patelofemoral x Osgood-Schlatter: que achado do exame fisico separa uma da outra?")
C1572 = _c("Idoso internado ha dias em antibiotico, com distensao abdominal importante e colon "
           "dilatado do ceco ao ascendente na radiografia.",
           "Colite pseudomembranosa x pseudo-obstrucao colonica aguda: qual sintoma esta sempre "
           "presente na colite e ausente na pseudo-obstrucao?")
C390 = _c("Paciente de area endemica com febre alta e artralgia intensa/incapacitante, "
          "acompanhadas de exantema pruriginoso e conjuntivite nao purulenta.",
          "Zika x chikungunya: qual das duas cursa com febre ALTA e artralgia intensa/incapacitante?")
C1571 = _c("Mulher de 23 anos com nodulo solido de 4 cm no figado, achado em ultrassom de rotina "
           "e hipercaptante na tomografia trifasica.",
           "Hemangioma x hiperplasia nodular focal: qual achado tomografico decide o caso?")
C1568 = _c("Homem em uso de alopurinol ha algumas semanas, com rash maculopapular difuso, febre, "
           "adenomegalia e edema de face e maos.",
           "Qual achado cutaneo-mucoso, AUSENTE nesse quadro, afastaria DRESS e fecharia "
           "Stevens-Johnson?")
C1184 = _c("Crianca com crises de olhar fixo ~15s, nao responde ao ser chamada, deixa cair "
           "objetos que segurava.",
           "O objeto cair e sinal de evento motor (mioclonia) ou de perda de consciencia (ausencia)?")
C279 = _c("Gestante de 24 semanas; USG morfologica mostra polidramnio e ausencia de bolha "
          "gastrica fetal.",
          "Por que a ausencia de bolha gastrica ao USG fetal aponta para atresia de esofago sem "
          "fistula, e nao para o tipo com fistula distal, que e o mais comum?")
C792 = _c("Adolescente com movimentos generalizados, versao ocular e perda de consciencia por "
          "1 min seguida de sonolencia.",
          "Qual achado, se presente durante o episodio, aponta para crise NAO epileptica?")


# ---------------------------------------------------------------------------
# P1 -- contexto redundante (eixo A). Corte PARAMETRIZADO.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("card,nome", [(C673, "#673"), (C525, "#525"), (C664, "#664")])
def test_p1_dispara_nos_positivos(card, nome):
    assert cc.checar_contexto_redundante(card), f"{nome} deveria acusar contexto redundante"


def test_p1_nao_dispara_no_negativo():
    """#284: vinheta com dado concreto (16 h, vomito bilioso, dupla bolha) que a pergunta precisa."""
    assert cc.checar_contexto_redundante(C284) is None


def test_p1_corte_e_parametro_nomeado_e_nao_constante_enterrada():
    assert cc.CORTE_CONTEXTO_REDUNDANTE == 0.8
    baixo = _c("alfa beta gama delta epsilon", "alfa beta zeta eta teta")   # containment 0.4
    assert cc.checar_contexto_redundante(baixo) is None
    original = cc.CORTE_CONTEXTO_REDUNDANTE
    try:
        cc.CORTE_CONTEXTO_REDUNDANTE = 0.3
        assert cc.checar_contexto_redundante(baixo), \
            "baixar o corte tem de mudar o veredito -- senao o parametro e decorativo"
    finally:
        cc.CORTE_CONTEXTO_REDUNDANTE = original


def test_p1_card_sem_contexto_nao_dispara():
    assert cc.checar_contexto_redundante(_c("", "Qual a conduta na apendicite aguda?")) is None


# ---------------------------------------------------------------------------
# P2 -- pergunta generica COM contexto (a clausula da conjuncao)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("card,nome", [(C1574, "#1574"), (C1572, "#1572"),
                                       (C390, "#390"), (C1571, "#1571")])
def test_p2_dispara_nos_positivos(card, nome):
    assert cc.checar_pergunta_generica_com_contexto(card), \
        f"{nome} pede discriminador geral entre o par nomeado -- a vinheta nao e lida"


def test_p2_nao_dispara_quando_a_pergunta_manda_aplicar_ao_caso():
    """🔴 O negativo que importa: #284 tem o MESMO shape `A x B` do #1574.

    A diferenca nao e lexica, e a TAREFA: "qual a hipotese mais provavel?" obriga a ler a
    vinheta; "que achado separa uma da outra?" se responde direto do livro. Um predicado que
    disparasse nos dois estaria decorando o shape, nao medindo o defeito.
    """
    assert cc.checar_pergunta_generica_com_contexto(C284) is None


def test_p2_exige_a_conjuncao_e_nao_so_o_par():
    """Sem contexto, o mesmo par nomeado NAO e defeito -- o card e legitimamente teorico."""
    sem_ctx = _c("", "Dor patelofemoral x Osgood-Schlatter: que achado separa uma da outra?")
    assert cc.checar_pergunta_generica_com_contexto(sem_ctx) is None


# ---------------------------------------------------------------------------
# P3 -- contrafactual mal-formado (sub-forma ESTREITA do eixo C)
# ---------------------------------------------------------------------------
def test_p3_dispara_no_contrafactual_sem_condicional():
    assert cc.checar_contrafactual_mal_formado(C1568), \
        "#1568 afirma o achado AUSENTE neste quadro e pede que ele feche o dx alternativo"


def test_p3_nao_dispara_quando_ausencia_e_o_nome_da_doenca():
    """🔴 Anti-overfit: em #1184 'ausencia' e a EPILEPSIA tipo ausencia, nao uma negacao."""
    assert cc.checar_contrafactual_mal_formado(C1184) is None


def test_p3_nao_dispara_quando_a_ausencia_e_o_achado_real():
    """#279: a ausencia de bolha gastrica E o achado, e o verbo e 'aponta para', nao exclusao."""
    assert cc.checar_contrafactual_mal_formado(C279) is None


def test_p3_o_condicional_e_o_que_separa_o_bem_formado_do_defeituoso():
    """🔴 O par de contraste que DEFINE o predicado.

    #792 e #1568 tem o mesmo desenho contrafactual. #792 traz "se presente durante o episodio"
    -- o condicional que torna a pergunta respondivel -- e por isso NAO e defeito neste eixo.
    #1568 nao traz, e por isso e. Se o predicado disparasse nos dois, ele estaria medindo
    "pergunta fala de ausencia", que nao e o defeito.
    """
    assert cc.checar_contrafactual_mal_formado(C792) is None
    assert cc.checar_contrafactual_mal_formado(C1568)


def test_p3_nao_dispara_no_discriminador_do_p2():
    """#1572 diz 'ausente na pseudo-obstrucao' -- e discriminador (P2), nao contrafactual."""
    assert cc.checar_contrafactual_mal_formado(C1572) is None


# ---------------------------------------------------------------------------
# Ponto cego DECLARADO -- sentinela, nao teste de regressao
# ---------------------------------------------------------------------------
def test_ponto_cego_declarado_o_eixo_C_pleno_nao_e_pego_por_nenhum_predicado():
    """🔴 LAPIDE, NAO PRESCRICAO.

    O eixo C pleno do F81 e a relacao SEMANTICA entre vinheta e pergunta: o contexto trabalha
    CONTRA a pergunta. #792 e o exemplar (vinheta de crise inequivocamente epileptica; pergunta
    cobra o achado de crise NAO epileptica) e nenhuma das tres metricas o alcanca --
    containment 0.000, maior_run 0, pergunta bem-formada.

    Se este teste um dia FALHAR, a leitura correta e "atualize a declaracao do ponto cego",
    JAMAIS "regressao": significaria que um predicado passou a cobrir o que a spec declara nao
    cobrir, e a spec e que precisa mudar (AGENTE.md secao 10.8, verification-stack).
    """
    assert cc.checar_contexto_redundante(C792) is None
    assert cc.checar_pergunta_generica_com_contexto(C792) is None
    assert cc.checar_contrafactual_mal_formado(C792) is None


# ---------------------------------------------------------------------------
# Os tres entram em validar_card como AVISO, nunca como ERRO (warning-first)
# ---------------------------------------------------------------------------
def test_os_tres_sao_aviso_e_nunca_erro():
    card = dict(C673, verso_resposta="Protecao imediata, sem depender de resposta imune.")
    res = cc.validar_card(card)
    assert any("contexto-redundante" in a for a in res["avisos"])
    assert not any("contexto-redundante" in e for e in res["erros"]), \
        "warning-first (AGENTE.md secao 6): vira BLOCK quando o passivo zerar, nao antes"


# ---------------------------------------------------------------------------
# Populacao -- re-medida contra o banco, com o comando na propria assercao
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not DB.exists(), reason="ipub.db e local-only (nao versionado)")
def test_populacao_medida_e_a_que_a_spec_declara():
    """A spec declara 12 / 4 / 1. Numero em spec envelhece: este teste re-mede.

    Falhar aqui NAO e bug do predicado -- e o baralho tendo mudado. A acao certa e atualizar a
    spec com a nova medicao (e, se o passivo do P1 zerou, apertar o corte), nunca afrouxar o
    predicado para o numero voltar.
    """
    con = sqlite3.connect(str(DB))
    try:
        rows = con.execute(
            "SELECT frente_contexto, frente_pergunta FROM flashcards "
            "WHERE COALESCE(frente_contexto,'') <> '' AND COALESCE(frente_pergunta,'') <> '' "
            "  AND COALESCE(needs_qualitative,0) < 2").fetchall()
    finally:
        con.close()
    cards = [_c(x, p) for x, p in rows]
    medido = {
        "P1": sum(1 for k in cards if cc.checar_contexto_redundante(k)),
        "P2": sum(1 for k in cards if cc.checar_pergunta_generica_com_contexto(k)),
        "P3": sum(1 for k in cards if cc.checar_contrafactual_mal_formado(k)),
    }
    assert medido == {"P1": 12, "P2": 4, "P3": 1}, (
        "populacao divergiu da spec (.vibeflow/specs/alinhamento-frente-do-card.md): "
        f"{medido}. Re-medir e ATUALIZAR a spec -- nunca afrouxar o predicado.")
