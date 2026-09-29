# Session 204 -- auditoria do F140: a causa estava errada, o achado não era novo, e dois achados novos saíram da medição

**Data:** 2026-09-28 (segunda, noite) - **Ferramenta:** Claude Code (Fable 5.1) - **Continuidade:** `session_203.md` - **/ai-eng:** não estava aberto (report deixado em arquivo no workspace dele)

---

## O que foi feito
1. **Pedido do operador:** verificar o documento que eu mesmo escrevi sobre o problema dos flashcards de hoje (F140), com subagentes Sonnet e Opus e o loop de auditoria; report ao /ai-eng no fim.
2. **Plano com DoD binário** (7 checks) e fan-out por eixo: O1 Opus (replay, escala, simulação), S1 Sonnet (alcance no código), S2 Sonnet (portadores de norma), O2 Opus (evidência externa, web isolada). Todos read-only; banco real intocado (cópia em `mode=ro`).
3. **Medição direta do principal**, antes e depois dos filhos: os 11 cards no banco, os lotes `28a`/`28b`, o fonte do py-fsrs instalado e a escala no revlog. Número só entrou com duas lentes batendo.
4. **Veredito do F140: PARTIAL.** 4 afirmações confirmadas, 2 imprecisas, 3 refutadas. A causa real é o `relearning_steps` no default do py-fsrs (1 passo de 10 min), não `learning_steps=()` com estabilidade baixa.
5. **Ledger:** F140 reescrito com lápides (texto original preservado) e promovido a GATE; ponteiro de reincidência no F32; F141 e F142 abertos como DECLARADOS.
6. **Report ao /ai-eng** em `~/ai-eng/HANDOFF-MEDHUB-F140-AUDITORIA-2026-09-28.md` (não há sessão dele viva; o precedente é handoff por arquivo na raiz do workspace dele).

## Achados de engenharia (ledger)
- **F140 -> GATE.** Nota 1 sobre card em `state=2` leva a `state=3` com `due = revisão + 10 min`; o lote seguinte do dia re-serve e GRAVA a 2ª nota. Replay 11/11; revlog inteiro reproduz em 3.579/3.579.
- **F140 é reincidência do F32** (s112, re-triado na s176). Escrevi o F140 sem consultar o ledger.
- **O comportamento está em contrato** (`revisao-calibrada-contract.md:232`, "o card volta hoje"): mudar é decisão de produto, pelo rito dos 3 passos.
- **F141 (novo, DECLARADO):** card de 1 dia servido na manhã seguinte com menos de 24 h cai no ramo de curto prazo da biblioteca. 212 revisões, 138 em setembro.
- **F142 (novo, DECLARADO):** sem trava de 2ª gravação do mesmo card no mesmo dia entre lotes; o teto conta linha do revlog. 83 re-revisões no mesmo dia.
- Selo derivado depois das edições: todo item com terminal nomeado, 0 discordâncias.

## Erros meus nesta sessão
- Reportei ao operador números parciais de escala **antes** de corrigir o fuso do revlog antigo (65, 145, 150, 412). Os corretos, com duas lentes: 49, 83, 212, 512. Correção declarada no relatório e no chat.

## Decisões tomadas
- Nenhuma do operador nesta sessão. Minha: anti-escopo total de código (nada em `app/`, `tools/`, `core/`), inclusive a deriva de documentação de esforço S, que fica junto do remédio.
- Hub **não** republicado: nenhum dado de estudo mudou.

## Artefatos criados/modificados
- `.vibeflow/audits/f140-fila-pos-bloco-audit.md` (novo)
- `AUDITORIA_MEDHUB.md` (F140, F141, F142, ponteiro no F32)
- `HANDOFF.md`, `history/INDEX.md`, `history/session_204.md`
- `tmp/f140_auditoria/` (local, fora do git): 4 relatórios crus + scripts e saídas do O1
- Fora do repo: `~/ai-eng/HANDOFF-MEDHUB-F140-AUDITORIA-2026-09-28.md`

## Custo dos subagentes (lido do `usage` do harness)
- O1 Opus 233.437 tokens, 54 chamadas, 15,4 min · S2 Sonnet 220.508, 74, 9,9 min · S1 Sonnet 169.222, 55, 8,5 min · O2 Opus 124.610, 40, 7,0 min. Total 747.777 tokens; 15,4 min de parede.

## Próximos passos
- **Operador (GATE do F140):** a nota 1 volta no mesmo dia (hoje) ou só no seguinte (remédio A, recomendado)? Novos por lote: 10 fixos ou o saldo do teto?
- **Operador (observação):** nota 4 = 379 de 522 notas da régua v2 (72,6%); o contrato a descreve como rara.
- **/ai-eng:** triagem de F141 e F142; checkpoint da s203 segue pendente.
- **Estudo:** UERJ 2021 (t1793) e a Autópsia dos erros, como estava no HANDOFF.
