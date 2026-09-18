"""Predicados PUROS de atomicidade de flashcard -- nucleo do gate (1.9a, s186).

Estas funcoes nasceram em `tools/audit_card_atomicity.py` e mudaram de endereco
por uma razao de dependencia, nao de gosto: `app/utils/db.py` precisa delas para
recusar uma reescrita, e ate 18/09/2026 as alcancava montando `sys.path` com
`__file__` para enxergar `tools/`. Isso inverte a seta -- `app/` passa a depender
da disposicao de pastas de `tools/`, e o import so falha em RUNTIME, dentro do
writer, onde o unico recurso e um `try/except` que decide se a escrita acontece.

Agora a seta aponta para o lado certo, no mesmo molde de `app/utils/areas.py` e
`app/utils/provas.py`: o NUCLEO puro vive em `app/` e os CLIs de `tools/` importam
daqui. O gate ficou **mais** fail-loud, nao menos: se este modulo quebrar,
`app/utils/db.py` nao importa, e nenhum writer roda -- em vez de cada chamada
decidir sozinha o que fazer com a falha (F85).

O que NAO veio junto, de proposito: `_conn`, `run_checks` e `main` seguem em
`tools/audit_card_atomicity.py`. Eles abrem o banco e falam com o terminal; nao
sao nucleo, sao a varredura. Dividir por PUREZA (nao por tema) e o que torna a
metade de baixo importavel de qualquer lugar sem arrastar sqlite e argparse.

Regua de conteudo: `.claude/commands/estilo-flashcard.md` §Formato atomico.
"""
import re


# --- duplo-ask -------------------------------------------------------------
# Cada alternativa e uma assinatura independente de "segunda demanda". O ponto
# comum: apos o interrogativo, um 'e' introduz um NOVO nucleo a ser respondido.
# Usa-se ' e ' com artigo/interrogativo/imperativo a seguir para nao casar
# enumeracao dentro de um mesmo fato ("dor e febre", "sifilis e cancro mole").
RE_DUPLO_ASK = re.compile(
    r"("
    r"\be\s+(qual|quais|quando|como|onde|quanto|quantos|quantas)\b"     # "qual X e qual Y"
    r"|\be\s+(por\s+qu[eê]|porqu[eê]|o\s+porqu[eê]|o\s+que|em\s+que|de\s+que)\b"
    r"|\be\s+(diga|explique|justifique|cite|indique|informe|classifique)\b"
    r"|\brespectivamente\b"
    r"|\b(as|os)\s+(duas|dois)\s+\w+"                                   # "quais as duas manifestacoes"
    r")",
    re.IGNORECASE)

# Segunda assinatura: pergunta com interrogativo + ' e ' + ARTIGO + substantivo.
# Exige o interrogativo para nao casar prosa de contexto.
RE_INTERROGATIVO = re.compile(
    r"\b(qual|quais|quando|como|onde|por\s+qu[eê]|o\s+que|quanto[as]?)\b",
    re.IGNORECASE)
RE_E_ARTIGO_NUCLEO = re.compile(
    r"\be\s+(a|o|as|os)\s+[a-zà-ÿ]{4,}", re.IGNORECASE)

# 🔴 DOIS GUARDAS DE PRECISAO (s128, achados ao auditar a propria worklist).
# O corpus grava sem acento (convencao da secao 4.5), o que colapsa dois 'e'
# distintos numa mesma letra -- sem estes guardas o detector superestima:
#   (a) COPULA: "Qual e a unica vacina ...?" e "qual E a", nao "qual E(conj) a".
#       Assinatura: interrogativo IMEDIATAMENTE antes do 'e'.
#   (b) CONSTRUCAO 'ENTRE X E Y': "intervalo entre a transfusao e a vacina",
#       "entre RN e adulto" -- o 'e' fecha um par, nao abre uma 2a demanda.
RE_COPULA = re.compile(
    r"\b(qual|quais|quando|onde|como|quanto[as]?|quem|que)\s+e\s+(a|o|as|os)\b",
    re.IGNORECASE)
RE_ENTRE = re.compile(r"\bentre\b", re.IGNORECASE)

# --- resposta-multifato ----------------------------------------------------
LIMITE_CHARS = 220          # acima disso ja nao e "uma frase"
LIMITE_FRASES = 3           # 3+ terminadores = paragrafo
RE_TERMINADOR = re.compile(r"[.!?](?:\s|$)")


def _conta_interrogacoes(txt):
    return txt.count("?")


def checar_front(txt):
    """Retorna o rotulo do padrao duplo-ask, ou None."""
    if not txt:
        return None
    if _conta_interrogacoes(txt) > 1:
        return "duplo-ask/duas-interrogacoes"
    if RE_DUPLO_ASK.search(txt):
        return "duplo-ask/conectivo"
    if RE_INTERROGATIVO.search(txt):
        for m in RE_E_ARTIGO_NUCLEO.finditer(txt):
            trecho_antes = txt[:m.start()]
            # guarda (a): o 'e' e copula ("qual e a ...") -> nao e 2a demanda.
            if RE_COPULA.search(txt[max(0, m.start() - 24):m.end()]):
                continue
            # guarda (b): 'entre X e Y' fecha um par -> nao e 2a demanda.
            if RE_ENTRE.search(trecho_antes):
                continue
            return "duplo-ask/segundo-nucleo"
    return None


def checar_verso(txt):
    """Retorna o rotulo do padrao resposta-multifato, ou None."""
    if not txt:
        return None
    n_frases = len(RE_TERMINADOR.findall(txt))
    if len(txt) > LIMITE_CHARS:
        return "resposta-multifato/paragrafo"
    if n_frases >= LIMITE_FRASES:
        return "resposta-multifato/multi-frase"
    return None


def medir_verso(txt):
    """(len, n_frases) do verso. Telemetria pura -- numeros, nunca o texto."""
    if not txt:
        return (0, 0)
    return (len(txt), len(RE_TERMINADOR.findall(txt)))


def checar_ratchet_verso(antes, depois):
    """Rotulo do CRESCIMENTO do verso numa reescrita, ou None. (s170)

    Complementa `checar_verso`, que e ABSOLUTO e por isso cego ao padrao real:
    um verso que vai de 100 para 219 chars nao estoura `LIMITE_CHARS` e mesmo
    assim inchou 2x. A auditoria da s170 mediu 46,8% de defeito nos cards em
    `card_version=4` (20/47 por verso estourado) -- cada rodada de reforja
    adicionava frase.

    Ratchet (so encolhe, nunca cresce):
        len(depois)      <= max(LIMITE_CHARS, len(antes))
        n_frases(depois) <= n_frases(antes)

    O teto usa `max(...)` de proposito: card que JA nascia acima do limite pode
    ser reescrito no mesmo tamanho -- o gate mede crescimento, nao pune heranca.
    """
    if not depois:
        return None
    len_a, frases_a = medir_verso(antes)
    len_d, frases_d = medir_verso(depois)
    teto = max(LIMITE_CHARS, len_a)
    if len_d > teto:
        return (f"ratchet-verso/crescimento ({len_a} -> {len_d} chars, teto {teto})")
    if frases_d > frases_a:
        return (f"ratchet-verso/frase-a-mais ({frases_a} -> {frases_d} frases)")
    return None
