# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-03 -- virada CRM/piso ENAMED + S14 SUS/Asma 94q (90%/90%) + dreno FSRS 50 cards (sessão 134)*

## > Proximo passo imediato

1. **Executar tarefa 3 de S14: Colecistite e Colangite Aguda (44q).** Aula-base D8 já entregue e pronta -- só rodar as questões e voltar com o resultado.
2. **Simulado #1 da semana** (quarta ou quinta) -- compromisso da cadência nova (2/semana, ver Pendências).
3. Manter ritmo de cards 30-50/dia nesta semana (calibrado pelo próprio ritmo real de hoje: 50 cards num só lote).

## Estado por frente
- **Volume & Metas:** 5.535 / 9.454 (perf. ~78,9%). Hoje: 94q (Preventiva 30 + Pediatria 20) via sessões-bulk + 50 cards FSRS. Ritmo-alvo ~47,2q/dia (83d p/ Cronograma EMED completo). [derivado: day_plan --handoff-block]
- **Conteúdo:** 76 resumos -- 2 editados hoje (SUS §5.4 discriminação de atributos; Cirurgia Infantil conteúdo herniário por sexo) + 1 **novo** (Pediatria/Asma.md, GINA 2025, não existia antes). [derivado: glob]
- **Erros & Cards:** 667+5 = 672 erros acumulados (5 hoje: 3 SUS + 2 Asma, cards 1083-1087). Fila de reforja por defeito de autoria em 9 cards (477,478,483,484,485,486,505,513,521) -- sinalizados no dreno de hoje, não processados ainda.
- **FSRS:** dívida 0 atrasados + 5 p/ hoje -- pool 541 nunca introduzidos (entram <=40/dia). Lote de 50 cards revisado hoje (muito acima do teto de 40) -- ver padrões abaixo.
- **Posição:** conteúdo real **S14**, tarefas 1-2/11 feitas (SUS, Asma), 3/11 preparada não executada (Colecistite), 4-11 não iniciadas. day_plan ainda sugere S13 -- Drive não ressincronizado (F36, ver Pendências), ignorar a sugestão.

## Última sessão -- sessão 134
- **VIRADA:** ENAMED agora também é piso de registro no CRM (~60% em simulado), condição anterior a qualquer competição por vaga de residência -- não reverte o multi-banca (s126), reordena a prioridade imediata. Cadência da semana fechada: 2 simulados (qua/qui + dom) + 30-50 cards/dia + acelerar S14.
- Dreno FSRS 50 cards: padrão-mestre discriminador-exclui reforçado 3x; "parou no detalhe" promovido a 🔴 (3x); achado NOVO "escalonar antes de checar gravidade" 2x em Síndromes Hipertensivas (eco obstétrico do bug de sequência do ATLS); 1 gap real corrigido (Cirurgia Infantil, conteúdo herniário por sexo); 9 cards flagados pra reforja.
- 3 aulas-base entregues (SUS D5, Asma D5, Colecistite D8 recalibrado pela fraqueza persistente -- 884 erros no radar). SUS 30q/90% (3 erros, mesma habilidade -- discriminação de atributos da APS por vinheta). Asma 20q/90% (2 erros -- 1 banca-dependente MART/dose, 1 gap real de gravidade de crise; resumo pediátrico criado do zero).
- Resync do Drive falhou 2x no relay binário via chat -- **reincidência confirmada de F36** (já documentado desde s128, não é achado novo). Contornado via `read_file_content` (texto puro). `Cronograma.pdf` extraído direto pra pegar questões/tarefa (grade.json só guarda total semanal).
- Colecistite/Colangite (tarefa 3, 44q): aula-base pronta, questões adiadas pelo usuário.

## Pendências/observações ativas
- Reforja: 9 cards com defeito de autoria (multi-fato) -- 477,478,483,484,485,486,505,513,521.
- Backlog antigo: 34 temas do simulado s131 ainda sem resumo/armadilha escrita.
- F36 (`--fetch-drive`) segue sem implementação -- 6a sessão seguida contornando via `read_file_content`; ver `AUDITORIA_MEDHUB.md`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_134.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
