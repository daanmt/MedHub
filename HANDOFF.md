# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-25 -- **s126: VIRADA MULTI-BANCA (fim do foco total ENAMED) + replanejamento de metas no codigo + drenagem FSRS 61/61 (divida ZERADA, 84% em 3-4) + 3 resumos reforjados. Aula-base D10 de Pneumo Intensiva II entregue.***

## > Proximo passo imediato

1. 🎯 **Pneumologia Intensiva II (VM)** -- aula-base D10 ja entregue (ancorada no PDF, escopo conferido no `Cronograma.pdf`: pags 58-83, secao 4.0). **Falta o bloco de 22 questoes.**
2. Depois, as 3 tasks restantes da S13 (ordem do usuario):
   - **Transtornos de Humor; Psiquiatria Social e Reforma Psiquiatrica** (Teoria)
   - **Introducao a Hepatologia e Ictericia Nao-obstrutiva; Hepatites Virais** (Revisao)
   - **Arboviroses; Meningites e Meningoencefalites; Sepse** (Revisao por Questoes)
3. 📊 **Ritmo novo: ~46q/dia corrido (~54q em 6 dias/semana)** -- nao cobrar mais 96q/dia.

## 🔄 VIRADA s126 -- ler antes de falar de meta

O foco **nao e mais so o ENAMED**. Provas: ENAMED (13/09) + **UERJ + USP (nov-dez, sem edital)**. Regime = **constancia > pico**.
- **Marcos novos:** `Cronograma EMED (grade completa) 9454 @ 25/10` -> `2o ciclo UERJ/USP 12500 @ 31/12` -> stretch 15000. **Ramp de 17.000 morto.**
- **Achado:** a grade fecha ~25/10, **6 semanas DEPOIS do ENAMED** -- o "96q/dia" era artefato de comprimir 13 semanas em 50 dias. Bug corrigido em `_cronograma_hoje`/`recomendar_dia` (dividiam a grade pelos dias ate o ENAMED).
- **Simulado agora CONTA no volume** (reverte s099), separado so na apresentacao (bloco dedicado). Teto de cards 30 -> **40/dia**.
- Memoria: `project_novo_norte_multi_banca` e a fonte de qualquer numero de meta/ritmo.

## Padroes de erro vivos -- atencao do scrum master

- 🔴 **Bug no1c (fato no contexto errado) -- DOIS eventos com IECA na s126:** #422 (trocar IECA por BRA: mesmo eixo, mesmo dano) e #358 (IECA em gestante = teratogeno). "IECA reduz proteinuria" e verdade na DRC e foi transportado para fora da condicao. **Ritual novo:** "em que condicao eu aprendi esse fato?"
- 🔴 **Padrao-mestre (`feedback_bug_discriminador_exclui`):** ancora no achado saliente e ignora o dado que EXCLUI. Provas s126: #213 (AESP+asmatico = pneumotorax, nao seletiva), #490 (sinais neuro = hipotireoidismo, nao leite materno), #95/#475 ("hipoplasia de VE" grudou no caso errado e desgrudou do certo).
- 🟢 **Vitorias:** #416 (K rabdomiolise, invertido antes) · #755/#756 (Febre Amarela reforco 4a, 2x sem reincidir) · #498 (cisto de cordao) · **#761 e #829 usaram o discriminador NEGATIVO ativamente** -- a habilidade-alvo funcionando.
- 🟢 **Imunizacoes 8/8 (nota 4)** num cluster "frio". O agente previu colapso e errou; usuario recusou o PREPARAR e acertou. Dificuldade recalibrada **D10 -> 6** (`agente_inferida`).

## Estado por frente
- **Volume & Metas:** 5232 / 9454 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~45.9q/dia (92d p/ Cronograma EMED (grade completa)). [derivado: day_plan --handoff-block]
- **FSRS:** divida 0 atrasados + 4 p/ hoje -- pool 372 nunca introduzidos (entram <=40/dia). [derivado] s126 drenou **61/61**: 37x4, 14x3, 6x2, 4x1.
- **Conteudo:** 71 resumos. Reforjados na s126: `Cardiopatias Congenitas.md` (matriz fluxo x idade + 5 armadilhas; hipoplasia de VE nao existia no arquivo), `Sindromes Hipertensivas da Gestacao.md` (IECA/BRA proibidos + sal), `Ictericia e Sepse Neonatal.md` (3 galhos da prolongada; hipotireoidismo ausente). `Lesao Renal Aguda.md` **auditado e NAO editado** -- ja cobria o ponto (gap de recall puro).
- **Erros & Cards:** 7 erros de DII em 24/07 (#589-595). Nenhum card novo na s126.
- **Posicao cronograma:** db=S13 (nominal S17, atraso 4 sem). Drive stale (F36 aberto).

## Pendencias ativas
Bloco de 22q de Pneumo Intensiva II. Reforja de `TCE.md` + `Sistemas de Informacao em Saude.md` (prosa fora do padrao). Card #828 (BCF/sonar) = WARN de auto-suficiencia, **confirmado pelo usuario ao vivo** ("card mal escrito"); #326 e #206 tambem sinalizados por ele -- fila de curadoria. Ledger `AUDITORIA_MEDHUB.md`: **F36** (boot Drive: binario grande via MCP nao materializa -> `--sync-drive` pulado 3 sessoes), **F35** (seletor de suite do `auto_check` nao pegou `test_orquestrador` mesmo com `db.py` alterado -- rodado a mao), F8 (isolamento PREPARAR D8+). Ano da diretriz de HAS (2020 x SBC 2025).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_126.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
