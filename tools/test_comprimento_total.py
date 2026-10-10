"""test_comprimento_total.py -- F115: o COMPRIMENTO TOTAL do card ganha gate (s187).

O achado (s186): drenando a previa do R2 em 18/09/2026, o operador marcou "card muito
longo" em **#92** e "card longo" em **#96**. Nao viu numero nenhum -- leu os cards. Eles
sao **p98,0 e p99,2** do baralho. Existia `card_atomicity.LIMITE_CHARS = 220`, mas mede
**o verso** e so roda **na reforja** (`checar_ratchet_verso`): um card nasce com 1.130
chars espalhados por contexto+pergunta+verso sem estourar nada.

Classe: **gate-miss por ESCOPO DE ALVO** -- o sensor existe, mede a coisa vizinha, e o
painel fica verde. Irmao do `cli_signature_check` (presenca != cobertura) e do escopo de
intencao do F113.

O CORTE NAO FOI ESCOLHIDO -- foi derivado, e a derivacao entrega uma BANDA.
Medido em 18/09/2026 sobre os 1.507 cards ativos (mediana 562, p90 880):

    maior NAO-marcado   #474   735 chars (p77,2)
    menor marcado       #92   1059 chars (p98,0)
    -> as marcas dele bound-eiam o corte em [736, 1059]

Dentro dessa banda TODO corte tem precisao identica no lote: 2/2 positivos, 4/4
negativos. O lote n=6 **nao discrimina por dentro** -- por construcao, nao por falta de
analise. E a banda e cara: 736 -> 334 cards (22,2%); 1059 -> 29 cards (1,9%).

`CORTE_COMPRIMENTO_TOTAL = 1059` e o unico ponto com regra de evidencia declarada:
*nenhum card sinalizado e mais curto que o mais curto que o operador chamou de longo.*
Qualquer corte menor sinaliza card que ele nunca viu. `test_o_corte_esta_dentro_da_banda`
e o guarda dessa regra: mexer no corte sem mexer na evidencia derruba a suite.

Limite declarado: comprimento e PROXY, nao defeito. Card longo pode ser longo com
razao (vinheta clinica load-bearing -- o #284 do F81 e o precedente). Por isso o predicado
nasce AVISO e sinaliza CANDIDATO; quem decide segue sendo leitura humana, pelo lifecycle
da fila de reforja (`--descartar` e desfecho legitimo, nao falha).
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.utils import card_checks as cc                       # noqa: E402
from app.utils import card_atomicity as aca                   # noqa: E402

# O banco que o teste VIVO mede (part-2a). Constante de módulo para o harness poder apontá-la
# para um arquivo inexistente e provar que, sem banco, o teste pula com motivo.
REAL_DB = Path(__file__).resolve().parents[1] / "ipub.db"

# --- EVIDENCIA CONGELADA: o lote de 6 cards que o operador drenou em 18/09/2026 -------
# Comprimentos medidos NAQUELE dia. Sao fato historico e nao se re-medem: se um destes
# cards for reforjado amanha, a marca do operador continua tendo sido dada sobre ESTE
# texto. (Regra "fixture que cicatriza e DADO", s177.) A populacao viva e re-medida no
# teste de populacao, que e outro.
#   card_id: (comprimento_total, marcado_por_comprimento, nota)
LOTE_18_09 = {
    92:  (1059, True,  "card muito longo"),
    96:  (1130, True,  "card longo"),
    53:  (597,  False, "marcado, mas por pergunta composta -- nao por comprimento"),
    474: (735,  False, ""),
    286: (685,  False, ""),
    69:  (617,  False, ""),
}


def _card(**campos):
    base = {c: "" for c in cc.CAMPOS_CARD}
    base["frente_pergunta"] = "Qual a conduta?"
    base["verso_resposta"] = "A conduta correta."
    base.update(campos)
    return base


def _com_total(n, campo="verso_resposta"):
    """Card cujo comprimento TOTAL e exatamente n chars, concentrado em `campo`."""
    c = {k: "" for k in cc.CAMPOS_CARD}
    c[campo] = "x" * n
    return c


# --- o corte e DERIVADO, nao escolhido ------------------------------------------------

def test_o_corte_esta_dentro_da_banda_que_as_marcas_do_operador_boundeiam():
    """O guarda central do F115: o corte nao pode sair da evidencia.

    Piso = maior NAO-marcado + 1 (abaixo disso o gate sinaliza card que ele viu e nao
    chamou de longo). Teto = menor marcado (acima disso o gate perde um card que ele
    chamou de longo). Mexer no corte sem mexer nas marcas derruba este teste -- que e
    exatamente o ponto: numero de sensor, nunca numero escolhido.
    """
    piso = max(v[0] for v in LOTE_18_09.values() if not v[1]) + 1
    teto = min(v[0] for v in LOTE_18_09.values() if v[1])
    assert piso <= cc.CORTE_COMPRIMENTO_TOTAL <= teto, (
        f"CORTE_COMPRIMENTO_TOTAL={cc.CORTE_COMPRIMENTO_TOTAL} fora da banda "
        f"[{piso}, {teto}] que as marcas do operador de 18/09 bound-eiam. Corte fora da "
        f"banda e numero ESCOLHIDO -- se a intencao e mover, mova a evidencia junto "
        f"(marcas novas do player).")


def test_o_corte_e_o_teto_da_banda_pela_regra_declarada():
    """A regra que escolhe o PONTO dentro da banda: nenhum sinalizado abaixo do menor
    que o operador chamou de longo. Isso e o TETO da banda, nao o meio nem o piso."""
    teto = min(v[0] for v in LOTE_18_09.values() if v[1])
    assert cc.CORTE_COMPRIMENTO_TOTAL == teto


def test_todo_card_do_lote_e_classificado_como_o_operador_classificou():
    """Precisao sobre as marcas dele -- 2/2 positivos, 4/4 negativos."""
    for cid, (total, esperado_positivo, nota) in sorted(LOTE_18_09.items()):
        disparou = cc.checar_comprimento_total(_com_total(total))
        assert bool(disparou) == esperado_positivo, (
            f"card#{cid} ({total} chars): esperado "
            f"{'disparar' if esperado_positivo else 'NAO disparar'}"
            f"{' -- ' + nota if nota else ''}")


# --- o que o LIMITE_CHARS nao via: escopo de alvo -------------------------------------

def test_soma_os_CINCO_campos_e_nao_so_o_verso():
    """A regressao que o F115 nomeia. Este card tem verso CURTO (dentro do
    LIMITE_CHARS=220) e mesmo assim e enorme -- e o padrao real dos #92/#96."""
    c = _card(frente_contexto="a" * 500, frente_pergunta="b" * 400,
              verso_resposta="c" * 100, verso_regra_mestre="d" * 60,
              verso_armadilha="e" * 60)
    assert cc.comprimento_total(c) == 1120
    assert aca.checar_verso(c["verso_resposta"]) is None, \
        "premissa do achado: o verso sozinho NAO estoura o LIMITE_CHARS"
    assert cc.checar_comprimento_total(c), \
        "o gate novo tem que pegar o que o gate do verso, por escopo de alvo, nunca veria"


def test_campo_none_nao_quebra_a_soma():
    c = {k: None for k in cc.CAMPOS_CARD}
    c["verso_resposta"] = "x" * 50
    assert cc.comprimento_total(c) == 50


def test_fronteira_exata_do_corte():
    """O corte e INCLUSIVO (`>=`), e isso nao e detalhe.

    O #92 tem exatamente 1059 chars e foi marcado pelo operador. Com `>` o gate perderia
    um dos DOIS cards que o originaram -- gate reprovado na propria evidencia fundadora.
    A primeira versao deste predicado tinha esse defeito, e foi este arquivo que o pegou.
    """
    assert cc.checar_comprimento_total(_com_total(cc.CORTE_COMPRIMENTO_TOTAL)), \
        "o card que esta EXATAMENTE no corte (#92) foi marcado pelo operador: tem que disparar"
    assert cc.checar_comprimento_total(_com_total(cc.CORTE_COMPRIMENTO_TOTAL - 1)) is None


def test_a_mensagem_diz_o_numero_e_o_corte():
    msg = cc.checar_comprimento_total(_com_total(1200))
    assert "1200" in msg and str(cc.CORTE_COMPRIMENTO_TOTAL) in msg
    assert "CANDIDATO" in msg, "a mensagem tem que dizer que e candidato, nao veredito"


# --- CANDIDATO nunca BLOCK ------------------------------------------------------------

def test_e_aviso_nunca_erro():
    """Condicao dura do achado: comprimento e proxy. Vinheta longa pode ser
    load-bearing (#284/F81). O gate nao pode impedir a escrita de card nenhum."""
    res = cc.validar_card(_card(frente_contexto="a" * 1200))
    assert any("comprimento-total" in a for a in res["avisos"])
    assert not any("comprimento-total" in e for e in res["erros"])


def test_card_longo_e_valido_para_o_writer():
    """Prova de que o predicado novo nao adiciona NENHUM erro a um card so-longo."""
    limpo = cc.validar_card(_card())
    longo = cc.validar_card(_card(frente_contexto="Vinheta clinica. " * 80))
    assert longo["erros"] == limpo["erros"], \
        "card longo nao pode ganhar erro novo -- CANDIDATO nunca BLOCK"


# --- o card inteiro NO NASCIMENTO + lifecycle ------------------------------------------

def test_esta_no_registro_de_predicados_verificaveis():
    """Sem isto a marca de reforja nasceria sem quem soubesse fecha-la (fila que so
    cresce) -- a recusa explicita de `reforja.py --ingerir`."""
    assert "comprimento_total" in cc.PREDICADOS_VERIFICAVEIS
    p = cc.PREDICADOS_VERIFICAVEIS["comprimento_total"]
    assert p(_com_total(1200)) and p(_com_total(100)) is None


def test_o_corte_e_parametro_nomeado_e_nao_constante_enterrada():
    """O LITERAL nao pode viver na LOGICA -- constante enterrada nao se re-deriva quando
    chegam marcas novas. Comentario e docstring PODEM cita-lo: documentar a proveniencia
    do numero e o oposto de enterra-lo. Por isso o teste olha o codigo executavel, nao o
    texto do arquivo (a 1a versao olhava o fonte cru e acusava o proprio comentario)."""
    import ast
    import inspect
    import textwrap
    src = inspect.getsource(cc.checar_comprimento_total)
    assert "CORTE_COMPRIMENTO_TOTAL" in src
    arvore = ast.parse(textwrap.dedent(src))
    literais = [n.value for n in ast.walk(arvore)
                if isinstance(n, ast.Constant) and isinstance(n.value, int)]
    assert cc.CORTE_COMPRIMENTO_TOTAL not in literais, \
        f"o corte aparece como literal {cc.CORTE_COMPRIMENTO_TOTAL} na logica da funcao"


# --- populacao VIVA (re-mede; nao congela) ---------------------------------------------

def _acusados_na_populacao(db_path):
    """(cards ativos, ids acusados) lidos de `db_path` pelo MESMO leitor da fila de reforja
    (`db.cards_ativos_para_predicado`) e julgados pelo MESMO predicado. O vivo e o gêmeo
    hermético passam por aqui -- um caminho só.

    `db.DB_PATH` é trocado só durante a leitura: o banco medido é o banco que a guarda
    conferiu, e não o que um teste anterior tenha deixado em `db.DB_PATH` (há suítes que o
    atribuem à mão)."""
    from app.utils import db
    anterior = db.DB_PATH
    db.DB_PATH = str(db_path)
    try:
        cards = db.cards_ativos_para_predicado()
    finally:
        db.DB_PATH = anterior
    return cards, [c["id"] for c in cards if cc.checar_comprimento_total(c)]


@pytest.mark.vivo
def test_populacao_viva_do_baralho():
    """Re-mede sobre o ipub.db real. NAO asserta um numero exato -- o baralho cresce e a
    reforja encolhe cards. Asserta a FORMA: o gate tem que ser raro (topo do baralho).

    Pula com motivo sem banco (`VIVO:`), e a guarda vem ANTES de qualquer conexão: o
    `sqlite3.connect` do leitor criaria um ipub.db vazio na raiz (part-2a). Que o sensor
    morde é o gêmeo hermético logo abaixo que prova, em qualquer checkout."""
    if not REAL_DB.is_file():
        pytest.skip("VIVO: ipub.db ausente -- fração do baralho real acima do "
                    "CORTE_COMPRIMENTO_TOTAL não medida")
    cards, acusados = _acusados_na_populacao(REAL_DB)
    if not cards:
        pytest.skip("VIVO: ipub.db sem card ativo -- fração do baralho acima do corte não medida")
    frac = len(acusados) / len(cards)
    print(f"  populacao: {len(acusados)}/{len(cards)} cards acima de "
          f"{cc.CORTE_COMPRIMENTO_TOTAL} chars ({100 * frac:.1f}%)")
    assert frac <= 0.10, (
        f"{100 * frac:.1f}% do baralho acusado -- o corte derivado mirava o topo ~2%. "
        f"Ou o baralho mudou de forma, ou o corte saiu da banda.")


def test_gemeo_hermetico_da_populacao_acusa_o_card_longo_plantado(db_sintetico):
    """Gêmeo hermético do vivo acima (part-2a): mesmo leitor, mesmo predicado, banco
    sintético com o defeito plantado. #1 longo e ativo (acusado); #2 curto (fora); #3 longo
    mas aposentado (`needs_qualitative = 2`, fora do leitor de ativos)."""
    from app.utils import db
    longo = "Vinheta clínica. " * 70                       # 1190 chars > corte
    assert len(longo) >= cc.CORTE_COMPRIMENTO_TOTAL
    conn = db.get_connection()
    try:
        for cid, contexto, nq in ((1, longo, 0), (2, "Homem de 40 anos.", 0), (3, longo, 2)):
            conn.execute("INSERT INTO flashcards (id, tema_id, frente_contexto, frente_pergunta, "
                         "verso_resposta, needs_qualitative) VALUES (?, 1, ?, ?, ?, ?)",
                         (cid, contexto, "Qual a conduta?", "A conduta correta.", nq))
        conn.commit()
    finally:
        conn.close()
    cards, acusados = _acusados_na_populacao(db_sintetico)
    assert [c["id"] for c in cards] == [1, 2], "o leitor de ativos deixa o aposentado de fora"
    assert acusados == [1], f"o sensor tem de acusar o card longo plantado: {acusados}"


def test_banda_viva_re_derivada_dos_cards_marcados():
    """A banda e uma QUERY sobre as marcas, nao um sensor novo: re-derivavel a qualquer
    momento. Aqui sobre a evidencia congelada; no fechamento de janela, sobre as marcas
    novas do player. Reporta [maior nao-marcado, menor marcado] e nada mais."""
    marcados = sorted(v[0] for v in LOTE_18_09.values() if v[1])
    nao = sorted(v[0] for v in LOTE_18_09.values() if not v[1])
    print(f"  banda 18/09: ({max(nao)}, {min(marcados)}]  "
          f"marcados={marcados}  nao-marcados={nao}")
    assert max(nao) < min(marcados), (
        "as marcas do operador se SOBREPOEM -- um card nao-marcado e mais longo que um "
        "marcado. Se isso acontecer com marcas novas, comprimento deixou de separar e o "
        "corte nao e mais derivavel dai. Declarar, nao remendar.")


if __name__ == "__main__":
    # Standalone via pytest (part-2a): o gêmeo pede o fixture `db_sintetico` do conftest e o
    # vivo pula com `pytest.skip`, que o laço caseiro anterior não sabia tratar.
    raise SystemExit(pytest.main([__file__, "-q"]))
