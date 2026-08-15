# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-15 -- drenagem de 100 cards + curadoria em escala + HAS/TCE-ABC (sessão 145)*

## > Próximo passo imediato

1. **Amanhã (16/08): SIMULADO agendado** (cadência 2/semana) -- é o próximo ato, não a fila FSRS
   (dívida baixíssima) nem cronograma novo.
2. **Ritmo decidido nesta sessão: 100q/dia, 5x/semana + 2 simulados/semana.** Projeção (ver
   `session_145.md`): **8.819 acumulado até 13/09** (93% da grade, alcança S20) e **13.019 até
   25/10** -- estoura o teto anual de 12.500 quase 2 meses cedo (cruza ~20/10). Vale revisitar a
   meta de fim de ano (subir pro stretch 15k?) quando chegar perto disso.
3. **Próxima sessão de flashcard: pool inteiro (529) vira prioridade**, não intake normal --
   usuário quer servir de camada de QA ao vivo (reforja/exclusão/fork), igual ao ritmo de hoje.
   Teto de cards fica em aberto até zerar o pool; revisitar depois.
4. **Confirmar S14 no Drive antes de assumir S15.** Dado desatualizado (20+ dias) -- pode listar
   tarefa já feita ou fora de ordem real. Rodar `tools/cronograma.py --sync-drive <xlsx>` primeiro.
5. **S15 (quando abrir):** 12 tasks / 384 questões. Destaque: **HAS Pt. 3** -- conecta direto com o
   bloco de fechamento de hoje. Também: Câncer de Mama, Assistência ao Parto, APS, Aleitamento
   Materno, Parasitoses (extensivo/teoria nova, sem revisão prévia).

## Estado por frente
- **Volume & Metas:** 6019 / 9454 (perf. ~78.4%). Hoje: 0 -- **2a sessão seguida sem volume** (s144
  também foi 100% engenharia). Ritmo-alvo ~48.4q/dia (71d p/ Cronograma EMED).
- **FSRS:** dívida 2 atrasados + 3 p/ hoje -- muito baixa após a drenagem de 100. Pool 529.
- **Conteudo:** 125 resumos em resumos/. [derivado: glob]
- **Posicao:** conteudo S14 (nominal S20, atraso 6 sem) -- S15 pronto pra abrir, ver passo 2 acima.
- **Erros & Cards:** cards ativos ~984 (12 defeitos reais de autoria corrigidos nesta sessão --
  reforges, forks, 7 duplicatas de import aposentadas).
- **Simulados:** S4 66/100 (13/08) foi o último. **Próximo: amanhã 16/08.**
- **Datas:** ENAMED **13/09** (prova) · grade EMED fecha **25/10** · UERJ/USP sem edital.
- **Infraestrutura:** **Boot v2 validado** -- 2 chamadas de ferramenta até o 1o ato útil (vs baseline
  ~15 da s144). Arquitetura da consolidação confirmada na prática, não só na teoria.

## Última sessão -- s145 (FLASHCARDS + CURADORIA, dia inteiro)
Boot v2 testado (2 chamadas) -> 100 cards FSRS drenados (93 gravados: 46/17/10/20 por nota; relearning
intra-sessão **finalmente executado de fato** -- gap documentado desde s077, nunca rodava até hoje) ->
26 tasks de curadoria de flashcard abertas ao vivo pelo usuário e todas fechadas (reforges in-place,
forks preservando `questao_id`, 7 duplicatas de import aposentadas, 1 incidente de taxonomia
auto-detectado e corrigido) -> Revisão Direcionada em 6 blocos: **HAS** e **TCE/ABC** densos (o
padrão nº1 de fraqueza confirmado 4x fora do domínio de origem -- é sobre acuidade em geral, não só
epilepsia), Toxoplasmose/Cardiopatias/Etilismo/Planejamento Familiar leves. Detalhe completo:
`history/session_145.md`.

## Pendências/observações ativas
- Volume zerado 2 sessões seguidas -- se virar padrão, o ritmo-alvo real fica pior que o calculado
  (que assume distribuição uniforme entre dias de estudo e engenharia).
- Bug do "(1250 erros)" no boot (`app/memory/manager.py:91-128`, `GROUP BY area` sozinho) segue aberto
  desde a s144 -- não tocado nesta sessão, conserto pequeno (~15 linhas).
- Ritmo é medido contra a **grade (25/10)**, nunca contra o ENAMED -- correção deliberada da s126.

---
*Histórico: history/INDEX.md * Macro: ESTADO.md * Sessão: history/session_145.md*
