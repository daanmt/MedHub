# Session 131 — Simulado ENARE/ENAMED (100q, 54%) + 2 padrões novos no ledger + playbook atualizado + estratégia multi-banca refinada

**Data:** 2026-08-02
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 130

---

## O que foi feito

### Simulado ENARE/ENAMED — 100 questões, 11:34 às 14:11 (com pausas longas)
Fecha o débito de simulado (política 1/semana, último em 28/06 — 5 semanas de atraso) e ataca diretamente a variância alta entre blocos (10,4pp) que o diagnóstico (`variancia.py --zona`) já prescrevia resolver com simulado, não mais bloco por tema.

- **100q / 54 acertos = 54,0%**, bem abaixo da média dos blocos por tema (78,2%). Registrado em `sessoes_bulk` (sessão 131, área Simulado, `--acumular` não necessário).
- **Diagnóstico de bloco (5 PDFs de 20q, sorteados — não por área):** Bloco 1 (Q1-20) 55% · Bloco 2 (Q21-40) 55% · Bloco 3 (Q41-60) 65% · **Bloco 4 (Q61-80) 35%** · Bloco 5 (Q81-100) 60%. O Bloco 4 concentrou 13 dos 46 erros. Verificado contra a dificuldade populacional média das questões erradas por bloco (48,7% a 59,8% — Bloco 4 em 51,2%, dentro da faixa): não foi conteúdo mais difícil, foi atenção dividida durante a prova (usuário relatou multitasking) — variância intra-prova também é sinal de execução.

### Os 46 erros — analisados em 2 lotes de 23, persistidos via `insert_questao.py --errors-file`
Todos com cards atômicos + FSRS inicializado. 0 duplicatas nos dois lotes (ids `questoes_erros` 622-667).

### Ledger de habilidades — 3 padrões cruzaram pra 🔴 PADRÃO DE RACIOCÍNIO
Via `tools/habilidades.py --backfill` + `--add` manual para consolidar fraseio (corrigido 1 erro de `--questao-id` no meio do processo, verificado e corrigido via UPDATE direto).

- **"Ler exame NORMAL como dado que EXCLUI"** (vivo desde s128, Hepato) → agora **5 especialidades, 100% erro**: +Cirurgia (obstrução por bridas sem peritonite), +Neurologia (demência vascular sem ventriculomegalia), +Obstetrícia (pré-eclâmpsia sem sinais de gravidade). Variante inversa também vista: cancroide vs sífilis (achado POSITIVO — dor presente — que exclui).
- **NOVO — "Incorpora diretriz/protocolo desatualizado"** → **4 especialidades**: SBC-HAS 2025 (pré-hipertensão 120-139/80-89), Reanimação Neonatal 2026 (sem aspiração traqueal de rotina), Dislipidemia 2025 (LDL<40 em risco extremo/eventos recorrentes), ATLS 11ª ed. (xABCDE — hemorragia exsanguinante antes da reposição volêmica).
- **NOVO — "Pula a hierarquia do exame inicial pro avançado"** → **3 especialidades**: lombalgia (RM em vez de radiografia), anemia perniciosa (biópsia de medula em vez de anti-FI), TCE leve (neurocirurgia em vez de TC).
- Semeado, observando (2 temas): "avalia pelo achado mais chamativo, não pela janela/curva esperada" (puericultura-crescimento + DNPM).

### Confirmações diretas de áreas fracas preexistentes
- **Drenagem biliar atingida 2x na mesma sessão** — colangite aguda (Q31) e coledocolitíase/CPRE-vs-colecistectomia (Q98) — mesmo tema do radar de 884 erros (`Abdome Agudo Inflamatório - Colecistite e Colangite Aguda`).
- **Tamponamento cardíaco antes de laparotomia** (Q86) bate na área "sequência ATLS desorganizada" já catalogada.

### `PLAYBOOK_EXECUCAO_PROVA.md` atualizado
2 novas linhas na tabela de sub-padrões, nova seção "sub-família à parte: conhecimento desatualizado" (eixo diferente — não é processo interrompido, é régua desatualizada), nova seção "Evidência da s131", e o reflexo de execução evoluiu de reflexo único para **tripé** (3 perguntas antes de marcar qualquer resposta).

### Estratégia multi-banca refinada (conversa com o usuário)
Não muda o plano da virada s126 (ENAMED 13/09 deixou de ser corrida de volume; grade fecha só ~25/10; UERJ/USP nov-dez sem edital) — refina a aplicação:
- Até o ENAMED: cronograma no ritmo atual (sem sprint pelo susto do 54%), tripé rodando em toda questão, simulado semanal virou compromisso (~5-6 restantes até 13/09).
- Pós-ENAMED: pivô pra provas antigas de UERJ/USP já planejado continua valendo; o tripé já vai pronto; primeira rodada de provas antigas de cada banca deve ser tratada como simulado diagnóstico.

---

## Artefatos criados/modificados
- `PLAYBOOK_EXECUCAO_PROVA.md` — 2 sub-padrões novos + seção de diretriz desatualizada + evidência s131 + tripé
- `HANDOFF.md` — rotacionado
- Memória: `feedback_bug_discriminador_exclui.md`, `project_decompose_bug_execucao_prova.md` — atualizadas com evidência s131
- `ipub.db` — 46 erros + 46 cards + FSRS (não versionado)

## Decisões tomadas
- Cronograma não acelera por causa do resultado do simulado (mantém constância > pico, decisão s126).
- Redação das armadilhas nos `resumos/*.md` dos ~35 temas novos fica como frente própria — não coube nesta sessão.
- Simulado semanal tratado como compromisso não-negociável (não mais aspiração) pelo resto da janela até o ENAMED.

## Próximos passos
1. Escrever armadilhas nos resumos dos ~35 temas novos (lista completa em `HANDOFF.md`).
2. Voltar ao ritmo normal: FSRS (62 vencidos) + questões S14.
3. Próximo simulado em até 7 dias.
