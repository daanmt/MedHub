# Session 059 — Análise de Questões: Demências e EM
**Data:** 2026-03-29
**Ferramenta:** Antigravity
**Continuidade:** Sessão 058

---

## O que foi feito
- Análise de 4 questões erradas de Clínica Médica / Neurologia oriundas de um bloco de 21 questões.
- Inserção estruturada dos 4 erros no banco SQLite (`ipub.db`) mapeando elos e armadilhas identificadas.
- Atualização substancial do resumo clínico `Demências.md` com os aprendizados práticos absorvidos.

## Padrões de erro identificados
- **Comprometimento funcional se sobrepondo a MEEM:** Falha em reconhecer que prejuízos de AVDs dictam o diagnóstico sindrômico demencial mesmo quando mascarado por MEEM gabaritado em pacientes de alta escolaridade.
- **Risco Epidemiológico:** Confundir Doença Priônica (raríssima) com Demência Vascular por pequenos vasos (forma comum/Binswanger).
- **Tríade de CADASIL:** Não associar demência executiva precoce com sintomas motores focais e história macrofamiliar de AVC à demência hereditária vascular.
- **Cognição na EM sem depressão ativa:** Dificuldade em priorizar Reabilitação Cognitiva ao invés do escalonamento medicamentoso quando o PHQ-9 (e exames/história) descartam um quadro depressivo em acompanhamento simultâneo do paciente com EM.

## Artefatos criados/modificados
- `resumos/Clínica Médica/Neurologia/Demências.md`
- `ipub.db` (via script)
- `ESTADO.md`
- `history/session_059.md`

## Decisões tomadas
- Armadilhas de interpretação de prova como a pegadinha do MEEM 29/30 e as prevalências epidemiológicas em demências ganham forte destaque dentro das Armadilhas de Prova de forma cumulativa, para forçar reflexão de segunda ordem.

## Próximos passos (se houver)
- Revisão FSRS pendente para Março.
