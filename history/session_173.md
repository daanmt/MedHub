# Session 173 -- 109 cards drenados: a coorte do Simulado 8 estreia em 43% (2x a media), e o re-drill ganha a regra do corte do loop

**Data:** 2026-09-09 (manha -> inicio da tarde) · **Ferramenta:** Claude Code (Fable 5.1) · **Continuidade:** `session_172.md`
**Sessao de ESTUDO.** Engenharia segue congelada (decisao do operador, s172). Zero questoes de bloco nesta janela: o usuario saiu para as listas da S17 e volta com os erros numa janela seguinte.

---

## 1. DRENAR -- 109 cards, 10 blocos de 11

O usuario pediu a fila inteira de uma vez: **65 vencidos (13 atrasados + 52 de hoje) + os 44 do Simulado 8** (ids #1547-#1590, 36 no bucket `novos` e 8 em `erros_frescos`). Passou do teto do contrato (60/90) por decisao dele, explicitada na abertura. Ordem: vencidos primeiro (card vencido decai; card novo ainda nao tem memoria a perder), depois a coorte nova.

**Resultado:** 105 gravados · 2 aposentados a pedido dele (#365 DO-Parte II, #610 iNO/ECMO -- pergunta dupla) · 3 segurados sem nota para reforja (#367 sem contexto, #1568 e #1574 contexto desalinhado da pergunta, classe F81).

| Bucket | n | Retencao (nota 4) |
|---|---|---|
| Atrasados | 12 | 58% |
| Hoje | 51 | 63% |
| Simulado 8, novos | 34 | 44% |
| Simulado 8, erros frescos | 8 | 38% |
| **Simulado 8, coorte inteira** | **42** | **43%** |
| Sessao | 105 | 54% |

Distribuicao: **57x4 · 22x3 · 4x2 · 22x1**. Divida FSRS zerada (atrasados 0).

### 1.1 A medida que a s172 pediu -- o teste de regenerabilidade funcionou
A s169 mediu a estreia de cards novos em **22%** e a de erros frescos em **25%**. A coorte que o operador triou (85 -> 44, com 25 inversoes) estreou em **43%** (novos 44%, erros frescos 38%). **O corte de regenerabilidade dobrou a taxa de estreia.** Uma coorte so, mesma janela de tempo (drill ~10 h apos a analise, como na s169), entao e um dado, nao uma tendencia -- mas aponta na direcao que ele apostou: conteudo arbitrario rende, discriminador regeneravel nao.

A cauda tem nome: **Imunizacoes, 3 de 4 em nota 1 no mesmo dia da analise** (#1582 HPV "2 doses", #1583 ACWY "nao sei", #1584 triplice viral "3 doses"). E o erro 14 do Simulado 8 voltando inteiro. No re-drill, o #1584 travou de novo no "3" -- o numero da hepatite B vazando para a triplice viral. Mapa mental instavel entre protocolos, exatamente como a memoria de fraquezas descreve.

### 1.2 Padroes de erro observados (leitura do drill, nao de questoes)
- **Armadilha literal do card marcada em 6 cards:** antifungico para VB (#665), grau III com lesao vascular (#238), HPV 2 doses (#1582), ceftriaxona 1 g (#1586), esquisto "1 semana" (#1559), operar CCR sem estadiar (#538). O distrator que o card documenta e o que ele escolhe.
- **Fato no contexto errado:** "calculos biliares sao isodensos" dado como resposta ao card da TC na pancreatite (#313) e depois, corretamente, ao card da coledocolitiase (#1482). O fato existe; o gatilho de aplicacao nao.
- **Ancoragem no achado saliente:** DM1 no enunciado -> "glicose ou glucagon" em vez de via aerea no pos-ictal inconsciente (#789); "idoso grave em UTI sem calculo" -> fecha colecistite alitiasica sem contar Tokyo A+B (#1381, nota 3).
- **Inconsistencia intra-sessao:** ligou West + esclerose tuberosa no #1455 e desligou dois cards depois no #1457 ("neurofibromatose").

### 1.3 Defeitos de card reportados na hora (Invariante F, excecao unica)
#792 frente ambigua (marcado para reforja pela 3a vez: s158, s166, s173) · #583 e #582 compostas · #1381, #1080, #421 binarias · #367 sem contexto · #1568 e #1574 contexto de um caso com pergunta sobre o outro diagnostico · #610 dupla. Reforjados no fechamento via `recurate_cards.py` (dry-run + apply, gate 4/4): **#367 v3, #1568 v2, #1574 v2**. O ratchet de nao-crescimento do verso (s170) barrou a 1a versao do #1568 (1 -> 2 frases) -- funcionou como desenhado.

## 2. Re-drill -- 26 cards nota 1-2, e a regra nova

Duas passagens: 23 de 26 sairam em nota 4. Tres travaram: **#1562 e #1571 em "nao lembro" duas vezes, #1584 no mesmo numero errado.** O usuario: *"em temas que nao me lembro, preciso de um reonboarding curto, senao trava."*

**Regra gravada em `.claude/commands/revisar.md` §Relearning (espelho sincronizado):** card que trava 2x em "nao lembro" no re-drill **sai do loop** e vira entrada da Revisao Direcionada com reonboarding curto (mecanismo + reguas, 1 paragrafo); so depois volta a ser sondado. Repetir a sonda sem reabordar a fonte trava o aluno -- e o principio "o card e a sonda, o resumo e a fonte" aplicado dentro do loop. Memoria-ponteiro: `feedback_redrill_reonboarding_curto`. Apos o reonboarding, #1562 e #1584 sairam; #1571 deu o diagnostico em vez do achado (cicatriz central) -- fechado sem insistir, volta amanha pelo FSRS.

## 3. Revisao Direcionada de fechamento -- 6 eixos + gatilhos

Entregue no chat em prosa, 1 fato por vez: (1) a caderneta do adolescente aos 16 -- 3 blocos do PNI, HPV dose unica com resgate ate 19, ACWY 11-14 sem resgate, triplice viral 2 doses ate 29, a conta "total da faixa etaria atual menos o registrado"; (2) colangite em 4 perguntas -- SE (sempre), QUANDO (grau TG18), POR ONDE (CPRE > DTPH > Kehr), DEPOIS (colecistectomia na mesma internacao), mais os portoes A+B de Tokyo, USG viu/nao viu, e TC so apos 72 h na pancreatite; (3) as 4 reguas da ictericia neonatal + Kasai < 60 d + ABO mae O; (4) a linha denteada como divisor de tudo na doenca hemorroidaria (dor, procedimentos, janela 48-72 h, resolucao 7-10 d); (5) hidronefrose (USG -> UCM ou renograma diuretico), hipospadia 6-18 m, AAST renal IV por lesao vascular, Perthes como dor referida; (6) reonboarding de liquido amniotico (motores produz/nao absorve, DM 25%, reguas 8/25 e 2/5) e nodulo hepatico na jovem (hemangioma x HNF x adenoma, cicatriz central decide). Gatilhos de 1 linha para os 9 que ja tinham saido no re-drill.

**Invariante B:** `review_log` carimbado em **11 temas** (`directed_review`, ids 132-142). **F18c:** `set_dificuldade(fonte='aula')` em 5 temas (Imunizacoes 9, Ictericia 6, Hemorroidaria 7, Liquido Amniotico 8, Lesoes Hepaticas 8); Colecistite/Colangite (10) e Cirurgia Infantil (8) tem nota soberana do usuario e nao foram tocadas.

**Siamese Twins:** `Imunizações.md` §4.1 expandido (HPV/ACWY com janelas e resgate explicitados, a conta do resgate das 3 que olham para tras) + 2 armadilhas novas em §14 (triplice 2 x hepatite B 3; ACWY sem resgate x HPV ate 19). `auto_check --changed` PASSED.

🔴 **Seis temas do Simulado 8 nao tem resumo nenhum no repo:** Doenca Hemorroidaria, Lesoes Hepaticas Focais, Abdome Agudo Obstrutivo (`16. Abdome agudo obstrutivo.pdf` existe, sem `.md`), Farmacodermias (PDF existe), Esquistossomose, Liquido Amniotico. A Revisao Direcionada ensinou do conhecimento clinico, nao do resumo -- e o diagnostico "resumo omisso" do protocolo, so que sem arquivo para expandir. Backlog de `criar-resumo`.

## 4. Bastidores da sessao
- **RAG reindexado** (`index_resumos.py`: 134 resumos, 2.334 chunks): o Ollama voltou; as 15 correcoes da s172 sao buscaveis. Item 3 do HANDOFF fechado.
- **Simulado 8 registrado:** `registrar_sessao_bulk --sessao 171 --area Simulado --feitas 100 --acertos 78 --data 2026-09-08`. **A planilha nao tem o dado** -- as tabelas "Desempenho Simulado Final" do Dashboard estao zeradas, e o Simulado 7 tambem foi direto pelo CLI (s167). O "nunca digitando (F37)" do HANDOFF anterior era uma atribuicao errada: F37 e sobre `questoes_realizadas` inflado na taxonomia. Acumulado **6.936 -> 7.036**.
- **Etica 20/20 ja estava registrada** (s170); o usuario mencionou como "ontem" e conferi antes de gravar em dobro.
- Artifact "Triagem do Simulado 8" (s172) foi **apagado** pelo usuario -- o watch encerrou sozinho. Sem acao.

## 5. A semana ate o ENAMED -- decidida pelo usuario, com um alerta registrado
| Dia | Cards | Questoes |
|---|---|---|
| Qua 09 | 109 feitos | 101 (Diarreia R 41 + Pneumonias Bact. T I 16 + Uro T I 20 + Pneumonias na Infancia T 24) -- fecha a S17 verde |
| Qui 10 | ~100 | Simulado 9 (100) |
| Sex 11 | ~100 | ~100 (Uro T II 13 + SUA R 42 + ~45 do que o simulado expuser) |
| Sab 12 | ~100 | Simulado 10 de manha; tarde de descanso |
| Dom 13 | fila do dia | **ENAMED** |

Projecao ate domingo: **~7.540** (setembro sobe de ~34/dia para ~50/dia na media). O sprint "S20 completa ate 12/09" da s168 esta **morto**: do sprint, 115 questoes foram feitas (95 na s169 + Etica 20 na s170); o rescope honesto e S17 verde fechada hoje + 3 tarefas da S18 ate sexta.

**Alerta dado uma vez:** ~100 cards/dia por 3 dias = ~175 novos introduzidos, e novo volta em 1-2 dias -- fila de domingo tende a 80+, a de segunda a 100+, acima do teto 60/90 que ele proprio fixou em 30/08. Propus intake por prevalencia + fraqueza em vez de FIFO. **Ele discordou:** *"Teremos que refinar a triagem dos cards gerados e quando o momento chegar avaliamos novamente, comigo te ajudando a definir o que e um card bom ou nao."* Decisao registrada: o gargalo e a **qualidade na geracao**, nao o teto diario, e a regua de "card bom" sera co-definida com ele. Nenhuma politica de intake muda por conta do agente.

## 6. Artefatos
- `.claude/commands/revisar.md` + espelho `.agents/skills/source-command-revisar/SKILL.md` -- corte do loop de re-drill
- `resumos/Pediatria/Imunizações.md` -- §4.1 expandido + 2 armadilhas
- `history/generation_log.jsonl` -- 5 eventos de reforja (2 aposentar, 3 refazer)
- `ipub.db` (local): 105 revlogs, 11 carimbos de `review_log`, 5 notas `fonte='aula'`, 1 linha em `sessoes_bulk`
- memoria: `feedback_redrill_reonboarding_curto` (+ indice)

## 7. Proximo passo
1. Janela seguinte: receber os erros das listas de hoje -> registrar volume por area ANTES de analisar -> `/analisar-questao` em 1 subagent por lote -> cards sob o teste de regenerabilidade.
2. Amanha: fila FSRS (~64 vencidos + 3 reforjados + 8 relearning) + Simulado 9.
3. Backlog: 6 resumos inexistentes dos temas do S8; #792 reforja (3a marcacao); #582/#583 compostas.
