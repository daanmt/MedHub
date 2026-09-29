# Session 204 -- F140 auditado e corrigido no mesmo dia, e o ledger rotacionado: só o que está em aberto fica na frente

**Data:** 2026-09-28 (segunda, noite) - **Ferramenta:** Claude Code (Fable 5.1) - **Continuidade:** `session_203.md` - **/ai-eng:** não estava aberto (report deixado em arquivo no workspace dele)

---

## O que foi feito
1. **Pedido do operador:** verificar o documento que eu mesmo escrevi sobre o problema dos flashcards de hoje (F140), com subagentes Sonnet e Opus e o loop de auditoria; report ao /ai-eng no fim.
2. **Plano com DoD binário** (7 checks) e fan-out por eixo: O1 Opus (replay, escala, simulação), S1 Sonnet (alcance no código), S2 Sonnet (portadores de norma), O2 Opus (evidência externa, web isolada). Todos read-only; banco real intocado (cópia em `mode=ro`).
3. **Medição direta do principal**, antes e depois dos filhos: os 11 cards no banco, os lotes `28a`/`28b`, o fonte do py-fsrs instalado e a escala no revlog. Número só entrou com duas lentes batendo.
4. **Veredito do F140: PARTIAL.** 4 afirmações confirmadas, 2 imprecisas, 3 refutadas. A causa real é o `relearning_steps` no default do py-fsrs (1 passo de 10 min), não `learning_steps=()` com estabilidade baixa.
5. **Ledger:** F140 reescrito com lápides (texto original preservado) e promovido a GATE; ponteiro de reincidência no F32; F141 e F142 abertos como DECLARADOS.
6. **Report ao /ai-eng** em `~/ai-eng/HANDOFF-MEDHUB-F140-AUDITORIA-2026-09-28.md` (não há sessão dele viva; o precedente é handoff por arquivo na raiz do workspace dele).
7. **Tique do `/hub-backend`** (disparado pelo `/loop` que seguia ligado nesta mesma sessão): lote `2026-09-28b` em 0/13, nada a fazer.
8. **Decisão do operador e o fix, pelo loop do vibeflow** (spec em 3 parts -> teste vermelho -> implementação -> auditoria PASS): (a) `relearning_steps=()` no adapter, com `KWARGS_BASE` como fonte única que o otimizador importa; (b) `--export-player` enche o saldo do teto com cards novos (`novos_do_lote`, duas passadas), fila do chat segue em 10; (c) rito dos 3 passos: `revisao-calibrada` v1.9, `fsrs-management` v1.6, `revisar.md`, `hub-backend.md`, 4 termos cadastrados.
9. **Golden do fix:** Scheduler antigo x novo sobre as mesmas 3.589 entradas -- estabilidade e dificuldade idênticas; só `state`/`due` mudam, nas 362 linhas que caíam no passo. Export contra o banco real: 53 cards (3 + 50).
10. **Push** autorizado por ele; **`/loop` desligado** por ordem dele (job `3f6af4b9`).
11. **Rotação do ledger** (decisão dele: *"o que resolvermos, sai da frente"*), pelo mesmo loop (spec em 3 parts -> teste vermelho -> implementação -> auditoria PASS): `tools/selo.py` lê os dois arquivos, ganha `--rotacionar` (dry-run, `--apply --expect N`) e `--onde`, e passa a listar TUDO que está em aberto (GATE e DECLARADO ficavam fora da saída: 12 achados invisíveis); `consistencia_check` ganha o check `frente`, que bloqueia resolvido na frente, aberto no histórico e índice velho.
12. **Migração de partida com prova de conservação:** 125 blocos com sha256 conservado, 153 segmentos no histórico byte a byte, conta de bytes fechando. Resultado: **19 em aberto na frente (58 KB), 105 resolvidos no histórico (350 KB)**.
13. **Lote novo publicado a pedido dele** (*"pode publicar o lote novo, incluir os que já estão na fila/atrasados"*): export de véspera para 29/09, 100 cards (3 atrasados + 44 do dia + 53 novos). Antes do publish: a página nova conferida contra a publicada (idêntica fora do bloco do lote) e os 100 cards lidos inteiros.

hub-backend: 2026-09-28b sem notas (0/13, nada a gravar) -> 2026-09-29a no ar (100 cards) -- Version 41

hub-backend: republicado com o mesmo lote 2026-09-29a (painel mudou) -- Version 42 -- /loop 1h religado a pedido dele (job 98a4cfaf)

## Achados de engenharia (ledger)
- **F140 -> GATE na auditoria, RESOLVIDO na mesma noite.** Nota 1 sobre card em `state=2` leva a `state=3` com `due = revisão + 10 min`; o lote seguinte do dia re-serve e GRAVA a 2ª nota. Replay 11/11; revlog inteiro reproduz em 3.579/3.579.
- **F140 é reincidência do F32** (s112, re-triado na s176). Escrevi o F140 sem consultar o ledger. **F32 RESOLVIDO** junto: a colisão acabou por remoção de uma das camadas.
- **O comportamento está em contrato** (`revisao-calibrada-contract.md:232`, "o card volta hoje"): mudar é decisão de produto, pelo rito dos 3 passos.
- **F141 (novo, DECLARADO):** card de 1 dia servido na manhã seguinte com menos de 24 h cai no ramo de curto prazo da biblioteca. 212 revisões, 138 em setembro.
- **F142 (novo, DECLARADO):** sem trava de 2ª gravação do mesmo card no mesmo dia entre lotes; o teto conta linha do revlog. 83 re-revisões no mesmo dia.
- Selo derivado no fim da sessão: 124 achados, 19 em aberto, 105 resolvidos; 0 discordâncias, 0 fora do lugar.

## Erros meus nesta sessão
- Escrevi no HANDOFF que o `/loop` do backend estava desligado. Estava ligado, nesta mesma sessão (ela continua a da s203 depois do `/clear`). Só vi quando o tique disparou; corrigido no HANDOFF.
- Reportei ao operador números parciais de escala **antes** de corrigir o fuso do revlog antigo (65, 145, 150, 412). Os corretos, com duas lentes: 49, 83, 212, 512. Correção declarada no relatório e no chat.

## Decisões tomadas
- **Operador (28/09, noite):** *"1. volta apenas no dia seguinte. 'hoje' é apenas no redrill, já contemplado. 2. saldo por teto, que deve passar a 100 cards/dia."* O teto já era 100/dia desde a s196; nada mudou nele.
- **Operador:** o ledger tem de deixar claro o que está aberto e o que foi resolvido; resolvido sai da frente; sem backlog infinito. Push autorizado; loops desligados.
- Minha, na fase de auditoria: anti-escopo total de código até a decisão dele.
- Operador: publicar o lote novo e encerrar formalmente.

## Artefatos criados/modificados
- `.vibeflow/audits/f140-fila-pos-bloco-audit.md` e `.vibeflow/audits/nota1-volta-no-dia-seguinte-audit.md` (novos)
- `.vibeflow/specs/nota1-volta-no-dia-seguinte-part-{1,2,3}.md` (novos)
- `app/utils/fsrs.py`, `tools/fsrs_optimize.py`, `tools/fsrs_queue.py` + testes (`test_fsrs.py`, `test_fsrs_optimize.py`, `test_fsrs_queue_player.py`)
- `core/contracts/revisao-calibrada-contract.md` (v1.9), `core/contracts/fsrs-management-contract.md` (v1.6), `.claude/commands/revisar.md`, `.claude/commands/hub-backend.md` (+ espelhos), `docs/MEMORIA-AUDITORIA.md`, `.vibeflow/index.md`, `.vibeflow/conventions.md`, `AGENTE.md` (linha gerada da tabela 7.4)
- `AUDITORIA_MEDHUB.md` (agora só os abertos) e `history/auditoria/resolvidos.md` (novo)
- `tools/selo.py`, `tools/consistencia_check.py`, `tools/auto_check.py`, `tools/habilidades.py`, `tools/test_selo_rotacao.py` (novo), `tools/test_consistencia_registros.py`, `pytest.ini`, `tools/_archive/migrations/rotacao_ledger_s204.py`
- `.vibeflow/specs/ledger-rotacao-part-{1,2,3}.md`, `.vibeflow/audits/ledger-rotacao-audit.md`, `.claude/commands/engenharia-cli.md` (+ espelho), `.agents/workflows/registrar-sessao.md`, `README.md`
- `HANDOFF.md`, `history/INDEX.md`, `history/session_204.md`
- `tmp/f140_auditoria/` (local, fora do git): 4 relatórios crus + scripts e saídas do O1
- Fora do repo: `~/ai-eng/HANDOFF-MEDHUB-F140-AUDITORIA-2026-09-28.md`

## Custo dos subagentes (lido do `usage` do harness)
- Auditoria: O1 Opus 233.437 tokens, 54 chamadas, 15,4 min · S2 Sonnet 220.508, 74, 9,9 min · S1 Sonnet 169.222, 55, 8,5 min · O2 Opus 124.610, 40, 7,0 min.
- Varredura do ledger: S3 Sonnet 231.199 tokens, 61 chamadas, 15,9 min.
- Total: 978.976 tokens em 5 filhos.

## Próximos passos
- **Operador (ledger):** 7 dos 19 abertos esperam decisão dele (F111, F87, F69, F68, F67, F65, F39). Decidir ou descartar é o que impede o backlog de crescer.
- **Cards:** lote `2026-09-29a` (100) no ar. 7 cards com o contexto cortado no meio da frase (#671 #762 #764 #765 #766 #767 #768) -> curadoria.
- **Operador (observação):** nota 4 = 379 de 522 notas da régua v2 (72,6%); o contrato a descreve como rara.
- **/ai-eng:** triagem de F141 e F142; checkpoint da s203 segue pendente.
- **Estudo:** UERJ 2021 (t1793) e a Autópsia dos erros, como estava no HANDOFF.
