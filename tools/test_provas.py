"""Suite da entidade multi-prova (spec consolidacao-part-4).

Cobre: parser de core/provas.json (ordenacao, tolerancia a arquivo ausente/
ilegivel/entrada malformada), countdown por tipo (prova x fecho de grade),
render do cabecalho e a FRONTEIRA DURA -- o countdown e display e nao pode
alimentar a formula de ritmo (que segue medida contra a grade, decisao s126).

Fixtures 100%% sinteticas: datas fake, nomes fake, zero conteudo clinico. O
unico teste que toca o arquivo real e o contrato de conteudo (ENAMED + grade).

Executavel standalone (python tools/test_provas.py) e coletavel pelo pytest.
"""
import inspect
import json
from datetime import date

import pytest

from tools.day_plan import (PROVAS_PATH, _cronograma_hoje, carregar_provas,
                            countdown_provas, render_countdown)

HOJE = date(2026, 1, 10)   # data sintetica de referencia


def _escrever(tmp_path, payload, nome="provas.json"):
    alvo = tmp_path / nome
    alvo.write_text(json.dumps(payload) if not isinstance(payload, str) else payload,
                    encoding="utf-8")
    return str(alvo)


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------

def test_carrega_e_ordena_por_data(tmp_path):
    p = _escrever(tmp_path, [
        {"nome": "PROVA-B", "data": "2026-05-20", "tipo": "prova"},
        {"nome": "PROVA-A", "data": "2026-02-01", "tipo": "prova"},
    ])
    provas = carregar_provas(p)
    assert [x["nome"] for x in provas] == ["PROVA-A", "PROVA-B"]
    assert provas[0]["data"] == date(2026, 2, 1)


def test_arquivo_ausente_warn_e_lista_vazia(tmp_path, capsys):
    provas = carregar_provas(str(tmp_path / "nao-existe.json"))
    assert provas == []
    assert "PROVAS_AUSENTE" in capsys.readouterr().err


def test_json_invalido_warn_e_lista_vazia(tmp_path, capsys):
    p = _escrever(tmp_path, "{isto nao e json")
    assert carregar_provas(p) == []
    assert "PROVAS_ILEGIVEL" in capsys.readouterr().err


def test_formato_nao_lista_warn_e_lista_vazia(tmp_path, capsys):
    p = _escrever(tmp_path, {"nome": "X", "data": "2026-02-01"})
    assert carregar_provas(p) == []
    assert "PROVAS_FORMATO" in capsys.readouterr().err


def test_entrada_malformada_nao_derruba_as_validas(tmp_path, capsys):
    p = _escrever(tmp_path, [
        {"nome": "BOA", "data": "2026-03-03", "tipo": "prova"},
        {"nome": "SEM-DATA", "data": "31/12/2026", "tipo": "prova"},
        {"nome": None, "data": "2026-04-04", "tipo": "prova"},
        "isto nao e objeto",
    ])
    provas = carregar_provas(p)
    assert [x["nome"] for x in provas] == ["BOA"]
    err = capsys.readouterr().err
    assert "PROVAS_DATA" in err and "PROVAS_NOME" in err and "PROVAS_ENTRADA" in err


def test_tipo_ausente_assume_prova(tmp_path):
    p = _escrever(tmp_path, [{"nome": "X", "data": "2026-03-03"}])
    assert carregar_provas(p)[0]["tipo"] == "prova"


# --------------------------------------------------------------------------
# Countdown
# --------------------------------------------------------------------------

def test_countdown_conta_dias_por_tipo(tmp_path):
    p = _escrever(tmp_path, [
        {"nome": "PROVA-X", "data": "2026-01-20", "tipo": "prova"},
        {"nome": "fim-grade-FAKE", "data": "2026-02-09", "tipo": "grade"},
    ])
    c = countdown_provas(HOJE, path=p)
    assert [x["dias"] for x in c] == [10, 30]
    assert c[0]["texto"] == "PROVA-X em 10d"
    assert c[1]["texto"] == "grade fecha em 30d"


def test_countdown_hoje_e_passado(tmp_path):
    p = _escrever(tmp_path, [
        {"nome": "PROVA-HOJE", "data": "2026-01-10", "tipo": "prova"},
        {"nome": "fim-grade-VELHA", "data": "2026-01-05", "tipo": "grade"},
        {"nome": "PROVA-VELHA", "data": "2026-01-08", "tipo": "prova"},
    ])
    por_nome = {x["nome"]: x["texto"] for x in countdown_provas(HOJE, path=p)}
    assert por_nome["PROVA-HOJE"] == "PROVA-HOJE e hoje"
    assert por_nome["PROVA-VELHA"] == "PROVA-VELHA foi ha 2d"
    assert por_nome["fim-grade-VELHA"] == "grade fechou ha 5d"


def test_render_junta_com_separador_e_vazio_e_silencioso(tmp_path):
    p = _escrever(tmp_path, [
        {"nome": "PROVA-X", "data": "2026-01-20", "tipo": "prova"},
        {"nome": "fim-grade-FAKE", "data": "2026-02-09", "tipo": "grade"},
    ])
    assert render_countdown(countdown_provas(HOJE, path=p)) == \
        "PROVA-X em 10d · grade fecha em 30d"
    assert render_countdown([]) == ""


def test_countdown_aceita_provas_injetadas_sem_tocar_disco():
    c = countdown_provas(HOJE, provas=[{"nome": "INJ", "data": date(2026, 1, 15),
                                        "tipo": "prova"}])
    assert c == [{"nome": "INJ", "tipo": "prova", "data": "2026-01-15",
                  "dias": 5, "texto": "INJ em 5d"}]


# --------------------------------------------------------------------------
# Fronteira dura + contrato do arquivo real
# --------------------------------------------------------------------------

def _codigo_sem_comentarios(func):
    """Fonte da funcao sem comentarios nem docstring.

    s159: a versao anterior deste teste greppava a fonte CRUA. Consequencia
    absurda descoberta ao vivo: escrever um comentario explicando *por que* a
    funcao nao le core/provas.json derrubava o teste, porque a palavra aparecia
    no texto. O gate punia a documentacao da regra que ele mesmo protege.
    A intencao sempre foi "o CODIGO nao consome provas" -- entao o teste passa
    a olhar so o codigo. Continua caindo se alguem realmente ler provas aqui.
    """
    linhas = []
    for linha in inspect.getsource(func).splitlines():
        if linha.strip().startswith("#"):
            continue
        linhas.append(linha.split("  #")[0])
    return chr(10).join(linhas)


def test_ritmo_nao_consome_provas():
    """s126: o ritmo NUNCA e medido contra a data de uma prova lida do countdown.
    O countdown e display -- se um dia ele entrar nesta funcao, o teste cai.

    s159: o divisor deixou de ser o fim da grade e passou a ser FIM_CONTEUDO_ALVO
    (constante de planejamento declarada em performance.py). A fronteira nao
    mudou: segue proibido consumir core/provas.json ou o countdown aqui dentro.
    Uma constante nomeada e auditavel; um countdown de display nao e.
    """
    src = _codigo_sem_comentarios(_cronograma_hoje)
    assert "provas" not in src and "countdown" not in src
    assert "dias_grade" in src   # o ritmo continua tendo um divisor nomeado


def test_ritmo_usa_alvo_de_conteudo_declarado():
    """s159: o divisor do ritmo da grade e uma DECISAO DE PLANEJAMENTO nomeada.

    Historico das duas correcoes do mesmo divisor:
    - s126: dividia pela data do ENAMED e comprimia a grade -> ~116q/dia ficticio.
      Corrigido para o fim da grade.
    - s159: dividir pelo fim do calendario do curso (09-11/10) media "consigo
      fechar dentro do EMED?", pergunta sem consequencia -- o curso acabar nao e
      um prazo. Passou a dividir por `FIM_CONTEUDO_ALVO`, a data-alvo declarada
      para cobrir o conteudo (hoje = data da UERJ).

    O teste trava as duas pontas: usa o alvo declarado E continua sem consumir
    provas/countdown (a fronteira dura da s126 segue valendo -- ver o teste
    irmao abaixo).
    """
    from performance import FIM_CONTEUDO_ALVO
    src = inspect.getsource(_cronograma_hoje)
    assert "FIM_CONTEUDO_ALVO" in src, "o divisor deixou de ser o alvo declarado"
    assert isinstance(FIM_CONTEUDO_ALVO, date), "o alvo tem que ser uma data"


def test_arquivo_real_tem_prova_e_grade():
    provas = carregar_provas(PROVAS_PATH)
    por_nome = {p["nome"]: p for p in provas}
    assert por_nome["ENAMED"]["tipo"] == "prova"
    assert por_nome["ENAMED"]["data"] == date(2026, 9, 13)
    assert por_nome["fim-grade-EMED"]["tipo"] == "grade"
    # s159: 25/10 -> 09/10. A leitura do xlsx do Drive (F36, adendo 4) mostrou que
    # a planilha real do usuario tem 28 semanas e termina em "05/10 a 09/10"; as
    # semanas 29 e 30 do Cronograma.pdf (que ja tinham 0 questoes) NAO existem
    # nela. 09/10 e tambem o fim do internato e a colacao de grau.
    assert por_nome["fim-grade-EMED"]["data"] == date(2026, 10, 9)
    assert por_nome["UERJ/MFC"]["tipo"] == "prova"
    assert por_nome["UERJ/MFC"]["data"] == date(2026, 11, 1)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
