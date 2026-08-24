# Session 154 -- Drenagem FSRS de 100 cards (10 blocos de 10) + 7 reforjas de card + auditoria de evidência (beta-hCG/ectópica)
**Data:** 2026-08-24
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 153

---

## O que foi feito

### Arco 1 -- Boot + drenagem de 100 cards em pipeline de 2 blocos

Sessão aberta com panorama de estado (ver HANDOFF da s153) e oferta de próximo ato. Usuário redirecionou: em vez de iniciar as Revisões por Questões de Pediatria/Ginecologia (pendentes desde o S16), pediu para drenar 100 cards FSRS em 10 blocos de 10. Fila puxada via `fsrs_queue.py --list --limit 100`: 57 atrasados + 21 hoje + 14 novos + 8 erros_frescos.

Conduzido no modo DRENAR com pipeline de 2 blocos em voo (protocolo validado na s152): feedback do bloco N entregue junto com as perguntas do bloco N+2, sem pausa. Card presentation seguiu o contrato P3 (sem vazar área/tema antes da revelação, `selection_reason` como tag curta).

**Correção de calibração do usuário no meio da sessão (após bloco 3):** "feedback só das notas 1 e 2" -- a skill já previa "uma linha" pra nota 3, mas o agente vinha dando parágrafos completos mesmo em acertos parciais. Ajustado e salvo em memória (`feedback_revisar_feedback_so_1_2`); dali em diante, notas 3/4 só entraram em tally compacto, exceto quando o usuário fez pergunta direta embutida na resposta (ex.: card 548, completar "relação aldosterona/renina") ou quando o card foi flagrado como defeituoso (que é outro eixo, sempre reportado).

**Distribuição final de notas (94 cards avaliados, direto do `fsrs_revlog`):** 58 nota 4 · 13 nota 3 · 10 nota 2 · 13 nota 1. Os 6 cards restantes (553, 1053, 155, 576, 293, 325) não geraram rating -- foram forjados/divididos em vez de respondidos (ver Arco 2), exceto 3 (1411, 283, 319) que ficaram sem defeito identificável pelo agente e sem resposta de conteúdo, pendentes de esclarecimento do usuário.

### Arco 2 -- 7 reforjas de card ao vivo + 1 correção de conteúdo via evidence-researcher

O usuário flagrou defeitos de card ativamente durante a drenagem (padrão já nomeado como F40: pacote-de-fatos/pergunta composta/circular). Cada flag foi investigado antes de agir -- 2 flags (cards 63/1411 e 90/283) não tiveram defeito confirmado pelo agente e ficaram em aberto.

**Reforjas de FORMULAÇÃO aplicadas (mesma família de F40):**
- `card_id=1053` (Vulvovaginites/Tricomoníase) -- pergunta fundia "qual o fármaco" + "por que não pode ser tópico"; o mecanismo do "por quê" nem constava na regra-mestre do card. Trimado para só o fármaco.
- `card_id=553` (HAS/pontos de corte) -- 5 cortes numéricos numa única frente. Dividido em 4 cards atômicos via `recurate_cards.py` + `insert_card_base.py` (553=consultório; 3 novos=vigília+MRPA parelhados, sono, 24h).
- `card_id=155` (Puericultura/APS) -- 2 perguntas coladas por "E" (baixo risco=só enfermeiro? alto risco sai da APS?). Dividido em 2 cards.
- `card_id=576` (DIU de cobre) -- mesma família, dividido em 2 (barreira pós-inserção; NIC1 contraindica).
- `card_id=293` (Binswanger x doença priônica) e `card_id=325` (peritonite/trauma) -- subpadrão NOVO: pergunta "por que X é mais provável/correto" respondida com uma reafirmação tautológica de X, sem mecanismo. Ambos vêm de tema `[bulk]` (import em lote). Reformulados para testar o princípio generalizável, não só o par específico.

**Correção de conteúdo via `evidence-researcher` (card_id=114, beta-hCG/gravidez ectópica):** o usuário contestou a nota 1 dada à resposta "ectópica" ("você pergunta o diagnóstico MAIS PROVÁVEL -- reforje o card"). Em vez de aceitar a contestação ou defender o card cegamente, disparado o mesmo protocolo do card GINA STEP1 (s153, `core/contracts/evidence-governance.md`). Veredito: **PRECISA AJUSTE** -- nem o card ("gestação tópica normal", certeza que nem FEBRASGO nem ACOG sustentam) nem a contestação do usuário ("ectópica é a mais provável") estavam corretos. O quadro é uma "pregnancy of unknown location" (PUL): falha da gestação (~50%) é o desfecho isolado mais provável, mais que gestação intrauterina evolutiva (~36%) ou ectópica (~11%). Fontes: ACOG Practice Bulletin 193 (PMID 29470343), Connolly et al. 2013 Obstet Gynecol (PMID 23262929), FEBRASGO. Card reformulado com a moldura de PUL + conduta de beta-hCG seriado em 48h (não mais "repetir USG em 15 dias").

**Achado de ledger:** o mesmo padrão de calibração de probabilidade pré-teste em Gravidez Ectópica já tinha sido pego há dezenas de sessões (F7, s108, `card_id=120`, heterotópica-vs-corpo-lúteo) e nunca foi auditado -- registrado como reincidência em F41.

Todas as reforjas passaram pelos 4 gates de `recurate_cards.py` (schema/encoding/formulação/atomicidade); 2 exigiram `--permitir-atomicidade` por serem discriminadores legítimos com conteúdo clínico genuinamente multi-branch (114) ou de raciocínio-padrão (293).

## Padrões de erro identificados

**1. "Remédio certo, sequência errada" -- confirmado fora do domínio de origem.** O padrão já nomeado no radar de fraquezas persistentes para Neurologia/Epilepsias (aplicar a conduta certa no momento clínico errado, ignorando ABC) apareceu 2x hoje em domínios novos:
- Card 36 (eclâmpsia): foi direto no MgSO4, pulando via aérea/O2 -- a convulsão eclâmptica é autolimitada, MgSO4 previne recorrência, não reverte a crise em curso.
- Card 76 (hematoma epidural): cravou diagnóstico E lateralidade (a parte mais difícil), mas parou em "IOT e suporte clínico" -- com sinal de herniação (midríase), o tratamento definitivo é craniotomia descompressiva de urgência; IOT é ponte, não destino.

Candidato forte a Revisão Direcionada dedicada -- ainda sem sessão própria.

**2. Inversão de pareamento hormonal em câncer de mama (2x no mesmo bloco).** Card 61: inibidor de aromatase é pós-menopausa (não pré); card 65: obesidade pós-menopausa aponta pra mama, não endométrio (esse card reserva anovulação pra endométrio). Não é lacuna de resumo -- é decoreba de pareamento fase/fator->alvo escorregando sob pressão.

**3. Pergunta composta: para na 1ª metade -- reincidiu >=6x nesta sessão** (cards 10, 17, 19, 40, 70, 81, entre outros de nota 3). Padrão já catalogado (`feedback_bug_pergunta_composta`), sem ação nova necessária além de continuar sinalizando.

**4. "Não lembro" como resposta explícita (5 cards: 72, 77, 80, 89, 94).** Distinto de erro conceitual -- são gaps de pool puro, preenchidos no ato sem necessidade de reensino profundo.

**5. Dois acertos que fecham ciclos abertos:** card 71 (reforço de Febre Amarela aos 4 anos) reverte diretamente a fraqueza persistente nomeada "Pediatria/Imunizações" no radar. Card 650 (GINA STEP1, corrigido na s153) bateu limpo, fechando a nota honesta sobre o feedback errado dado no redrill da s152.

## Artefatos criados/modificados
- `ipub.db`: 7 cards reforjados (1053, 553, 155, 576, 293, 325, 114), 5 cards novos (`insert_card_base.py`, tipo `nuance`) -- 3 de HAS/cortes, 1 de puericultura/alto risco, 1 de DIU/NIC1. 94 avaliações gravadas em `fsrs_revlog`.
- `AUDITORIA_MEDHUB.md`: achado **F41** (6 novas instâncias de F40 + subpadrão tautológico em cards `[bulk]` + reincidência do padrão F7/id=120 em Gravidez Ectópica + 3 flags do usuário sem defeito identificado). Ponteiro de próximos achados atualizado F41->F42.
- Memória (`feedback_revisar_feedback_so_1_2.md`): nova -- feedback explicativo só pra notas 1-2 no DRENAR de blocos grandes; defeito de card continua sempre reportado (eixo distinto).
- `HANDOFF.md`: fechamento desta sessão.

## Decisões tomadas
- Card com defeito de FORMULAÇÃO (pacote-de-fatos/composta/circular) é dividido em cards atômicos preservando o card_id original pra 1 dos fragmentos (FSRS intacto) -- mesmo padrão já validado na s152.
- Card com defeito de CONTEÚDO decisório (ex.: 114) vai para `evidence-researcher` antes de qualquer edição -- nunca aceitar a contestação do usuário nem defender o card por julgamento próprio quando o tema é clinicamente decisório.
- Flag de defeito sem confirmação do agente (63/1411, 90/283, 98/319) NÃO é editado por default -- fica pendente de esclarecimento explícito do usuário, para não reforjar conteúdo às cegas.
- "Feedback só notas 1-2" é a calibração vigente pra DRENAR em blocos grandes; nuance real em nota 3/4 (ex.: resposta mais precisa que o gabarito) não vira mais parágrafo, só tally.

## Próximos passos
1. **Esclarecer com o usuário** o que motivou as flags dos cards 1411 (Ca mama, cirurgia prévia x biópsia com atipia), 283 (estenose duodenal parcial) e 319 (banca-específica, secção ductal pancreática) -- decidir se é 5º subtipo de F40 ou calibração a ajustar.
2. **`card_id=120`** (Gravidez Ectópica, heterotópica-vs-corpo-lúteo, F7) para `/pesquisar-evidencia` -- mesmo precedente metodológico do 114.
3. **Revisão Direcionada dedicada** pro padrão "remédio certo, sequência errada" transversal (eclâmpsia + TCE hoje; epilepsia historicamente) -- ainda sem sessão própria, junto com "exame normal exclui" (pendente desde antes).
4. **Revisão por Questões Pediatria (51q) e Ginecologia (57q)** -- seguem as últimas tarefas do S16 não iniciadas, com aula de apoio publicada na s153.
5. Auditoria ampla do banco (pendente desde s148, agora com F41 somado ao escopo).
6. 20 cards novos surgiram na fila após o dreno de 100 (11 hoje + 8 erros_frescos + 1 atrasado) -- resíduo natural além do lote pedido, não dívida deixada para trás; considerar numa próxima sessão de revisão.
