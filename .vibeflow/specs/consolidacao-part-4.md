# Spec: consolidacao-part-4 — boot barato + entidade multi-prova

> PRD: `consolidacao-alcancabilidade.md` · Consertos 3/7 do handoff (D5/D6) + decisão "entidade multi-prova". É o conserto que resolve a reclamação-origem (boot de 13min/15 calls).

## Objective
O boot para de pagar duas vezes pela mesma regra e de tentar o impossível; o cronograma passa a saber que ENAMED (13/09) ≠ fim de grade (25/10) ≠ UERJ/USP (TBD).

## Definition of Done
1. [ ] `AGENTE.md §2 passo 4` reescrito (~272→≤60 palavras): o Plano do Dia JÁ vem injetado pelo hook `SessionStart` (não re-rodar salvo `--difficulty`/`--tempo` sob demanda); sync do Drive DEIXA de ser obrigação do agente; W8 vira ponteiro para `reconcile-contract.md` (zero duplicação verbatim).
2. [ ] W8/`cronograma-contract.md` reescrito com o achado §8: **conclusão** lê a coluna `Realizada?` da planilha Google Sheets nativa "Dashboard EMED 2026" via `read_file_content` (fileId em `importar-planilha.md:32`) — texto puro, sem base64; **ordem** (xlsx reordenado à mão) vira ritual do usuário (`cronograma.py --sync-drive <path>` local), com caveat honesto quando ausente. Nenhum passo de boot pode exigir binário via MCP.
3. [ ] **`core/provas.json`** (novo, versionado): `[{nome, data, tipo: prova|grade, peso?}]` com ENAMED 2026-09-13 (prova), fim-grade-EMED 2026-10-25 (grade); UERJ/USP entram quando houver edital (sem código). `day_plan.py`: countdown por prova no cabeçalho do plano (`ENAMED em N dias · grade fecha em M dias`); ritmo continua calculado contra a GRADE (deliberado s126 — preservar); teste do parser/countdown com fixture.
4. [ ] `AGENTE.md` não mistura mais referenciais ("~94q/dia p/ ENAMED" corrigido para citar grade vs prova conforme provas.json).
5. [ ] Poda de acreção: `ESTADO.md` e `HANDOFF.md` trazidos aos próprios contratos (indicador = linha, não narrativa; HANDOFF ≤60 linhas) — conteúdo narrativo migra para `history/session_144.md` (selo da sessão de engenharia de hoje, ainda pendente) — NADA se perde, muda de endereço; `reconcile` B1 (HANDOFF>60) promovido de WARN a BLOCKING real no check correspondente.
6. [ ] `pytest` verde + smoke: `python tools/day_plan.py` imprime countdowns e nenhum passo do §2 instrui duplicata do hook.

## Scope
`AGENTE.md` (§2 passo 4 + refs de ritmo) · `core/contracts/{cronograma-contract.md,reconcile-contract.md}` (W8/B1) · `core/provas.json`✚ · `tools/day_plan.py` · `ESTADO.md` · `HANDOFF.md` · `history/session_144.md`✚ · teste novo.

## Anti-scope
NÃO mudar a fórmula de ritmo (s126); NÃO implementar leitura do Sheets em Python (é ação MCP do agente em runtime — a mudança aqui é de PROTOCOLO); NÃO tocar grade.json/dados do cronograma.
