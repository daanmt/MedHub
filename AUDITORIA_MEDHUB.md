---
type: report
layer: root
status: working-draft
relates_to: [AGENTE, ESTADO, HANDOFF]
---

# AUDITORIA_MEDHUB -- o que esta EM ABERTO

> **Este arquivo so tem achado em aberto.** O que foi resolvido mora em
> `history/auditoria/resolvidos.md`, com o texto inteiro e as secoes narrativas de cada sessao.
> Decisao do operador em 28/09/2026 (s204): *"o que resolvermos, sai da frente"*.
>
> **Encoding:** ASCII limpo, Zero LaTeX, sem setas Unicode (AGENTE.md secao 4.5). Usar `->`, `<=`, `--`.

## Como usar

1. **Ver o estado:** `python tools/selo.py` -- aberto x resolvido, e quem decide cada item. **Achar um achado:** `python tools/selo.py --onde F38`.
2. **Antes de escrever achado novo:** buscar o mecanismo AQUI e no historico (`grep` pelos termos). Se ja existe, a entrada nova cita a antiga. Gate-miss da s204: o F140 re-derivou errado o que o F32 ja tinha certo.  <!-- NAO-VERIFICAVEL: nada le a intencao de escrever um achado; conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->
3. **Cabecalho do achado:** id, titulo, severidade e status, nesta ordem, separados por ` -- `. Severidade: ALTA (fere integridade de estado/SSOT), MEDIA (custo recorrente), BAIXA (polimento). Status que FICA na frente: ABERTO, GATE (pergunta ao operador), DECLARADO (remedio proposto ou nao-verificavel datado), PARCIAL, MITIGADO. Status que SAI: RESOLVIDO, SUPERADO, RETRATADO.
4. **No selo da sessao:** `python tools/selo.py --rotacionar` (dry-run) e depois `--apply --expect N`. O bloco viaja inteiro; nada e reescrito, resumido nem apagado.  <!-- CHECK: test_repo_real_consistente -->

## Indice

<!-- selo:indice:inicio -->
**Em aberto: 19** · Resolvidos: 105 (em `history/auditoria/resolvidos.md`) · indice gerado por `python tools/selo.py --rotacionar`, nunca editado a mao

| Id | Sev. | Status | Quem decide | Achado |
|---|---|---|---|---|
| F142 | MEDIA | DECLARADO | /ai-eng | nao existe trava de 2a GRAVACAO do mesmo card no mesmo dia entre lotes, e o teto do dia conta LINHA do revl... |
| F141 | MEDIA | DECLARADO | /ai-eng | card de intervalo de 1 dia servido na MANHA seguinte (menos de 24 h) cai no ramo de "mesmo dia" do py-fsrs:... |
| F129 | MEDIA | PARCIAL | engenharia | 1o drill completo no hub (220 cards, 23/09): o operador marcou 50 defeitos (23%); o residuo do F113 e a que... |
| F128 | BAIXA | DECLARADO | /ai-eng | o mapa das provas UERJ rotulou a Q8 de 2023 como "Tuberculose (suspeita de TB peritoneal)" e o gabarito e S... |
| F127 | BAIXA | DECLARADO | /ai-eng | `registrar_sessao_bulk` nao tem caminho de CORRECAO: o operador declarou duas respostas depois do registro... |
| F122 | BAIXA | DECLARADO | /ai-eng | o `grade_extensivo.json` nao tem 6 blocos de tarefa que o PDF tem (S48 T17-T22, 5 deles com lista), e o tes... |
| F114 | MEDIA | MITIGADO | engenharia | parametro do modelo que o otimizador NAO ajustou (por ausencia de exemplo) sai do JSON indistinguivel de pa... |
| F113 | MEDIA | PARCIAL | engenharia | cards cunhados SEM acentuacao (ASCII) sao lidos pelo usuario como "erro de portugues"; a convencao de encod... |
| F111 | MEDIA | GATE | operador | Fase 2 do plano (extensivo, leitura-first: 465 tarefas de teoria em 735; 39q/dia nativo) nao garante recall... |
| F87 | MEDIA | GATE | operador | O harness de flashcard verifica FORMA e e cego a RENDIMENTO: os 13 cards que o operador reprovou passam em... |
| F78 | MEDIA | DECLARADO | engenharia | Extracao de PDF descarta em silencio todo conteudo que vive em FIGURA, e nada no harness mede essa perda |
| F69 | MEDIA | GATE | operador | resumos com lacuna de diretriz nova = risco banca-dependente (s165) |
| F68 | MEDIA | GATE | operador | 15 temas de alta/media prevalencia ENAMED sem linha na taxonomia (s165) |
| F67 | MEDIA | GATE | operador | taxonomia duplicada divide o sinal do FSRS e da dormencia (s165, Claude Code/Fable 5.1, 2026-09-05) |
| F65 | MEDIA | GATE | operador | o balde `[bulk] <Area>` esconde 72 cards do radar de dormencia |
| F63 | MEDIA | PARCIAL | engenharia | a prioridade que governa o estudo nao viaja com o repo (o usuario e a camada de transporte) |
| F39 | ALTA | PARCIAL | operador | 40% do baralho viola o principio atomico; a nota FSRS vira ininterpretavel |
| F16 | MEDIA | PARCIAL | engenharia | Tema cirurgico de alto rendimento sem SSOT clinico (.md); so o PDF-fonte existe |
| F2 | MEDIA | DECLARADO | engenharia | Latencia de shell no ambiente Windows |
<!-- selo:indice:fim -->

## Achados em aberto

### F142 -- nao existe trava de 2a GRAVACAO do mesmo card no mesmo dia entre lotes, e o teto do dia conta LINHA do revlog, nao card: 83 re-revisoes no mesmo dia, todas descontadas do teto -- **MEDIA** -- **DECLARADO (s204) -- remedio proposto, aguarda triagem do /ai-eng**

- **Como apareceu:** auditoria do F140 (s204, 28/09/2026). Ao medir quantas revisoes do mesmo dia vinham do passo de relearning, sobraram 34 que NAO vinham dele.
- 🔬 **Medido (duas lentes, mesmos numeros: principal e filho Opus, revlog com fuso corrigido):** 83 pares (card, dia) com 2 revisoes gravadas, em 10 de 66 dias com revisao. **49** vieram de card em `state=3` servido pelo bucket `hoje` (o mecanismo do F140); **34** vieram de card em `state=2` com `due` no FUTURO (`reason_servido='futuro'`): 08/08 (19), 25/09 (14) e 05/07 (1). Pior dia: 08/08, 30 de 108 revisoes (27,8%).
- 🔬 **Causa medida dos 14 de 25/09:** lotes sobrepostos -- `player_2026-09-25a` (06:00, 60 cards) e `25b` (06:53, 90) tem cards em comum; o card revisto de manha foi revisto de novo as 19h pelo lote velho. As 19 de 08/08 NAO foram atribuidas a um caminho.
- 🔬 **No codigo (leitura do filho Sonnet, conferida a olho):** `core/templates/player.html` so impede a 2a nota DENTRO do mesmo lote (estado escopado por `LOTE.sessao`); `app/utils/notas_player.situacao()` so barra por ORDEM de tempo -- nota com horario posterior a ultima revisao sempre e `NOVA` e grava por `record_review`. O teto sai de `day_plan.realizado_do_dia` (`tools/day_plan.py:1352-1354`, `COUNT(*)` sem `DISTINCT`), lido em `tools/day_plan.py:895` e descontado em `tools/fsrs_queue.py:159`.
- 🔴 **Classe:** a regra "uma nota por card por sessao" (`revisar.md` §Relearning intra-sessao) e conduta dentro do lote; entre lotes do mesmo dia nao ha mecanismo. Trocar lote em curso (pedido legitimo do operador) e o gatilho.
- **Remedio proposto (`spec`, nada implementado):** (a) `--record-lote` manda para a quarentena a nota de card ja revisto no mesmo dia-calendario quando o card nao estava vencido; (b) o teto passa a contar `COUNT(DISTINCT card_id)`. Depende da decisao do F140: sob o remedio A deixa de existir 2a revisao legitima no mesmo dia, e a trava fica sem excecao.
- ⚠️ **Limites declarados:** revisar card antes do `due` e valido para o modelo; o defeito e a 2a nota no MESMO dia, nao a antecipacao. Nenhum teste foi escrito.

### F141 -- card de intervalo de 1 dia servido na MANHA seguinte (menos de 24 h) cai no ramo de "mesmo dia" do py-fsrs: a biblioteca mede por 24 h truncadas, a fila serve por dia-calendario -- **MEDIA** -- **DECLARADO (s204) -- remedio proposto, aguarda triagem do /ai-eng**

- **Como apareceu:** auditoria do F140 (s204). O card `638` foi visto pela 1a vez em 27/09 16:56 (nota 1), servido pelo bucket `hoje` em 28/09 14:24 (21,5 h depois, ANTES do `due` das 16:56) e a estabilidade caiu 0,212 -> 0,083 pela formula de curto prazo.
- 🔬 **Mecanismo (fonte do py-fsrs 6.3.1 instalado):** `days_since_last_review = (review_datetime - card.last_review).days`; `< 1` -> `_short_term_stability`, que ignora o tempo decorrido. O bucket `hoje` (`app/utils/db.py:1176-1178`) serve desde 00:00 tudo que vence ate 23:59. O otimizador do Anki usa dia-calendario com hora de virada (filho Opus de evidencia externa; a documentacao nao comenta a diferenca).
- 🔬 **Medido (duas lentes, mesmos numeros):** 295 revisoes no ramo curto (11,2% das 2.625 com historico); **212 em dia-calendario DIFERENTE** -- 144 de card `state=2` servido antes do `due`, 68 de card `state=3` servido como `atrasado` no dia seguinte. Por mes: jun 29, jul 8, ago 37, **set 138** (cresceu com a rotina de lote de manha). 512 de 2.629 revisoes (19,5%) foram servidas antes do `due`.
- 🔬 **Contrafactual SO DE MODELO (mesma nota aplicada no `due`, 144 casos):** nota 3 -> S 2,58 contra 0,80 gravado; nota 4 -> 4,12 contra 1,09; nota 2 -> 1,94 contra 0,38. Direcao do erro: estabilidade subestimada -> o card volta mais cedo -> consome teto. Conservador para a retencao, caro para a carga.
- 🔴 **Classe:** dois relogios para "um dia" -- o motor conta 24 h, a fila conta calendario. Mesma familia do F80 (dois relogios na mesma fila).
- **Remedio proposto (`spec`, nada implementado):** o adapter passa a contar o decorrido por dia-calendario local antes de chamar a biblioteca. Golden de partida ja existe: o replay do revlog reproduz S, D e state em 3.579 de 3.579.
- ⚠️ **Limites declarados:** o contrafactual nao mede o que o operador responderia no `due`. Nenhum dos remedios A/B/C do F140 mexe neste achado. O py-fsrs 6.3.2 existe (`pip index versions fsrs`) e corrigiria a queda com nota 2 no mesmo dia -- UMA fonte so, changelog nao conferido por 2a lente.

### F129 -- 1o drill completo no hub (220 cards, 23/09): o operador marcou 50 defeitos (23%); o residuo do F113 e a queixa dominante e a Autopsia UERJ 2023 cunhou armadilha de QUESTAO em card -- **MEDIA** -- **PARCIAL (s194: armadilhas da Autopsia refeitas; acento segue aberto; s195: +18 defeitos no lote de 24/09 e o veredito dele sobre COMPRIMENTO -- cards, aulas e reports "muito longos, carga cognitiva")**
- **Como apareceu:** lote `2026-09-22h` drenado inteiro no hub (170 notas gravadas pelo `--record-lote`, 0 rejeitadas, 0 FORA DE ORDEM). Motivos dos 50 `defeito`: portugues ~33, pergunta composta/dupla ~13, longo ~6, circular 3, verso incompleto 1 (#736 nao cita a classe do ATB), armadilha citando alternativa inexistente 1 (#1723, *"notei outros assim tbm"*). Todos viraram `marcar_reforja` origem `player`.
- 🔬 **Acento (reincidencia do F113):** os 35 marcados por portugues estao sem acento -- "nao e", "e" no lugar de "é", "arteria", "osseo", "deletereo". Uma lente por palavra que SEMPRE leva acento (`ja sao ha ate unica pos pre sistemico classico especifico` ...) acusa **749/1.600 cards** com >= 1 ocorrencia (ruidosa: `esta`/`so` tem uso legitimo; e piso, nao medida). A s185 ja tinha dito: o residuo nao fecha por regra; pede lexico ou olho. Remedio candidato (`spec`, para o /ai-eng): passada por LLM campo a campo, com o invariante `unidecode(antes) == unidecode(depois)` do s185 + revisao a olho dos pares minimos (`e/é`, `esta/está`, `diferencia`), sob o rito 10.7.
- ✅ **Armadilha de questao em card -- fechado no ato:** os 8 cards da Autopsia UERJ 2023 (#1721-1728, cunhados por mim na s190/s191) tinham como armadilha a pegadinha da QUESTAO ("A D oferece...", "O enunciado entrega..."), duas delas copiadas em pares (1724=1725, 1726=1727) e a do #1721 sobre outra alternativa. Refeitos via `recurate_cards.py` (8 itens, v1->v2, FSRS preservado): armadilha = o erro tentador da pergunta do card. Varredura por letra de alternativa no baralho inteiro: fora desse lote, so falso positivo (#334 "o C" do ABC, #687 hemoglobina A, #881 hepatite B...). 🔴 **Classe:** a armadilha tem dono -- a pergunta do card --, e cunhar card a partir de questao sem trocar de dono carrega o gabarito para dentro do verso. Candidato a clausula em `estilo-flashcard.md`.
- **Pendente:** comprimento e pergunta composta ja tem gate (F115, atomicidade); os ~19 marcados dessa classe estao na fila de reforja com o motivo dele.

### F128 -- o mapa das provas UERJ rotulou a Q8 de 2023 como "Tuberculose (suspeita de TB peritoneal)" e o gabarito e SINDROME NEFROTICA; e o insumo que eu montei para a Autopsia sequestrou a Q8 pelo item "8)" da folha de instrucoes da capa -- **BAIXA** -- **DECLARADO (s190) -- remedio proposto, aguarda triagem do /ai-eng**

- **Como apareceu:** Autopsia do simulado UERJ 2023 (s190, 20-21/09/2026). (a) `simulados/uerj/uerj_mapa_questoes_2021-2026.json`, edicao 2023, n=8: `area=Infecto`, `tema=Tuberculose`, `foco="investigacao de ascite com SAAG baixo (suspeita de TB peritoneal)"`, `confianca=media` -- o gabarito oficial e C (proteinuria + biopsia renal): anasarca, albumina 2,0, GASA 0,7 com proteina do liquido 2,3 e 120 celulas = nefrotica. O rotulo do filho (Sonnet, s188) seguiu o distrator. Consequencia medida: a `prevalencia_uerj.json` conta 13 questoes de TB com esta dentro, e a minha primeira tabela de contingencia mandou a Q8 para a aula de TB. (b) O meu extrator de enunciados (`re.split` por `\n8)`) pegou o item 8 das instrucoes da capa; quem achou foi o subagente do bloco, nao eu.
- 🔴 **Classe:** (a) rotulo de filho consumido como dado sem lente independente por questao -- o `_schema` ja declara ~80-90% de acuracia "consumir em faixas", e este e um caso concreto dentro da margem; (b) insumo de fan-out sem validacao de forma antes do spawn.
- **Remedio proposto:** `so-dado` para (a) -- corrigir a linha n=8/2023 do mapa (Nefrologia | Doencas Glomerulares, foco sindrome nefrotica) e regerar a prevalencia JUNTO da 1a recalibracao legitima (mesma janela das faixas, decisao do `/ai-eng` na s189; mexer no mapa agora muda a entrada fixada do gerador). A cada prova UERJ resolvida, a Autopsia confere os rotulos do mapa DAQUELA edicao contra o gabarito (lente independente que passa a existir de graca). (b) virou licao de brief na memoria do harness (validar "tem a) b) c) d)" por item antes de spawnar).

### F127 -- `registrar_sessao_bulk` nao tem caminho de CORRECAO: o operador declarou duas respostas depois do registro (56 -> 58 acertos) e a unica saida foi um script pontual com UPDATE direto -- **BAIXA** -- **DECLARADO (s190) -- remedio proposto, aguarda triagem do /ai-eng**

- **Como apareceu:** s190, simulado UERJ 2023. O rito manda registrar o volume ANTES de analisar; o PDF anotado tinha duas questoes sem letra marcada (Q32, Q56) e o operador as declarou minutos depois (ambas C, ambas chute certo). `--acumular --feitas 0 --acertos 2` cai no guard `acertos > feitas`; nao existe `--corrigir`. Corrigido por `scratchpad/corrige_bulk130.py`: backup (`ipub_backup_20260921_000800.db`), dry-run, assert da linha esperada, COUNT-ASSERT 1+1 (`sessoes_bulk.id=130` e o balde `[bulk] Simulado` da taxonomia, espelhando o delta que o writer aplicaria), observacao da linha carimbada com a correcao.
- 🔴 **Classe:** o AGENTE.md §10.7 manda passar pelos writers e o writer nao cobre o caso -- a regra empurra para fora dela. Registrar-antes-de-analisar (rito certo) torna a correcao posterior um caso NORMAL, nao excepcional.
- **Remedio proposto:** `spec` pequena -- `registrar_sessao_bulk.py --corrigir ID --acertos N [--feitas M]` (dry-run por default; grava o delta na linha E no balde da taxonomia; anexa `corrigido de X para Y` na observacao; recusa se a linha nao existir). Ate la, o script pontual com backup + COUNT-ASSERT e o precedente.

### F122 -- o `grade_extensivo.json` nao tem 6 blocos de tarefa que o PDF tem (S48 T17-T22, 5 deles com lista), e o teste trava o numero errado como se fosse medido -- **BAIXA** -- **DECLARADO (s188) -- remedio proposto, aguarda triagem do /ai-eng**

- **Como apareceu:** efeito colateral do extrator de links (F119). Lendo a geometria da tabela do `[52 wk] Cronograma Extensivo.pdf` ele achou 741 blocos de tarefa; o JSON derivado tem 735. Os 6 que sobram sao S48 T17-T22. Comando: `python -X utf8 extrair_links.py` (scratch da s188), secao "blocos do PDF sem tarefa no JSON".
- 🔴 **Por que nenhum gate viu:** `test_fontes_reais_reproduzem_os_numeros_medidos` e `--expect-tasks` (default 735) PRENDEM o 735. O numero foi medido pelo MESMO parser que ele valida -- sensor e remedio do mesmo insumo (`feedback_metrica_auto_confirmante`). A lente independente so apareceu quando outro metodo (geometria + anotacao) leu o mesmo PDF.
- **Remedio proposto:** `spec` pequena no parser do extensivo + atualizar o `--expect-tasks`. Sem urgencia: S48 e o fim da Fase 2. **Nao re-medido pelo principal** -- o numero e do filho, com o comando acima.

### F114 -- parametro do modelo que o otimizador NAO ajustou (por ausencia de exemplo) sai do JSON indistinguivel de parametro ajustado: `w3` e `w16` da visao `remap` sao o default do py-fsrs, e a regua nova VAI emitir o rotulo que eles governam -- **MEDIA** -- **MITIGADO (s186: gate de `regua_do_fit` no carregador); a causa de fundo fica DECLARADA**

- **Como apareceu:** medindo, para o R2, quanto a adocao dos parametros do R1 mudaria o agendamento real. O numero de nota 4 nao fechava com a intuicao (o "sem esforco" agendando IGUAL ao "lembrou"), e o diff indice a indice explicou:

```
python -X utf8 -c "<diff: Scheduler().parameters x core/fsrs_params.json::visoes.remap.parametros>"
  w3   8.295600 == 8.295600   <-- INTOCADO
  w16  1.872900 == 1.872900   <-- INTOCADO
  (os outros 19 se moveram; na visao `cru` os dois TAMBEM se movem: w3=8.433273, w16=1.958405)
```

- 🔬 **Causa medida:** `w3` (stability inicial de Easy) e `w16` (bonus de Easy) sao os dois parametros que governam a nota 4. O mapa do R1 manda `4 -> 3`, entao `visoes.remap.distribuicao_notas_efetivas` e `{"1": 918, "2": 536, "3": 1613}` -- **nao existe chave "4"**. Sem um unico exemplo de Easy o otimizador nao tem gradiente nesses eixos: eles nao convergiram, **nunca foram tocados**. Na visao `cru`, onde ha 1.613 notas 4, os dois se movem -- o que confirma que a causa e ausencia de dado, nao estabilidade do ajuste.
- 🔴 **Classe (serie §10.8):** *parametro sem dado que o identifique e default com carimbo de medido*. O JSON versionado apresenta os 21 numeros em pe de igualdade; dois deles sao herdados por omissao e nada no arquivo dizia isso. E a mesma familia da **metrica auto-confirmante** do F113 (o medidor que so procurava o que o corretor sabia consertar) e do `cli_signature_check` (presenca != cobertura): *a saida parece medicao porque veio do instrumento de medicao.*
- ⚠️ **Por que isso e ALTO-RISCO exatamente agora:** a regua v2 reabilita a nota 4 com sentido proprio ("sem esforco"). Adotar `remap` seria pedir ao modelo que agende um rotulo que o fit dele nunca viu. Medido no baralho real (830 cards em Review, replay sob os dois conjuntos): nota 2 cairia de mediana **24d -> 8d** (o ganho do F112) mas nota 4 cairia de **70d -> 50d**, colapsando no 3 -- o "sem esforco" deixaria de valer mais que o "lembrou".
- 🔧 **Mitigacao (s186):** `app/utils/regua.carregar_parametros` so entrega um conjunto quando o arquivo declara `adotado: true` **e** `regua_do_fit` igual a regua de escrita; ausencia de `regua_do_fit` **nao vira permissao** (recusa). `analisar_visao` passou a gravar `regua_do_fit` + `reguas_no_corpus` em toda visao. 4 testes, um por ramo de recusa (`tools/test_regua_fsrs.py`).
- ⚠️ **FRONTEIRA DECLARADA, nao resolvida:** o gate barra *adotar sob a regua errada*. Ele **nao** detecta "parametro que o fit nao identificou" no caso geral -- para isso seria preciso medir a cobertura de cada eixo no corpus, e isso nao existe hoje. Quando houver historico sob a regua v2 com nota 4 real, re-rodar o R1 e conferir se `w3`/`w16` saem do default e a verificacao que fecha o eixo. Ate la, a nao-adocao e a unica garantia.

### F113 -- cards cunhados SEM acentuacao (ASCII) sao lidos pelo usuario como "erro de portugues"; a convencao de encoding (AGENTE §4.5) foi aplicada ao TEXTO CLINICO do card, nao so a pontuacao -- **MEDIA** -- **PARCIAL (s185: 1.796 correcoes em 4 lotes + 1 corrupcao revertida; residuo IRREGULAR declarado)**
- **Como apareceu:** no lote de 90 do player (s184), o usuario marcou defeito em #685 (*"pergunta composta e erros de portugues"*) e #689 (*"outro exemplo de card com erro de portugues. aplicar o feedback a todos os cards da sessao"*). Os dois cards estao escritos sem acentos/cedilha ("Crianca falcemica", "compativel", "Sindrome do Olho Vermelho" no tema) -- o que a regra §4.5 (Zero LaTeX, sem setas Unicode, sem travessao) nunca pediu: ela proibe pontuacao especial, nao a ortografia.
- 🔬 **Medido (lote de 90):** cards de safras recentes (ids >= ~1500, cunhados por subagente/lotes ASCII) vs. safras antigas com acentos; a proporcao exata no baralho **nao foi medida** (sessao de estudo, permit consumido) -- item da spec: `grep` de vogais acentuadas ausentes por card e uma regua de "ASCII puro em texto clinico".
- 🔴 **Classe:** regra certa aplicada ao alvo errado (o F90 do encoding): o gate `card_checks` verifica forma e nao ve ortografia; `recurate_cards.py` e o writer certo para a reforja em lote (preserva FSRS; ratchet do verso vale).
- **Remedio proposto:** `spec` -- (1) medir a proporcao de cards sem acentuacao; (2) reforja em lote via `recurate_cards.py` com dry-run + COUNT-ASSERT (texto identico exceto acentos -> ratchet do verso nao dispara); (3) instrucao explicita em `estilo-flashcard.md`: portugues acentuado no texto clinico; ASCII so na pontuacao. Marcas de reforja de hoje: #419, #685, #688, #689, #373 (origem `player`).
- 🔬 **MEDIDO (s185, 17/09/2026) -- a premissa "safras recentes" subestimava muito:** **875 de 1.476 cards ativos (59,3%)** tinham acentuacao removida. Por faixa de id: 0-500 = 42,0% · 500-1000 = 55,3% · 1000-1500 = 62,2% · **1500+ = 94,2%**. Top palavras: `nao` 635x, `diagnostico` 122x, `apos` 115x, `doenca` 84x, `crianca` 81x. Regua de deteccao: palavra que OBRIGATORIAMENTE leva acento aparecendo sem ele -- nao "card sem acento nenhum", que teria falso positivo em frase curta legitima.
- ✅ **APLICADO (s185)** -- lote de **749** cards via `recurate_cards.py --apply`, sob o rito do 10.7: dry-run -> `backup_db.py` (`ipub_backup_20260917_224901.db`) -> apply -> COUNT-ASSERT. FSRS preservado (flashcards 1543 / fsrs_revlog 3067 / fsrs_cards 1543 identicos antes e depois). **Invariante provado item a item antes de gerar o lote:** `unidecode(antes) == unidecode(depois)` em todos os 2.277 campos tocados -- a edicao e SO-ACENTO, e o gerador aborta sem escrever se um unico item violar.
- 📐 **COUNT-ASSERT reconciliado:** restaram **141**, nao 126. Diferenca explicada e fechada: **125** sao o lote B (travado pelo gate de atomicidade) + **16** disparam so por `media`/`medio`, as duas palavras que o gerador EXCLUI de proposito (ambiguas: "media" tambem e o imperfeito de *medir*, e restaurar acento ali reescreveria sentido clinico).
- ✅ **ACHADO NOVO FECHADO -- gate sem ESCOPO DE INTENCAO.** `recurate_cards.py:297` (`bloqueia_atom = bool(avisos) and not permitir_atomicidade`) reprovou **125 cards** com "reforja(s) NAO resolveram o defeito", porque roda o detector de atomicidade sobre o conteudo PROPOSTO. A edicao so-acento **nao se propunha** a resolver atomicidade, e provadamente nao a altera. Splitar foi o certo, nao contorno: esses 125 ja estao na fila de reforja e serao reescritos de verdade, quando o acento sai de graca. Mas o gate nao distingue "edicao que falhou em consertar" de "edicao que nunca mirou aquilo" -- classe: gate sem escopo de intencao.
- 🔧 **Remedio (s185):** `recurate_cards.validar` calcula `_so_acentuacao(campos, atual_do_banco)` por ITEM e, quando o invariante vale, **pula os gates 4 e 6** -- os dois que perguntam *"a reforja resolveu?"*. Os demais (schema, encoding, formulacao, resposta-embutida, ratchet do verso) seguem valendo: nenhum deles pergunta sobre intencao, todos medem o texto proposto. 🔴 A isencao e **verificada por item, nunca declarada por flag** -- flag se usa errado, invariante se prova; campo que nasce (banco NULL) derruba a isencao do item inteiro. Suite `tools/test_recurate_escopo.py` (6 testes, escritos antes do fix): o so-acento passa E entra no plano, a edicao semantica no mesmo card segue cobrada, acento+1 palavra perde a isencao, e a isencao vale por item num lote misto. Entra na serie **§10.8** como *gate sem escopo de intencao*, irma do `cli_signature_check` (presenca != cobertura).
- ⚠️ **RESIDUO DECLARADO (por isso PARCIAL, nao RESOLVIDO):** (a) os 125 do lote B; (b) 16 por ambiguidade deliberada; (c) **a lista de palavras e curada e conservadora** -- cobre as de alta frequencia, nao garante ortografia completa. Exemplo vivo: **#689** ganhou `diagnóstico` mas segue com "Uveite" (deveria ser "Uveíte"), e **#685** -- um dos dois que o operador marcou -- esta no lote B intocado, porque a outra metade da queixa dele naquele card era "pergunta composta". Afirmar "F113 resolvido" seria claim falso.
- 🔴 **O "0% restante" que reportei apos o 1o lote era FALSO, e o defeito era de metodo.** Medidor e corretor compartilhavam a mesma lista de ~110 palavras: o medidor so procurava o que o corretor sabia consertar, e por isso reportou verde. **Metrica auto-confirmante** -- a mesma familia do `cli_signature_check` inflando cobertura por presenca de string, e do proprio F106 lendo `grep -l` como cobertura. Um detector independente, **por sufixo**, mediu **897 cards (60,8%)** ainda sem acento: praticamente o numero original. Licao: quando o sensor e o remedio nascem do mesmo insumo, o verde nao e evidencia.
- ✅ **Lote B, 125 cards (s185)** -- os travados pelo gate. Liberados depois que o gate ganhou **escopo de intencao** (abaixo), sob o mesmo rito 10.7.
- ✅ **Lote C, 22 cards (s185)** -- os ambiguos `media`/`medio`. Li os 22 um a um: **nenhum era o verbo**; sao `arteria meningea media`, `otite media`, `camada media`, `linha media`, `PA media`, `terco medio`, `vida media`, `em media`. A ambiguidade era teorica; medida neste corpus, zero. Triagem caso a caso, nao heuristica.
- ✅ **Lote D, 877 cards (s185)** -- acentuacao por **REGRA DE SUFIXO**, nao por lista: `-cao/-coes`, `-sao/-soes`, `-avel/-ivel`, `-encia/-ancia`, `-logico/-logica`, `-orio`. Deliberadamente FORA por terem excecao real: `-oria` (categoria/teoria/maioria nao levam acento), `-cia`, `-logia` (cardiologia), `-ico`.
- 🔴 **EU INTRODUZI UMA CORRUPCAO E ELA FOI REVERTIDA (lote E, 23 cards).** A regra de sufixo `-encia` transformou **verbo em substantivo**: a pergunta *"Como se diferencia, na pratica, pancreas anular de atresia duodenal?"* (verbo, sem acento) virou *"Como se difer**e**ncia"* com E-CIRCUNFLEXO, palavra que nem existe. **Isso derruba uma premissa que eu havia afirmado nesta mesma sessao:** o invariante `unidecode(antes) == unidecode(depois)` prova **mesmas letras, NAO mesmo sentido**. Portugues tem pares minimos distinguidos por acento (`diferencia`/`diferencia`, `evidencia`/`evidencia`, `influencia`, `potencia`, `distancia`, `substancia`) -- sufixo NOMINAL (`-cao`, `-sao`, `-avel`, `-orio`) e seguro; `-encia`/`-ancia` nao sao, porque coincidem com 3a pessoa de verbos em `-enciar`/`-anciar`. Quem pegou foi **leitura a olho de amostra aleatoria**, nao gate nenhum: o card #285 apareceu com "Como se diferencia" numa amostra de 4. Regra derivada: **"so-acento" nao e sinonimo de "semanticamente nulo" em portugues**, e nenhum invariante mecanico que eu tinha teria pego isso.
- 📐 **Como foi revertido:** `diferencia` (com circunflexo) **nao existe** em portugues -- o substantivo e `diferenca` -- logo toda ocorrencia era corrupcao, e isso deu um criterio limpo. Os demais lemas ambiguos (`distancia`, `substancia`, `potencia`, `evidencia`) foram lidos um a um nos 62 contextos: **todos substantivos corretos**. Estado final: 0 corrompidos, 72 verbos `diferencia` intactos.
- ⚠️ **RESIDUO, e por isso segue PARCIAL:** o que sobra e **irregular e nao fecha por regra**. Uma terceira lente (`-aria/-ario/-eria/-ite/-icia`) acusa 514 cards, mas e imprestavel como medida: `apendicite`, `artrite`, `ascite`, `abortaria`, `causaria` estao **corretas** sem acento, enquanto `arteria`, `bacteria`, `calendario`, `etaria` precisam -- e nenhum sufixo distingue. Exemplos vivos: **#685** (`series`, `leucocitaria`, `plaquetaria`, `Leucocitos`, `obrigatoria`) e **#689** (`Uveite`). Fechar isso exige **lexico ou olho humano**, nao a proxima regra; gerar mais um lote por padrao seria repetir o erro do lote D com outro sufixo.
- 📜 **CAUSA-RAIZ FECHADA:** a frase "usar exclusivamente ASCII/Markdown limpo" (`estilo-flashcard.md:132` e `AGENTE.md §4.5`) era lida por quem cunha card como "tire os acentos". Os dois portadores ganharam clausula explicita: a regra governa **pontuacao e notacao, jamais ortografia**.

---

### F111 -- Fase 2 do plano (extensivo, leitura-first: 465 tarefas de teoria em 735; 39q/dia nativo) nao garante recall no dia da primeira exposicao: tarefa T sem bloco de questoes gera ZERO sonda -- **MEDIA** -- **ABERTO (decisao do operador; prazo 02/11/2026)**
- **Como apareceu:** o video 1 resolve a primeira exposicao com "3 exposicoes em 24h" (video -> cards do tema na mesma noite -> revisao na manha). No MedHub o card nasce de ERRO (`insert_questao`) ou de andaime (`insert_card_base`); o R1 mini-drill (`orquestracao-contract`) so ve erros frescos de 48h. Na Fase 1 (question-first) isso nao aparece; na Fase 2 aparece por construcao.
- **Evidencia a favor de agir:** Rawson 2013 (relearning ate criterio: >60% x <20% em 24 dias); Murre & Dros (primeiro intervalo apos uma noite). **Evidencia que limita o remedio:** Deng 2015 (deck pronto nao prediz; cards proprios predizem) e Step 2 CK sem beneficio de Anki -- intake **filtrado e pequeno**, nunca bulk.
- 📬 **DECISION BRIEF (R8, entregue na s187; devido ao operador ate 02/11) -- 10 linhas:**
  1. **O problema so existe na Fase 2.** Na Fase 1 (question-first) todo tema chega com bloco de questoes, e o erro gera card. No extensivo, **465 das 735 tarefas sao teoria pura**: o tema e lido e nao deixa sonda nenhuma.
  2. **O que muda no seu dia:** ao rodar `plano.py --concluir` numa tarefa de TEORIA, eu te mostro 5-8 cards candidatos do corpus EMED daquele tema; voce aprova ou corta um a um (30-60 s); os aprovados entram hoje, dentro do teto de 60.
  3. **O que NAO muda:** teto diario, regua de nota, fila FSRS, e o fato de que card de ERRO continua nascendo do erro. Isto so cobre a tarefa que hoje nao gera sonda alguma.
  4. **Custo:** ~1 minuto por tarefa de teoria concluida.
  5. **Evidencia a favor:** Rawson 2013 (relearning ate criterio: 60% x 20% de retencao em 24 dias) e a queda do primeiro intervalo apos uma noite (Murre & Dros).
  6. **Evidencia que LIMITA:** Deng 2015 -- deck pronto **nao** prediz desempenho, card proprio prediz; e Step 2 CK sem beneficio de Anki. Por isso o intake e **filtrado e pequeno**, com triagem sua, nunca bulk.
  7. 🔴 **O risco real nao e tecnico, e de volume:** 465 tarefas x 5 cards = 2.300 cards se a triagem afrouxar. A divida atual ja e 103 vencidos. **A triagem humana e o unico freio**, e ela e sua.
  8. **Reversivel:** sim, e barato. O intake e opt-in por tarefa; cards entrados ficam marcados pela origem e saem por `cards_prune.py` com criterio nomeado. Nada toca revlog nem cards existentes.
  9. **Nao-reversivel:** nada.
  10. ⏰ **Quando decidir: na proxima sessao**, junto com a adocao do cronograma extensivo -- e exatamente ai que o defeito passa a morder. Decidir antes seria decidir no escuro; depois, seria tarde.

- **Remedio proposto (spec, apos GO do operador):** intake por tarefa concluida -- `plano.py --concluir` -> `emed_flashcards.py --query` do tema -> triagem pelo teste de regenerabilidade (humana) -> `insert_card_base` dos sobreviventes no mesmo dia, dentro do teto 60. Muda politica de estudo: precedente F64 (politica e posicao do operador).

### F87 -- O harness de flashcard verifica FORMA e e cego a RENDIMENTO: os 13 cards que o operador reprovou passam em TODOS os predicados -- **MEDIA** -- **ABERTO**

- **Como apareceu:** o 6o principio do `estilo-flashcard` (alternativa errada = no) foi aplicado ao Simulado 8 e rendeu **85 candidatos para 17 erros**. O agente triou para 45; o operador julgou os 85 um a um numa bancada dedicada e **inverteu 25 vereditos (29%)**, fechando em 44. Veredito literal dele: *"ampliou os pontos de conteudo passiveis de expansao, mas cunhou bastante ruido -- o que eu justamente temia. nesse sentido, os cards realmente precisam de juizes de qualidade ate mesmo pedagogica."*
- 🔴 **A evidencia dura:** os **13 cards que ele cortou passam** no `audit_card_atomicity.py`, no `card_self_sufficiency.py` e nos predicados de `tools/card_checks.py`. Sao atomicos, tem UM criterio de acerto, frente gerativa, verso curto, contexto alinhado. **Nenhum predicado do repo mede se o card vale a pena.** O harness responde "esta bem formado?" e nunca "isto acrescenta recall?".
- **O sinal, medido:** o que ele RESGATOU (12 cards) era `conteudo` em 8 dos 12 -- fato arbitrario que nao se deduz (janela de 48-72 h; resolucao em 7-10 dias; SIRI em 4-8 semanas; bilirrubina > 0,2 mg/dl/h; diabetes = 25% dos polidramnios; "grao de cafe"; doxiciclina 100 mg 12/12 h por 7 d; reforco faltante da febre amarela). O que ele CORTOU (13 cards) era `discriminador` (5), `mecanismo` (2) e `nuance` (2) -- resposta **regeneravel** a partir do card-nucleo mais o mecanismo, ou o proprio raciocinio da questao reescrito como pergunta.
- ⚰️ **O caso que derruba a intuicao do agente:** *"por que insuficiencia uteroplacentaria, RCF e pos-datismo cursam com oligoamnio?"* foi celebrado na s171 como o melhor achado do 6o principio (um card resolvendo tres alternativas pelo mesmo mecanismo). **O operador cortou.** Resolver tres alternativas de uma vez e o sintoma, nao a virtude: se um mecanismo unico explica as tres, o aluno as reconstroi e o card nao mede nada.
- **O nucleo nunca oscilou:** dos 85 candidatos, os **12 `elo_quebrado` sobreviveram sem uma unica inversao**. O criterio "nucleo do erro intocavel" esta validado; o que falhou foi tudo o que orbita.
- 🔎 **O unico predicado que reagiu -- e reagiu no lugar certo.** Apos aplicar o corte dele, o `insert_questao.py` emitiu `[AVISO-CARD] distrator-perdido` em exatamente **2 dos 17 erros** (Liquido Amniotico e HIV): sao os dois em que os cards cortados eram justamente os que carregavam a alternativa marcada. **Existe UM predicado adjacente a rendimento no repo, ele funciona, e ele nao bloqueia** -- ele marca a tensao real entre o 6o principio (ler as alternativas) e o filtro de regenerabilidade (cortar o que se deduz). Candidato natural a fixture de qualquer predicado futuro de rendimento.
- **Remedio aplicado agora (documental, nao codigo):** `estilo-flashcard.md` ganhou o §Triagem com o **teste de regenerabilidade** e o corolario que inverte a heuristica (`conteudo` rende mais que `discriminador` derivado da mesma questao). A triagem fica **humana e antes do `insert_questao.py`**, com a lista integral guardada em disco para o operador derrubar o corte.
- **Classe:** familia CONTEUDO (com F79/F79b/F81 -- `card_checks` cego a defeito de card), mas num eixo novo: os anteriores sao **defeito de forma que o gate nao ve**; F87 e **ausencia de forma defeituosa em card que nao deveria existir**.
- ⏸️ **s187 -- o eixo IRMAO ganhou sensor; ESTE eixo segue GATE do operador.** Ele pediu "derivar do FSRS", e ao construir ficou claro que **o FSRS nao pode alcancar este achado**: os 13 cards que ele cortou **nunca entraram no baralho** -- nao tem `reps`, `lapses` nem stability. Entregue `tools/cards_rendimento.py`, que mede o eixo vizinho (entre os cards que EXISTEM, quais consomem revisao sem reter): corte DERIVADO do baralho (`lapses >= 2` e `stability < mediana`, re-medida a cada execucao, porque o limiar do Anki de 8 lapsos acharia zero -- o maximo daqui e 4), **48 de 822 revisados (5,8%)**, com `#70` em 11 revisoes e stability 0,67d. 🔴 **O doc do modulo DECLARA que nao fecha o F87**, e o teste `test_o_limite_do_F87_esta_declarado` prende essa frase -- dizer o contrario seria cobertura aparente, a classe que o item 1.10 existe para impedir. Corroboracao do limite: 2 dos 6 piores sao de `Polipos e Neoplasias Intestinais`, area onde a memoria registra "capota completa, 9 de 9 cards" -- nao sao cards defeituosos, e **fundacao ausente**, que pede andaime. Um gate de rendimento, se algum dia existir, nao e um predicado sobre o texto do card -- e sobre a relacao entre o card e o resto do conjunto.

### F78 -- Extracao de PDF descarta em silencio todo conteudo que vive em FIGURA, e nada no harness mede essa perda -- **MEDIA** -- **DECLARADO nao-verificavel (s187)** -- medir a perda exigiria comparar o PDF-fonte com o `.txt` extraido por conteudo SEMANTICO (a figura nao deixa marca no texto: a extracao retorna sucesso e o buraco e invisivel). Sensor nenhum existe hoje e o custo nao se paga sem mais dado. A mitigacao demonstrada segue sendo a leitura humana do resumo contra a fonte -- revisar: 2027-03-31
- **Evidencia (s169):** 10 resumos do sprint S17-S20 foram cunhados em paralelo a partir dos PDFs do EMED. Dois agentes independentes reportaram a mesma lacuna com origem unica: `tools/extract_pdfs.py` so captura camada de texto; infografico e tabela renderizados como imagem saem VAZIOS do `.txt`.
  - Caso 1 (Tumores Anexiais): o `.txt` traz literalmente *"a seguir esta o estadiamento da FIGO"* e a pagina seguinte vem so com cabecalho/rodape. O estadiamento inteiro (IA a IVB) evaporou.
  - Caso 2 (Pneumonias Bacterianas): CURB-65, CRB-65 e os tres algoritmos de antibioticoterapia por nivel de cuidado estavam todos em figura.
- **Nao e incidente isolado, e a mesma familia ja declarada:** as "lacunas honestas" do artifact da s168 -- estadios FIGO do CA de ovario, 10 grupos de Robson, minimo de servicos do Decreto 7.508 e a tabela SBC 2025 -- tem exatamente esta causa. Quatro ocorrencias registradas antes desta sessao, tratadas cada vez como limitacao pontual, nunca como classe.
- **O defeito real e o SILENCIO, nao a perda.** A extracao retorna sucesso, o `.txt` existe, o resumo e escrito e passa no `audit_resumos.py` com "AUDITORIA PERFEITA". Nenhum gate compara o que o PDF tem com o que o `.txt` entregou. So um leitor que ja conhece o tema percebe o buraco -- ou seja, exatamente quem nao precisa do resumo. Um resumo com o estadiamento faltando e indistinguivel, para o harness, de um resumo completo.
- **Mitigacao DEMONSTRADA na propria sessao:** o agente de Pneumonias Bacterianas, ao perceber a lacuna, renderizou as paginas relevantes com **PyMuPDF (fitz)** e leu os infograficos visualmente antes de redigir. Todos os itens e cortes do CURB-65/CRB-65 e os esquemas de antibiotico do resumo vieram dessas imagens do PDF-fonte, nao de memoria. Mesmo problema, resolvido -- por iniciativa ad-hoc de um agente, sem estar em lugar nenhum do contrato.
- **Remedio (S):** `extract_pdfs.py` emitir WARN por pagina cujo texto extraido seja despropocionalmente curto para a area da pagina (heuristica: pagina com imagem e < N caracteres). Transforma o silencio em sinal, sem prometer resolver a leitura.
- **Remedio (M):** dar ao `extract_pdfs.py` um modo `--render <paginas>` que gera PNG das paginas indicadas, promovendo a mitigacao acima a passo de primeira classe do workflow `criar-resumo` -- hoje ela depende de um agente ter a ideia sozinho.
- **Remedio (L):** gate de cobertura que cruze os titulos do sumario do PDF com os headers do `.md` gerado.
- **Acao tomada na s169:** subagente `evidence-researcher` acionado para preencher o estadiamento FIGO no resumo de Tumores Anexiais a partir de fonte externa auditavel (hierarquia de `evidence-governance.md`), com citacao de fonte e ano -- em vez de deixar a lacuna declarada em blockquote.
- **Desdobramento (s169, mesma sessao):** o preenchimento do FIGO fechou com fonte canonica (documento oficial FIGO 2014, reconfirmado no update FIGO 2021; espelhado em portugues pela SBP 2019) -- e revelou um agravante que o F78 nao previa: **a figura do EMED nao estava so ausente, estava DESATUALIZADA**. A enumeracao preservada no PDF-fonte lista o estadio **IIC**, extinto na revisao de 2014, e nao tem IC1/IC2/IC3 nem IIIA1/IIIA2. Ou seja: onde a figura extrai, o conteudo pode estar velho; onde nao extrai, ninguem confere. Os dois modos de falha convergem no mesmo ponto cego -- nada no pipeline compara o material do cursinho com a diretriz vigente. Isso aproxima o F78 da lista de "diretrizes novas a conferir" do HANDOFF, que hoje e mantida a mao.
- **Nota de processo:** o subagente `evidence-researcher` foi acionado com um brief que mandava EDITAR o arquivo -- ele e read-only por contrato e nao tem `Edit`/`Write`. Recusou corretamente e devolveu o bloco pronto; a aplicacao foi feita pelo orquestrador. Brief mal-formado, nao falha do agente: pedir escrita a um agente de leitura desperdica um ciclo inteiro.
- **Padrao de fundo:** primo direto do achado de alcancabilidade e do F77 -- um dado que **existe na fonte e e perdido no caminho**, sem que nenhum instrumento acuse a perda. A diferenca para o F77 e que la o descarte era deliberado e documentado; aqui e invisivel ate para quem escreveu o pipeline.

### F69 -- resumos com lacuna de diretriz nova = risco banca-dependente (s165) -- **MEDIA** -- **GATE do operador** (quais diretrizes 2026 entram e decisao clinica dele; lista viva no HANDOFF)
**Evidencia (grep):** `[CIR] Trauma.md` ja tem X-ABCDE, torniquete, hipotensao permissiva, ABC score, pneumotorax oculto/3,5 cm, Beck, tranexamico; **falta** "sangue total > 1:1:1" e "Sellick contraindicada", e a classificacao do choque ainda cita "classe I" (11a ed = leve/moderado/grave). `Prevenção Secundária Pós-IAM (Dislipidemia).md`: 1 mencao a PREVENT/Lp(a)/bempedoico (diretriz 2025 rasa). `Sistemas de Informação em Saúde.md`: conferir SINAN 2026 (esporotricose, anomalias, Oropouche, parotidite). HAS Pt2 (130/80, MAPA) e Epilepsias (levetiracetam EV) ja atualizados. **Fix:** Revisao Direcionada com Regra de Acumulo; os `padroes_banca` do JSON sao a fonte.

### F68 -- 15 temas de alta/media prevalencia ENAMED sem linha na taxonomia (s165) -- **MEDIA** -- **GATE do operador** (criar linha de tema e decisao de escopo de estudo dele)
**Evidencia:** `core/cronograma/prevalencia_enamed.json` (`tema_id: null`): SCA/dor toracica, DPOC, Derrame pleural, Crise hipertensiva, Parkinsonismo, Dermatoses infecciosas, SUA, Sindrome de Down, Dx nutricional, Choque em pediatria, TB na infancia, Vasculite IgA, SIMP, Saude do trabalhador, Doencas de vulva e vagina. Sem linha nao ha card, erro, dormencia nem nota -- o tema e invisivel ao motor. **Agrava F65:** `[bulk] Cirurgia` guarda **148 erros** sem tema (eram 72 cards na s162), `[bulk] Pneumo` 17. **Fix:** criar as linhas (via cunhagem/`insert_card_base`) e reclassificar os `[bulk]` pelo titulo do erro.

### F67 -- taxonomia duplicada divide o sinal do FSRS e da dormencia (s165, Claude Code/Fable 5.1, 2026-09-05) -- **MEDIA** -- **GATE do operador** (RODADA 3, mesma familia do F65: colapsar par e edicao de DADO com cards e erros pendurados)
**Evidencia (db, read-only):** o mesmo tema vive em 2-5 linhas de `taxonomia_cronograma`: Rastreamento de colo x2 (`...do Câncer de Colo do Útero` 12 ativos/8 erros e `...do Cancer de Colo Uterino` 2/1), TH x2 (`Climatério e Terapia Hormonal` 6/2 e `Terapia Hormonal do Climaterio` 0/1), Asma x5 (`Asma`, `Asma - Crise Aguda`, `Asma na Infância`, `Asma na infância`, `Asma - Exacerbacao`), `Planejamento Familiar` x `Contracepção`, Ulceras x2, TCE x3 (Neuro, Cirurgia leve, Ped), `Cirurgia Infantil` x `Cirurgia Infantil I`, APS x2. **Efeito:** `review_radar`, `infer_nota` e `--cluster` leem metades; a dedup da s083 (`dedup_taxonomia.py`, merge MAX) nao pegou variantes por acento/caixa/sufixo. **Fix candidato:** normalizacao NFKD + casefold + tabela de alias em `normalize_taxonomia.py`, com `--dry-run`. **Re-medido em 2026-09-09 (s174, dry-run A6):** chave NFKD+casefold (sem sufixo romano/"na infancia") acha **10 grupos / 22 linhas / 193 cards + 104 erros**; 5 dos 10 sao a area fantasma `GO`/`Clinica Medica` de volta (F89). Decisao de fusao por grupo = operador (`docs/DRYRUN-F65-F67-2026-09-09.md` §4).

### F65 -- o balde `[bulk] <Area>` esconde 72 cards do radar de dormencia -- **MEDIA** -- **GATE do operador** (RODADA 3: reclassificar balde e decisao de DADO dele, nao de codigo; `normalize_taxonomia` esta vazio para isto por medicao -- `docs/DRYRUN-F65-F67-2026-09-09.md`)

**Classe:** taxonomia que corrompe sensor (familia F37/dedup de taxonomia).

**Observado.** Drenando 45 cards na s162, cards de temas completamente distintos apareceram sob
o pseudo-tema `[bulk] Cirurgia`: **pancreatite** (311, 313, 317), **trauma abdominal** (325),
**demencia/MEEM** (291) e **esclerose multipla** (297). Contagem no banco:

| balde | cards |
|---|---|
| `[bulk] Cirurgia` | 55 |
| `[bulk] Pneumo` | 8 |
| outros 6 baldes | 9 |
| **total** | **72** |

**O defeito.** `(area, tema)` e a chave de identidade do tema (invariante anti-poluicao, s083) e
e o que alimenta `review_radar.py` (dormencia), o cluster de frieza do `day_plan --review-plan`
e o gatilho de PREPARAR do `/revisar`. Card sem tema real e **invisivel para toda essa camada**:
sua frieza e diluida num balde que nunca esfria como um tema, e ele nunca dispara aquecimento.
Sintoma direto medido na sessao: `--review-plan` devolveu **40 clusters para 77 cards** e nenhum
sinal frio acionavel (maximo 15.4, gatilho 25) -- fragmentacao que faz o sensor calar.

**Efeito colateral confirmado no uso.** Os cards 311 e 313 (ambos "por que nao TC na
pancreatite", eixos diferentes: etiologia x janela de 72h) cairam no **mesmo bloco** e se
canibalizaram -- o usuario respondeu 313 com o conteudo de 311 e apagou no 311, 2 notas 1 de
interferencia. Com tema real, `detect_clones.py` teria visto o par; no balde, nao ha por-tema
para comparar.

**Direcao (nao implementada).** Reclassificar os 72 por tema real (o texto do card carrega o
tema; `normalize_taxonomia.py` + `dedup_taxonomia.py` sao os portadores existentes) e adicionar
check no `auto_check`: card em tema `[bulk] *` nasce como WARN de taxonomia. Rodar
`detect_clones.py` depois da reclassificacao -- o par 311/313 e o primeiro caso conhecido.

**Severidade:** ALTA (72 cards, 5,7% do banco ativo, cegos ao mecanismo central do projeto).

> **Re-medido em 2026-09-09 (s174, dry-run A6):** **35** cards ativos presos em `[bulk]` (28 em Cirurgia) + **201 erros** em balde -- lista nominal em `docs/DRYRUN-F65-F67-2026-09-09.md` §3. O normalizador nao tem regra para isto (F89, achado-irmao); a reclassificacao e conteudo do operador.

> **Adendo honesto ao F65.** A limpeza dos baldes `[bulk]`/`Geral` **ja estava listada** como
> pendencia Tier-3 em `ESTADO.md §Proximos passos` item 5 -- este achado nao a descobre, ele a
> **quantifica** (72 cards, 5,7% do banco) e nomeia o dano concreto (sensor de dormencia cego +
> colisao de clones medida em 2 notas 1). E o padrao exato da frente de **alcancabilidade**
> (`project_alcancabilidade_auditoria`): a pendencia estava escrita, correta e inalcancada por
> tempo indeterminado, porque nada no harness a transformava em trabalho. O check de WARN
> proposto acima e o que converte a linha de texto em fila.

### F63 -- a prioridade que governa o estudo nao viaja com o repo (o usuario e a camada de transporte) -- **MEDIA** -- **PARCIAL** (o DADO viajou na s165: `core/cronograma/prevalencia_enamed.json`, 89 temas, + `fsrs_queue --prevalencia`; falta ligar ao `infer_nota` -- residuo nomeado)

**Classe:** input do boot nao e verdadeiro (mesma familia de F45/F47) + regra load-bearing fora
do portador (P7, mas na camada de ESTUDO, nao na de engenharia).

**Observado.** O usuario reordenou o xlsx do Drive a mao por um codigo de cores
**Roxo > Rosa > Salmao** (prioridade por prevalencia no ENAMED, derivada do guia estatistico do
EMED). Essa ordem e o que de fato decide o que ele estuda ate 13/09: das 11 tasks da S17, so
**6 sao roxas** (Diarreia Teoria, SUA Teoria, APS Revisao, Diarreia Revisao, Urologia I,
Pneumonias Bacterianas I). As outras 5 (Cirurgia Vascular Revisao, Vitalidade Fetal, Neoplasias
de Estomago e Esofago, Nefrolitiase, APS Teoria III) nao entram na janela.

**O defeito.** `core/cronograma/grade.json` e um parse **fiel** do `Cronograma.pdf` -- verificado
task a task contra a planilha do usuario nesta sessao: 11/11 batem, mesma ordem. O que ele **nao**
carrega e a cor. Logo:
- nenhum consumidor (`day_plan.py`, `cronograma.py --radar`, `preparacao.py`) sabe distinguir
  roxo de salmao; as 11 tasks pesam igual;
- `infer_nota()` tem o **eixo 4 desenhado para consumir `prevalencia_enamed`** e roda em peso
  neutro por falta do campo -- soquete cabeado, sinal existente, ninguem ligou os dois
  (`core/contracts/revisao-calibrada-contract.md:119`, `docs/plans/s094-revisao-calibrada-PRD.md:265`);
- o snapshot `--sync-drive` (unica ponte para o xlsx real) esta **38 dias velho**.

**Consequencia medida.** A regra so existe em prosa (`HANDOFF.md:9`, `session_161.md:14`) e na
cabeca do usuario. Resultado: ele **reenuncia a prioridade a cada sessao e a cada harness** --
para o Antigravity em 02/09 e para o Claude Code no mesmo dia. O humano virou o transporte de um
dado que o repo deveria carregar. Registrado como "achado registrado, nao resolvido" desde a
**s147** (`history/session_147.md:18`) -- 15 dias em aberto.

**Por que importa agora.** E a propria tese do ciclo DESCOLAR (P7: "regra load-bearing vai para o
portador do repo, nao para a memoria do harness") violada na camada que o projeto existe para
servir. A des-colagem consertou o motor; a prioridade do estudo continua colada no operador.

**Direcao (nao implementada).** `grade.json` ganha `prioridade` por task (roxo|rosa|salmao) via
`cronograma.py --sync-drive` lendo o fill/font color da celula do xlsx; `prevalencia_enamed`
passa a ser derivada dela e o eixo 4 do `infer_nota()` liga sozinho -- **zero mudanca** em
`infer_nota()` (o contrato ja previu essa porta). Sensor de staleness do snapshot do Drive vira
WARN no painel de DIVIDA.

**Severidade:** ALTA (governa a alocacao de tempo a 11 dias do ENAMED e 60 da UERJ).

### F63 -- atualizacao (s165)
O insumo `prevalencia_enamed` agora EXISTE (89 temas, 5 aulas EMED) e ja governa o bucket `novos` via `fsrs_queue --prevalencia`. Falta: `cronograma.py`/`day_plan.py` consumirem o mesmo arquivo para o eixo 4 do `infer_nota()` (contrato §7.7 previa "basta fornecer o campo") e para a prioridade roxa da grade.

### F39 -- 40% do baralho viola o principio atomico; a nota FSRS vira ininterpretavel -- **ALTA** -- **PARCIAL: mecanismo COMPLETO (s177, item 1.6); 270 cards agora RASTREAVEIS, a reforja em si e do operador**
- **Origem:** achado do USUARIO durante o dreno da s128, formulado melhor do que o contrato tinha:
  *"e importante que a informacao solicitada no card seja clara, que os cards nao tenham diversos
  requisitos de acerto, e focassem no nucleo epistemologico do erro"*. Ele percebeu ao vivo que a
  frente que ele via era comprimida enquanto o verso (que so o agente lia) trazia exigencias extras,
  pelas quais estava sendo descontado.
- **Evidencia (medida, nao estimada):** `tools/audit_card_atomicity.py` (criado nesta sessao) acusou
  **364 cards**: 220 com **duplo-ask** (a frente cobra duas respostas) e 259 com
  **resposta-multifato** (verso em paragrafo, viola a regra 3 do formato atomico); 122 com ambos.
  Temas mais afetados: Cirurgia Infantil (40), Hemostasia I (29), Cardiopatias Congenitas (21).
- 🔴 **DUAS CORRECOES DE MEDIDA feitas na propria sessao (registrar, para nao repetir):**
  1. **Denominador errado no 1o relato.** Reportei "~40% de ~900 cards ativos". Os ~900 eram o TOTAL
     da tabela; **230 cards estao aposentados** (`needs_qualitative >= 2`) e o detector nunca os le.
     A base ativa era ~678 -> a taxa real era **~54%**, nao 40%. O problema era pior do que o relato.
  2. **Dois bugs de precisao no proprio detector.** O corpus grava sem acento (secao 4.5), o que
     colapsa a copula "e" e a conjuncao "e" na mesma letra: `"Qual e a unica vacina ...?"` casava
     como duplo-ask. Idem a construcao `"entre X e Y"`. Dois guardas + teste de regressao derrubaram
     **220 -> 203** cards de duplo-ask (~8% era falso-positivo). Ambos os bugs so apareceram ao
     **auditar a propria worklist item a item** -- nao ao escrever o detector.
- **Leitura de sistema -- por que e ALTA e nao cosmetica:** um card com 2 criterios de acerto admite
  "acertei metade", e **a nota FSRS deixa de significar alguma coisa**. Nota 2 num card duplo nao
  distingue "sabe metade" de "nao sabe nada", e o agendamento passa a mentir sobre a curva. O defeito
  nao degrada so a experiencia -- **corrompe a medida** que governa toda a repeticao espacada.
- **Dano colateral confirmado:** o agente contabilizou 6 ocorrencias de um padrao de erro do usuario
  (*"para na primeira metade da pergunta"*) usando cards duplos como evidencia. **5 das 6 eram
  defeito do card.** O ruido do baralho estava sendo importado para o prontuario cognitivo do aluno --
  a pior consequencia possivel, porque muda o que ele treina.
- **Entregue nesta sessao:** detector `tools/audit_card_atomicity.py` (read-only, WARN-first, com a
  classe de falso-positivo do **card discriminador** documentada); check 9 do `auto_check`; clausula
  "UM CRITERIO DE ACERTO por card" em `estilo-flashcard.md` + espelho sincronizado; **8 cards
  atomizados** (370, 372, 406, 407, 408, 447, 456, 457 reescritos in-place com FSRS preservado +
  12 desmembramentos via `insert_card_extra`).
- **Onda 2 (mesma sessao, 4 subagentes em paralelo -- pedido do usuario):** 91 cards dos temas mais
  contaminados (Hemostasia I, Cardiopatias, Cirurgia Infantil, Quadril Pediatrico, Polipos,
  Vulvovaginites, Arboviroses, Meningites, Imunizacoes) reescritos in-place + **109 splits**.
  **Arquitetura que tornou isso seguro: os agentes AUTORAM (db em `mode=ro`), o orquestrador
  PERSISTE.** Uma unica mao escrevendo -> zero contencao de lock no SQLite e um so ponto de gate.
  - Gate de aplicacao novo: `tools/apply_reforja.py` -- valida schema + encoding + **atomicidade do
    conteudo PROPOSTO** (o remedio auditado pelo criterio que diagnosticou a doenca), all-or-nothing,
    dry-run por default. Pegou 1 card que os agentes deixaram passar ("Coombs positivo ou negativo
    **e por que**") e 4 falso-positivos que exigiram olho humano.
  - Os agentes fizeram **triagem honesta**: o grupo B classificou 8 dos seus 23 como falso-positivo
    e os manteve quase intactos, em vez de inventar defeito para cumprir tarefa.
- **Estado:** de **364 -> 264 cards afetados**; duplo-ask **220 -> 125**. Base ativa 787 (34%).
  A queda tem tres componentes distintos, nao confundir: **91 consertos reais**, **~17 falso-positivos
  eliminados** pelos guardas do detector, e **diluicao** (109 cards novos, atomicos por construcao,
  engordam o denominador).
- **Aberto:** **264 cards**. Ordem: (1) os **125 de duplo-ask** -- sao os que corrompem a nota;
  (2) os ~139 so-multifato depois -- degradam retencao, nao a medida. Lotes por tema, priorizando
  os que caem na fila FSRS dos proximos dias. Nunca big-bang.
- 🔴 **Custo colateral a monitorar:** a onda cunhou 109 cards novos, todos entrando no pool
  (`state=0`), que foi de 383 para ~684. Com teto de 40/dia isso e divida de consolidacao, nao
  ativo -- **escalonar o intake priorizando os temas fracos**, sob pena de trocar um problema de
  qualidade por um de volume.

---

### F16 -- Tema cirurgico de alto rendimento sem SSOT clinico (.md); so o PDF-fonte existe -- **MEDIA** -- **PARCIAL (mecanismo feito, conteudo aberto)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** a hipotese (a) FOI construida -- `tools/cobertura_conhecimento.py` e o relatorio `pdf-sem-md` que o achado pedia. O conteudo segue aberto e agora tem numero: `python tools/cobertura_conhecimento.py` -> **395 PDFs-fonte, 135 `.md`, 68 cobertos (61 exato + 7 fuzzy), 327 orfaos**. A evidencia original continua literalmente valida: **apendicite segue sem `.md`** (glob por `*apendic*` em `resumos/**/*.md` = vazio). 🔴 **Residuo de ALCANCE, nao de mecanismo:** `reachability_check --tabela` mostra o CLI alcancado so por `/extrair-pdf` -- nem o boot nem o `auto_check` o consultam, entao os 327 orfaos so aparecem para quem ja foi olhar. Mesma familia da frente de alcancabilidade (s144).
- **Evidencia:** apendicite ("um dos temas mais cobrados na prova de Cirurgia Geral", segundo a propria fonte EMED) tem em `resumos/Cirurgia/` apenas o PDF-fonte gitignored (`8. Abdome Agudo Inflamatorio - Apendicite Aguda.pdf`) e **nenhum `.md`**. Glob por `*Apendic*` retorna so o PDF; grep de termos (Alvarado/apendice/carcinoide) nos `.md` acha so mencoes tangenciais (Cirurgia Infantil, Polipose/CCR), nao resumo dedicado. Para cunhar a aula foi preciso extrair o PDF a mao na sessao.
- **Leitura de sistema:** `resumos/**/*.md` e o SSOT de conhecimento clinico E o unico corpus que o RAG indexa (`index_resumos.py`; AGENTE secao 6). Tema sem `.md` fica (a) invisivel ao RAG semantico (`obsidian-notes-rag search_notes` volta vazio p/ apendicite), (b) sem fonte consultavel nem armadilhas cumulativas, (c) re-extraido a mao a cada aula. O HANDOFF lista gaps pontuais (TCE.md, Sistemas de Informacao) mas nao ha check sistematico de cobertura.
- **Verificacao sugerida:** cruzar `resumos/**/*.pdf` (fontes EMED presentes) contra `resumos/**/*.md` (SSOTs existentes); listar temas com PDF sem `.md` par e quantos sao de alto rendimento.
- **Hipotese de melhoria:** (a) relatorio de cobertura `pdf-sem-md` (CLI ou check WARN no `auto_check`) que torna o gap visivel e priorizavel; (b) rodar o workflow `criar-resumo` p/ apendicite -- fecha o gap de conteudo E realimenta o RAG. A aula-base desta sessao ja e insumo pronto p/ o `.md`.

### F2 -- Latencia de shell no ambiente Windows -- **MEDIA** -- **DECLARADO nao-verificavel** (propriedade do ambiente, nao do repo; nenhum codigo nosso a controla -- revisar: 2027-03-31)
- **Evidencia:** comandos via Bash (`git log`, `ls resumos/**`) estouraram o timeout de 120s nesta sessao. CLIs Python (`fsrs_queue.py`, etc.) rodam normalmente e rapido.
- **Leitura de sistema:** qualquer hook ou rotina que faca *shell-out* pesado -- em especial o pre-commit `auto_check --staged` e o `day_plan.py` se dependerem de globbing amplo ou de `git` custoso -- herda essa latencia. Risco: hook lento demais ser abortado ou o operador aprender a fazer bypass.
- **Verificacao sugerida:** cronometrar `auto_check --staged` e `day_plan.py` isoladamente; identificar se o custo esta no `git`, no profile do shell, ou no glob de `resumos/**`. Testar se o gargalo e o carregamento do profile PowerShell/Bash vs. o comando em si.
- **Hipotese de melhoria:** (a) garantir que hooks usem caminhos diretos e evitem `ls`/`find` recursivo (preferir Python `pathlib` com escopo staged); (b) cache de indice quando aplicavel; (c) documentar em AGENTE.md que a superficie de tooling e Python-CLI-first, shell-glob-last.
