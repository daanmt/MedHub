# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-14 -- consolidação: boot barato + multi-prova (sessão 144)*

## > Próximo passo imediato

1. **Novo boot como teste de aceitação.** O usuário pediu para aferir se a arquitetura melhorou depois
   dos consertos. Medir: **chamadas de ferramenta até o primeiro ato útil**. Baseline s144 = **~15**;
   alvo = **0-1** (o hook `SessionStart` já entrega o Plano do Dia antes do 1º turno e o `AGENTE.md §2
   passo 4` não manda mais rodar de novo).
2. **Dívida de estudo herdada da s143, intocada** (s144 foi 100% engenharia, volume do dia = 0):
   redrill dos **42 cards nota < 4** (`tmp/redrill42.json`) e os 3 gaps de Revisão Direcionada --
   AGC/colpocitologia (card 453), escores estimados em vez de somados (PRAM/Caprini/Apgar),
   "diagnóstico feito != pode tratar" (card 538). Ambos os cards já estão na fila.
3. **GO do operador sobre o resto da consolidação:** partes **5, 6 e 7** das specs
   (`.vibeflow/specs/consolidacao-part-{5,6,7}.md`) -- normas que mentem + sensores mal calibrados (D1/D2/D3),
   wiring e check de alcançabilidade v0 (D4), auto-higiene no rito de encerramento. Partes 1-4 entregues.

## Estado por frente
- **Volume & Metas:** 6019 / 9454 (perf. ~78.4%). Hoje: 0. Ritmo-alvo ~47.7q/dia (72d p/ Cronograma EMED (grade completa)).
- **FSRS:** divida 3 atrasados + 40 p/ hoje -- pool 554 nunca introduzidos (entram <=40/dia).
- **Conteudo:** 125 resumos em resumos/. [derivado: glob]
- **Posicao:** conteudo S14 (nominal S20, atraso 6 sem) [derivado: preparacao_estado]
- **Erros & Cards:** 812 erros · 978 cards ativos · ~280 na worklist de atomicidade (WARN).
- **Simulados:** S2 54/100 (02/08) -> S3 60/100 (06/08) -> S4 66/100 (13/08). Próximo pendente.
- **Datas:** ENAMED **13/09** (prova) · grade EMED fecha **25/10** (não é prova) · UERJ/USP sem edital.
  Fonte única: `core/provas.json`; o plano do dia imprime o countdown de cada uma.
- **Infraestrutura:** B1 do reconcile (HANDOFF > 60 linhas) virou **BLOCKING real** no `auto_check`
  (check 10) -- estourar o teto agora quebra o harness, não só adverte.

## Última sessão -- s144 (ENGENHARIA, dia inteiro)
- **Auditoria de arquitetura** dos 7 sistemas não-flashcard (7 subagents + verificação adversarial):
  a acumulação é de **alcançabilidade**, não de desleixo -- os gates verificam se está correto, nada
  verifica se alguém chega lá. 6 defeitos estruturais D1-D6.
- **3 ciclos de consertos no mesmo dia:** flashcards-integridade (partes 1-6, audit PASS 6/6),
  flashcards-p3 (partes 1-4, audit PASS 4/4), consolidação (partes 1-4). Selo com hashes em `session_144.md`.
- **Boot barato (part-4):** `AGENTE.md §2 passo 4` de 272 -> 56 palavras; sync do Drive deixa de exigir
  binário via MCP (conclusão pelo `Realizada?` do Dashboard; ordem = ritual do usuário).
- **Poda de acreção:** ESTADO 3.071 -> 1.095 palavras, HANDOFF dentro do teto; **nada foi apagado** --
  a narrativa migrou para `history/session_144.md §Anexo`.
- **Bug aberto:** o `(1250 erros)` do boot vem de `app/memory/manager.py:91-128` (`GROUP BY area` sozinho
  + substring com `break`). Conserto ~15 linhas, sem schema.

## Pendências/observações ativas
- Ritmo é medido contra a **grade (25/10)**, nunca contra o ENAMED -- correção deliberada da s126, com
  teste que cai se alguém reencostar o countdown na fórmula.
- `sync_skills --check` falha desde 17/07 (WARN de paridade); entra na part-5.

---
*Histórico: history/INDEX.md * Macro: ESTADO.md * Sessão: history/session_144.md*
*Auditoria: ai-eng/HANDOFF_MEDHUB_SISTEMAS.md * Relatório: artifact 5d536604*
