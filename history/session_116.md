# Session 116 -- HAS Pt.2 + Distúrbios do Potássio (42q cold): 12 erros -> 12 cards + 2 resumos gold + planejamento S13

**Data:** 2026-07-09
**Ferramenta:** Claude Code (Fable 5)
**Continuidade:** Sessão 115 (engenharia -- PRD boot-cronograma-drive-confiavel)

---

## O que foi feito

**Boot -- sync-drive obrigatório (a máquina da s115 em produção):** o `day_plan` abriu com `Drive desatualizado (1d)`, então o `--sync-drive` rodou como passo obrigatório (W8). Baixei o xlsx via MCP Drive, decodifiquei e rodei `cronograma.py --sync-drive` (352 tasks, 121 concluídas). O snapshot fresco **mudou a fila**: HAS Pt.2 (teoria) e Distúrbios do Potássio (teoria) apareceram **riscados no Drive** -- os dois pedidos #1/#2 do HANDOFF -- e o próximo pendente real da S12 virou Cefaleias; Epilepsias. O boot ofereceu o ato e o usuário confirmou: ele fez HAS (20q) e Potássio (22q) **cold, sem recall**, e forneceu os 12 erros.

**Volume (SSOT antes dos erros):** `registrar_sessao_bulk --sessao 116` -- Cardiologia 20/15 (75%) + Nefrologia 22/15 (68,2%) = **42q/30a**. Acumulado 4865 -> 4907.

**Os 12 erros -> 12 cards (776-787), batch único (`insert_questao --errors-file`, exit 0):**
- **HAS (H1-H5), Cardiologia:** H1 iniciou fármaco antes de fechar diagnóstico em baixo risco (PA = média das 2 últimas; dx exige 2ª consulta/MAPA); H2 escolheu BRA no lugar do IECA no diabético; H3 não priorizou cessação do tabagismo (maior impacto CV) frente a exercício; H4 enunciado negativo (BB não é 1ª linha, marcou BCC); H5 evidência de desfecho (IECA/DM2 sólido vs BRA/DRC-não-diabética fraco).
- **Potássio (K1-K7), Nefrologia:** K1 dose parenteral (1 mEq/kg, marcou 5); K2 enunciado negativo (gluconato de cálcio NÃO reduz K, marcou poliestireno); K3 leu só a acidose e foi em ATR quando hipoNa+hiperK+hipoglicemia no RN = insuf. adrenal (HAC); K4 superestimou ECG (K 6.8 = só T apiculada, não QRS alargado); K5 rabdomiólise -> padrão de hiperK, não QTc; K6 atribuiu hipoK+alcalose à diarreia (que dá acidose); K7 não investigou HAS secundária no jovem com hipoK (hiperaldo).

**2 resumos gold ancorados nos erros (Siamese Twins), auto_check PASS:**
- `Hipertensão Arterial Sistêmica (Parte 2) - Tratamento.md` (283 linhas, tema-zero) -- escopo inteiro do tratamento, 12 armadilhas; os 5 erros de HAS entram no bloco temático certo (limiar §1.1, MEV/tabagismo §2, 1ª linha/BB §3.1/§4.4, diabético §5.1, renoproteção §5.3).
- `Distúrbios do Potássio.md` (166 linhas, tema-zero) -- homeostase, hipo/hiper, ECG por nível, causas secundárias; 8 armadilhas; os 7 erros de Potássio ancorados. Desambiguou ATR tipo 4 (hiperK) x tipos 1/2 (hipoK).
- Autorados em paralelo por subagentes com o PDF extraído + `estilo-resumo.md` + as armadilhas diagnosticadas; auditoria final (auto_check --changed) BLOCK=0 WARN=0.

**Prep de amanhã -- Colecistite e Colangite Aguda:** autorado como resumo gold (tema-zero, fonte presente, 13 seções, 17 armadilhas) -- prep do bloco de amanhã, incluído no commit da s116. auto_check PASS nos 3 resumos. (O autor pegou o rótulo Kehr trocado no PDF -- Kehr é ombro esquerdo, não direito -- e não propagou.)

**Dificuldade calibrada (pós-análise, `agente_inferida`):** HAS **D6** (cold 75%, gap de execução + hierarquia IECA), Potássio **D7** (cold 68%, gaps em ECG-nível/ácido-base/causas secundárias). Calibra a descompressão da futura revisão.

**Relatório de planejamento até o ENAMED (a pedido):** contagem real por-task extraída do `Cronograma.pdf` (o `grade.json` só guarda total/semana e rateia igual -- fui ao `_parse_detail`, binding validado pelo `tema_detail`: HAS Pt.2=20q e Potássio=22q bateram com o que ele fez). Temas de amanhã (101q): Cefaleias;Epilepsias 30, DITC II 24, Imunizações III 29, Colecistite 18. **S13 completa = 387q em 12 tasks** (tabela entregue no chat) + proposta de divisão em ~4 dias. Gap: acumulado 4907; meta 10k pede ~77q/dia; fechar a grade (5826q restantes) pede ~88q/dia; ritmo real ~71-84/dia -> a meta é alcançável, a cauda da grade exige acelerar. Acertos 79,2% geral / **80,4% últimos 7 dias** (estável, levemente pra cima).

## Padrões de erro identificados

- 🔴 **Enunciado negativo -- REINCIDENTE (2x):** H4 (BB) e K2 (gluconato de cálcio). Padrão já catalogado (`feedback_enunciado_negativo`); candidato a mini-drill dedicado -- rotular cada opção V/F antes de marcar.
- 🔴 **Leitura parcial do painel (família bug nº1, 3x):** K3 (tríade eletrolítica ignorada, foi em ATR = oposto), K6 (ácido-base não casado com o mecanismo), K4 (ECG superestimado pro nível de K). Ler o conjunto, não o eixo isolado.
- 🔴 **IECA-primeiro-no-diabético (lacuna de conteúdo, 2x):** H2 e H5. IECA é obrigatório de 1ª linha no diabético; BRA só na intolerância. Agora coberto no resumo.
- 🔴 **Fechamento precoce / tratar antes de verificar (2x):** H1 (fármaco antes do dx) e K7 (não investigou secundária). Assinatura da família bug nº1.
- **Cluster ECG-hipercalemia (K4, K5):** nuance nível×achado; cards 784/785 atacam direto.

## Artefatos criados/modificados

- `resumos/Clínica Médica/Cardiologia/Hipertensão Arterial Sistêmica (Parte 2) - Tratamento.md` -- NOVO, gold, 283 linhas.
- `resumos/Clínica Médica/Nefrologia/Distúrbios do Potássio.md` -- NOVO, gold, 166 linhas.
- `resumos/Cirurgia/Abdome Agudo Inflamatório - Colecistite e Colangite Aguda.md` -- NOVO, gold, prep de amanhã (adendo).
- `ipub.db` -- +42q/30a (sessões_bulk s116 Cardiologia+Nefrologia); +12 erros -> 12 cards (776-787); dificuldade recalibrada em 2 temas (HAS D6, Potássio D7, agente_inferida); snapshot Drive fresco em `preparacao_estado`. Local-only.

## Decisões tomadas

- **Resumos de amanhã com resumo existente (DITC II, Imunizações III) ficam para estender no momento do estudo** -- com o escopo exato da parte III/II + os erros que surgirem -- em vez de inflar especulativamente agora.
- **Colecistite autorado adiantado** (tema-zero, fonte presente, sem erro para ancorar ainda) -- prep pura do PDF.
- Ano da diretriz de HAS deixado genérico ("a diretriz brasileira") -- o PDF-fonte cita 2020 e "SBC 2025" de forma inconsistente; confirmar com o usuário qual a banca fixa.

## Próximos passos

1. **Amanhã (batch do usuário, 101q):** Cefaleias; Epilepsias (30q) + DITC II (24q) + Imunizações III (29q) + Colecistite (18q).
2. 🔴 **Bloqueado -- preciso do PDF-fonte de Cefaleias; Epilepsias (adulto/Neuro):** não existe no repo (só "Cefaleias na infância", Pediatria). Sem ele o tema-zero de maior risco fica sem substrato.
3. **Estender no estudo:** `DITC.md` (parte II) e `Imunizações.md` (Teoria III).
4. **S13 (387q):** dividir em ~4 dias conforme a proposta (Dia 2: SUS+Endometriose+Pré-Natal+Pneumo 91q; Dia 3: Imunizações Rev+Sepse Rev 92q; Dia 4: DII+Humor+Hepato 100q; Dia 5: Rev.Questões 57q + simulado de domingo).
5. **Mini-drill de enunciado negativo** -- reincidente confirmado.
6. FSRS: 9 atrasados + 5 hoje, backlog 412 novos.
7. Reforjar `Sistemas de Informação em Saúde.md` + `TCE.md` (dívidas antigas).
