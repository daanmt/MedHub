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
(fonte única pré-existente); `apply_reforja` a consome como gate 3.
"""
import re
import unicodedata

# AGENTE.md secao 4.5 — encoding limpo, zero LaTeX. FONTE ÚNICA (movido de
# apply_reforja na part-3; o CLI importa daqui).
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
    return {"erros": erros, "avisos": avisos}
