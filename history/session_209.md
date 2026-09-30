# Session 209 -- 2ª lente independente das provas UERJ: trilha recalibrada, anuladas oficiais, 4 resumos

**Data:** 2026-09-30 (quarta, 12h-14h) - **Ferramenta:** Claude Code (Fable 5.1) - **Continuidade:** `session_208.md`

---

## Pedido

O operador recebeu um material de terceiros sobre a banca UERJ (561 páginas: dossiê, as provas 2022-2026 comentadas e um livro de revisão) e pediu: analisar, comparar com os nossos dados e plano, apontar o gap e o que recalibrar. Depois do relatório: *"Pode aplicar os três com subagent Opus 5.5 lhe ajudando"* (plano, dados, resumos), *"pode utilizar a API que criamos do EMED, para cobrir o gap, também com subagent"* e, sobre o material: *"Eu e mais 3 amigos dividimos o preço desse dossiê e podemos utilizá-lo. Ainda assim, não suba isso para o git (apenas o conhecimento da análise das questões)"* -- os comentários das questões podem complementar a análise de erros dos simulados UERJ.

## O que foi feito

1. **Material lido e verificado por lentes independentes.**
   - Recontagem das 460 questões pelos rótulos: bate com as tabelas do material.
   - Gabarito letra a letra contra o nosso: 444 de 444.
   - Anuladas contra o gabarito pós-recurso do Cepuerj (fonte primária; subagente isolado + releitura minha do PDF por coordenada e cor): o material omite a Q43 de 2023.
   - Prevalência por grupo e formato por bloco concordam com o nosso mapa (`prevalencia_uerj.json`, campo `formato`).
   - Caixas de atualização de diretriz, amostra de 8 afirmações (`evidence-researcher`): 5 confirmadas, 2 não verificáveis, 1 com histórico errado (GINA).
2. **Gaps no nosso dado, medidos.**
   - Anuladas oficiais: 2022 Q50; 2023 Q43, Q72, Q73, Q84; 2024 Q46, Q84; 2026 sete questões. O nosso JSON dizia NAO VERIFICADO.
   - UERJ 2023 do operador = **60**, não 58 (Q43 e Q73 contavam como erro; edital 8.5).
   - F128 com 2ª lente: seis rótulos do nosso mapa puxaram tarefa para a fila (Tópicos em Pediatria, Princípios da Anestesiologia, Neoplasias de Estômago e Esôfago, Febre sem sinais localizatórios, Síndromes Genéticas, Psiquiatria Infantil).
3. **Trilha da Fase 1 recalibrada (OK dele).**
   - Saem para a Fase 2: 22 tarefas (2ª a 4ª lista do mesmo tema e os rótulos errados).
   - Entram 6 listas: #393, #380, #19, #58, #320, #557.
   - Entram 3 aulas: #5424 imagem obstétrica (S4), #5425 rodapés (S5), #5426 leitura final por banca (S7).
   - Reescopo: #889 (saúde mental do adolescente), #887 (sinais de alarme oncológicos), #882 (depressão e luto no idoso, abstinência alcoólica).
   - #530 (REMIT e cicatrização) abre a fila; #100 desce para a S6 (fica na Fase 1 porque a aula do hub está ligada a ela: `test_hub::test_repo_real_monta_sem_problema` acusou a aula órfã).
   - Gerador: propriedades OK (CM 20,2% · CIR 20,0% · GO 19,1% · PED 22,6%). Fase 1: 2831q pendentes -> 10.319 fechando o plano.
   - Reserva: faixa ALTA sem linha na fila caiu de 8 para 3 (só teorias de tema com revisão já feita).
4. **Dados corrigidos (OK dele).**
   - `simulados/uerj/gabaritos_2021-2026.json`: anuladas de 2022/2023/2024/2026 + fonte pós-recurso; golden de `test_prova_pdf.py` atualizado (59, 96, 98 e 93 questões).
   - `sessoes_bulk.id=130`: 58 -> 60, script pontual com backup (`ipub_backup_20260930_124812`) e COUNT-ASSERT de 1 linha; total de acertos 5902 -> 5904.
5. **Quatro resumos corrigidos (OK dele; subagente Opus, diff conferido por mim).**
   - CA de Mama: MS 50-74 bienal, 40-49 e acima de 74 por demanda (Nota Técnica 626/2025); lápide do 50-69.
   - Doença Ulcerosa Péptica: 1ª linha do V Consenso Brasileiro de H. pylori (2026), tríplice simples desencorajada, armadilha banca-dependente.
   - Insuficiência Cardíaca: armadilha banca-dependente da 2ª Definição Universal (06/2026); cortes mantidos.
   - Trauma: xABCDE (ATLS 11); choque em 3 categorias e hemotórax por hipotensão ficam como pendência de conferência.
6. **Hub (subagente Opus).** Sem recusa, sem 401/429, lista em curso (t1793) intocada.
   - Anuladas fora dos simulados no hub: t1794 60 -> 59, t892 100 -> 98, t890 100 -> 93 (as três sem resposta nenhuma). O banco local segue com 60/100/100 linhas: não há CLI para retirar linha de `emed_questoes` (um `--exportar` futuro traria as anuladas de volta).
   - Seis listas pela API do EMED, todas no hub (achadas / gravadas / discursivas): t393 52/50/2 · t380 55/49/6 · t19 42/42/0 · t58 43/41/2 · t320 42/39/3 · **t557 24/23/1 contra 43 previstas no plano** (o operador precisa conferir o caderno).
   - Hub republicado com o mesmo lote de cards (`2026-09-30a`, 0/150 notas): **Version 53** (plano e quadro de aulas mudaram).

## Artefatos criados/modificados

- Versionados: `core/cronograma/trilha/custom.json`, `core/cronograma/plano_custom.json`, `core/cronograma/plano_trilha.json` (gerado), `docs/RESERVA-FASE1.md` (gerado), `simulados/uerj/gabaritos_2021-2026.json`, `tools/test_prova_pdf.py`, os 4 resumos.
- Fora do git (`tmp/dossie_uerj/`): `ANALISE-2026-09-30.md` (cruzamento completo), `pacote_s209.json` (proposta com racional), `dryrun_trilha.py`, `aplicar_pacote.py`, `anuladas_uerj_verificacao.md`, `pages_clean.json` e `dossie_questoes.json` (texto e rótulos do material, sem a marca d'água; SPOILER).
- Banco: `plano_tarefas` (3 linhas novas, 34 atualizadas), `sessoes_bulk.id=130`.

## Decisões tomadas

- Peso de bloco não muda (regra da s189); a 2ª lente mexe em ordem e escopo DENTRO do bloco.
- Nada do material vai para o git nem para o hub (repo público); racional versionado cita "2ª lente independente das provas 2022-2026".
- 🔴 Spoiler: o operador não abre o material antes dos simulados de 2022, 2024, 2025 e 2026; o livro de revisão é a leitura da última semana (#5426), depois do simulado de 2026. O agente nunca cita ano + número de questão antes de cada prova feita.
- O gabarito comentado do material entra como 2ª lente da Autópsia de cada simulado UERJ, depois de ele resolver a prova.
- A contagem das listas trazidas pela API foi delegada por ele neste lote; os números ficam no HANDOFF para conferência.

## Custo (usage do harness)

- Anuladas (Sonnet): 207.039 tokens, 67 chamadas, 14,4 min.
- Amostra de evidência (Opus): 140.128 tokens, 25 chamadas, 10,3 min.
- Resumos (Opus): 171.357 tokens, 55 chamadas, 10,6 min.
- Hub (Opus): 292.730 tokens, 92 chamadas, 15,9 min.

## Candidatos ao ledger (não escritos; levar ao /ai-eng)

- `emed_banco` sem caminho para retirar questão anulada do banco; `--exportar` grava `q_previstas` como float.

- F128 agora tem 2ª lente: os seis rótulos acima, com consequência no plano.
- Gabarito preliminar tratado como oficial desde a s188 (anuladas NAO VERIFICADO por 12 dias).
- `sessoes_bulk` segue sem caminho de correção (2ª ocorrência do script pontual).

## Próximos passos

1. Card #1338 (CA de Mama) afirma a regra antiga (50-69): reforjar pela Nota Técnica 626/2025. Três cards de trauma inicial não conferidos.
2. Aulas a montar: #530 (REMIT, abre a fila), #5424, #5425 (incluir DRGE cirúrgica: fundoplicatura, hérnia de hiato, Los Angeles), e as três reescopadas. Lente de escopo: a seção da subárea em `tmp/dossie_uerj/pages_clean.json`.
3. Atualizações não auditadas (conferir quando o tema entrar na fila): TEP 2026, AVC 2026, SBD 2025, dislipidemia 2025, apendicite (Jerusalem 2025), bariátrica (CFM 2.429/2025), Caderneta da Gestante 2026, cálcio na gestação, SOP, ferro SBP 2026, ATLS 11 (choque e hemotórax).
4. A página da Autópsia da UERJ 2023 no hub ainda mostra 58 (histórico do dia).
5. Conferir com o operador a lista t557 (cirrose): a API achou 24 questões no caderno do link do plano, que previa 43.
