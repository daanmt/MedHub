# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-09 -- **s115 (ENGENHARIA, sem questoes): auditoria do boot -> PRD `boot-cronograma-drive-confiavel` em 3 partes (vibeflow, 3 audits PASS). Fecha a costura headless/Drive: disparo OBRIGATORIO do `--sync-drive` + ordem real do xlsx (part-1); `material_indicado` verificado contra o `.md` + WARN de lastro (F30/F31, part-2); contador derivado + ESTADO nao-diario (part-3). Ledger: F30/F31 RESOLVIDO + F34; F21 aberto.***

## > Proximo passo imediato
1. **Proxima sessao (pedido do operador): HAS Pt. 2 -- QUESTOES.** Teoria; so PDF cru em `resumos/Clínica Médica/Cardiologia/` -- extrair+autorar o resumo ANTES do bloco.
2. **Disturbios do Potassio -- QUESTOES.** Tema-zero (so PDF cru); extrair+autorar antes do bloco.
3. Ainda pendentes da S12 depois disso: DITC II (Teoria, estende `DITC.md` existente -- nao e tema-zero); Cefaleias+Epilepsias (tema-zero, PDF-fonte nao localizado -- maior risco da semana).
4. **No boot: rodar `--sync-drive`** -- o snapshot do Drive esta ~1d velho; agora e passo OBRIGATORIO quando o `day_plan` mostra `Drive desatualizado` (buscar o xlsx via MCP + `python tools/cronograma.py --sync-drive <path>` antes de confiar nos "proximos temas").
5. FSRS: 9 atrasados + 5 hoje (backlog 400 novos) -- `/revisar` ou `fsrs_queue.py`.

## Padroes de erro vivos -- atencao do scrum master
*(s115 = engenharia, sem questoes novas; os padroes abaixo carregam da s114 sem novo evento.)*
- RED **REINCIDENCIA CONFIRMADA (2x): crianca DM1 doente = hipoglicemia, nao CAD** -- cruzou automatico com o erro #229 (overlap 0,63) MESMO apos a aula-base da propria sessao (s114) ter citado o cenario quase literalmente horas antes. Ensinar nao bastou -- candidato a mini-drill dedicado do card 775 (`fsrs_queue --pre-bloco`), nao so mais uma entrada na fila normal.
- RED **Ancoragem no farmaco (familia bug no1b):** glibenclamida marcada por reflexo "remedio de diabetes conhecido" num quadro de acidose latica por METFORMINA -- nao checou se o mecanismo do farmaco batia com o quadro (AG aumentado, sem cetose).
- RED **Fato certo, pergunta errada (familia bug no1c):** "albuminuria e mais precoce que creatinina" (verdadeiro p/ ESTADIAR nefropatia) aplicado numa pergunta de CLEARANCE (por que hipoglicemiou -- creatinina/TFGe e quem responde).
- RED **Enunciado longo com ruido decisivo escondido:** DM2 grave tinha os 2 numeros que decidiam (GJ 323, HbA1c 10,7%) afogados em painel de 15+ itens com red herrings -- extrair o que decide antes de resolver.
- Padroes antigos (enunciado negativo, pe de Charcot, mapa de reforco instavel, ferro x folato) seguem arquivados, sem novo evento.

## Estado por frente
- **Volume & Metas:** 4865 / 10000 (perf. ~79.4%). Hoje: 100. Ritmo-alvo ~77.8q/dia (66d p/ ENAMED). [derivado: day_plan --handoff-block]
- **Conteudo:** 63 resumos em resumos/. [derivado: glob] s115 nao criou/editou resumos (engenharia). Gaps abertos: `Sistemas de Informacao em Saude.md` (reforja, prosa fora do padrao-ouro, autoria s069) e `TCE.md`.
- **Erros & Cards:** sem novos nesta sessao (engenharia). Totais inalterados.
- **FSRS:** 9 atrasados + 5 hoje. Backlog: 400 novos. [derivado: day_plan --handoff-block]
- **Infraestrutura:** s115 entregou o PRD `boot-cronograma-drive-confiavel` (3 partes, audits PASS): `--sync-drive` captura `ordem` do xlsx no snapshot; `day_plan` ordena "proximos temas" pela ordem real (fallback PDF) + banner `Drive desatualizado (Nd)`; `AGENTE §2.4`/`reconcile W8` tornam o sync ACAO OBRIGATORIA quando STALE (degradacao graciosa, nunca BLOCK); F30 (`material_indicado` rebaixado a extensivo sem `.md`) + F31 (WARN `[SEM-LASTRO]` no insert); contador de resumos DERIVADO no `--handoff-block`; linha "Indicador" do ESTADO enxugada (deixou de ser diario) + `estado-contract` reforcado. **Contratos versionados:** cronograma Clausula 5, reconcile W8, estado-contract. **Pitfall registrado:** rodar `pytest` completo, nao so `auto_check --changed` (o seletor de suite por arquivo-mudado nao mapeia todos os consumidores de um simbolo -- a part-1 quebrou `test_orquestrador.py` e so o pytest do audit pegou). Dois SSOTs do cronograma seguem valendo (ordem=xlsx Drive / detalhamento=`Cronograma.pdf`, `project_cronograma_dual_ssot`).

## Pendencias ativas
Aula-base de Pre-Natal I (debito antigo -- resumo pronto, falta so a escada de degraus). Apendicite Aguda -- verificar status do resumo (F16). Reescrever `TCE.md` + `Sistemas de Informacao em Saude.md`. Reforjar cards 95/120 (120 via gate de evidencia). Rotulo `sessao_num=115` em `sessoes_bulk` e de um bloco Endocrino da s114 (mislabel; agrega por area+data, nao afeta volume/perf -- so rastreabilidade) -- reconciliar quando conveniente; NB: a s115-engenharia nao tem volume, entao nao ha conflito com este `history/session_115.md`. Ledger `AUDITORIA_MEDHUB.md`: **F21 segue aberto**; **F30/F31 RESOLVIDO + F34 documentado** nesta sessao; proximos achados em **F35**. Candidato F35: mecanizar o reconcile de volume W1/F29 + fechar o blind spot do seletor de suite do `auto_check`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_115.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
