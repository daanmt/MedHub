"""Leitor UNICO do vocabulario de area (`core/areas.json`) -- F89, s176.

Antes existiam DUAS copias da lista, ja divergentes: `tools/registrar_sessao_bulk.py:31`
(21 itens, com "Simulado") e `tools/performance.py:73` (20, sem). O anexo de menores do
ledger registrava a divergencia; o spec de `performance` a previu como Risk #8 ("basta
editar nos dois locais") -- e editar nos dois locais e exatamente o que nao acontece.
Pior: nenhum dos 3 writers de `taxonomia_cronograma` consultava lista nenhuma, e foi por
ali que as areas `GO` e `Clinica Medica`, dissolvidas na s097, **voltaram** (7 linhas,
39 cards + 33 erros, medido no dry-run A6 de 09-09).

Molde: `app/utils/provas.py` sobre `core/provas.json` (F88) -- dado versionado em `core/`,
um leitor em `app/`. Vive em `app/` porque `app/` nao pode importar `tools/` sem inverter
a dependencia; os CLIs de `tools/` importam daqui.

🔴 **Diferenca DELIBERADA em relacao ao `provas.py`: este leitor NAO e tolerante.**
Arquivo ausente, ilegivel ou vazio **levanta** `VocabularioIndisponivel`; nunca devolve
lista vazia. `provas.py` pode degradar porque countdown ausente e cosmetico. Aqui nao: um
validador sem vocabulario ou reprova tudo ou aprova tudo, e as duas leituras sao falsas --
e a licao do F91 (retorno degradado que o chamador confunde com resposta valida).

A LISTA e do OPERADOR (RODADA 3, Tier 2.1). Este modulo e o MECANISMO; ele nao muda quando
ela mudar.
"""
import difflib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AREAS_PATH = os.path.join(ROOT, "core", "areas.json")


class VocabularioIndisponivel(RuntimeError):
    """O vocabulario nao pode ser lido. Nunca degrada para lista vazia."""


class AreaInvalida(ValueError):
    """Area fora do vocabulario -- escrita recusada na porta (fail-loud)."""


def _carregar(path=None):
    alvo = path or AREAS_PATH
    try:
        with open(alvo, encoding="utf-8") as fh:
            dados = json.load(fh)
    except FileNotFoundError:
        raise VocabularioIndisponivel(
            f"vocabulario de area ausente: {alvo}. Sem ele nao ha como validar area "
            "-- e reprovar tudo e aprovar tudo seriam ambos falsos (F89).")
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        raise VocabularioIndisponivel(f"vocabulario de area ilegivel ({alvo}): {e}")
    clinicas = tuple(dados.get("clinicas") or ())
    agregadas = tuple(dados.get("agregadas") or ())
    if not clinicas:
        raise VocabularioIndisponivel(
            f"vocabulario de area VAZIO em {alvo} -- lista vazia nao e resposta valida.")
    return clinicas, agregadas


AREAS_CLINICAS, AREAS_AGREGADAS = _carregar()
#: Aceitas para ESCRITA. `AREAS_CLINICAS` e o subconjunto que responde por "especialidade"
#: -- e a lista dos gaps do `/performance`, onde "Simulado" seria ruido (ele e slot de
#: volume agregado, nao materia que se possa deixar de estudar).
AREAS_VALIDAS = AREAS_CLINICAS + AREAS_AGREGADAS


#: Os dois fantasmas que a s097 dissolveu e voltaram (F89) sao AMBIGUOS por natureza --
#: `GO` e Ginecologia OU Obstetricia, `Clinica Medica` e qualquer uma das clinicas. Dar um
#: palpite unico aqui seria repetir o erro da s110, onde 3 linhas de `Clinica Medica` eram
#: Infecto, Hemato e Oftalmo. Entao a dica e a AMBIGUIDADE, nao um nome.
_AMBIGUAS = {
    "go": "GO nao e area: escolha Ginecologia OU Obstetricia",
    "clinica medica": "Clinica Medica nao e area: escolha a especialidade real "
                      "(na s110 foram Infecto, Hemato e Oftalmo, uma por linha)",
    "clínica médica": "Clinica Medica nao e area: escolha a especialidade real "
                      "(na s110 foram Infecto, Hemato e Oftalmo, uma por linha)",
}


def sugestao(area):
    """Palpite mais proximo dentro do vocabulario, ou None. `Obste` -> `Obstetrícia`."""
    if not area:
        return None
    alvo = str(area).strip()
    perto = difflib.get_close_matches(alvo, AREAS_VALIDAS, n=1, cutoff=0.6)
    if perto:
        return perto[0]
    baixo = alvo.casefold()
    for valida in AREAS_VALIDAS:           # prefixo: 'GO' -> nada, 'Obste' -> 'Obstetrícia'
        if valida.casefold().startswith(baixo) and len(baixo) >= 3:
            return valida
    return None


def validar_area(area, origem=""):
    """Gate de escrita: devolve a area ou levanta `AreaInvalida` nomeando o palpite.

    NAO normaliza. Adivinhar area no ato da escrita e como o `Clinica Medica` da s110
    virou 3 areas erradas -- o writer sugere e recusa; quem decide e quem chamou.
    """
    limpo = (area or "").strip()
    if limpo in AREAS_VALIDAS:
        return limpo
    ambigua = _AMBIGUAS.get(limpo.casefold())
    if ambigua:
        dica = f" {ambigua}."
    else:
        palpite = sugestao(limpo)
        dica = f" Voce quis dizer {palpite!r}?" if palpite else ""
    onde = f" [{origem}]" if origem else ""
    raise AreaInvalida(
        f"area fora do vocabulario{onde}: {limpo!r}.{dica} "
        f"Validas ({len(AREAS_VALIDAS)}): {', '.join(AREAS_VALIDAS)}. "
        f"Mudar a lista e decisao do operador em {os.path.relpath(AREAS_PATH, ROOT)} (F89).")


def area_valida(area):
    """Predicado puro, sem excecao -- para sensores e relatorios."""
    return (area or "").strip() in AREAS_VALIDAS
