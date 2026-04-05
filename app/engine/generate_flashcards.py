"""
generate_flashcards — geração contextual de flashcards v5 ancorada nos resumos do usuário.

quality_source='contextual' quando resumo_content presente (geração via Claude Haiku).
quality_source='heuristic' como fallback (sem resumo, ANTHROPIC_API_KEY ausente ou falha na API).

Uso:
    from app.engine import generate_contextual_cards

    ctx = get_topic_context("Sepse Neonatal")
    cards = generate_contextual_cards(
        tema="Sepse Neonatal",
        elo_quebrado="critério de SIRS em neonatos",
        armadilha="SIRS não se aplica igual a adultos",
        resumo_content=ctx["resumo_content"],
    )
"""
from __future__ import annotations

import json
import os
from typing import Optional

_GENERIC_PREFIXES = ("qual é o", "descreva", "o que é", "qual a")


def _extract_relevant_section(resumo_content: str, elo_quebrado: str) -> str:
    """Extrai trecho relevante do resumo por keyword match em headers H3 e bullets.

    Fallback: primeiros 2000 chars se nenhum header H3 tiver match.
    """
    palavras = [w.lower() for w in elo_quebrado.split() if len(w) > 3]
    linhas = resumo_content.splitlines()

    melhor_score = 0
    melhor_inicio = 0
    melhor_fim = len(linhas)

    for i, linha in enumerate(linhas):
        if linha.startswith("###"):
            score = sum(1 for p in palavras if p in linha.lower())
            if score > melhor_score:
                fim = len(linhas)
                for j in range(i + 1, len(linhas)):
                    if linhas[j].startswith("##"):
                        fim = j
                        break
                melhor_score = score
                melhor_inicio = i
                melhor_fim = fim

    if melhor_score > 0:
        return "\n".join(linhas[melhor_inicio:melhor_fim])

    return resumo_content[:2000]


def _heuristic_generate(elo_quebrado: str, armadilha: Optional[str]) -> list[dict]:
    """Gera flashcards via heurística de inversão de elo (sem LLM).

    Replica a lógica de _invert_elo_to_question de tools/insert_questao.py.
    """
    elo_lower = elo_quebrado.lower()

    if any(x in elo_lower for x in ["limiar", "ponto de corte", "mg/dl", "bpm", "semanas", "dias"]):
        frente_pergunta = f"Qual o valor limiar/critério correto para: {elo_quebrado.rstrip('.')}?"
    elif any(x in elo_lower for x in ["antes", "primeiro", "prioritário", "sequência", "ordem"]):
        frente_pergunta = (
            f"Qual a sequência/prioridade correta? (Dica: a ordem importa)\n{elo_quebrado.rstrip('.')}"
        )
    elif any(x in elo_lower for x in ["diferença", "distinguir", "diferencial", "versus", " vs "]):
        frente_pergunta = f"Como diferenciar corretamente: {elo_quebrado.rstrip('.')}?"
    else:
        elo_clean = elo_quebrado.rstrip(".").strip()
        if len(elo_clean) > 20 and not elo_clean.endswith("?"):
            frente_pergunta = f"{elo_clean}?"
        else:
            frente_pergunta = f"Qual a abordagem correta para: {elo_quebrado.rstrip('.')}?"

    tem_armadilha = armadilha and len(armadilha) > 20 and armadilha != "N/A"

    cards: list[dict] = [
        {
            "tipo": "elo_quebrado",
            "frente_contexto": "",
            "frente_pergunta": frente_pergunta,
            "verso_resposta": f"Revisão necessária: {elo_quebrado}",
            "verso_regra_mestre": None,
            "verso_armadilha": armadilha if tem_armadilha else None,
            "quality_source": "heuristic",
            "needs_qualitative": 1,
        }
    ]

    if tem_armadilha:
        cards.append(
            {
                "tipo": "armadilha",
                "frente_contexto": "",
                "frente_pergunta": f"Qual a armadilha clínica em: {elo_quebrado.rstrip('.')}?",
                "verso_resposta": armadilha,
                "verso_regra_mestre": None,
                "verso_armadilha": None,
                "quality_source": "heuristic",
                "needs_qualitative": 1,
            }
        )

    return cards


def _llm_generate(elo_quebrado: str, armadilha: Optional[str], trecho: str) -> list[dict]:
    """Gera flashcards via Claude Haiku com contexto do resumo.

    Lança exceção se a chamada falhar; o chamador faz fallback para heurística.
    """
    import anthropic  # noqa: PLC0415

    client = anthropic.Anthropic()

    armadilha_instrucao = (
        f"\nArmadilha identificada: {armadilha}"
        if armadilha and armadilha != "N/A"
        else ""
    )

    prompt = f"""Você é um especialista em elaboração de flashcards para residência médica.
Com base no trecho do resumo clínico abaixo, crie 1-2 flashcards no formato v5.

Elo quebrado (conceito não dominado): {elo_quebrado}{armadilha_instrucao}

Trecho do resumo clínico:
---
{trecho}
---

Regras obrigatórias:
- frente_pergunta NÃO pode começar com "Qual é o", "Descreva", "O que é" ou "Qual a" (muito genérico)
- frente_pergunta deve ser específica, cirúrgica, ancorada no elo quebrado
- verso_resposta deve ser concisa (1-3 linhas), não uma explicação longa
- verso_regra_mestre deve ser uma regra mnêmica curta (máx 20 palavras), pode ser null
- Se houver armadilha identificada, inclua no verso_armadilha do primeiro card

Responda SOMENTE com JSON válido, sem markdown, no formato:
[
  {{
    "tipo": "elo_quebrado",
    "frente_contexto": "<contexto clínico breve, pode ser string vazia>",
    "frente_pergunta": "<pergunta específica e cirúrgica>",
    "verso_resposta": "<resposta concisa>",
    "verso_regra_mestre": "<regra mnemônica curta ou null>",
    "verso_armadilha": "<armadilha ou null>"
  }}
]"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    cards = json.loads(raw)

    # Validação pós-geração: rejeitar frente_pergunta genérica → fallback heurístico
    for card in cards:
        fp = card.get("frente_pergunta", "").lower()
        if any(fp.startswith(pref) for pref in _GENERIC_PREFIXES):
            return _heuristic_generate(elo_quebrado, armadilha)

    return cards


def generate_contextual_cards(
    tema: str,
    elo_quebrado: str,
    armadilha: Optional[str] = None,
    resumo_content: Optional[str] = None,
) -> list[dict]:
    """Retorna até 2 flashcards v5 para o erro analisado.

    quality_source='contextual' se resumo_content presente e chamada LLM OK.
    quality_source='heuristic' como fallback em qualquer outro caso.

    Args:
        tema: Nome do tema clínico (usado apenas para contexto heurístico).
        elo_quebrado: Conceito/raciocínio que falhou — âncora do card.
        armadilha: Texto da armadilha de prova (opcional).
        resumo_content: Conteúdo do resumo .md injetado pelo chamador
            (tipicamente via get_topic_context()["resumo_content"]).

    Returns:
        list[dict] com campos v5 completos:
            tipo, frente_contexto, frente_pergunta, verso_resposta,
            verso_regra_mestre, verso_armadilha, quality_source, needs_qualitative.
    """
    if resumo_content:
        try:
            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise ValueError("ANTHROPIC_API_KEY não definida")
            trecho = _extract_relevant_section(resumo_content, elo_quebrado)
            cards = _llm_generate(elo_quebrado, armadilha, trecho)
            for c in cards:
                c["quality_source"] = "contextual"
                c["needs_qualitative"] = 0
            return cards
        except Exception:
            return _heuristic_generate(elo_quebrado, armadilha)
    else:
        return _heuristic_generate(elo_quebrado, armadilha)
