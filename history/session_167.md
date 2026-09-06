# Session 167 -- Drenagem de 90 cards (divida zerada, 90% retencao) + Simulado 7 (82%, 18 erros autopsiados)
**Data:** 2026-09-06 (17h45 -> 20h) -- estudo e registro no mesmo dia; o Simulado 7 foi feito pelo usuario a tarde, fora da sessao
**Ferramenta:** Claude Code (Fable 5.1) -- effort max; 1 fork (autopsia dos 18 erros)
**Continuidade:** Sessao 166 (Claude Code / Fable 5.1)

---

## O que aconteceu

### Estudo -- DRENAR, 10 blocos de 9 (decisao do usuario: "5 agora e 5 apos o simulado", depois "vamos ate o 10 direto")
1. **Boot** limpo. Fila: 55 atrasados (02-05/09) + 33 de hoje + 2 novos por prevalencia (Planejamento Familiar; Cirurgia Infantil segurada ate o tronco D10) = 90. 10 cards em relearning da s166 (#245, #740, #741, #577, #1381, #736, #313, #706, #709, #1270) drillados so pela frente, sem regravar.
2. **Pipeline de 2 blocos em voo**, feedback so de notas 1-2, notas 3/4 em tally. Sem PREPARAR (regime de divida).
3. **Blocos 1-6 (atrasados, 54 cards):** 37x4 / 12x3 / 1x2 / 4x1. Gaps: #120 heterotopica (Doppler negativo lido como exclusao), #419 LRA pre-renal (ancorou no captopril/nimesulida, ignorou Na 10/osm 720 -- bug 1b, familia do #1381), #19 crise asmatica (fez a media dos parametros; SpO2 88% = muito grave), #1424 (sem resposta, composta), #148 (RMM desacelera por melhora da vigilancia). Cluster Indicadores 5/6, atrasados desse cluster saltaram p/ 2027.
4. **Blocos 7-10 (hoje + novos, 36 cards):** 17x4 / 6x3 / 2x2 / 1x1 gravados + 10 no-record. Gaps: #735 dreno (perfuracao != risco localizado), #1073 transicao toracoabdominal (conservador -> VLP sempre), #703 pseudocisto ("cisto" nao discrimina). Redrill s166: 6 fecharam de primeira (#1381, #736, #313, #706, #577, #740); 4 reincidiram (#709 Hartmann no reto, 3a vez; #1270 colposcopia no braco endometrial do AGC, 3a vez; #741 lactobacillus na vaginose; #245 Kasai, 4a queda).
5. **Totais gravados: 80 cards, 54x4 / 18x3 / 3x2 / 5x1 = 90% retencao, 68% perfeito** (s164 54%, s166 77%). Divida de atrasados = 0. Carga 07-13/09 = 145 revisoes (~21/dia).
6. **Redrill (pela frente, sem gravar):** R1 (12 de nota 1-2 + reincidentes) 11/12; R2 (18 de nota 3) 4/18 -- "me lembre" em serie apos 102 cards = fadiga, nao recall. Parei o loop e entreguei a **Revisao Direcionada** (5 eixos + lista de cristalizacao); R3 pos-RD 14/17. Sobras: #1112 (EGB 35-37, oscilou 37/34/34-36), #567 (conduta do cefalohematoma nunca dita -- bug "para na 1a metade"), #513 (card p/ fork). `review_log` 116-125 (directed_review: Trauma Abd, Trauma Penetrante, Hanseniase, Rastreio Colo, Endometriose, Pre-Natal, Cuidados Neonatais, Exantematicas, Asma Ped, Ictericia Neonatal).
7. **Defeitos de card (12 em 90, 13%):** 5 compostas (#175, #1041, #1424, #572, #581), 2 binarias (#151, #837), #526 ctx=pergunta, #1112 ctx contradiz, #258 tema errado, #910 frente aberta, #527 truncado, #513 lista sem vinheta. Todos p/ reforja (ledger 4q).

### Simulado 7 (Estrategia MED, FINAL ENAMED, feito 06/09 a tarde)
8. **82/100.** Registrado ANTES da analise: `registrar_sessao_bulk --sessao 167 --area Simulado --feitas 100 --acertos 82`. Acumulado 6821.
9. **Extracao das 18 erradas** direto do PDF do gabarito (`simulados/Simulado 7.pdf`, 43 pags) pela cor dos spans (verde 0x1e9e6e = gabarito, vermelho 0x85342d = marcada) com PyMuPDF; enunciados+alternativas em `scratchpad/s7_qs.json`. O usuario colou os 18 comentarios.
10. **Autopsia por 1 fork** (memoria: lote <= ~15-18 = subagente unico) -> `core/simulados/_s7_erros_batch.json` (18 itens, 43 cards; 1 composta corrigida por mim antes do insert) -> `insert_questao.py --errors-file`: 18 inseridos, cards 1484-1526, 0 dedupe. Backup previo `ipub_backup_20260906_193256.db`. 4 temas novos: Cardiologia/Semiologia Cardiaca, Hepato/Nodulos Hepaticos Benignos, Obstetricia/Infeccao Urinaria na Gestacao, Dermato/Piodermites. Reincidencia F25: Q89 x erro 568 (Imunizacoes, fraqueza nº 2).
11. **Leitura de termometro:** execucao 8/18 (S6: 10/18) -- Q32 ATLS (A antes da TC, padrao documentado), Q25/Q61/Q73/Q81 ancoragem que ignora o dado que EXCLUI (45d assintomatica + amilase; jovem + B + LDH; 5 anos + crosta; testiculo 2 mL), Q24/Q26/Q58 ordem de conduta. Conhecimento 10/18 -- piso: Q63 (HBsAg reagente lido como resolvida), Q67 (gestante interna), Q59 (albumina PBE), Q50 (fluconazol x Aspergillus); Q18, Q44, Q60, Q77; diretriz 2026: Q79 (GINA ICS-formoterol resgate 6-11a), Q89 (PNI idoso pneumo 20V acamado, covid semestral). Corrigir so a execucao leva 82 -> ~90.
12. `habilidades.py --backfill`: +62 habilidades. Reincidente nº 1 do ledger agora e **"incorporar atualizacao recente de diretriz"** (7 temas distintos) -- confirma F69.

### Engenharia
13. Ledger 4q: evidencias F40/F41 (12 defeitos), F67 (#1095/#1446 clones em GO x Ginecologia), leech candidatos (#245, #1112, #567); **F76** novo (`--record --reason` aceita proveniencia divergente: #559 gravado como `agendado` sendo `vencido`).

## Padroes de erro (estudo + simulado)
- **Padrao-mestre (ancorar no saliente, ignorar o que exclui):** cards #120, #419, #19, #709; simulado Q25, Q61, Q73, Q81, Q32. Mesma familia em 9 instancias no dia.
- **Braco/mapa errado:** #1270 (colposcopia x USGTV nos 2 bracos do AGC, 3a vez), #741 (lactobacilo x anaerobio), #322/#1073 (trajeto define o metodo: dedo/VLP/TC tripla -- 3 respostas diferentes p/ 2 trajetos).
- **Rotulos trocados:** #201 (tipo 1 x tipo 2 hansenica: disse Th1, depois tipo 2), Q18 (fixo x paradoxal), Q63 (HBsAg).
- **Para na 1a metade:** #567 (3x), #422, Q24.
- **Dado numerico sem ancora:** #245 (Kasai, fechou na 5a com ancora de mecanismo), #1112 (EGB), #56 (ADA), Q44 (RMM), Q59 (albumina).

## Artefatos
- Banco (local): 80 revlogs + 18 `questoes_erros` + 43 cards + `review_log` 116-125 + `sessoes_bulk` s167 + 62 habilidades (backfill).
- `core/simulados/_s7_erros_batch.json` (novo, versionado como o da S6); `simulados/Simulado 7.pdf` (gitignored).
- `AUDITORIA_MEDHUB.md` (§4q), `HANDOFF.md`, `history/session_167.md`, `history/INDEX.md`.

## Decisoes
- Blocos de 9 (pedido do usuario) mantiveram o pipeline de 2; o formato "Card N -- #id . reason" sem area/tema antes do verso (contrato de apresentacao) foi aceito sem queixa.
- Redrill de notas 3 sob fadiga: parar e reabordar a fonte (Revisao Direcionada) > moer a sonda. R3 pos-RD subiu de 4/18 p/ 14/17.
- Composta flagrada pelo usuario com metade respondida: nota pelo alvo respondido (4) + reforja; composta sem resposta (#1424): 1 com override aberto.
- Proposta de scrum master ao usuario (nao decidida): 07-13/09 cards = revisoes (~21/dia) + 30-40 novos por prevalencia (~60/dia) e devolver as tardes as questoes (setembro = 90q em 6 dias; alvo 64-66/dia). O sprint 120 e decisao dele (s165); so mostrei o custo (450q).

## Proximos passos
Ver `HANDOFF.md`.
