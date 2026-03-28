#!/usr/bin/env python3
"""
MedHub — Passe Qualitativo LLM para Flashcards

Pipeline: export → rewrite (LLM) → apply

Uso:
    # 1. Exportar cards que precisam de revisão
    python Tools/audit_flashcard_quality.py --export problematic.json

    # 2. Reescrever com LLM (requer ANTHROPIC_API_KEY)
    python Tools/regenerate_cards_llm.py --input problematic.json --output improved.json
    python Tools/regenerate_cards_llm.py --input problematic.json --output improved.json --pilot 20

    # 3. Aplicar ao banco
    python Tools/regenerate_cards.py --apply improved.json

Regras obrigatórias do prompt de reescrita:
    - Proibido qualquer referência "(A)", "(B)", "alternativa C", "gabarito"
    - Proibido prefixo "Sobre [especialidade]:"
    - frente_pergunta: pergunta clínica real, direta, discriminativa
    - verso_resposta: resposta curta (max 2 frases), sem badge/markdown
    - verso_regra_mestre: mecanismo/regra de ouro (max 3 frases)
    - verso_armadilha: só se pedagogicamente distinta da regra (senão vazio)
    - Armadilhas afirmativas → converter para pergunta ou marcar status=retired
"""

import sys, os, json, argparse, time

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SYSTEM_PROMPT = """Você é um especialista em medicina clínica criando flashcards de alta qualidade para um candidato a residência médica.

Você receberá dados brutos de um erro de questão médica e deve gerar campos estruturados para um flashcard.

REGRAS ABSOLUTAS — violação invalida o card:
1. NUNCA inclua referências de gabarito: "(A)", "(B)", "alternativa C", "Resposta D", "gabarito", etc.
2. NUNCA use o prefixo "Sobre [especialidade]:" na frente_pergunta.
3. NUNCA copie o badge "RESPOSTA DIRETA" ou formatação Markdown pesada (✅, 🧠) no output.
4. frente_pergunta DEVE terminar com "?" e ser uma pergunta clínica real.
5. verso_resposta DEVE ser curto (1-2 frases), claro e sem formatação markdown.
6. verso_regra_mestre DEVE conter o mecanismo/regra de ouro que explica a conduta.
7. verso_armadilha: preencher APENAS se houver distrator pedagógico distinto. Se não houver, retornar string vazia.
8. Para cards tipo "armadilha": frente_pergunta deve ser uma pergunta real sobre o distrator, nunca uma afirmação.

FORMATO DE SAÍDA — JSON puro, sem explicação adicional:
{
  "id": <int>,
  "frente_contexto": "<cenário clínico em 1-2 frases, sem referência de gabarito>",
  "frente_pergunta": "<pergunta clínica direta, termina com ?>",
  "verso_resposta": "<resposta em 1-2 frases, sem formatação>",
  "verso_regra_mestre": "<mecanismo/regra de ouro em 2-3 frases>",
  "verso_armadilha": "<distrator específico OU string vazia se não houver>"
}"""

USER_TEMPLATE = """Tipo: {tipo}
Título: {titulo}
Área/Tema: {area} / {tema}

Enunciado:
{enunciado}

Alternativa correta (texto original):
{alternativa_correta}

Habilidades sequenciais (elo quebrado):
{habilidades_sequenciais}

O que faltou saber:
{o_que_faltou}

Explicação correta:
{explicacao_correta}

Armadilha da prova:
{armadilha_prova}

---
Gere o JSON do flashcard seguindo as regras acima."""


def rewrite_card(client, card: dict) -> dict | None:
    """Chama a API para reescrever um card. Retorna dict ou None em caso de erro."""
    user_msg = USER_TEMPLATE.format(
        tipo=card.get('tipo', ''),
        titulo=card.get('titulo', ''),
        area=card.get('area', ''),
        tema=card.get('tema', ''),
        enunciado=card.get('enunciado', ''),
        alternativa_correta=card.get('alternativa_correta', ''),
        habilidades_sequenciais=card.get('habilidades_sequenciais', 'N/A'),
        o_que_faltou=card.get('o_que_faltou', 'N/A'),
        explicacao_correta=card.get('explicacao_correta', ''),
        armadilha_prova=card.get('armadilha_prova', ''),
    )

    try:
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',  # rápido e barato para batch
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': user_msg}],
        )
        raw = response.content[0].text.strip()

        # Extrair JSON da resposta
        if raw.startswith('{'):
            result = json.loads(raw)
        else:
            # Às vezes vem entre ```json ... ```
            import re
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                result = json.loads(m.group())
            else:
                print(f"  [WARN] card {card['id']}: resposta não é JSON válido")
                return None

        result['id'] = card['id']
        return result

    except json.JSONDecodeError as e:
        print(f"  [ERRO] card {card['id']}: JSON inválido — {e}")
        return None
    except Exception as e:
        print(f"  [ERRO] card {card['id']}: {e}")
        return None


def validate_output(result: dict) -> list[str]:
    """Valida as regras obrigatórias. Retorna lista de violações."""
    violations = []
    fp = result.get('frente_pergunta', '')
    vr = result.get('verso_resposta', '')
    vrm = result.get('verso_regra_mestre', '')

    if not fp.strip().endswith('?'):
        violations.append('frente_pergunta não termina com ?')

    for field, value in [('frente_pergunta', fp), ('verso_resposta', vr), ('verso_regra_mestre', vrm)]:
        for pattern in ['(A)', '(B)', '(C)', '(D)', '(E)', 'gabarito', 'alternativa correta']:
            if pattern.lower() in value.lower():
                violations.append(f"{field} contém '{pattern}'")

    if fp.lower().startswith('sobre ') and ':' in fp:
        violations.append('frente_pergunta começa com "Sobre X:"')

    if len(vr.strip()) < 8:
        violations.append('verso_resposta muito curto')

    return violations


def main():
    p = argparse.ArgumentParser(description='MedHub — Passe Qualitativo LLM')
    p.add_argument('--input',  required=True, metavar='FILE',
                   help='JSON exportado por audit_flashcard_quality.py --export')
    p.add_argument('--output', required=True, metavar='FILE',
                   help='JSON de output para usar com regenerate_cards.py --apply')
    p.add_argument('--pilot', type=int, default=0,
                   help='Processar apenas N cards (piloto)')
    p.add_argument('--delay', type=float, default=0.5,
                   help='Delay em segundos entre chamadas (default: 0.5)')
    args = p.parse_args()

    # Importar anthropic apenas quando necessário
    try:
        import anthropic
    except ImportError:
        print('ERRO: pip install anthropic')
        sys.exit(1)

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('ERRO: ANTHROPIC_API_KEY não definida')
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    with open(args.input, encoding='utf-8') as f:
        data = json.load(f)

    cards = data.get('cards', [])
    if args.pilot > 0:
        cards = cards[:args.pilot]
        print(f"Modo piloto: processando {len(cards)} cards")
    else:
        print(f"Processando {len(cards)} cards")

    results = []
    errors = []
    violations_total = 0

    for i, card in enumerate(cards, 1):
        print(f"  [{i}/{len(cards)}] card={card['id']} tipo={card.get('tipo','?')} ", end='', flush=True)
        result = rewrite_card(client, card)

        if result is None:
            errors.append(card['id'])
            print('ERRO')
            continue

        viols = validate_output(result)
        if viols:
            violations_total += len(viols)
            print(f'VIOLAÇÕES: {viols}')
            # Marcar para revisão manual mas incluir no output
            result['_violations'] = viols
        else:
            print('OK')

        results.append(result)

        if args.delay > 0 and i < len(cards):
            time.sleep(args.delay)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print()
    print(f"Concluído: {len(results)} cards reescritos, {len(errors)} erros, {violations_total} violações")
    print(f"Output: {args.output}")
    if errors:
        print(f"Cards com erro: {errors}")
    if violations_total > 0:
        print("Cards com violações incluídos no output com campo '_violations' — revisar manualmente.")
    print()
    print("Próximo passo:")
    print(f"  python Tools/regenerate_cards.py --apply {args.output}")


if __name__ == '__main__':
    main()
