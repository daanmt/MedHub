"""card_checks.py — biblioteca ÚNICA de predicados de qualidade de flashcard.

Núcleo PURO (zero I/O de banco): recebe dicts, devolve violações. Duas
superfícies consomem os MESMOS predicados (part-3, flashcards-integridade):

  - write-gate: os writers chamam `validar_card()` antes de INSERT/UPDATE —
    `erros` bloqueiam a escrita; `avisos` são impressos (warn-first).
  - batch: os auditores rodam os predicados sobre o baralho (part-5).

Severidade por contrato (não por palpite): ERRO = campos obrigatórios,
encoding (AGENTE.md §4.5), pergunta_template e resposta_embutida (os dois
padrões com incidente real + proibição verbatim na spec estilo-flashcard.md).
AVISO = multi_parte, negativo_orfao, contexto_artefato, distrator_perdido.

Atomicidade NÃO mora aqui — segue em `audit_card_atomicity.checar_front/verso`
(fonte única pré-existente); `recurate_cards` a consome como gate 2.
"""
import re
import unicodedata

# AGENTE.md secao 4.5 — encoding limpo, zero LaTeX. FONTE ÚNICA (movido de
# apply_reforja na part-3; o reescritor canonico recurate_cards importa daqui
# desde a consolidacao part-6, que absorveu o apply_reforja).
RE_PROIBIDO = [
    (re.compile(r"\$[^$]*\$"), "LaTeX inline ($...$)"),
    (re.compile(r"\\(rightarrow|leftarrow|le\b|ge\b|mu\b|times\b|approx)"), "comando LaTeX"),
    (re.compile(r"[\u2192\u2190\u2194\u21d2]"), "seta Unicode"),
    (re.compile(r"[\u2018\u2019\u201c\u201d]"), "aspa inteligente"),
    (re.compile(r"[\u2013\u2014]"), "travessao inteligente"),
]

# Templates banidos (spec estilo-flashcard.md princípio 3 + incidente dos 68).
RE_TEMPLATES = [
    (re.compile(r"qual a conduta\s*/\s*criterio correto", re.I), "template-conduta-criterio"),
    (re.compile(r"qual o distrator tipico", re.I), "template-distrator-tipico"),
    (re.compile(r"^\s*sobre\s+", re.I), "template-sobre-prefixo"),
    (re.compile(r"habilidade\s+\d", re.I), "template-habilidade-n"),
]

# Contexto que confessa artefato de pipeline ("78% acertaram") — inclui o verbo
# `acertar` que era o near-miss do RE_PCT_FAKE no incidente dos 68.
RE_ARTEFATO = re.compile(
    r"\d{1,3}\s*%\s*(?:d[oa]s\s+)?(?:alunos|candidatos|pessoas)?\s*"
    r"(?:acertaram|acertam|caem|caiu|marcam|marcaram|erram|erraram|confundem|optam)", re.I)

RE_NEGATIVO = re.compile(r"\b(NAO|EXCETO|INCORRETA?)\b|\bNÃO\b")
RE_LISTA = re.compile(r"(?:^|\n)\s*(?:[-•*]|[a-eA-E]\))\s")
RE_MULTI_CONECTIVO = re.compile(r"\be\s+(?:por\s+que|por\s+qual|qual|quais|como|quando)\b", re.I)

CAMPOS_CARD = ("frente_contexto", "frente_pergunta", "verso_resposta",
               "verso_regra_mestre", "verso_armadilha")

# Limiares da deteccao relacional (ponto de partida explicito; a calibracao da
# part-5 mede contra os 68 do incidente ANTES de qualquer endurecimento).
RUN_MIN = 6          # tokens CONSECUTIVOS compartilhados frente x alvo
JACCARD_MIN = 0.6    # sobreposicao de conjuntos (so quando ambos >= 5 tokens)
JACCARD_MIN_TOKENS = 5

# --- F81 / B1 (s176): alinhamento interno da FRENTE (contexto x pergunta) ---
# Corte PARAMETRIZADO, nunca enterrado no corpo da funcao. Proveniencia da
# escolha, medida em 10/09/2026 sobre 951 cards ativos com contexto E pergunta:
#   >= 0.5 -> 91 | >= 0.6 -> 48 | >= 0.7 -> 26 | >= 0.8 -> 12 | >= 0.9 -> 4 | 1.0 -> 3
# O 0.7 do achado original foi estimado sobre 904 cards; o degrau real de
# qualidade esta em 0.8-0.9. Spec: .vibeflow/specs/alinhamento-frente-do-card.md
CORTE_CONTEXTO_REDUNDANTE = 0.8

# P2: pergunta que pede um DISCRIMINADOR GERAL entre duas entidades nomeadas --
# respondivel de cabeca, sem a vinheta. Distinta da que manda APLICAR ao caso.
_RE_PAR_NOMEADO = re.compile(r"\S\s+x\s+\S", re.I)
_RE_DISCRIMINADOR = re.compile(
    r"qual\s+d[ao]s\s+duas"
    r"|(?:que|qual)\s+\w+(?:\s+\w+){0,3}\s+(?:separa|distingue|diferencia|decide)"
    r"|presente\s+n[ao]\b.{0,60}?\bausente\s+n[ao]\b", re.I | re.S)
_RE_APLICA_AO_CASO = re.compile(
    r"hip[oó]tese\s+mais\s+prov[aá]vel|qual\s+[eé]?\s*[ao]\s+diagn[oó]stico"
    r"|qual\s+[eé]?\s*a\s+conduta|conduta\s+(?:imediata|inicial)", re.I)

# P3: sub-forma ESTREITA do eixo C. "ausencia" so conta quando (a) e qualificada
# como deste quadro e (b) alimenta um verbo de EXCLUSAO -- sem o condicional que
# tornaria a pergunta bem-formada. Estreito de proposito: "ausencia" tambem e o
# NOME de uma epilepsia (#1184) e um achado clinico legitimo (#279).
_RE_AUSENTE_DEIXIS = re.compile(
    r"\bausent\w*\b[^.?!]{0,40}?\b(?:nesse|neste|nesta|nessa|no|na)\s+"
    r"(?:quadro|caso|paciente|cen[aá]rio)"
    r"|\b(?:nesse|neste|nesta|nessa)\s+(?:quadro|caso|paciente|cen[aá]rio)"
    r"[^.?!]{0,40}?\bausent\w*\b", re.I)
_RE_VERBO_EXCLUSAO = re.compile(
    r"\b(?:afastar\w*|descartar\w*|excluir\w*|fechar\w*)\b", re.I)
_RE_CONDICIONAL = re.compile(
    r"\bse\s+estivesse\b|\bcaso\s+estivesse\b|\bse\s+presente\b"
    r"|\bse\s+houvesse\b|\bcaso\s+houvesse\b", re.I)


def _norm_tokens(texto):
    """Tokens normalizados (casefold, sem acento, sem pontuação), EM ORDEM."""
    s = unicodedata.normalize("NFKD", texto or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).casefold()
    return re.findall(r"[a-z0-9]+", s)


def _maior_run_comum(a, b):
    """Maior sequência CONTÍGUA de tokens compartilhada entre as listas a e b."""
    if not a or not b:
        return 0
    melhor, prev = 0, [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        atual = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                atual[j] = prev[j - 1] + 1
                if atual[j] > melhor:
                    melhor = atual[j]
        prev = atual
    return melhor


def checar_pergunta_template(card, contexto=None):
    """ERRO: pergunta gerada por template banido (spec) ou prefixada pelo tema."""
    fp = card.get("frente_pergunta") or ""
    for rx, nome in RE_TEMPLATES:
        if rx.search(fp):
            return nome
    tema = (contexto or {}).get("tema") or ""
    if tema and fp.casefold().strip().startswith(tema.casefold() + ":"):
        return "template-prefixo-tema"
    return None


def checar_resposta_embutida(card, contexto=None):
    """ERRO: a frente entrega a resposta — run contíguo >= RUN_MIN tokens (ou
    Jaccard alto) entre frente e verso_resposta/titulo da questão-mãe."""
    frente = _norm_tokens((card.get("frente_contexto") or "") + " " +
                          (card.get("frente_pergunta") or ""))
    alvos = [("verso_resposta", _norm_tokens(card.get("verso_resposta") or ""))]
    titulo = (contexto or {}).get("titulo") or ""
    if titulo:
        alvos.append(("titulo do erro", _norm_tokens(titulo)))
    for nome, alvo in alvos:
        if not alvo:
            continue
        if _maior_run_comum(frente, alvo) >= RUN_MIN:
            return f"resposta-embutida ({nome}, run>={RUN_MIN})"
        sa, sb = set(frente), set(alvo)
        if len(sa) >= JACCARD_MIN_TOKENS and len(sb) >= JACCARD_MIN_TOKENS:
            j = len(sa & sb) / len(sa | sb)
            if j > JACCARD_MIN:
                return f"resposta-embutida ({nome}, jaccard {j:.2f})"
    return None


def checar_multi_parte(card):
    """AVISO: pergunta multi-parte (viola atomicidade da demanda)."""
    fp = card.get("frente_pergunta") or ""
    if fp.count("?") > 1:
        return "multi-parte (duas interrogacoes)"
    if RE_MULTI_CONECTIVO.search(fp):
        return "multi-parte (conectivo composto)"
    return None


def checar_negativo_orfao(card):
    """AVISO: enunciado negativo (NAO/EXCETO) sem lista de alternativas no card
    — irrespondível fora da prova original."""
    fp = card.get("frente_pergunta") or ""
    if not RE_NEGATIVO.search(fp):
        return None
    for campo in CAMPOS_CARD:
        if RE_LISTA.search(card.get(campo) or ""):
            return None
    return "negativo-orfao (NAO/EXCETO sem lista no card)"


def checar_contexto_artefato(card):
    """AVISO: contexto/pergunta com percentual de artefato de pipeline
    ('78% acertaram') — o verbo `acertar` era o near-miss do incidente."""
    texto = (card.get("frente_contexto") or "") + " " + (card.get("frente_pergunta") or "")
    if RE_ARTEFATO.search(texto):
        return "contexto-artefato (percentual de pipeline)"
    return None


def checar_encoding(card):
    """ERROs de encoding (AGENTE.md §4.5) por campo presente."""
    erros = []
    for campo in CAMPOS_CARD:
        v = card.get(campo)
        if v is None:
            continue
        if not isinstance(v, str):
            erros.append(f"campo {campo} nao e string")
            continue
        for rx, nome in RE_PROIBIDO:
            if rx.search(v):
                erros.append(f"{nome} proibido em {campo}")
    return erros


def checar_distrator(questao, cards):
    """AVISO por QUESTÃO: `alternativa_marcada` existe no registro de erro mas
    não aparece em nenhum campo dos cards derivados — o card treina o fato e
    descarta a discriminação que originou o erro (modo de falha #6)."""
    marcada = str((questao or {}).get("alternativa_marcada") or "").strip()
    if not marcada or marcada.upper() == "N/A":
        return None
    alvo = _norm_tokens(marcada)
    if not alvo:
        return None
    for card in cards or []:
        for campo in CAMPOS_CARD:
            if _maior_run_comum(alvo, _norm_tokens(card.get(campo) or "")) >= min(len(alvo), 3):
                return None
    return ("distrator-perdido (alternativa_marcada nao aparece em nenhum "
            "campo dos cards derivados)")


def _containment_contexto(card):
    """Fracao dos tokens do CONTEXTO que a pergunta reengole. 0.0 se sem contexto."""
    tc = set(_norm_tokens(card.get("frente_contexto") or ""))
    if not tc:
        return 0.0
    tp = set(_norm_tokens(card.get("frente_pergunta") or ""))
    return len(tc & tp) / len(tc)


def checar_contexto_redundante(card):
    """AVISO (F81 eixo A): a pergunta reengole o contexto -- ele nao faz trabalho.

    O contexto existe para trazer DADO que a pergunta precisa. Quando a pergunta
    ja contem tudo o que o contexto diz, ele so ocupa a tela antes de o texto se
    repetir. Casos extremos medidos: #673 (contexto == pergunta, palavra por
    palavra), #525, #664.

    Corte em `CORTE_CONTEXTO_REDUNDANTE` -- parametro, nao constante enterrada.
    """
    v = _containment_contexto(card)
    if v >= CORTE_CONTEXTO_REDUNDANTE:
        return ("contexto-redundante (a pergunta reengole %.0f%% do contexto; "
                "corte %.0f%%)" % (v * 100, CORTE_CONTEXTO_REDUNDANTE * 100))
    return None


def checar_pergunta_generica_com_contexto(card):
    """AVISO (F81, clausula da CONJUNCAO): vinheta decorativa.

    Dispara so na conjuncao de tres condicoes: a pergunta nomeia um par `A x B`,
    pede um DISCRIMINADOR GERAL entre os dois (respondivel de cabeca, direto do
    livro) e existe contexto. Nesse arranjo a vinheta nao e lida -- a resposta
    sai igual sem ela.

    🔴 NAO dispara quando a pergunta manda APLICAR ao caso ("qual a hipotese mais
    provavel?"): ai a vinheta e load-bearing e o card esta certo. E o que separa
    o #1574 (dispara) do #284 (nao dispara), que tem o mesmo shape `A x B`.
    """
    fp = card.get("frente_pergunta") or ""
    if not (card.get("frente_contexto") or "").strip():
        return None
    if not _RE_PAR_NOMEADO.search(fp):
        return None
    if _RE_APLICA_AO_CASO.search(fp):
        return None
    if _RE_DISCRIMINADOR.search(fp):
        return ("pergunta-generica-com-contexto (pede discriminador geral entre o "
                "par nomeado; a vinheta nao e necessaria para responder)")
    return None


def checar_contrafactual_mal_formado(card):
    """AVISO (F81, sub-forma ESTREITA do eixo C): contrafactual sem o condicional.

    A pergunta afirma que um achado esta ausente NESTE quadro e, ao mesmo tempo,
    pede que esse achado exclua um diagnostico -- sem o "se estivesse presente"
    que tornaria a pergunta respondivel. Fixture: #1568 ("Qual achado
    cutaneo-mucoso, AUSENTE nesse quadro, afastaria DRESS e fecharia SJS?").

    🔴 DELIBERADAMENTE ESTREITO. "ausencia" tambem e o NOME de uma epilepsia
    (#1184: "perda de consciencia (ausencia)") e um achado clinico legitimo
    (#279: "a ausencia de bolha gastrica aponta para..."). Um predicado sobre a
    palavra solta acusaria os dois. Exige a deixis E o verbo de exclusao.

    Isto NAO cobre o eixo C pleno -- ver o ponto cego declarado (#792) na spec.
    """
    fp = card.get("frente_pergunta") or ""
    if not (card.get("frente_contexto") or "").strip():
        return None
    if _RE_CONDICIONAL.search(fp):
        return None
    if _RE_AUSENTE_DEIXIS.search(fp) and _RE_VERBO_EXCLUSAO.search(fp):
        return ("contrafactual-mal-formado (afirma o achado AUSENTE neste quadro e "
                "pede que ele exclua um dx, sem o 'se estivesse presente')")
    return None


def validar_card(card, contexto=None):
    """Valida UM card. Retorna {'erros': [...], 'avisos': [...]}.

    `contexto` opcional: {'titulo', 'tema', 'area'} da questão-mãe — habilita
    os predicados relacionais (template-prefixo-tema, resposta-embutida×titulo).
    Puro: não abre banco, não imprime, não levanta exceção."""
    erros, avisos = [], []
    fp = (card.get("frente_pergunta") or "").strip()
    vr = (card.get("verso_resposta") or "").strip()
    if not fp:
        erros.append("frente_pergunta vazia")
    if not vr:
        erros.append("verso_resposta vazia")
    erros.extend(checar_encoding(card))
    if fp:
        t = checar_pergunta_template(card, contexto)
        if t:
            erros.append(t)
        e = checar_resposta_embutida(card, contexto)
        if e:
            erros.append(e)
        m = checar_multi_parte(card)
        if m:
            avisos.append(m)
        n = checar_negativo_orfao(card)
        if n:
            avisos.append(n)
    a = checar_contexto_artefato(card)
    if a:
        avisos.append(a)
    # F81/B1 (s176): alinhamento interno da FRENTE. Os tres nascem WARN
    # (warning-first, AGENTE.md secao 6) -- viram BLOCK quando o passivo zerar.
    for predicado in (checar_contexto_redundante,
                      checar_pergunta_generica_com_contexto,
                      checar_contrafactual_mal_formado):
        v = predicado(card)
        if v:
            avisos.append(v)
    return {"erros": erros, "avisos": avisos}
