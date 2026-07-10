# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-09 -- **s116: HAS Pt.2 (20q/15a) + Distúrbios do Potássio (22q/15a) COLD -- 42q, 12 erros -> 12 cards (776-787). 3 resumos gold novos (HAS Pt.2 Tratamento, Distúrbios do Potássio, Colecistite e Colangite -- este prep de amanhã), auto_check PASS. Boot: sync-drive obrigatório rodou e provou valor (fila avançou: HAS/Potássio riscados no Drive). Relatório de planejamento S13 entregue. Dificuldade calibrada (HAS D6, Potássio D7).***

## > Proximo passo imediato
1. **Amanhã (batch do usuário, 101q):** Cefaleias; Epilepsias (30q) + DITC II (24q) + Imunizações III (29q) + Colecistite e Colangite (18q). Colecistite JÁ tem resumo (pronto nesta sessão).
2. 🔴 **BLOQUEADO -- preciso do PDF-fonte de Cefaleias; Epilepsias (adulto/Neuro):** não existe no repo (só "Cefaleias na infância", Pediatria). Sem ele, o tema-zero de maior risco de amanhã fica sem substrato. Pedir ao usuário.
3. **Estender no momento do estudo:** `DITC.md` (parte II) e `Imunizações.md` (Teoria III) -- resumos já existem; estender com o escopo exato + erros que surgirem, não inflar antes.
4. **S13 (387q, 12 tasks):** dividir em ~4 dias -- Dia2 SUS+Endometriose+Pré-Natal+Pneumo (91q); Dia3 Imunizações Rev+Sepse Rev (92q); Dia4 DII+Humor+Hepato (100q); Dia5 Rev.Questões (57q) + simulado de domingo.
5. **Mini-drill dedicado de enunciado negativo** -- reincidente confirmado nesta sessão (2x).
6. FSRS: 9 atrasados + 5 hoje (backlog 412 novos) -- `/revisar` ou `fsrs_queue.py`.

## Padroes de erro vivos -- atencao do scrum master
- RED **Enunciado negativo -- REINCIDENTE (2x nesta sessão):** H4 (betabloqueador não é 1ª linha, marcou BCC) e K2 (gluconato de cálcio NÃO reduz K, marcou poliestireno). Padrão já catalogado -> candidato a mini-drill. Ritual: rotular cada opção V/F antes de marcar.
- RED **Leitura parcial do painel (família bug nº1, 3x):** K3 (leu só a acidose, foi em ATR quando hipoNa+hiperK+hipoglicemia no RN = insuf. adrenal -- ATR daria o oposto), K6 (ácido-base não casado -- diarreia dá acidose, não alcalose), K4 (ECG superestimado -- K 6.8 = só T apiculada). Ler o conjunto, não o eixo.
- RED **IECA-primeiro-no-diabético (lacuna de conteúdo, 2x):** H2 (escolheu BRA) e H5 (IECA/DM2 é o desfecho sólido). Agora coberto no resumo novo.
- RED **Fechamento precoce / tratar antes de verificar (2x):** H1 (fármaco antes do dx em baixo risco) e K7 (não investigou HAS secundária no jovem com hipoK).
- Carregado da s114 (sem novo evento): criança DM1 doente = hipoglicemia não CAD (reincidência 2x, card 775); ancoragem no fármaco; fato certo/pergunta errada.

## Estado por frente
- **Volume & Metas:** 4907 / 10000 (perf. ~79.4%). Hoje: 142. Ritmo-alvo ~77.2q/dia (66d p/ ENAMED). Fechar a grade inteira pede ~88q/dia; ritmo real ~71-84/dia. [derivado: day_plan --handoff-block]
- **Conteudo:** 66 resumos em resumos/ (+3 nesta sessão: HAS Pt.2 Tratamento, Distúrbios do Potássio, Colecistite e Colangite). [derivado: glob] Gaps abertos: `Sistemas de Informacao em Saude.md` + `TCE.md` (reforja). DITC II / Imunizações III a estender no estudo.
- **Erros & Cards:** +12 nesta sessão (cards 776-787). Dificuldade recalibrada: HAS D6, Potássio D7 (agente_inferida).
- **FSRS:** 9 atrasados + 5 hoje. Backlog: 412 novos. [derivado: day_plan --handoff-block]
- **Infraestrutura:** boot rodou o `--sync-drive` obrigatório (W8) e a máquina da s115 provou valor -- o snapshot fresco reordenou os `próximos temas` e capturou que HAS Pt.2/Potássio já estavam riscados no Drive, avançando a fila para Cefaleias;Epilepsias. Nenhuma mudança de contrato/script nesta sessão (só conteúdo + operação normal).

## Pendencias ativas
🔴 PDF-fonte de Cefaleias; Epilepsias (adulto) -- pedir ao usuário. Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Estender `DITC.md`/`Imunizações.md` no estudo. Aula-base de Pré-Natal I (débito antigo -- resumo pronto, falta a escada de degraus). Reforjar cards 95/120 (120 via gate de evidência). Rótulo `sessao_num=115` (bloco Endocrino da s114, mislabel) segue pendente -- reconciliar quando conveniente. Ledger `AUDITORIA_MEDHUB.md`: **F21 aberto**; próximos achados em F35 (candidato: mecanizar reconcile de volume W1/F29 + fechar o blind spot do seletor de suite do auto_check). Ano da diretriz de HAS (2020 x SBC 2025) -- confirmar qual a banca fixa.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_116.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
