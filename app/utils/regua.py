"""Portador UNICO da regua de notas do FSRS -- R2/F112, s186.

A regua de notas do MedHub e a semantica do motor **eram a mesma escala com
significados diferentes**. O `/revisar` (passo 4) definia a nota por COMPLETUDE
da resposta -- *"cravou conceito + regra-mestre -> 4 ... recall parcial/na zona
mas sem o alvo -> 2"* -- e o py-fsrs le a mesma escala por ESFORCO DE
RECUPERACAO: `Again` e o unico lapso, `Hard` e *recuperou com esforco*, `Easy` e
*sem esforco*. As duas coincidem no 1 e divergem em todo o resto. Medido no F112:
a nota 2 -- o card que o aluno **nao** lembrou -- voltava em ~14 dias porque o
motor a lia como acerto.

O operador decidiu a **opcao (b)** em 17/09/2026: a regua do MedHub passa a SER a
nativa. Este modulo e a consequencia -- e a consequencia tem duas metades, nao uma:

  1. **A regua nova** (`REGUA_ATUAL = 2`), com os rotulos que instruem quem da a
     nota. Esta metade e vocabulario.
  2. **A regua VELHA nao desaparece** -- ela esta gravada em 3.067 revisoes que
     ninguem vai reescrever. Por isso a regua e uma propriedade **da linha**, e a
     traducao para a semantica nativa acontece por linha, na leitura, so na
     ENTRADA do Optimizer. O `fsrs_revlog` e imutavel.

Sem a metade 2, trocar o vocabulario faria o historico inteiro mudar de sentido
retroativamente: as 340 notas 2 dadas sob "sem o alvo" passariam a ser lidas como
"lembrou com esforco", e o F112 voltaria pela porta dos fundos -- desta vez
*inserido por nos*, e sem deixar rastro.

Molde: `app/utils/areas.py` (F89) e `app/utils/provas.py` (F88) -- dado em
`core/`, leitor unico em `app/`. Vive em `app/` porque `app/` nao pode importar
`tools/` sem inverter a dependencia; os CLIs de `tools/` importam daqui.

🔴 **Nao tolerante, de proposito** (licao do F91): regua desconhecida LEVANTA em
vez de virar v1 por omissao, e parametro ajustado sob outra regua e RECUSADO por
nome em vez de usado em silencio.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARAMS_PATH = os.path.join(ROOT, "core", "fsrs_params.json")

#: Quantos parametros o modelo DSR do py-fsrs tem (6.x). Conjunto de outro
#: tamanho e de outra versao do algoritmo -- nao serve, e nao se adivinha.
N_PARAMETROS = 21

#: A regua sob a qual TODA revisao nova e gravada.
REGUA_ATUAL = 2

#: Regua herdada -- a que governou o revlog inteiro ate o R2 pousar.
REGUA_LEGADA = 1

_ROTULOS = {
    1: {  # ⚰️ REVOGADA em 18/09/2026 (R2/F112). Preservada porque 3.067 linhas
          # do revlog foram gravadas sob ela: apagar o vocabulario nao apaga o
          # dado, so torna o dado ilegivel.
        1: "errou ou 'nao sei'",
        2: "recall parcial/na zona mas sem o alvo",
        3: "acertou o nucleo, faltou detalhe",
        4: "cravou conceito + regra-mestre",
    },
    2: {  # regua NATIVA do FSRS -- a semantica do motor, decidida em 17/09/2026
        1: "falhou",
        2: "lembrou com esforco",
        3: "lembrou",
        4: "lembrou sem esforco",
    },
}

#: Traducao da regua v1 para a semantica nativa. Herdado VERBATIM do R1
#: (`tools/fsrs_optimize.py`, commit b394f2f) -- se este dict divergir de la, os
#: numeros que o operador usou para decidir a opcao (b) deixam de valer.
MAPA_V1_PARA_NATIVO = {1: 1, 2: 1, 3: 2, 4: 3}

JUSTIFICATIVA_V1 = {
    "1->1": "errou ou 'nao sei' = Again (identidade)",
    "2->1": "recall parcial/na zona mas SEM O ALVO = falha de recuperacao, "
            "nao 'recuperou com esforco' (F112)",
    "3->2": "acertou o nucleo, faltou detalhe = Hard (recuperou com esforco)",
    "4->3": "cravou conceito + regra-mestre = Good (acerto padrao); a regua v1 "
            "nao tinha degrau de 'sem esforco', entao Easy fica vazio",
}

#: As duas leituras possiveis do revlog. `cru` = "o que o motor VIU" (identidade
#: sempre, qualquer que seja a regua da linha). `nativo` = "o que a revisao
#: SIGNIFICA", traduzido linha a linha. Elas divergem so onde ha linha v1.
VISOES = ("cru", "nativo")


class ReguaDesconhecida(ValueError):
    """Versao de regua que nenhum portador declara. Nunca degrada para v1."""


def rotulos(regua=None):
    """{nota: rotulo} da regua pedida (default: a atual)."""
    versao = REGUA_ATUAL if regua is None else int(regua)
    if versao not in _ROTULOS:
        raise ReguaDesconhecida("regua v%s nao declarada" % versao)
    return dict(_ROTULOS[versao])


def regua_da_linha(gravado):
    """Versao da regua de UMA linha do revlog.

    `NULL`/`0` -> v1. A ausencia da coluna e exatamente o que o historico
    anterior ao R2 tem, e ela **significa** v1 -- por declaracao aqui e no
    contrato, nunca por inferencia no ponto de uso.
    """
    if gravado is None or gravado == 0 or gravado == "":
        return REGUA_LEGADA
    versao = int(gravado)
    if versao not in _ROTULOS:
        raise ReguaDesconhecida(
            "linha do revlog com regua v%s, que nenhum portador declara -- "
            "recusado em vez de assumido como v%s" % (versao, REGUA_LEGADA))
    return versao


def nota_nativa(rating, regua):
    """Nota como o MOTOR deve le-la, dada a regua sob a qual ela foi dada."""
    nota = int(rating)
    if nota not in (1, 2, 3, 4):
        raise ValueError("nota fora de 1..4: %r" % (rating,))
    if regua_da_linha(regua) == REGUA_LEGADA:
        return MAPA_V1_PARA_NATIVO[nota]
    return nota


def nota_efetiva(rating, regua, visao="nativo"):
    """Nota sob a VISAO pedida. `cru` = identidade; `nativo` = traduzida."""
    if visao not in VISOES:
        raise ValueError("visao %r desconhecida -- use uma de %s"
                         % (visao, ", ".join(VISOES)))
    if visao == "cru":
        nota = int(rating)
        if nota not in (1, 2, 3, 4):
            raise ValueError("nota fora de 1..4: %r" % (rating,))
        return nota
    return nota_nativa(rating, regua)


# ----------------------------------------------------- parametros adotados

def carregar_parametros(path=None, regua=None):
    """`(parametros | None, motivo)`. `None` = usar o default do py-fsrs.

    Tres das quatro saidas sao `None`, e isso e o desenho: **numero reportado
    nao e numero adotado** (o proprio `core/fsrs_params.json` do R1 diz isso na
    chave `aviso_adocao`). O carregador so entrega quando o arquivo afirma
    `adotado: true` E declara `regua_do_fit` igual a regua de escrita.

    🔴 O gate da regua e o **F114**: os parametros da visao `remap` do R1 tem
    `w3` e `w16` -- stability inicial e bonus de Easy -- identicos ao default do
    py-fsrs, porque aquela visao mapeia `4 -> 3` e portanto tem ZERO exemplo de
    Easy. Eles nao convergiram; nunca foram tocados. Adota-los para uma regua que
    VAI emitir nota 4 e pedir ao modelo que agende um rotulo que ele nunca viu.
    O motivo devolvido e sempre nomeado -- gate que recusa em silencio nao ensina.
    """
    alvo = str(path or PARAMS_PATH)
    esperada = REGUA_ATUAL if regua is None else int(regua)
    if not os.path.isfile(alvo):
        return None, "sem %s -- default do py-fsrs" % os.path.basename(alvo)
    try:
        with open(alvo, encoding="utf-8") as fh:
            dados = json.load(fh)
    except (OSError, ValueError) as e:
        return None, "%s ilegivel (%s) -- default do py-fsrs" % (
            os.path.basename(alvo), e)
    if not dados.get("adotado"):
        return None, ("parametros REPORTADOS, nao adotados (`adotado` != true) "
                      "-- default do py-fsrs")
    fit = dados.get("regua_do_fit")
    if fit is None:
        return None, ("parametros sem `regua_do_fit` declarada: nao da para "
                      "saber sob que regua foram ajustados -- default do py-fsrs")
    if int(fit) != esperada:
        return None, ("parametros ajustados sob a regua v%s, escrita sob a v%s "
                      "-- RECUSADOS (F114), default do py-fsrs" % (int(fit), esperada))
    params = dados.get("parametros")
    if not isinstance(params, (list, tuple)) or len(params) != N_PARAMETROS:
        return None, ("`parametros` precisa ter %d floats (tem %s) -- default "
                      "do py-fsrs" % (N_PARAMETROS,
                                      len(params) if hasattr(params, "__len__") else "?"))
    try:
        params = [float(p) for p in params]
    except (TypeError, ValueError):
        return None, "`parametros` com valor nao-numerico -- default do py-fsrs"
    return params, ("adotados de %s (visao %s, regua v%s)"
                    % (os.path.basename(alvo), dados.get("visao_adotada", "?"), esperada))
