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

Fase 0 Lote 0 part-2b (10/10/2026): o teste de população é `vivo` (pula com motivo `VIVO:` sem o
banco) e mede a FORMA -- cada predicado dentro de uma banda declarada do baralho --, não a contagem
12 / 4 / 1; o gêmeo hermético sobre o `db_sintetico` planta um positivo de cada e exige a acusação.
"""
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import card_checks as cc  # noqa: E402

#: O banco que o vivo mede (part-2b; era `DB`). Constante de módulo para o teste de skip apontá-la
#: para um arquivo inexistente.
REAL_DB = ROOT / "ipub.db"


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

    🔴 SIGNIFICADO DA FALHA AQUI: **REGRESSAO**. #792 entra neste teste no papel de fixture
    NEGATIVO do P3 -- falhar significa que o predicado perdeu a discriminacao e passou a acusar
    contrafactual bem-formado. Nao confundir com o papel de SENTINELA que o mesmo card exerce em
    `test_ponto_cego_declarado_...`, onde falhar significa o oposto (atualize a declaracao).
    Dois papeis, dois testes, dois significados -- denominadores separados de proposito.
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

    🔴 SIGNIFICADO DA FALHA AQUI: **ATUALIZE A DECLARACAO**, jamais "regressao". Falhar
    significaria que um predicado passou a cobrir o que a spec declara NAO cobrir -- e entao e a
    spec que precisa mudar (AGENTE.md secao 10.8, verification-stack).

    🔴 O MESMO #792 exerce um SEGUNDO papel, noutro teste: fixture negativo do P3 em
    `test_p3_o_condicional_e_o_que_separa_...`, onde falhar significa REGRESSAO. Dois papeis do
    mesmo card, deliberadamente em testes SEPARADOS: um teste unico com dois significados de
    falha e denominador misturado -- quem lesse o vermelho nao saberia qual das duas leituras
    aplicar.
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
#: Banda declarada (part-2b, decisão técnica 2; o mesmo modelo do `test_comprimento_total`): cada
#: predicado acusa no máximo esta fração dos cards com contexto e pergunta. Medido em 10/10/2026:
#: P1 1,1% · P2 0,4% · P3 0,1% de 984. Acima dela, o predicado deixou de discriminar.
BANDA_ALINHAMENTO = 0.05

_PREDICADOS = {"P1": cc.checar_contexto_redundante,
               "P2": cc.checar_pergunta_generica_com_contexto,
               "P3": cc.checar_contrafactual_mal_formado}


def _populacao(db_path):
    """({id: card}, {"P1"|"P2"|"P3": [ids acusados]}) dos cards ativos com contexto e pergunta de
    `db_path`, lidos em read-only (`mode=ro`: nunca cria nem grava o banco). O vivo e o gêmeo
    hermético passam por aqui -- um caminho só."""
    con = sqlite3.connect(f"file:{Path(db_path).as_posix()}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT id, frente_contexto, frente_pergunta FROM flashcards "
            "WHERE COALESCE(frente_contexto,'') <> '' AND COALESCE(frente_pergunta,'') <> '' "
            "  AND COALESCE(needs_qualitative,0) < 2 ORDER BY id").fetchall()
    finally:
        con.close()
    cards = {cid: _c(x, p) for cid, x, p in rows}
    return cards, {nome: [cid for cid, k in cards.items() if pred(k)]
                   for nome, pred in _PREDICADOS.items()}


def _fora_da_banda(cards, acusados, banda=BANDA_ALINHAMENTO):
    """{predicado: "n/total"} dos que acusam mais que `banda` do baralho medido ({} = forma ok)."""
    return {nome: f"{len(ids)}/{len(cards)}" for nome, ids in acusados.items()
            if cards and len(ids) / len(cards) > banda}


@pytest.mark.vivo
def test_populacao_medida_e_a_que_a_spec_declara():
    """Re-mede P1/P2/P3 sobre o ipub.db real e asserta a FORMA (part-2b): nenhum predicado acusa mais
    que `BANDA_ALINHAMENTO` dos cards com contexto e pergunta. A contagem sai no print -- é relatório,
    não regressão: o baralho muda quando o operador reforja ou cria card. O passivo pode zerar; que
    cada predicado MORDE é o gêmeo hermético logo abaixo que prova, em qualquer checkout.

    Pula com motivo sem banco (`VIVO:`), com a guarda antes de qualquer conexão (part-2a)."""
    if not REAL_DB.is_file():
        pytest.skip("VIVO: ipub.db ausente -- fração do baralho real acusada por P1/P2/P3 não medida")
    cards, acusados = _populacao(REAL_DB)
    if not cards:
        pytest.skip("VIVO: ipub.db sem card ativo com contexto e pergunta -- P1/P2/P3 não medidos")
    medido = {nome: len(ids) for nome, ids in acusados.items()}
    print(f"  populacao: {medido} em {len(cards)} cards com contexto e pergunta")
    # ⚰️ 10/10/2026 (part-2b): `medido == {"P1": 11, "P2": 4, "P3": 1}`, re-escrito à mão a cada mudança
    # legítima do baralho com o predicado intocado -- P1 12 -> 13 em 17/09 (s185: a acentuação do F113
    # fez os dois campos grafarem as mesmas palavras) e 13 -> 11 em 29/09 (s206: a reforja apagou
    # vinhetas redundantes). Contagem é relatório; o teste mede a banda.
    fora = _fora_da_banda(cards, acusados)
    assert not fora, (
        f"predicado acima da banda de {BANDA_ALINHAMENTO:.0%} do baralho: {fora}. Ou ele perdeu a "
        "discriminação, ou o baralho mudou de forma -- re-medir e declarar, nunca afrouxar o predicado.")


def test_gemeo_hermetico_da_populacao_acusa_cada_predicado_plantado(db_sintetico):
    """Gêmeo hermético do vivo acima (part-2b): mesmo leitor (`_populacao`), mesmos predicados, banco
    sintético com um positivo de cada (#673 P1, #1574 P2, #1568 P3), os negativos que um regex ingênuo
    pegaria (#284 tem o shape `A x B`; #792 o desenho contrafactual), um card sem contexto (fora da
    query) e um positivo aposentado (`needs_qualitative = 2`, fora). Num baralho de 5, cada acusado
    vale 20%: a banda também acusa."""
    from app.utils import db
    plantados = {673: (C673, 0), 1574: (C1574, 0), 1568: (C1568, 0), 284: (C284, 0), 792: (C792, 0),
                 10: (_c("", "Qual a conduta na apendicite aguda?"), 0), 525: (C525, 2)}
    conn = db.get_connection()
    try:
        for cid, (card, nq) in plantados.items():
            conn.execute("INSERT INTO flashcards (id, tema_id, frente_contexto, frente_pergunta, "
                         "verso_resposta, needs_qualitative) VALUES (?, 1, ?, ?, ?, ?)",
                         (cid, card["frente_contexto"], card["frente_pergunta"], "Resposta.", nq))
        conn.commit()
    finally:
        conn.close()
    cards, acusados = _populacao(db_sintetico)
    assert sorted(cards) == [284, 673, 792, 1568, 1574], "sem contexto e aposentado ficam fora da query"
    assert acusados == {"P1": [673], "P2": [1574], "P3": [1568]}, acusados
    assert set(_fora_da_banda(cards, acusados)) == {"P1", "P2", "P3"}, "1 em 5 = 20% > a banda"
    assert _fora_da_banda(cards, acusados, banda=0.25) == {}


def test_vivo_pula_com_motivo_sem_banco(tmp_path, monkeypatch):
    """DoD 1 da part-2b: sem o banco, o vivo PULA com motivo `VIVO:` (não volta verde nem vermelho)
    e não cria o arquivo -- a guarda vem antes de qualquer conexão."""
    ausente = tmp_path / "ipub.db"
    monkeypatch.setitem(globals(), "REAL_DB", ausente)
    with pytest.raises(pytest.skip.Exception, match=r"VIVO:"):
        test_populacao_medida_e_a_que_a_spec_declara()
    assert not ausente.exists(), "a guarda tem de vir antes do connect"
