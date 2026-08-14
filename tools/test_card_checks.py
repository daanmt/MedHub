"""test_card_checks.py — predicados da biblioteca de qualidade (part-3).

1 fixture positiva + 1 controle por predicado, com texto DUMMY que replica a
ESTRUTURA dos 68 cards do incidente (2026-08-13) — nenhum conteudo clinico
real entra no repo. Nucleo puro: nenhum teste abre banco. Pytest-nativo +
standalone.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import card_checks as cc  # noqa: E402


def _card(**kw):
    base = {"tipo": "conteudo", "frente_contexto": "",
            "frente_pergunta": "Qual o criterio diagnostico da sindrome X?",
            "verso_resposta": "Criterio Y maior que limiar Z.",
            "verso_regra_mestre": "", "verso_armadilha": ""}
    base.update(kw)
    return base


def _erros(card, ctx=None):
    return cc.validar_card(card, contexto=ctx)["erros"]


def _avisos(card, ctx=None):
    return cc.validar_card(card, contexto=ctx)["avisos"]


# --- templates banidos (ERRO) -------------------------------------------------

def test_template_conduta_criterio():
    c = _card(frente_pergunta="Tema Generico: qual a conduta/criterio correto?")
    assert any("template-conduta-criterio" in e for e in _erros(c)), _erros(c)


def test_template_distrator_tipico():
    c = _card(frente_pergunta="Qual o distrator tipico do examinador em: lorem ipsum?")
    assert any("template-distrator-tipico" in e for e in _erros(c))


def test_template_prefixo_tema_via_contexto():
    ctx = {"tema": "Sindrome Ficticia", "titulo": "t", "area": "A"}
    c = _card(frente_pergunta="Sindrome Ficticia: qual o achado principal?")
    assert any("template-prefixo-tema" in e for e in _erros(c, ctx))


def test_template_controle_limpo():
    c = _card()
    assert not any(e.startswith("template") for e in _erros(c))


# --- resposta embutida (ERRO) -------------------------------------------------

def test_resposta_embutida_titulo_na_pergunta():
    # replica o padrao do incidente: titulo declarativo colado na pergunta
    titulo = "na sindrome ficticia o criterio maior sempre precede o tratamento de resgate"
    ctx = {"titulo": titulo, "tema": "Sindrome Ficticia", "area": "A"}
    c = _card(frente_pergunta=f"Por que {titulo}?")
    assert any("resposta-embutida" in e for e in _erros(c, ctx)), _erros(c, ctx)


def test_resposta_embutida_verso_na_frente():
    resposta = "iniciar farmaco alfa em dose plena por sete dias consecutivos completos"
    c = _card(frente_contexto=f"Paciente em que se decidiu {resposta}.",
              frente_pergunta="Qual a conduta indicada?",
              verso_resposta=resposta.capitalize() + ".")
    assert any("resposta-embutida" in e for e in _erros(c))


def test_resposta_embutida_controle_overlap_curto():
    c = _card(frente_pergunta="Qual a conduta na apendicite nao complicada?",
              verso_resposta="Apendicectomia direta, sem exame de imagem.")
    assert not any("resposta-embutida" in e for e in _erros(c))


# --- avisos (warn-first) ------------------------------------------------------

def test_multi_parte_duas_interrogacoes():
    c = _card(frente_pergunta="Qual o criterio? E qual a conduta?")
    assert any("multi-parte" in a for a in _avisos(c))


def test_negativo_orfao_sem_lista():
    c = _card(frente_pergunta="Qual alternativa NAO pertence ao criterio?")
    assert any("negativo-orfao" in a for a in _avisos(c))


def test_negativo_com_lista_nao_dispara():
    c = _card(frente_pergunta="Qual alternativa NAO pertence ao criterio?",
              frente_contexto="Alternativas:\n- alfa\n- beta\n- gama")
    assert not any("negativo-orfao" in a for a in _avisos(c))


def test_contexto_artefato_pct_acertaram():
    c = _card(frente_contexto="Questao em que 78% acertaram a alternativa correta.")
    assert any("contexto-artefato" in a for a in _avisos(c))


def test_distrator_perdido_e_presente():
    q = {"alternativa_marcada": "farmaco beta em dose reduzida"}
    sem = [_card()]
    com = [_card(verso_armadilha="Marcar farmaco beta em dose reduzida e o erro classico.")]
    assert cc.checar_distrator(q, sem), "marcada ausente -> aviso"
    assert cc.checar_distrator(q, com) is None, "marcada presente em campo -> sem aviso"
    assert cc.checar_distrator({"alternativa_marcada": "N/A"}, sem) is None


# --- encoding + campos (ERRO) -------------------------------------------------

def test_encoding_seta_unicode():
    c = _card(verso_resposta="A → B em duas etapas.")
    assert any("seta Unicode" in e for e in _erros(c))


def test_campos_obrigatorios():
    c = _card(verso_resposta="  ")
    assert any("verso_resposta vazia" in e for e in _erros(c))


def test_controle_limpo_sem_nada():
    r = cc.validar_card(_card(), contexto={"titulo": "erro pontual de criterio",
                                           "tema": "Sindrome Ficticia", "area": "A"})
    assert r == {"erros": [], "avisos": []}, r


def test_nucleo_puro_sem_banco():
    import inspect
    fonte = inspect.getsource(cc)
    assert "sqlite3" not in fonte and "get_connection" not in fonte, \
        "biblioteca deve permanecer pura (sem I/O de banco)"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    falhas = 0
    for fn in fns:
        try:
            fn()
            print("  OK  " + fn.__name__)
        except AssertionError as e:
            falhas += 1
            print("  XX  %s: %s" % (fn.__name__, e))
    print()
    if falhas:
        print("FALHOU: %d teste(s)" % falhas)
        sys.exit(1)
    print("TODOS OS TESTES PASSARAM (flashcards-integridade part-3)")
