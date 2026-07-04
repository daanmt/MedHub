---
name: "source-command-refrescar"
description: "Refresh narrativo diário de um tema DORMENTE — re-hidrata a memória de temas não vistos há tempo, com contexto menos comprimido. Distinto do /revisar (card-a-card). Não toca o FSRS."
---

# source-command-refrescar

Use this skill when the user asks to run the migrated source command `refrescar`.

## Command Template

# Skill: Refrescar (tema dormente)

> Ritual diário da **gestão da curva de esquecimento**. Pega 1 tema dormente, re-ensina em prosa clínica reconstrutiva (menos comprimida) e carimba a revisão. **Não cunha card, não avalia, não toca o FSRS.**
> Seleção em `tools/review_radar.py`; CLI em `tools/dormant_refresh.py`. (Contrato formal `core/contracts/forgetting-curve-contract.md` = fase posterior.)

## Quando

- No boot (Plano do Dia), 1×/dia, antes do bloco de questões/cards.
- Sob demanda: "refresca X" ou `/refrescar [tema]`.

## Distinção de `/revisar` (não confundir)

| | `/revisar` | `/refrescar` (este) |
|---|---|---|
| Unidade | card a card (FSRS) | TEMA inteiro |
| Forma | sonda → avalia 1-4 | narrativa reconstrutiva |
| Compressão | calibrada (Camada 0) | sempre **descomprime** |
| Toca FSRS? | sim (grava rating) | **não** (só `review_log`) |
| Gatilho | fila vencida | dormência (dias sem rever) |

## Protocolo (atômico — sem orquestração numerada cruzada)

1. **Pick** — `python tools/dormant_refresh.py --pick [--area X]` → tema do dia (JSON). `{"empty": true}` = sem tema elegível → pular.
2. **Substrato** — `python tools/dormant_refresh.py --context --tema "<tema>" --area "<area>"` → JSON com `resumo_content`, `erros_recentes`, `relevant_chunks`, `cards_ativos`, `weak_areas`.
3. **Narrar (inline, menos comprimido)** — 3-6 parágrafos curtos de **prosa clínica reconstrutiva** a partir do `resumo_content`: reconta o tema como um fio causal **mecanismo → conduta → armadilha**, não bullets de gabarito. Puxar 2-4 armadilhas vivas + os `erros_recentes`/`weak_areas` do estudante naquele tema. Fechar com **"o elo que você costuma quebrar aqui"**. Densidade Gold Standard (AGENTE §4), sem tabelas. Se `resumo_content` for nulo, narrar a partir de `relevant_chunks` + `erros_recentes` e sinalizar que falta resumo de base.
4. **Carimbar** — `python tools/dormant_refresh.py --stamp --tema-id <id> --resumo "<resumo_path>" --note "<1 linha>"`. Grava em `review_log` (kind=dormant_refresh) → o tema esfria no radar e entra na janela anti-repetição (default 7 dias).

## Saída (template)

> 🌡️ **Refresh dormente — <Tema>** (<área> · <dias>d sem rever · <n_cards> cards)
>
> [3-6 parágrafos de prosa reconstrutiva — mecanismo → conduta → armadilha]
>
> **O elo que você costuma quebrar aqui:** [1-2 frases ancoradas nos erros/weak_areas do tema].

## Princípios

- **Re-ensino, não teste.** Não pergunta-e-avalia (isso é `/revisar`); entrega a narrativa pronta para reler.
- **Menos comprimido = reconstrução causal**, para re-hidratar a memória dormente — não listar fatos.
- **Fronteira dura:** nunca chamar `record_review`/`insert_questao`/`insert_card_base`. O único write é o `--stamp` (`review_log`).
- **Rotação:** a janela anti-repetição garante que, ao longo do tempo, todos os temas com cards passem pelo refresh — a base fidedigna de tempo-desde-revisão.
