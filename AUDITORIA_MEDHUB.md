---
type: report
layer: root
status: working-draft
relates_to: [AGENTE, ESTADO, HANDOFF]
---

# AUDITORIA_MEDHUB -- Relatorio de Engenharia do Ambiente

> **Proposito.** Documento de trabalho para auditar o MedHub *como sistema de software*
> (camada de estado, contratos, CLIs, filas, hooks) e alimentar um PRD de melhorias.
> Escrito em registro de engenharia de sistemas -- o conteudo de dominio (clinico) e
> tratado como *payload*/dado das estruturas, nunca como o assunto do documento.
> Aberto para aprofundamento por sessao subsequente (agente de engenharia).
>
> **Encoding:** ASCII limpo, Zero LaTeX, sem setas Unicode (AGENTE.md secao 4.5). Usar `->`, `<=`, `--`.

**Data de abertura:** 2026-07-05
**Metodo:** observacao do ambiente em uso real (boot + sessao de drenagem da fila FSRS) + leitura da arvore de governanca (AGENTE.md, HANDOFF.md, contratos, tools/).
**Escopo v1 (este doc):** achados de primeira passada (F1-F9) + hipoteses de melhoria + aprendizados de processo + ponto de entrada para o agente de engenharia (Fable). **Nao** e ainda o PRD -- e o insumo para ele. **Status: pronto para pickup do Fable** (secao 8).
**Origem dos achados:** F1/F2/F4/F5/F6 = leitura da arvore de governanca; **F3/F7/F8/F9 = nascidos direto do uso vivo** (drenagem de 43 cards FSRS na s108). O dogfooding rendeu os achados que a leitura estatica nao pegaria.

---

## 0. Como usar este documento

1. Cada achado tem: **ID · titulo · severidade · evidencia · verificacao sugerida · hipotese de melhoria.**
2. A severidade e operacional: **ALTA** (fere integridade de estado/SSOT), **MEDIA** (custo de eficiencia/DX recorrente), **BAIXA** (polimento).
3. A secao 5 (andaime de prompt) existe para estruturar o pedido ao agente de engenharia de forma que o trabalho seja lido como engenharia de sistemas -- reduzindo a chance de o classificador automatico do modelo marcar o fluxo como sensivel por causa do vocabulario de dominio.
4. O aprofundamento deve **verificar cada achado** (a coluna "verificacao sugerida") antes de virar item de PRD. Achados aqui sao de primeira passada, nao veredito.

---

## 1. Achados de integridade de estado

### F1 -- Drift do ponteiro de sessao no HANDOFF -- **MEDIA**
- **Evidencia:** `HANDOFF.md` declara no cabecalho "s108" e "Proximo passo -- s109", mas o log mais recente em `history/` e `session_107.md`. Nao existe `session_108.md`. O hook de boot (`SessionStart`) sinalizou: *"HANDOFF.md cita s108, mas o ultimo log e history/session_107.md -- considerar reconcile"*.
- **Leitura de sistema:** o Protocolo de Fechamento (AGENTE.md secao 3) tem 4 passos -- (1) atualizar HANDOFF, (2) ESTADO se macro mudou, (3) **registrar `history/session_NNN.md`**, (4) git. O passo 1 avancou o ponteiro sem o passo 3 selar a sessao. A disciplina de fechamento permite essa dessincronia sem barreira automatica.
- **RESOLVIDO na s108:** o "s108" do HANDOFF era renumeracao antecipada (o s107 escreveu o ponteiro apontando para a proxima sessao antes dela existir). Esta sessao **e** a s108 (drenagem FSRS + auditoria), entao o fechamento correto -- registrar `history/session_108.md` -- **fecha o drift naturalmente** (o ponteiro passa a ter log correspondente). Nao foi preciso sessao retroativa.
- **Hipotese de melhoria (permanece valida):** invariante verificavel no `auto_check.py` (ou no boot): *o ponteiro de sessao do HANDOFF nunca deve exceder `max(session_NNN)` em `history/` + 1*. Nasce WARN (politica de severidade de s106/107), vira BLOCK quando a base zerar. Fecha a lacuna entre o passo 1 e o passo 3 do fechamento -- o drift so foi possivel porque nada barra o HANDOFF de anunciar uma sessao que ainda nao foi selada.

---

## 2. Achados de tooling / DX / confiabilidade de hooks

### F2 -- Latencia de shell no ambiente Windows -- **MEDIA**
- **Evidencia:** comandos via Bash (`git log`, `ls resumos/**`) estouraram o timeout de 120s nesta sessao. CLIs Python (`fsrs_queue.py`, etc.) rodam normalmente e rapido.
- **Leitura de sistema:** qualquer hook ou rotina que faca *shell-out* pesado -- em especial o pre-commit `auto_check --staged` e o `day_plan.py` se dependerem de globbing amplo ou de `git` custoso -- herda essa latencia. Risco: hook lento demais ser abortado ou o operador aprender a fazer bypass.
- **Verificacao sugerida:** cronometrar `auto_check --staged` e `day_plan.py` isoladamente; identificar se o custo esta no `git`, no profile do shell, ou no glob de `resumos/**`. Testar se o gargalo e o carregamento do profile PowerShell/Bash vs. o comando em si.
- **Hipotese de melhoria:** (a) garantir que hooks usem caminhos diretos e evitem `ls`/`find` recursivo (preferir Python `pathlib` com escopo staged); (b) cache de indice quando aplicavel; (c) documentar em AGENTE.md que a superficie de tooling e Python-CLI-first, shell-glob-last.

### F3 -- Ordenacao da fila FSRS ignora clusterizacao por tema -- **MEDIA**
- **Evidencia:** `fsrs_queue.py::_ordered_queue` achata os buckets na ordem `atrasados -> hoje -> novos`, intercalando temas. Na fila real observada (59 cards) os temas ja vinham naturalmente agrupados nos dados, mas a ordem de entrega mistura Dermato, Gineco, Cirurgia, etc. O agente teve de **re-agrupar manualmente por tema** para conduzir a revisao em cluster.
- **Leitura de sistema:** a Camada 0 do contrato de `/revisar` prega "esquentar o tema antes de sondar". Revisar em cluster (todos os cards de um tema juntos) permite **um** refresh que aquece o tema e drena o cluster inteiro -- pedagogicamente superior e alinhado ao contrato. A ordem atual forca ou o re-agrupamento manual (custo de agente) ou refreshes fragmentados.
- **Verificacao sugerida:** confirmar em `app/utils/db.py::get_cards_by_bucket` se ha campo `tema` disponivel para ordenacao secundaria (ha -- os cards trazem `area`/`tema`).
- **Hipotese de melhoria:** flag `--cluster` (ou `--by-tema`) em `fsrs_queue.py` que, preservando a prioridade de bucket, ordene secundariamente por `(area, tema)` e mantenha cards do mesmo tema contiguos. Alternativa/adicional: `day_plan.py` emite um "plano de revisao" que ja lista os clusters do dia com contagem. Ganho barato, observado direto do uso.

### F4 -- Backlog FSRS vs. politica de teto diario -- **MEDIA**
- **Evidencia:** fila do dia = 40 atrasados + 4 hoje + 15 novos puxados; backlog de novos reportado em ~322-351 (day_plan/HANDOFF divergem: 322 vs 351 -- ver F5). A politica de cards diaria registrada em memoria e "teto 30/dia (agendados + 15 backlog)". Os **44 agendados (atrasados+hoje) ja excedem o teto** antes de qualquer card novo.
- **Leitura de sistema:** ha tensao estrutural entre a politica de teto e a divida real de cards vencidos. Se o teto e respeitado, o backlog de atrasados nunca drena; se o backlog e drenado, o teto e violado todo dia. Nenhum dos dois esta errado isoladamente -- falta uma **estrategia de drenagem de divida** explicitada.
- **Verificacao sugerida:** medir a taxa de crescimento do backlog (novos/dia entrando) vs. taxa de drenagem sustentavel; conferir a fonte da divergencia 322 vs 351.
- **Hipotese de melhoria:** (a) `day_plan.py` expor "divida de atrasados" como metrica de primeira classe (hoje ela fica diluida no bucket FSRS); (b) definir politica de drenagem (ex.: subconjunto priorizado por dormencia/stability quando o backlog estoura N); (c) reconciliar a politica de teto com a realidade de 44 vencidos -- ou o teto sobe em regime de divida, ou ha um "modo mutirao".

---

## 3. Achados de protocolo / carga cognitiva do agente

### F5 -- PREPARAR (Camada 0) e reativo, nao proativo -- **BAIXA** -- ⚰️ **ENTREGUE (p5) -> OBJETO REVOGADO**
- ⚰️ **LAPIDE (2026-09-08, s171).** Mecanismo **ENTREGUE (p5)** -- sinal de frieza por cluster no `--review-plan` + clausula de oferta proativa do PREPARAR (limiar >=25 no contrato) -- e depois **objeto revogado** em `revisao-calibrada-contract.md` Clausula 11 (v1.3, s170): o PREPARAR deixou de existir e o cluster frio passou a **entrar na fila de prioridade da Revisao Direcionada de fechamento**, nao a disparar aquecimento. O achado nao foi invalidado nem esquecido -- o gatilho que ele pedia MIGROU de superficie. **Nao re-derivar:** se alguem reintroduzir aquecimento pre-bloco, o F5 volta junto. O sinal (`review_radar.py` / `--review-plan`) segue vivo: morreu o consumidor, nao o sensor.
- **Evidencia:** o refresh-antes-de-card-frio so aconteceu porque o operador pediu explicitamente ("quick refresh antes de pegar os cards a frio"). O contrato preve o PREPARAR, mas o gatilho ficou no operador, nao no agente.
- **Leitura de sistema:** o sinal de "tema frio" e objetivo e ja esta nos dados (stability media + taxa de acerto do cluster + dormencia via `review_radar.py`). O agente poderia **detectar o cluster frio e oferecer o PREPARAR** antes de sondar, em vez de esperar o pedido.
- **Verificacao sugerida:** conferir se `fsrs_queue`/`day_plan` ja expoem stability por card/cluster; se nao, o sinal vem de `review_radar.py`.
- **Hipotese de melhoria:** ao abrir um cluster no fluxo DRENAR, o protocolo de `/revisar` checa o sinal de frieza e, se frio, oferece o PREPARAR proativamente ("cluster X esta frio -- aqueco antes?"). Mantem a fronteira dura (PREPARAR nao toca FSRS).

### F6 -- Divergencia de numeros entre HANDOFF e day_plan -- **BAIXA/MEDIA**
- **Evidencia:** volume acumulado -- HANDOFF diz "4.418"; day_plan do boot diz "4454 acum.". Backlog de novos -- HANDOFF "322"; day_plan "351". FSRS atrasados -- HANDOFF "27 atrasados + 13 hoje"; day_plan "40 atrasados + 4 hoje"; fila real puxada agora = 40 atrasados + 4 hoje.
- **Leitura de sistema:** o `day_plan.py` (derivado, ao vivo do db) e a fila real concordam (40+4). O `HANDOFF.md` (texto, escrito a mao no fechamento) esta defasado. Confirma que **a fonte viva (db/day_plan) e fiel; o HANDOFF textual drifta** -- mesmo padrao de F1.
- **Verificacao sugerida:** nenhuma -- e consequencia de F1 (fechamento incompleto). Tratar junto.
- **Hipotese de melhoria:** o bloco "Estado por frente" do HANDOFF que carrega numeros (volume, FSRS, backlog) poderia ser **gerado** por `day_plan.py --handoff-block` em vez de digitado, eliminando a classe inteira de drift numerico. Texto qualitativo continua manual; numeros viram derivados.

---

### F7 -- Defeito de autoria de card: discriminacao incompleta (stem nao exclui o competidor real) -- **MEDIA**
- **Evidencia:** card `id=95` (tema Cardiopatias Congenitas). Stem: RN 2 dias, choque, cianose, cardiomegalia, RX com hiperfluxo, ECG com desvio a direita + HVD. Resposta esperada = Hipoplasia do VE (HCE). A `verso_armadilha` do card so cita **um** competidor (Tetralogia de Fallot, que e hipofluxo/tardia -- facil de excluir). Mas o stem, como escrito, **nao exclui a Transposicao das Grandes Arterias (TGA)** -- que tambem cursa com apresentacao precoce, hiperfluxo, cardiomegalia e predominio de VD. O operador respondeu TGA aplicando o framework corretamente (cianotica de hiperfluxo); o card marca como erro sem que o stem sustente a discriminacao.
- **Leitura de sistema:** o card ensina uma discriminacao que seu proprio enunciado nao suporta -- defende-se contra o competidor facil (Fallot) e ignora o competidor verdadeiro (TGA). Alem disso, o mesmo cluster ja tem o card `id=94` como HCE explicito (com eco), tornando o `id=95` um segundo HCE de baixa diferenciacao. Pela politica do projeto, "defeito de card e de autoria -> reforjar ancorado no erro" (memoria `curadoria_e_temas_zero`).
- **Fator de confusao registrado (honestidade de metodo):** nesta sessao o refresh PREPARAR do agente **pre-induziu TGA** ao descrever o quadro de hiperfluxo cianotico -- contaminando o trial. Isso e um risco intrinseco do PREPARAR: o refresh que aquece pode **vazar a resposta** ou enviesar o recall. Ver F8.
- **Verificacao sugerida:** revisar o stem do `id=95` -- ou (a) adicionar ao enunciado o discriminador que exclui TGA (ex.: relacao das grandes arterias / eco), ou (b) expandir a `verso_armadilha` para nomear TGA como o competidor e dar o criterio de exclusao. Conferir se ha outros cards do deck com o mesmo padrao (armadilha defende-se do competidor errado).
- **Segundo caso (mesmo padrao, outra especialidade):** card `id=120` (tema Gravidez Ectopica). Stem: gestacao intrauterina viavel confirmada (embriao + CCN 3mm) + massa anexial **sem fluxo** ao Doppler + beta-hCG subindo, **em gestacao espontanea (sem TRA/FIV)**. Resposta esperada = **heterotopica**. Problema de calibracao: heterotopica espontanea e ~1:30.000; na ausencia de TRA e sem features de ectopica ativa (o "sem fluxo" ate argumenta *contra*), a resposta estatisticamente dominante e **gestacao topica + corpo luteo**. O card forca o diagnostico raro como se fosse o provavel. O operador respondeu "gestacao normal" -- **clinicamente mais defensavel** para o cenario espontaneo -- e o card marca como erro. Candidato a **auditoria de evidencia** (`/pesquisar-evidencia`): quando a banca espera heterotopica e a probabilidade basal diz corpo luteo, e o tipo de conflito banca-dependente que o `evidence-governance` existe para arbitrar.
- **Hipotese de melhoria:** rodar `/curar-cards` (workflow `curar-cards.md`) com foco em "discriminacao incompleta" e "diagnostico raro forcado"; possivel heuristica para o linter `audit_flashcard_quality.py`: sinalizar cards cuja `verso_armadilha` nomeia um competidor de categoria **diferente** da resposta (ex.: Fallot=hipofluxo vs resposta=hiperfluxo) sem nomear nenhum competidor da **mesma** categoria. Sinal fraco, mas barato. Para o `id=120`, submeter a resposta esperada ao gate de evidencia antes de reforjar.

### F8 -- Risco de vazamento de resposta no PREPARAR -- **BAIXA/MEDIA** -- ⚰️ **ENTREGUE (p3) -> OBJETO REVOGADO**
- ⚰️ **LAPIDE (2026-09-08, s171).** Mecanismo **ENTREGUE (p3)** -- Invariante D (isolamento de conteudo do PREPARAR) no contrato v1.1 -- e depois **objeto revogado** em `revisao-calibrada-contract.md:74` (v1.3, s170), que ja carrega lapide propria: sem aquecimento pre-drill nao ha o que isolar, e toda nota do DRENAR volta a ser recall a frio. **Nao re-derivar:** aquecimento pre-bloco reintroduzido traz de volta o vazamento, e os TRES canais medidos abaixo (vazamento de resposta, card de fato puro, erro de ensino amplificado) seguem validos como descricao do risco. 🔴 **O corpo abaixo e evidencia historica, nao norma ativa.**
- **Evidencia:** o refresh pre-bloco de Cardiopatias Congenitas nomeou explicitamente "TGA" como o exemplo canonico de cianotica de hiperfluxo, momentos antes de um card cuja resposta era HCE (tambem hiperfluxo). O aquecimento moldou a resposta.
- **Leitura de sistema:** o PREPARAR (Camada 0) existe para aquecer o tema, mas ha uma fronteira fina entre **aquecer a fundacao** e **entregar a resposta do card que vem a seguir**. Quando o refresh e feito pelo mesmo agente que conhece as respostas dos cards, o vies e estrutural.
- **Verificacao sugerida:** revisar o contrato de `/revisar` (Camada 0) -- ha alguma clausula que isole o conteudo do refresh das respostas especificas dos cards do bloco? (Aparentemente nao.)
- **Hipotese de melhoria:** clausula no contrato: o PREPARAR aquece **conceitos e mecanismos**, nunca **o par pergunta-resposta especifico** dos cards do bloco. Operacionalmente: o agente monta o refresh a partir do resumo do tema (substrato via engine/RAG), **antes** de olhar os versos dos cards -- ou explicitamente evita ancorar exemplos nas respostas que sabe que virao. Preserva a validade do trial de recall.
- **Refinamento observado (3a passada, cluster Arboviroses):** ha uma classe de card para a qual o PREPARAR e **contraindicado**, nao apenas arriscado -- os cards de **fato/definicao puro** (ex.: `id=402` "familia e genoma do virus da febre amarela"; `id=403` "sinal semiologico classico da febre amarela"). Aquecer esses cards no refresh **e** entregar a resposta -- nao ha "conceito de fundo" a warmar que nao seja o proprio fato cobrado. Regra derivada: o PREPARAR distingue **cards de raciocinio/conduta** (refresh do framework e legitimo; nota mede "pegou o framework") de **cards de fato puro** (refresh se limita a orientacao de entorno; a resposta especifica e retida para o recall). Operacionalizavel se os cards carregarem o campo `tipo`/altura (base/mecanismo/nuance/topo) -- fato puro tende a ser `topo`/`nuance`; ver [[project_cards_altura_graduada]].
- **Refinamento observado (2a passada, cluster Gravidez Ectopica):** o refresh foi montado sem abrir os versos (disciplina F8 aplicada) e ainda assim **contaminou por dois canais distintos**: (1) *cards de conduta* -- ensinar o framework "beta baixo isolado -> faca a curva" pre-resolve os cards `id=116`/`id=114`, cuja resposta E "faca a curva"; aquecer o framework e legitimo, mas invalida o trial de recall desses cards. (2) *erro de acuracia no aquecimento* -- o refresh afirmou de forma **absoluta** "GIU + massa anexial = topica + corpo luteo (NAO heterotopica)", uma simplificacao que empurrou o operador para longe da resposta do card `id=120`. Licao: o vies do PREPARAR nao e so vazamento de resposta; e tambem **erro de ensino amplificado** -- uma imprecisao no refresh vira erro induzido no card seguinte. Mitigacao adicional: regras do refresh formuladas como tendencia ("geralmente corpo luteo, mas considerar heterotopica se TRA/features de ectopica"), nunca como absoluto; e, para clusters de conduta, aceitar que a nota pos-refresh mede "pegou o framework", nao recall a frio (ja previsto na Camada 0, mas reforcar).

---

### F9 -- Sem caminho de amend/override para rating FSRS ja gravado -- **MEDIA**
- **Evidencia:** o contrato de `/revisar` (passo 4) diz que "o usuario pode sobrepor a nota". O CLI `fsrs_queue.py --record` e **append-only** (`db.record_review` = INSERT em `fsrs_revlog` + UPDATE em `fsrs_cards`). Quando o override chega **depois** do record, honra-lo grava uma **2a linha** no revlog e recalcula o FSRS a partir do estado **ja mutado** pela 1a nota -- resultado != "nota correta de primeira". Observado nesta sessao: card `id=403` gravado 2 (o operador escreveu "Paget"), depois corrigido para 4 (sabia "Faget"); o re-record moveu o `due` de 2026-07-19 para 2026-07-26, deixando 2 linhas de revlog para o mesmo card na mesma sessao.
- **Leitura de sistema:** contradicao entre duas clausulas do proprio contrato -- "usuario pode sobrepor" vs. "nunca `--record` duas vezes o mesmo card (regra anti-duplo-registro)". A regra anti-dup protege contra o duplo **acidental**, mas nao previu o override **intencional** pos-record.
- **Verificacao sugerida:** confirmar que `db.record_review` nao expoe rollback/replace; medir se ha outros pontos que assumem um-record-por-card-por-sessao.
- **Hipotese de melhoria (preferida):** mudar o **protocolo do loop**, nao o schema -- o agente so chama `--record` **apos** a janela de override (apresenta a nota proposta, espera confirmacao/correcao, entao grava uma vez). Elimina a classe inteira sem tocar o banco. Alternativa pesada: `fsrs_queue.py --amend CARD_ID --rating N` que remove a ultima revlog row da sessao e reverte `fsrs_cards` ao estado pre-review (exige `record_review` retornar o estado anterior para rollback). Preferir a mudanca de protocolo.

---

## 3b. Sessao de engenharia (Fable, 2026-07-05) -- verificacao F1-F9, achados F10-F15, entrega das 5 ondas

> Pickup da secao 8 executado: ledger -> PRD (`.vibeflow/prds/engenharia-ledger-f1-f13.md`) -> 5 specs -> implement -> audit (fluxo vibeflow completo). Cada achado foi VERIFICADO contra o codigo antes de virar spec (secao 0.4). Commits: d7ad6ea (PRD+specs), d488cfe (p1), 5e19dab (p2), a669a6f (p3), a47967d (p4), p5 no commit desta edicao. Audits PASS em `.vibeflow/audits/engenharia-ledger-part-*.md`.

**Status F1-F9:**
- F1 -> **ENTREGUE (p1)**: invariante executavel `check_session_pointer` no auto_check (WARN `SESSION_POINTER_DRIFT`; ponteiro <= max(session)+1); roda em --all e quando HANDOFF/history no diff.
- F2 -> **NAO REPRODUZIDO (medido, p5)**: mediana de 3 runs via PowerShell, cwd=repo, 2026-07-05 -- `auto_check --staged` 0.15s; `day_plan` 0.89s; `git status` 0.07s. O timeout de 120s da s108 era do ambiente Bash daquela sessao (profile/globbing do harness), nao do tooling do repo. Achado fica ABERTO-DORMENTE: se reproduzir em sessao de uso, medir com este mesmo metodo antes de consertar.
- F3 -> **ENTREGUE (p2)**: `fsrs_queue --cluster` (opt-in, buckets preservados, temas contiguos; sem a flag = byte-identico) + `day_plan --review-plan` (clusters derivados da fila real).
- F4 -> **ENTREGUE (p2)**: teto dinamico (decisao do operador 2026-07-05): TETO_BASE=30; atrasados>30 -> teto dobra (cap 60) ate drenar. Norma no fsrs-management-contract v1.1; campo `divida` no day_plan.
- F5 -> **ENTREGUE (p5)**: sinal de frieza por cluster no `--review-plan` (via review_radar, fallback silencioso) + clausula de oferta proativa do PREPARAR (limiar >=25 no contrato, nao no CLI).
- F6 -> **ENTREGUE (p1)**: `day_plan --handoff-block` (bloco numerico derivado; AGENTE §3 passo 1 atualizado). Bonus: expos inconsistencia do manual antigo (/10.000 convivendo com ritmo de 12k).
- F7 -> **PARCIAL (p5 + curadoria pendente)**: heuristica com lexico opcional (`tools/data/competidores_categorias.json`) no audit_flashcard_quality -- WARN experimental, gate anti-decorativo (3 execucoes sem sinal acionavel -> remover). Calibrada: dispara no card 95. Reforge dos cards 95/120 segue com o agente-player (/curar-cards; id=120 via gate de evidencia).
- F8 -> **ENTREGUE (p3)**: Invariante D no contrato v1.1 (PREPARAR isolado: sem abrir versos; tendencia nunca absoluto; fato puro nao se aquece).
- F9 -> **ENTREGUE (p3)**: Invariante C (janela de override ANTES do record; 1 record por card; sem amend pos-record). Contradicao v1.0 eliminada.

**Achados novos (scan estatico + friccao de implementacao):**

### F10 -- Dashboard bypassava a camada db -- **MEDIA** -- **RESOLVIDO (p4)**
- Evidencia: `app/pages/1_dashboard.py` fazia `import sqlite3` + `DB_PATH='ipub.db'` relativo (quebra se cwd != raiz; violava db-access-layer.md). Fix: 3 funcoes novas em db.py (SQL identico, DataFrames validados .equals=True); app/pages/ agora 100% sem sqlite3.

### F11 -- Blob ipub.db no historico git -- **BAIXA** -- **RESOLVIDO (2026-07-06, expurgo executado)**
- Evidencia: blob versionado ate s058 (`d99ff02`); ~1.6MB de dado local-only em todo clone. Runbook em `docs/runbook-expurgo-ipub-git.md`.
- **EXECUTADO 2026-07-06 (go nominal do operador):** push previo -> mirror de backup atualizado -> `git filter-repo --invert-paths --path ipub.db --force` -> force push. Validado em clone fresco do GitHub: 0 commits tocando ipub.db; size-pack ~18M -> 2.91 MiB; ipub.db local intacto (untracked). Backups: `C:/Users/daanm/medhub-backup-pre-expurgo.git` (mirror pre-expurgo completo). NB: TODOS os SHAs mudaram na reescrita -- SHAs pre-expurgo citados neste ledger/audits/HANDOFF sao referencias do historico antigo (narrativa preservada; ponteiros obsoletos por design).

### F12 -- Testes sem harness formal -- **MEDIA** -- **RESOLVIDO (p4)**
- Evidencia: 4 test_*.py scripts avulsos. Fix: pytest.ini + conftest.py + bridge subprocess (exit code assertado; coleta crua daria verde decorativo -- funcoes de check sem assert). `pytest` na raiz: 7 passed. Standalone preservado.

### F13 -- Hooks de boot nao versionados -- **MEDIA** -- **RESOLVIDO (p1)**
- Evidencia: SessionStart/PostToolUse so em settings.local.json com paths absolutos da maquina -- boot deterministico nao sobrevivia a clone. Fix: `.claude/settings.json` versionado com $CLAUDE_PROJECT_DIR.

### F14 -- test_revisao_calibrada e cwd-sensivel -- **BAIXA** -- **RESOLVIDO (3d)**
- Evidencia: rodado fora da raiz do repo, falha 4 checks; com cwd=raiz, passa. O auto_check sempre o invoca com cwd correto (mascarava). Mitigado no pytest via bridge (cwd=raiz); o script standalone segue exigindo cwd na raiz.
- Hipotese de melhoria: resolver paths por `__file__` nos 4 checks afetados (baixo custo, sessao futura). *(Resolucao real: causa era no engine, nao no teste -- ver 3d.)*

### F15 -- test_memory quebra em pipe cp1252 -- **BAIXA** -- **RESOLVIDO (3d)**
- Evidencia: imprime U+2192 (seta unicode) sem reconfigure de stdout -> UnicodeEncodeError sob pipe; viola o decision de 2026-04-23 (CLIs com nao-ASCII devem reconfigurar) e a convencao de encoding (AGENTE §4.5). Mitigado no bridge via PYTHONIOENCODING=utf-8.
- Hipotese de melhoria: aplicar o snippet canonico de reconfigure + trocar as setas por `->` (4 linhas).

---

## 3c. Sessao de uso s109 (coordenador-observador) -- achados F16-F19

> **Origem:** uso vivo da s109 -- forja da aula-base de apendicite (prova de R+ em gastroenterologia). O papel de coordenador-observador (contrato do operador, 2026-07-05) alimenta o ledger **F16+** enquanto conduz o estudo. Trilha de ENGENHARIA: o conteudo clinico (apendicite, questoes, erros) vai para `history/` + HANDOFF, nao aqui (secao 7.6). Achados de primeira passada -- **verificar** antes de virar spec do ciclo 2.

### F16 -- Tema cirurgico de alto rendimento sem SSOT clinico (.md); so o PDF-fonte existe -- **MEDIA** -- **PARCIAL (mecanismo feito, conteudo aberto)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** a hipotese (a) FOI construida -- `tools/cobertura_conhecimento.py` e o relatorio `pdf-sem-md` que o achado pedia. O conteudo segue aberto e agora tem numero: `python tools/cobertura_conhecimento.py` -> **395 PDFs-fonte, 135 `.md`, 68 cobertos (61 exato + 7 fuzzy), 327 orfaos**. A evidencia original continua literalmente valida: **apendicite segue sem `.md`** (glob por `*apendic*` em `resumos/**/*.md` = vazio). 🔴 **Residuo de ALCANCE, nao de mecanismo:** `reachability_check --tabela` mostra o CLI alcancado so por `/extrair-pdf` -- nem o boot nem o `auto_check` o consultam, entao os 327 orfaos so aparecem para quem ja foi olhar. Mesma familia da frente de alcancabilidade (s144).
- **Evidencia:** apendicite ("um dos temas mais cobrados na prova de Cirurgia Geral", segundo a propria fonte EMED) tem em `resumos/Cirurgia/` apenas o PDF-fonte gitignored (`8. Abdome Agudo Inflamatorio - Apendicite Aguda.pdf`) e **nenhum `.md`**. Glob por `*Apendic*` retorna so o PDF; grep de termos (Alvarado/apendice/carcinoide) nos `.md` acha so mencoes tangenciais (Cirurgia Infantil, Polipose/CCR), nao resumo dedicado. Para cunhar a aula foi preciso extrair o PDF a mao na sessao.
- **Leitura de sistema:** `resumos/**/*.md` e o SSOT de conhecimento clinico E o unico corpus que o RAG indexa (`index_resumos.py`; AGENTE secao 6). Tema sem `.md` fica (a) invisivel ao RAG semantico (`obsidian-notes-rag search_notes` volta vazio p/ apendicite), (b) sem fonte consultavel nem armadilhas cumulativas, (c) re-extraido a mao a cada aula. O HANDOFF lista gaps pontuais (TCE.md, Sistemas de Informacao) mas nao ha check sistematico de cobertura.
- **Verificacao sugerida:** cruzar `resumos/**/*.pdf` (fontes EMED presentes) contra `resumos/**/*.md` (SSOTs existentes); listar temas com PDF sem `.md` par e quantos sao de alto rendimento.
- **Hipotese de melhoria:** (a) relatorio de cobertura `pdf-sem-md` (CLI ou check WARN no `auto_check`) que torna o gap visivel e priorizavel; (b) rodar o workflow `criar-resumo` p/ apendicite -- fecha o gap de conteudo E realimenta o RAG. A aula-base desta sessao ja e insumo pronto p/ o `.md`.

### F17 -- PDFs-fonte retidos "para o RAG" nao sao indexados; o proposito da decisao s086 esta desconectado do wiring -- **MEDIA** -- ⚰️ **SUPERADO por decisao de arquitetura (gold-only)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** o achado supunha que o wiring estava atrasado em relacao a intencao. Foi o contrario: a **intencao** e que morreu. A consolidacao part-2 tornou o RAG **gold-only** (`AGENTE.md:152`: a collection `pdf_raw` e o `search_two_tier()` foram REMOVIDOS), e `tools/index_resumos.py` indexa `.md` por contrato -- o PDF e insumo de AUTORIA, nao fonte de busca. Escolha (a) da propria hipotese, tomada de fato e nunca escrita. 🔴 **Residuo corrigido nesta sessao:** `AGENTE.md:159` ainda declarava que os PDFs sao mantidos *"pois serao usados para alimentar o RAG"* -- premissa morta contradizendo a linha 152 do MESMO documento, no portador que o boot le. Lapidada (mesma classe do F90: premissa orfa sobrevivendo no carrier).
- **Evidencia:** a decisao s086 (AGENTE secao 6) reteve os PDFs do EMED dentro de `resumos/` "pois serao usados para alimentar o RAG". Mas `index_resumos.py` indexa `resumos/**/*.md` -- o PDF fica no lugar, **un-indexado**. O texto do PDF so entra no RAG se/quando transcrito a mao para `.md`.
- **Leitura de sistema:** gap entre a intencao declarada (PDF alimenta o RAG) e o wiring (RAG so le `.md`). O caminho real e implicito: PDF -> extracao manual -> `.md` -> index. Enquanto o `.md` nao e cunhado, o PDF e IP retido sem retorno de busca. F17 e a causa-sistemica de F16 existir silenciosamente.
- **Verificacao sugerida:** confirmar que `index_resumos.py` nao ingere PDF (aparentemente so glob de `*.md`); contar PDFs em `resumos/**` sem `.md` par.
- **Hipotese de melhoria (escolha de arquitetura p/ ai-eng):** ou (a) canonizar PDF->md como o unico caminho (entao F16 e "so" execucao de conteudo + o relatorio de cobertura basta), ou (b) `index_resumos` passa a ingerir texto extraido de PDF como fonte secundaria do RAG (com metadado de origem) -- amplia cobertura sem trabalho de autoria, mas indexa material bruto fora do `/estilo-resumo`.

### F18 -- Aula-base e efemera (chat-only); sem artefato de persistencia/reuso nem registro de calibracao -- **BAIXA/MEDIA** -- **SUPERADO na forma; residuo de ALCANCE**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** as tres pontas se moveram. (1) A aula deixou de ser chat-only: desde a s149 toda aula-base sai como **Artifact HTML** com URL propria (`.claude/commands/aula-base.md` e o contrato de renderizacao). (2) A forma duravel do CONTEUDO e o `.md` gold -- opcao (a) da propria hipotese, hoje canonica. (3) A calibracao **e** gravada: `taxonomia_cronograma.dificuldade` tem **30 de 288** temas com nota (F18c, `db.set_dificuldade`). 🔴 **Residuo medido:** nao existe `aulas/` nem `*.aula.md`, e **nenhum campo liga tema -> URL da aula**. O artefato agora persiste e continua **inalcancavel a partir do repo** -- a efemeridade virou irrecuperabilidade, que e um defeito diferente e menor.
- **Evidencia:** a aula-base de apendicite foi construida e entregue so no chat. Nao ha `aulas/` nem campo que vincule aula a tema; a proxima vez o artefato e re-forjado do zero. A nota de dificuldade 1-10 que calibrou a descompressao (D10 pela regra do extensivo) tambem nao foi registrada (`taxonomia_cronograma.dificuldade` intocada nesta sessao).
- **Leitura de sistema:** a aula-base e artefato pedagogico validado (memoria: "leitura mais prazerosa"; efeito de cobertura 53%->75%) e caro de produzir (extracao + escada). Efemeridade = re-trabalho, zero acumulo, sem reuso cross-sessao -- tensao com o objetivo "melhor app de estudos". Pode ser efemera-por-design SE o `.md` (F16) for a forma duravel e a aula for so a sua renderizacao descomprimida.
- **Verificacao sugerida:** decidir se a forma duravel do ensino e o `.md` gold (aula = derivada efemera) ou se a aula merece artefato proprio; conferir se `db.set_dificuldade` pode registrar a calibracao mesmo em prova fora do cronograma.
- **Hipotese de melhoria (p/ ai-eng decidir):** (a) `.md` como forma duravel + aula como render efemero (fecha via F16, custo zero de infra); ou (b) persistir a aula (`{Tema}.aula.md` ou secao); e, minimamente, (c) registrar a nota de dificuldade do tema no ato da aula, alimentando a Revisao Calibrada.

### F19 -- Ambiente e ENAMED/cronograma-centrico; prova paralela (R+ gastro) sem suporte de primeira classe -- **BAIXA** -- ⚰️ **SUPERADO (multi-prova de 1a classe, s159/s174)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** `core/provas.json` e hoje o leitor unico de datas e tem **3 entradas** (ENAMED 13/09, fim-grade-EMED 09/10, UERJ/MFC 01/11). O boot conta regressiva **por prova**, o ritmo-alvo e parametrizado pela prova-alvo (o plano de hoje diz *"faltam 3274 p/ UERJ/MFC (prova 01/11) em 52d"*) e o **blackout do FSRS** (F71) e por prova, lido de la e nunca hardcoded. O single-target morreu na virada da s159. **Residuo declarado, sem data:** nao existe sub-plano de volume/metrica ESCOPADO por prova paralela -- mas a demanda nao voltou desde a s108, e o eixo tema atende.
- **Evidencia:** a sessao atual e p/ uma "prova de R+ em gastroenterologia", fora do `Cronograma.pdf`/grade ENAMED. Todo o boot (day_plan: volume-vs-meta, ritmo-alvo ~107.8q/dia, "faltam p/ ENAMED em 70d", proximos temas do cronograma) assume o alvo ENAMED. A maquinaria por tema (fraquezas, FSRS, cards, RAG) e agnostica de prova e serve; mas nao ha como escopar/trackear um alvo paralelo.
- **Leitura de sistema:** o modelo de "para que estou estudando" e single-target (ENAMED). Provas paralelas (R+, especificas de residencia -- UERJ/USP/IPUB ja estao na direcao estrategica) sao atendidas ad-hoc pelo eixo tema, sem metrica/escopo proprio. Nao e defeito -- e limite de modelo de dominio, relevante ao objetivo de produto.
- **Verificacao sugerida:** mapear superficies ENAMED-hardcoded (day_plan metas/ritmo, cronograma) vs. agnosticas (insert_questao, fsrs, rag); avaliar recorrencia de provas paralelas.
- **Hipotese de melhoria (p/ ai-eng/produto):** conceito leve de "prova-alvo" (tag/escopo) que reusa o eixo tema e permite um sub-plano; ou decisao explicita de manter single-target e tratar paralelas so pelo eixo tema. Baixa urgencia; registrar p/ nao perder o sinal.

---

## 3d. Sessao de engenharia -- ciclo 2, rodada 1 (Fable/ai-eng, 2026-07-05, paralela a s109)

> Rodada de suporte iniciada ANTES da s109 abrir (e concluida em paralelo a ela). Do escopo autorizado do ciclo 2: entregue (a)-parcial e (b), mais F14/F15 (pendencias BAIXA do ciclo 1). (c) reforge + triagem de F16-F19 correm com a leva do operador. Corrida de escrita neste ledger detectada e respeitada: a s109 tomou a secao 3c e F16-F19; esta rodada usa 3d e F20.

**F11 (expurgo ipub.db) -- JANELA PREPARADA na rodada 1; EXECUTADO 2026-07-06 (ver secao 3b/F11):**
- Pre-condicoes conferidas na janela (2026-07-05, pre-s109): tree limpo, main == origin/main (b9bca29), sem lock; blob confirmado no historico (10+ commits ate d99ff02).
- Backup mirror CRIADO: `C:/Users/daanm/medhub-backup-pre-expurgo.git` (18M). `git-filter-repo` INSTALADO (pip --user; ferramenta de operador, fora do requirements.txt).
- O rewrite foi BLOQUEADO pelo gate de permissao do harness da sessao de engenharia (history-rewrite sem pedido nominal na conversa). Decisao: nao contornar -- gate humano no momento da execucao e o espirito do runbook ("aval NESTA janela"). Historico INTACTO. Com a s109 aberta, a janela FECHOU de qualquer forma (sem rewrite com sessao ativa).
- Proxima janela: pos-s109, tree limpo de novo -> operador da o go nominal na conversa do Fable (rota preferida: runbook completo + validacao em clone fresco) OU roda os passos 2-5 do runbook direto no terminal.

**F4/(b) -- teto dinamico VALIDADO com dados reais:**
- Vivo (hoje, pre-s109): 1 atrasado -> regime normal, teto 30. Render do day_plan confere ("Teto do dia: 30 cards (base 30)").
- Retrospectivo (s108 = maior divida real observada): 40 atrasados -> teto = min(30+40, 60) = 60; drenagem real da s108 foi 43+4 = 47 <= 60. O parametro teria coberto o pior caso real.
- Observacao de design: a formula satura no cap ja na primeira entrada do regime (31 atrasados -> min(61, 60) = 60) -- na pratica e um degrau binario 30/60, nao rampa. Funciona na escala real; NAO mexer salvo divida real >60 aparecer (gate anti-decorativo).

**F14 -> RESOLVIDO:** a verificacao achou a causa no ENGINE, nao no teste -- `app/engine/get_topic_context.py::_build_index` usava `Path("resumos")` relativo ao cwd (streamlit/CLIs rodando da raiz mascaravam). Fix: `_ROOT` resolvido por `__file__`; indice interno absoluto; `resumo_path` do retorno relativizado (contrato documentado preservado). Repro antes (fora da raiz): 4 checks XX; depois: TODOS PASSARAM. pytest 7 passed.

**F15 -> RESOLVIDO:** snippet canonico de reconfigure (precedente: test_revisao_calibrada.py:15-18) + 4 prints com seta U+2192 trocados por `->`. Repro antes (sob pipe): UnicodeEncodeError; depois: 5/5 sob pipe.

### F20 -- .venv dessincronizado do requirements.txt (fsrs ausente) -- **BAIXA** -- ⚰️ **RESOLVIDO (opcao (i): venv sincronizado)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** a reproducao original nao reproduz mais. `./.venv/Scripts/python.exe tools/day_plan.py` **roda e imprime o Plano do Dia** (nao levanta `ModuleNotFoundError: fsrs`), e `./.venv/Scripts/python.exe -m pip check` -> *"No broken requirements found"*. **Residuo declarado:** nenhum doc canonico diz QUAL runtime e o oficial -- os dois funcionam hoje, e a unica mencao ao assunto segue dentro de `test_revisao_calibrada.py`. Nao vale spec; vale saber que a escolha e implicita.
- **Evidencia:** `./.venv/Scripts/python tools/day_plan.py` -> `ModuleNotFoundError: No module named 'fsrs'` (traceback cru); `requirements.txt` declara `fsrs>=6.3.1`; o python global roda tudo. `test_revisao_calibrada.py:25-30` ja conhece e trata (mensagem clara + exit 2) -- mas so ali.
- **Leitura de sistema:** o venv existe e engana -- agente/dev que o ative nao roda day_plan nem db.py. O runtime canonico de fato e o python global, mas isso so esta documentado dentro de um teste.
- **Verificacao sugerida:** conferir quem depende do venv (streamlit? hooks?) antes de escolher a hipotese.
- **Hipotese de melhoria:** (i) sincronizar o venv (`pip install -r requirements.txt`) e mante-lo canonico, OU (ii) aposentar o venv e documentar o python global como runtime no AGENTE/README, OU (iii) guard com mensagem clara (padrao do test_revisao_calibrada) nos CLIs de `tools/`. Decisao do operador.

---

## 3e. Sessao de uso s109 (coordenador-observador) -- analise do 1o lote de questoes -- achado F21

> Corrida de escrita respeitada (convencao da secao 3d): a rodada 1 do ciclo 2 tomou 3d e F20; esta continuacao da s109 usa 3e e F21. Origem: analise do 1o lote de apendicite (18 questoes, 5 erros) -- trilha de ENGENHARIA. O conteudo clinico (os 5 cards ancorados nos erros) foi para o `ipub.db` via `insert_questao.py` (flashcards 727-731), nao aqui (secao 7.6).

### F21 -- Compressao por dificuldade (Revisao Calibrada) eliminou um ponto de decisao de alto rendimento, nao so encurtou profundidade -- **MEDIA**
- **Evidencia:** a aula-base de apendicite foi re-renderizada em D7 (pedido do operador, baixando do D10). A compressao D10 -> D7 removeu o galho "isquemia de base apendicular junto ao ceco -> ileotiflectomia/ileocolectomia" (presente no D10; cortado no D7 como "detalhe cirurgico de baixo rendimento"). A Q2 do lote (42% de acerto) caiu exatamente nesse galho -- o operador marcou Ochsner (invaginacao), gabarito ileotiflectomia. Erro em parte atribuivel ao corte da aula.
- **Leitura de sistema:** a Revisao Calibrada mapeia a nota 1-10 a degraus de descompressao (D10/D8/D5/D2). Mas a regra de cobertura (`feedback_aula_base_cobertura_escopo`, normada em AGENTE secao 1.2) diz que a profundidade calibra, a **cobertura nao** -- nunca cortar tema/ponto de pega de banca. O D7 violou isso: comprimiu ELIMINANDO um ponto de decisao testavel em vez de encurta-lo. O knob de dificuldade nao tem um "piso de cobertura" operacional no ato de render a aula.
- **Verificacao sugerida:** revisar `core/contracts/revisao-calibrada-contract.md` -- ha clausula que separe "profundidade/descompressao" (calibravel pela nota) de "cobertura de pontos de decisao de alto rendimento" (piso fixo por tema)? A regra existe em memoria/AGENTE mas nao esta operacionalizada por nota.
- **Hipotese de melhoria:** a nota calibra descompressao/prosa, nunca a lista de pontos de decisao de alto rendimento -- que e um checklist de cobertura fixo por tema, derivado do sumario da fonte (EMED). Operacionalmente, mesmo em D2/D5/D7 o render passa por esse checklist antes de fechar. Conecta com F18 (persistir aula + calibracao) e com o padrao ja validado (s089: extrair o sumario do PDF como checklist de cobertura antes de redigir).

---

## 3f. Sessao de uso s109 (coordenador-observador) -- 2o lote de questoes -- achados F22-F26

> Corrida de escrita respeitada (convencao 3d): 3c=F16-F19, 3d=F20, 3e=F21, esta secao=3f/F22-F26. Origem: 2o lote de apendicite (42 questoes, 11 erros) -- trilha de ENGENHARIA (os 5 cards de conteudo foram para `ipub.db`, flashcards 732-736). O operador pediu explicitamente (2026-07-05) alimentar o ledger com erros de processo, tentativas insatisfeitas, bugs, capacidades inexploradas e inconsistencias -- esta safra responde a isso.

### F22 -- `registrar_sessao_bulk` idempotente por (sessao_num, area) impede 2o bloco da mesma area na mesma sessao -- **MEDIA** -- **RESOLVIDO (3g)**
- **Evidencia:** o 1o bloco de apendicite foi gravado como s109/Cirurgia (18q). Ao registrar o 2o bloco (42q) na mesma sessao/area, a guarda de idempotencia (`registrar_sessao_bulk.py:56-65`, "SELECT ... WHERE sessao_num=? AND area=?") retornaria "[AVISO] ... Nada alterado" -- nem soma nem atualiza. Contornei com `--sessao 110` (+ `--obs` "s109 bloco 2"); senao o volume das 42q seria perdido.
- **Leitura de sistema:** a guarda protege contra duplo-registro acidental, mas trata "mesma sessao + mesma area" como duplicata sempre. Um dia com 2+ blocos da mesma area (comum: manha e tarde de Cirurgia) nao tem como ser gravado sem falsear o `sessao_num` -- que passa a acumular um valor (110) sem `history/session_110` correspondente. Inconsistencia entre rotulo de volume e ponteiro de sessao.
- **Verificacao sugerida:** confirmar se `day_plan`/dashboard somam volume por SUM de linhas (110 nao quebraria o total, so o rotulo) ou assumem 1 linha por sessao.
- **Hipotese de melhoria:** (a) UPSERT acumulativo (mesma sessao+area soma feitas/acertos), OU (b) `--bloco N` como parte da chave, OU (c) desacoplar `sessao_num` do volume (chave por `data`+area+bloco). A idempotencia anti-duplo deveria olhar um hash do lote, nao (sessao, area).

### F23 -- Cards de erro recem-cunhados (state 0) nao sao surfaced antes do proximo bloco do mesmo tema -> reincidencia -- **MEDIA** -- **RESOLVIDO (3g)**
- **Evidencia:** o link "quadro classico jovem <48h = operar, nao pedir imagem" foi cunhado no bloco 1 desta MESMA sessao (card 730, horas antes). No 2o lote (mesmo dia, mesmo tema) o operador reincidiu no MESMO link **3x** (Q4 pediu US, Q8 pediu TC, Q11 pediu US). O card 730 e state 0 (novo), sem `due` proximo -> nao foi drilado no intervalo entre os blocos. Reincidencia em HORAS, nao dias -- torna o achado mais forte.
- **Leitura de sistema:** para um tema ATIVO (blocos consecutivos), o FSRS puro (agenda por curva) nao serve o card fresco a tempo -- ele so entra pela fila de novos. Falta um gatilho "voce tem cards de erro frescos do tema X que vai treinar agora -> mini-drill antes do bloco" (PREPARAR DIRECIONADO por tema-alvo). A regra do `analisar-questao` ("nao tolere errar 2x pelo mesmo motivo") existe no papel, mas nada a opera.
- **Verificacao sugerida:** confirmar que cards state 0 nao entram na fila de vencidos same-day; medir quantos dos 11 erros batem em links ja carded no 1o lote (>= 3: Q4/Q8/Q11 -> 730; Q8 tambem toca 729).
- **Hipotese de melhoria:** um "pre-bloco por tema-alvo" -- antes de um bloco anunciado de tema X, oferecer drill dos cards de erro frescos (state 0) de X. Estende o PREPARAR (F5) do dormente para o tema-quente-recem-errado. Fecha o buraco entre cunhar o card e ele virar util.

### F24 -- `insert_questao.py` sem modo batch; N erros = N chamadas longas -> exige driver ad-hoc -- **BAIXA/MEDIA** -- **RESOLVIDO (3g)**
- **Evidencia:** um lote de 11 erros nao tem caminho de insercao em lote. Cada erro e uma chamada com ~17 args longos; encadear via shell quebrou por quoting (`bash -c`, aspas desbalanceadas, exit 2, ZERO inseridos). A solucao foi um driver Python (`run_inserts.py`, depois `run_inserts2.py`) passando args por LISTA (sem shell). `--cards-file` existe, mas so adiciona cards a um erro ja criado -- nao cria N pares questao+card novos.
- **Leitura de sistema:** o pipeline e otimo para 1 erro por vez, mas lotes de prova (10-40q) sao o caso real. A ausencia de batch empurra o agente para scripts ad-hoc a cada sessao -- custo e superficie de erro recorrentes (a falha de quoting inutilizou a 1a tentativa).
- **Verificacao sugerida:** confirmar que `--cards-file` nao cria a linha em `questoes_erros` (so cards); medir o atrito de 5-11 inserts sequenciais.
- **Hipotese de melhoria:** `insert_questao.py --errors-file errors.json` aceitando uma LISTA de erros completos (metadados + 5 campos de card cada), inseridos numa transacao. O agente escreve 1 JSON (sem quoting de shell) e chama 1x. Elimina a classe inteira de driver ad-hoc + falha de quoting.

### F25 -- Sem detector de reincidencia: "errar 2x pelo mesmo motivo" nao e sinalizado automaticamente -- **MEDIA** -- **RESOLVIDO (3g)**
- **Evidencia:** para descobrir que Q4/Q8/Q11 do 2o lote batiam no card 730 (do 1o lote), o agente cruzou manualmente os erros novos contra os cards existentes. Nada no `insert_questao`/db avisa "este erro reincide sobre um elo ja carded". O `analisar-questao.md` eleva isso a "alerta critico", mas o sinal depende 100% da memoria do agente na sessao.
- **Leitura de sistema:** o dado existe (`questoes_erros` tem `elo`/`tipo_erro`/`o_que_faltou`; cards tem tema+links). Um matcher (tema + similaridade do `elo`/`o_que_faltou`) marcaria reincidencia no ato do insert -> promoveria o erro a "padrao vivo" no HANDOFF e ao envelope de fraquezas (LangMem, R1 da Autogovernanca). Capacidade inexplorada.
- **Verificacao sugerida:** avaliar se um match por (tema + tipo_erro + overlap de tokens do elo) tem precisao suficiente; comecar como WARN (politica s106/107).
- **Hipotese de melhoria:** no `insert_questao`, apos inserir, checar "ha erro/card anterior no mesmo tema com elo semelhante?" e, se sim, emitir flag de REINCIDENCIA (contagem + link). Alimenta a trilha de conteudo (HANDOFF padroes vivos) e a de fraquezas. Conecta com F23 (surfacing) e R1.

### F26 -- Questoes anuladas/banca-dependentes contam como erro "limpo"; sem tag -- **BAIXA/MEDIA** -- **RESOLVIDO (3g)**
- **Evidencia:** no 2o lote, Q10 tinha "GABARITO OFICIAL: A" x "GABARITO EMED: C" -- o operador marcou C (alinhado ao EMED: "nao existe sinal de McBurney, e PONTO"), "errou" so pelo gabarito oficial. Q5 trazia "nenhuma alternativa esta correta" (banca manteve D com duracao tecnicamente errada). Ambas entram no bruto de 11 erros como se fossem erro limpo de conteudo.
- **Leitura de sistema:** o volume/erro nao distingue "erro real de conteudo" de "questao anulada/controversa onde o operador acertou com razao" -- mesma familia do F7 (1o ciclo). Sem tag, a taxa de erro e o pipeline de cards ficam poluidos por questoes que nao medem lacuna real. Inconsistencia de sinal.
- **Verificacao sugerida:** estimar a frequencia de anuladas/divergentes nos lotes reais; decidir se merece um campo.
- **Hipotese de melhoria:** flag opcional no registro do erro (`--status anulada|banca-divergente`) que (a) nao gera card de "erro" (ou gera card de conteudo neutro), (b) nao conta contra a taxa de acerto real, (c) aciona o gate de evidencia (`/pesquisar-evidencia`) quando banca x diretriz divergem. Estende o mecanismo do F7 do card para a propria questao.

---

## 3g. Sessao de engenharia -- ciclo 2, rodada 2 (Fable/ai-eng, 2026-07-06) -- ORQUESTRACAO ENTREGUE

> Fluxo vibeflow completo delegado pelo operador (2026-07-05, pos-s109): discover -> PRD
> (`.vibeflow/prds/orquestracao-preparacao.md`) -> 4 specs -> implement -> audit **PASS 4/4**
> (`.vibeflow/audits/orquestracao-preparacao-part-*-audit.md`). Tema do PRD veio da decisao
> de produto do operador: ORQUESTRACAO DA PREPARACAO (posicao nunca errada; distribuir carga
> cognitiva pelo follow-up real; descanso/simulado como saidas legitimas). pytest: 13 -> 36 passed.

**Entregas (verificadas contra o codigo antes de spec; regra 0.4):**
- **op-3 (posicao) -> SISTEMA NOVO (part-1):** semana de conteudo = estado de primeira classe
  no db (`preparacao_estado`); CLI `tools/preparacao.py` (--set-semana/--show); day_plan
  db-first (regex `Proxima = SNN` rebaixada a fallback com WARN; nominal virou comparativo);
  `--handoff-block` EMITE a posicao; invariante `POSICAO_DRIFT` no auto_check (WARN).
  O smoke expos na hora: conteudo S12 vs nominal S15 -- 3 semanas de atraso que o fallback
  nominal mascarava.
- **F22 -> RESOLVIDO (part-1):** `--acumular` soma o 2o bloco na mesma (sessao, area) com
  delta-only na taxonomia (sem dupla contagem); guarda anti-duplo preservada por default;
  `--semana N` atualiza a posicao no ato do registro.
- **Recomendador do dia -> ENTREGUE (part-2):** `recomendar_dia()` pura e deterministica
  (R1 mini-drill, R2 descanso, R3 simulado, R4 questoes, R5 fsrs) + projecao (ritmo real
  14d vs necessario, folga em dias) + `--tempo H`/`--energia alta|media|baixa` com defaults
  declarados e registro da condicao. Norma com parametros nomeados:
  `core/contracts/orquestracao-contract.md` (paridade contrato<->CLI TESTADA); AGENTE 2
  passo 4 aponta. Gate anti-decorativo declarado (3 sessoes sem alterar decisao -> revisar).
  Smoke real: "ritmo real 65.6q/dia -> grade fecha em ~96d (folga -27d); necessario 91q/dia".
- **F23 -> RESOLVIDO (part-3):** `fsrs_queue --pre-bloco TEMA [--janela-horas]` lista so os
  cards de erro frescos (state 0) do tema-alvo; rating segue o caminho unico. Smoke real:
  10 cards frescos de Apendicite (727-736) servidos.
- **F25 -> RESOLVIDO (part-3):** matcher lexical pos-insert (tokens normalizados,
  LIMIAR_OVERLAP=0.5) emite `[REINCIDENCIA]` apontando card/erro existente -- WARN
  informativo, nunca bloqueia. Fixture positiva = caso real s109 (Q4 vs card 730).
- **F24 -> RESOLVIDO (part-4):** `insert_questao --errors-file lote.json` -- N erros numa
  transacao unica; validacao pre-transacao aponta item/campo; rollback TOTAL em excecao;
  dedupe por conteudo em re-execucao. Elimina a classe driver-ad-hoc/quoting.
- **F26 -> RESOLVIDO (part-4):** `--status anulada|banca-divergente` (coluna nova
  `questoes_erros.status`, ALTER idempotente): registra o erro SEM cunhar card +
  `[GATE-EVIDENCIA]`; taxa real limpa por construcao.

**Fora do ciclo (registro honesto):**
- **F21 -- RECONCILIADO 2026-07-12 (dois planos):** (1) **conduta = RESOLVIDA** -- a clausula
  "descompressao calibravel x cobertura piso fixo" entrou em `core/contracts/revisao-calibrada-contract.md`
  v1.2 (Clausula 10 + Invariante E: "compressao encurta, nunca corta"). (2) **enforcement mecanico
  = PENDENTE** -- o checklist automatico de cobertura (WARN quando o tema da semana nao tem `.md`)
  esta na spec `mecanismo-conhecimento-consolidacao-part-3`. Ou seja: a barreira de conduta ja vale;
  o motor mecanico vem com a cobertura (o proprio contrato v1.2 declara isso, L138).
- **F16-F19 (pipeline de conhecimento)** -- anti-escopo declarado do PRD; ciclo 3
  (decisao de arquitetura ja registrada: two-tier, .md canon + collection pdf_raw).

### F27 -- Modo single do insert_questao sai com exit 0 mesmo em falha -- **BAIXA** -- ⚰️ **RESOLVIDO (com teste)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** `grep -n sys.exit tools/insert_questao.py` -> **`:481 sys.exit(0 if ok else 1)`** (modo single) e `:516` (batch) -- simetricos, como a hipotese pedia. `pytest tools/test_batch_insert.py -k single` -> **4 passed**. Ja estava documentado em `.claude/commands/analisar-questao.md §9` (*"Exit code (F27): modo single retorna 0 em sucesso e 1 em falha"*); faltava so o marcador aqui.
- **Evidencia:** a docstring promete "Exit 0 em sucesso, 1 em falha", mas o main nao
  captura o retorno de `insert_questao()` -- falha imprime erro e sai 0. Pre-existente;
  descoberto na verificacao da part-4 (que implementou exit 1 no caminho --errors-file).
- **Hipotese de melhoria:** `sys.exit(0 if ok else 1)` no modo single (1 linha; conferir
  se algum chamador depende do exit 0 atual antes).

### F28 -- Arg `--elo` (required) nao e persistido em coluna propria -- **BAIXA** -- ⚰️ **RESOLVIDO por decisao (opcao (b): documentar, nao migrar)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** o fato medido nao mudou -- `PRAGMA table_info(questoes_erros)` devolve **14 colunas e nenhuma se chama `elo`**. O que mudou e que isso deixou de ser lacuna e virou **contrato escrito**: `.claude/commands/analisar-questao.md §9` carrega a tabela arg->coluna, declara que o campo canonico do elo e **`o_que_faltou`** (via `--faltou`), explica que o `--elo` e consumido pelo matcher de reincidencia F25 (`insert_questao.py:286`, `checar_reincidencia`) e **proibe** explicitamente que uma sessao futura crie a coluna. Decisao de schema tomada e versionada.
- **Evidencia:** o INSERT de `questoes_erros` grava habilidades/faltou/armadilha; o `elo`
  era recebido e IGNORADO ate a part-3 (o matcher F25 virou seu 1o consumidor real).
  O "elo" semantico vive espalhado em `o_que_faltou`/cards.
- **Hipotese de melhoria:** ou persistir (coluna `elo`), ou documentar no workflow que o
  campo canonico e `o_que_faltou` e deprecar o arg. Decisao de schema -- operador.

### F29 -- Drift planilha-db nao pego pelo boot (reconcile B4/W1 pulado) -- **ALTA** -- **RESOLVIDO (s110p2, 2026-07-06)**
- **Evidencia:** a sessao abriu com `/performance` + `/cronograma` direto do cache do hook
  (`day_plan`), sem rodar o check de reconcile (AGENTE.md secao 2 passo 3 / reconcile-contract
  B4/W1) contra a planilha `Dashboard EMED 2026`. Relatei 4584q ao operador; ele corrigiu para
  4660 (76q de delta) -- residuo ja existente ANTES desta sessao comecar, nao gerado por ela.
- **Causa raiz (dupla, achada via `download_file_content`+openpyxl nas 20 abas por disciplina
  da planilha):** (1) **mislabel** -- `'GO'` (id 38) e 3x `'Clinica Medica'` (ids 64/65/66,
  sessoes 103-105, gap Antigravity sem fechamento) eram rotulos invalidos escondendo
  Ginecologia/Infecto/Hemato/Oftalmo reais (casamento exato feitas+acertos digito a digito,
  zero ambiguidade); (2) **volume nunca registrado** -- Ortopedia (29q/24a, Quadril Pediatrico)
  e um residual de Cirurgia (47q/40a, tarefa especifica nao identificavel) existiam na
  planilha sob nenhum rotulo no db.
- **EXECUTADO:** `tools/fix_data_delta_110.py` (relabel dos 4 ids; arquivado em
  `tools/_archive/migrations/`) + `registrar_sessao_bulk.py --acumular` (Ortopedia/Cirurgia).
  Backup previo (`ipub_backup_20260706_201837.db`). Validado: `performance.py` bate
  4660q/3684a/79.1% identico a planilha; as 20 areas conferem 1:1 contra as abas por disciplina.
- **Hipotese de melhoria (o que falta para nao reincidir):** o boot hoje SO reconcilia se o
  agente decidir rodar manualmente -- nao ha barreira mecanica. Promover B4/W1 a um passo
  automatico do `day_plan.py`/hook (mesmo que so um WARN comparando total local vs total via
  MCP), em vez de depender do agente lembrar de rodar `/importar-planilha` toda sessao.

### F30 -- `material_indicado` do cronograma nao verifica se o resumo realmente existe -- **MEDIA** -- **RESOLVIDO (s115, boot-cronograma-drive-confiavel part-2)**
- **Evidencia:** a task de Pre-Natal em S12 vem marcada `material_indicado: resumo` (implica
  "so ler o resumo existente"), mas `resumos/GO/Pré-Natal.md` NUNCA existiu -- so o PDF-fonte
  (`25. Pré-Natal.pdf`, 90 paginas). Descoberto ao vivo: operador fez cold recall de 18q (sem
  aula previa) e so na analise pos-questoes percebi que era tema-zero, tendo que construir o
  resumo do zero a partir do PDF (mesmo padrao do F16 -- Apendicite).
- **Leitura de sistema:** a heuristica `material_indicado` (mencionada em `AGENTE.md` secao 1.2,
  refinada 79%->44% na s107) provavelmente infere o rotulo do TIPO de tarefa do PDF do cronograma
  (`Teoria` vs `Revisão`), nao de uma checagem real contra `resumos/**/*.md`. Isso pode levar a
  aula/estudo com expectativa de material leve quando na verdade e tema-zero.
- **Verificacao sugerida:** conferir quantas outras tasks com `material_indicado: resumo` tambem
  carecem de `.md` correspondente (cruzar `core/cronograma/grade.json` x `resumos/**/*.md` por
  `_find_resumo`).
- **Hipotese de melhoria:** `cronograma.py` (ou `day_plan.py --difficulty`) checar em tempo real
  se o resumo existe via `_find_resumo` e rebaixar `material_indicado` para `extensivo`
  automaticamente quando nao existir -- fecha o mesmo buraco do F16 de forma preventiva, para
  qualquer tema futuro, nao so Apendicite.

### F31 -- Cards FSRS podem existir sem NENHUM lastro clinico (nem .md nem PDF-fonte) -- **MEDIA** -- **RESOLVIDO (s115, boot-cronograma-drive-confiavel part-2)**
- **Evidencia:** card_id 205 (Leishmaniose, area Infecto) foi drenado na s112 e o usuario relatou
  "muita dificuldade" pedindo refresh amplo -- `find resumos -iname "*leishmaniose*"` retornou
  vazio E nao ha PDF-fonte tampouco (diferente do F16/F30, onde ao menos o PDF EMED existia). O
  card nasceu de um erro real via `insert_questao.py` (Siamese Twins: erro->db, licao->resumo),
  mas o lado "licao->resumo" nunca foi executado -- e nao ha checagem no momento da insercao que
  force ou ao menos sinalize a ausencia.
- **Leitura de sistema:** o par Siamese Twins (`AGENTE.md` secao 6) e uma convencao, nao um
  invariante mecanico -- `insert_questao.py` grava o erro/card mesmo se o resumo do tema
  (area,tema) nao existir em `resumos/**/*.md` nem como PDF-fonte. Generaliza F16/F30 (tema COM
  pdf sem .md) para o caso mais severo: tema sem nenhum lastro escrito.
- **Verificacao sugerida:** cruzar `taxonomia_cronograma` (todas as `(area,tema)` com card ativo)
  x `resumos/**/*.md` x `resumos/**/*.pdf`; listar temas com card ativo e ZERO lastro escrito.
- **Hipotese de melhoria:** `insert_questao.py` fazer um check read-only (WARN nao bloqueante)
  quando `_find_resumo(area,tema)` retorna None -- sinaliza no ato da insercao, nao meses depois
  num refresh de FSRS.

### F32 -- Re-drill intra-sessao do `/revisar` colide com o relearning nativo do FSRS (state=3) -- **BAIXA** -- **PARCIAL (colisao permanente por desenho, mitigada por contrato)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** a colisao **continua existindo e vai continuar** -- e estrutural: `select state, count(*) from fsrs_cards` -> **8 cards em `state=3`, os 8 com `due <= hoje`**. Duas camadas resolvendo o mesmo problema por vias diferentes nao se fundem sem matar uma. O que a mitiga hoje e contrato, nao codigo: `revisar.md §Relearning intra-sessao` fixa que o re-drill **nao chama `--record`** e que a nota do FSRS e **uma so por card por sessao** (a 1a honesta), e a s173 acrescentou o corte do loop (travou 2x -> sai e vira reonboarding). 🔴 **Residuo nomeado, nao consertado:** o `--list` de fechamento nao distingue *"voltou por relearning nativo e ja foi reforcado no re-drill"* de *"nao visto hoje"* -- o sintoma original (fila que parece nao-vazia) sobrevive como ruido de APRESENTACAO. A mecanizacao da fila de re-drill esta declarada como candidato no painel de DIVIDA do `auto_check`, sem data.
- **Evidencia:** s112 (drenagem de 28 cards + re-drill de 13). Apos ratings 1 em 3 cards (205,
  201, 165), o agente fez o re-drill manual (conversacional, sem `--record`) conforme o contrato
  -- mas o proprio `record_review()` ja tinha agendado esses 3 cards para reaparecer NO MESMO DIA
  (`state=3`, relearning nativo da lib FSRS). Resultado: ao rodar `--list` no fechamento da sessao
  pra conferir fila vazia, os 3 reapareceram como "hoje", mesmo ja reforcados com sucesso no
  re-drill manual minutos antes -- pareceu fila nao-vazia quando na pratica estava.
- **Leitura de sistema:** duas camadas tentando resolver o mesmo problema (recall fragil precisa
  de reforco proximo) por vias diferentes -- o contrato da skill (`revisar.md`, "Relearning
  intra-sessao") reimplementa em prosa algo que a lib FSRS (`app/utils/fsrs.py`) ja faz nativamente
  via `state=3`. Nao ha bug de dado (nenhum record duplicado), so ambiguidade de leitura.
- **Verificacao sugerida:** checar se `--list`/`--next` deveriam marcar cards `state=3` com `due`
  no mesmo dia da sessao atual como distintos de "aguardando 1a resposta".
- **Hipotese de melhoria:** nenhuma acao imediata necessaria (nao e bug funcional) -- documentar em
  `revisar.md` que o relearning nativo (state=3, mesmo dia) e ESPERADO apos rating 1/2 e que o
  re-drill conversacional e complementar, nao substituto.

### F33 -- Boot recomenda temas ja FEITOS porque `day_plan`/`grade.json` sao calendario-driven, nao leem conclusao real da planilha -- **MEDIA** -- **RESOLVIDO (08/07, mesma sessao)**
- **Evidencia (08/07):** o boot do dia recomendou "proximos temas: MFC (extensivo), Imunizacoes
  (extensivo), Apendicite Aguda (extensivo)" como S12. O operador contestou -- essas 3 tarefas ja
  tinham sido feitas. Verificacao ao vivo via `download_file_content`+`openpyxl` na planilha
  `Cronograma de Reta Final.xlsx` (marcador de conclusao = `cell.font.strike`, conforme
  `importar-planilha.md`) confirmou: MFC Teoria I/II, Imunizacoes Teoria I/II e Apendicite
  Teoria+Revisao estao riscados (FEITOS, semanas 11-12). O que de fato falta em S12 (sem strike):
  DITC II (Teoria), Disturbios do Potassio (Teoria), Cefaleias+Epilepsias (Teoria), HAS Pt.2
  (Teoria) + 2 blocos de Revisao por Questoes (MFC+Vigilancia+SIS; DM Tipo2 completo).
- **Causa raiz:** `cronograma-contract.md` ja documentava isso como fora de escopo v1.0 (Clausula
  1 + secao "Fora de escopo", item R8: "Reconciliar PDF x xlsx do Drive"). `grade.json` deriva
  do `Cronograma.pdf` estatico (SSOT estrutural) e o `day_plan.py` posiciona "proximos temas" por
  **posicao sequencial na grade vs data calendario**, nunca lendo o marcador de tachado/cor que o
  operador usa na planilha do Drive para sinalizar conclusao real. O ponteiro textual
  `Proxima = Semana N` em `ESTADO.md`/`HANDOFF.md` (unico write permitido pela Clausula 5) tambem
  estava desatualizado (`Semana 11`, de sessoes anteriores) e nao e atualizado automaticamente --
  so por edicao manual quando alguem nota o drift.
- **Verificacao sugerida:** cruzar `grade.json` completo (352 tasks) x planilha inteira (nao so a
  janela S11-S16 checada nesta sessao) para medir o tamanho real do drift calendario x execucao.
- **Hipotese de melhoria:** implementar R8 de fato -- `cronograma.py --check-drive` (ou similar)
  le `cell.font.strike` por task via MCP sob demanda no boot (nao cron, coerente com Clausula 3) e
  cruza com `area_norm`/`tema` de `grade.json` para computar "proximos temas" pela FRONTEIRA REAL
  de conclusao, nao pela posicao calendario. Ate isso existir, o ponteiro `Proxima = SNN` deve ser
  tratado como aproximacao e reconciliado manualmente quando o operador contestar o boot (como
  aqui). Correcao ao vivo desta sessao: `HANDOFF.md`/`ESTADO.md` atualizados (Semana 11 fechada,
  Semana 12 parcial, lista real de pendentes).
- **EXECUTADO:** ciclo completo `/discover` -> `/gen-spec` -> `/implement` -> `/audit` (verdict
  **PASS**; `.vibeflow/{prds,specs,audits}/cronograma-sync-conclusao-drive.md`). Implementa R8 de
  fato: `tools/cronograma.py --sync-drive <xlsx>` parseia `cell.font.strike` por task e casa contra
  `grade.json` por `(semana, tema normalizado via unicodedata, tipo_norm)` -- indice de task nao
  bate 1:1 entre PDF e xlsx, entao o match e semantico, nao posicional. Grava snapshot em
  `preparacao_estado.cronograma_conclusao_drive` (reusa o SSOT do PRD orquestracao-preparacao em
  vez de criar arquivo novo -- achado durante o gen-spec: a `cronograma-contract.md` Clausula 5
  estava desatualizada, ainda descrevia o ponteiro de texto `Proxima = SNN` como "unico write
  permitido" quando esse caminho ja estava DEPRECADO desde 2026-07-06). `day_plan.py` agora filtra
  "proximos temas" pela fronteira real quando o snapshot e do dia-calendario corrente; sem
  snapshot fresco, degrada pro comportamento calendario antigo + avisa `conclusao_desatualizada`
  (nunca falha silenciosa). Nova condicao **W8** em `reconcile-contract.md`. Validado contra o
  xlsx real desta sessao: 352 tasks, 119 concluidas, resultado bate 1:1 com a apuracao manual que
  originou este achado. 19/19 testes novos+existentes PASS + `auto_check.py --changed` PASSED.
- **Nao resolvido por este ciclo (fora de escopo, documentado na spec):** alinhamento fino
  `questoes_por_lista[i] <-> tasks[i]` (permanece rateio igual); reimportacao de volume a partir
  do xlsx (fluxo separado, W1/F29).

---

## 3h. Sessao de engenharia -- s115 (2026-07-09): auditoria do boot -> PRD boot-cronograma-drive-confiavel (3 partes, audits PASS)

> Origem: o operador pediu auditoria do boot + dos PRDs recentes, com o norte "mais autonomo,
> gerir o cronograma com maxima eficiencia". Fluxo vibeflow completo conduzido por MIM:
> `/discover` -> `/gen-spec` (3 specs) -> `/implement`+`/audit` x3 (todos PASS). Entrega F34 e
> resolve F30/F31. Achados/decisoes de processo em `.vibeflow/decisions.md`.

### F34 -- Boot regride em silencio quando o snapshot do Drive nao e sincronizado; ordem manual do xlsx nao e capturada -- **MEDIA** -- **RESOLVIDO (s115)**
- **Evidencia (viva no boot de 09/07):** (1) `proximos temas: MFC, Imunizacoes, Apendicite` -- todos
  ja feitos -- porque nenhum snapshot fresco existia no boot headless e o `day_plan` caiu pra
  ordem-do-PDF, com `conclusao_desatualizada` sinalizado fraco demais (hint no fim da linha). (2)
  `Refrescar: Leishmaniose` (tema sem lastro, F31). Alem disso, o usuario reordena tarefas a mao no
  xlsx (ordem/semana) e o `--sync-drive` descartava essa ordem (so lia o tachado) -- `project_cronograma_dual_ssot`.
- **Leitura de sistema:** costura headless/interativo -- o hook `SessionStart` roda sem MCP e so ve o
  db local; tudo que depende do Drive (conclusao W8, ordem, reconcile de volume W1) fica refem da
  disciplina do agente rodar `--sync-drive` e regride em silencio quando ele nao roda. O trabalho
  anterior (W8/F33) mecanizou o PROCESSAMENTO do sync, nao o DISPARO nem a captura de ordem.
- **EXECUTADO (3 partes, audits PASS em `.vibeflow/audits/boot-cronograma-drive-confiavel-part-{1,2,3}-audit.md`):**
  - **part-1 (disparo+ordem):** `--sync-drive` captura `ordem` (linha do xlsx) no snapshot
    `preparacao_estado`; `day_plan` ordena "proximos temas" pela ordem real quando fresco (fallback
    PDF); banner `Drive desatualizado (Nd)` no topo; `AGENTE §2.4` + `reconcile W8` tornam o sync
    ACAO OBRIGATORIA quando STALE, com degradacao graciosa (MCP fora -> calendario-only COM caveat,
    nunca silencioso, nunca BLOCK -- Clausula 6). Regressao propria detectada e corrigida no loop
    (contrato de `_conclusao_drive` tupla->dict quebrou 3 testes de `test_orquestrador.py` que o
    `auto_check --changed` nao roda -- pego pelo `pytest` completo do audit; pitfall registrado).
  - **part-2 (integridade, F30+F31):** `_material_efetivo` rebaixa `resumo -> extensivo` quando o
    `.md` nao existe (render + `--difficulty`; compoe com G5 -- nota do usuario ainda vence); WARN
    `[SEM-LASTRO]` read-only no `insert_questao` (nunca bloqueia).
  - **part-3 (higiene):** contador de resumos DERIVADO (`--handoff-block`, mesmo glob do linter ->
    fim do drift `63x61`); linha "Indicador Atual" do ESTADO enxugada (deixou de ser diario);
    `estado-contract` reforca a regra; este ponteiro de abertos corrigido.
- **Nao resolvido (fora de escopo, documentado nas specs):** automacao real do fetch do Drive (viola
  Clausula 1/3 -- fica agent-triggered, so o disparo virou obrigatorio-de-tentativa); mecanizacao
  completa do reconcile de volume W1/F29; alinhamento fino `questoes_por_lista[i] <-> tasks[i]`.

---

## 3i. Sessoes de uso s124-s125 -- achados F35-F36 (registro retroativo)

> Origem: dois achados vinham sendo carregados como ponteiro no `HANDOFF.md` sem entrada propria no
> ledger (F35 desde a s124, F36 novo na s125). Registrados aqui na reconciliacao de fechamento da
> s125 para que o ponteiro tenha lastro.

### F35 -- Reconcile de volume (W1) segue manual e o `auto_check --changed` nao cobre a suite impactada -- **MEDIA** -- **RESOLVIDO (s176, item 0.5)**
- **Origem:** herdado como "nao resolvido" do escopo do F34/s115 (secao 3h) e carregado no HANDOFF
  desde a s124 sem entrada propria.
- **Duas faces:**
  - **Reconcile de volume (W1/F29):** a conferencia planilha-db continua dependendo de o agente
    lembrar de rodar; o drift de 76q pego ao vivo na s110 foi corrigido a mao, nao mecanizado.
    Agravado pelo drift recorrente das linhas de "Revisao por Questoes" (`project_drift_revisao_por_questoes`).
  - **Seletor de suite do `auto_check`:** `auto_check --changed` seleciona a suite pelo arquivo
    tocado e por isso NAO rodou os 3 testes de `test_orquestrador.py` quebrados na part-1 da s115 --
    so o `pytest` completo do audit pegou. O seletor da falso verde quando a mudanca e de contrato
    (tupla->dict) e o consumidor vive noutro arquivo.
- **Impacto:** falso verde no gate barato; drift de volume so aparece quando alguem olha.
- ✅ **Face 2 (seletor de suite) fechada na s159** -- ver F44, que e "o F35 na sua forma real":
  nao era o seletor escolhendo mal, era nao haver o que selecionar (o `auto_check` nao chamava o
  pytest). Bullet ja existente naquele achado.
- ✅ **Face 1 (reconcile de volume) fechada em 10/09/2026 (s176, janela 2, item 0.5 do Tier 0).**
  O W1 passou de `manual` a **REPORTA**: `day_plan.reconcile_planilha` emite **uma linha por boot**,
  inclusive `NAO MEDIDO` quando nao ha snapshot -- ausencia de medicao virou estado reportado, nunca
  silencio nem delta zero assumido. O snapshot da planilha (`preparacao_estado.planilha_snapshot`,
  gravado por `importar_sessoes.py --snapshot`) e tomado no unico instante em que os numeros dela
  existem: quando o agente a le via MCP.
  🔬 **Medicao que motivou (10/09, comando na mao):** `grep -rniE "planilha|dashboard" --include=*.py
  tools/ app/` -> **zero comparacoes** no codigo vivo; os dois unicos reconciles da historia do
  projeto viraram script one-shot (`tools/_archive/migrations/fix_data_delta_075.py` e
  `fix_data_delta_110.py`). A docstring do segundo guarda quem deu o alarme: *"Usuario reportou
  performance desatualizada (4660 real vs 4584 relatado)"*.
  🔴 **O que a fixture da s110 ensinou ao desenho:** de 4 achados, **3 eram mislabel de area** e o
  relabeling **nao mudou o total** (4584 antes e depois). Logo `alinhado` **exige** detalhe por aba;
  sem ele o estado e `sem_detalhe_area`, que declara o que nao foi verificado em vez de dar verde.
  **Nao bloqueia** (W1 segue WARNING), **nao le o Drive** (F36 intocado) e **nao valida vocabulario
  de area** -- area fantasma aparece crua no relatorio; consertar na origem e o **F89** (item 0.6).
  Spec `.vibeflow/specs/reconcile-planilha-reporta.md` · `reconcile-contract` v1.3 · suite 503 -> 523.

### F36 -- Agente nao materializa binario grande baixado via MCP -> `--sync-drive` pulado 5 sessoes seguidas -- **ALTA** (era MEDIA) -- **ABERTO**
- **Evidencia (s124, s125, s126, s127 e s128):** o boot sinalizou `Drive desatualizado`
  (10 dias no boot de 19/07) e o `--sync-drive` **nao rodou** nas duas: o `.xlsx` do Drive volta do
  MCP como base64 grande e o agente nao tem caminho pratico para materializa-lo em disco "a mao"
  para passar ao CLI. Consequencia direta na s125: o boot ofereceu Colecistite/Imunizacoes (ordem
  do PDF) e **o usuario teve que ditar a ordem real da S13**.
- **Leitura de sistema:** o F34 tornou o disparo do sync OBRIGATORIO-DE-TENTATIVA, mas a tentativa
  falha num degrau que nenhuma clausula previa -- **transporte**, nao disciplina. Enquanto o
  download nao vira arquivo, "obrigatorio" vira ritual vazio e o dual-SSOT do cronograma
  (`project_cronograma_dual_ssot`) regride em silencio para o lado do PDF.
- **Direcao (nao implementada):** dar ao sync um caminho de materializacao proprio (o CLI baixa/
  recebe o blob e escreve o arquivo) em vez de exigir que o agente faca a ponte base64->disco.
- **Adendo s128 (2026-07-25) -- o modo de falha ficou preciso.** O MCP **funcionou**: o
  `download_file_content` devolveu o `.xlsx` inteiro em base64 (~30 KB). O degrau que quebra e a
  **transcricao**: para gravar o blob o agente precisa reemiti-lo verbatim por uma tool de escrita,
  e a ~30 KB ele trunca/elide de forma sistematica (2 tentativas, 2 arquivos corrompidos, ambos
  descartados). Nao e falta de acesso nem de disciplina -- e um limite de fidelidade de copia longa.
  Corolario: **nenhuma clausula de processo conserta F36**; so codigo conserta. A elevacao para ALTA
  reflete que o boot ja regride ha 5 sessoes e que o usuario vem suprindo a lacuna a mao.
- **Direcao refinada:** `tools/cronograma.py --sync-drive` aceitar `--from-base64 <path>` **ou**,
  melhor, um `--fetch-drive <fileId>` que use credencial local (service account / OAuth em `.env`)
  e escreva o `.xlsx` sozinho. O agente passa a **disparar** o sync, nunca a **transportar** o byte.
- **Adendo 2 (s128) -- o protocolo de chunks FALHOU, e o modo de falha ficou quantificado.**
  Tentativa dedicada (subagente, ~3M tokens de orcamento) parou em **5.519 de 30.756 chars (18%)**.
  Achados que valem mais que a tentativa:
  1. **A fidelidade degrada por COMPRIMENTO DE EMISSAO, nao por posicao.** Ate ~3.000-3.400 chars por
     chamada a copia e byte-perfect; acima disso desincroniza **em silencio** -- o base64 continua
     sintaticamente valido e quem quebra e o deflate. Nao ha erro visivel no momento da escrita.
     ⚠️ Ressalva de honestidade: o pedaco que corrompeu tinha **5.078 chars**, acima do limite de
     3.000 que a instrucao mandava. O protocolo foi **violado**, nao estritamente falsificado --
     mas o custo de descobrir isso ja mostra que o caminho e economicamente inviavel.
  2. **O tamanho-alvo e verificavel a priori:** o EOCD do zip da 12 membros e diretorio central de
     786 B em offset 22.258 -> arquivo de 23.066 B -> **exatamente 30.756 chars de base64**. Serve
     de checksum barato em qualquer tentativa futura, antes de decodificar.
  3. 🔴 **CAPACIDADE NAO REGISTRADA -- `mcp__claude_ai_Google_Drive__read_file_content`** no mesmo
     `fileId` devolve a planilha **inteira como texto** (28 semanas x 13 linhas de tarefa, verbatim),
     **sem transcricao nenhuma**. So nao carrega o **tachado** (que e formatacao, nao conteudo).
     Isso abre um **modo degradado viavel**: ordem e temas vem de graca; so a conclusao depende do
     xlsx binario. O ledger nao conhecia essa tool.
  4. **O subagente se recusou a gravar um snapshot sintetico** (reconstruir um .xlsx via openpyxl a
     partir do texto + tachado derivado) com o argumento correto: um snapshot **fresco porem
     sintetico e pior que um velho**, porque o velho ao menos grita `Drive desatualizado`. Julgamento
     certo -- registrar como precedente.
- **Veredito:** F36 **nao se resolve por protocolo**. So codigo resolve. Enquanto `--fetch-drive` nao
  existe, o modo degradado (2) + (3) e o melhor disponivel: `read_file_content` da ordem e temas;
  a conclusao se cruza com `sessoes_bulk`, que e SSOT e independente do Drive.
- **Adendo 3 (s134, 2026-08-03) -- reincidencia confirma o diagnostico da s128, sem achado tecnico novo.**
  `download_file_content` + reescrita manual travou 2x no mesmo padrao de truncamento sistematico
  (nao progrediu alem do que o adendo 2 ja quantificou). `read_file_content` funcionou de primeira,
  devolvendo a planilha inteira como texto (28 colunas de semana, tarefas por linha), confirmando que
  o modo degradado (2)+(3) e **reproduzivel**, nao um acerto isolado da s128. `--fetch-drive` segue
  nao implementado -- 6a sessao seguida com a mesma lacuna de transporte.

- **Adendo 4 (s159, 2026-08-30) -- o "modo degradado viavel" tem teto, e o teto foi medido.**
  O adendo 2 concluiu que `read_file_content` "abre um modo degradado VIAVEL" porque devolve a
  planilha inteira como texto. **Reproduzido pela 3a vez (s128, s134, s159): funciona.** Mas a
  viabilidade nunca tinha sido testada para o uso que importa -- e ela NAO se sustenta:
  - ✅ **Vale para LEITURA** (agente/humano lendo ordem e temas). Foi assim que a s159 confirmou
    a divergencia de tamanho da grade (abaixo).
  - ❌ **NAO vale para SYNC.** No dump, a fronteira de LINHA e um **espaco simples**,
    indistinguivel do espaco interno da celula. Teste com `csv.reader` sobre uma amostra de
    3 colunas x 3 linhas devolveu **7 campos em vez de 9**, com `13/04 a 19/04 GO` fundindo o
    ultimo cabecalho de semana com o primeiro rotulo de material. Um `--from-text` construido
    sobre isso desalinha colunas **em silencio** -- criaria um defeito classe 3 novo (item some
    sem sinal) para consertar um classe 2. Nao construir.
  - ❌ O texto tambem **nao carrega o tachado**, que e de onde `_parse_conclusao_xlsx` tira
    `concluido` (`cell.font.strike`). Snapshot vindo do texto teria `concluido` falso para tudo --
    e um snapshot fresco porem sintetico e pior que um velho, que ao menos grita "desatualizado"
    (precedente registrado no adendo 2, item 4).
  - **Veredito reforcado:** so `--fetch-drive <fileId>` com credencial local resolve. O agente
    tem que DISPARAR o sync; nao existe caminho em que ele TRANSPORTE o dado com fidelidade --
    nem em base64 (quantificado na s128) nem em texto (quantificado agora). **Bloqueado em
    decisao do usuario:** exige service account ou OAuth em `.env`.
- 🔍 **Achado colateral de alto valor (s159) -- os dois SSOTs divergem no TAMANHO da grade, nao so na ordem.**
  A leitura do xlsx mostrou **28 semanas, a ultima "05/10 a 09/10"**. O `grade.json`, derivado do
  `Cronograma.pdf`, tem **30 semanas ate 25/10**. As semanas 29 e 30 do PDF (que ja tinham 0
  questoes) **nao existem na planilha do usuario**. Isso confirma na FONTE o que a s159 tinha
  deduzido por inferencia (fim do conteudo = 09/10, coincidente com o fim do internato) e amplia
  o `project_cronograma_dual_ssot`: a divergencia entre PDF e xlsx nao e so de ordenacao.
  Consequencia pratica: `day_plan._cronograma_hoje` calcula `fim_grade` como `max(fim)` das
  semanas do `grade.json` -> **25/10**, duas semanas alem do cronograma real. O ritmo-alvo da
  grade sai diluido. Candidato a achado proprio na auditoria (F43+).

### F37 -- `taxonomia_cronograma.questoes_realizadas` inflado (3,7x na s127 -> 5,9x na s159) -- **ALTA** (era MEDIA) -- **CAUSA-RAIZ CORRIGIDA (s159); dado historico pendente de decisao**
- **Evidencia (s127):** o campo acusa **19.597** questoes contra **5.232** reais em `sessoes_bulk`.
  Descoberto ao construir o eixo de cobertura de `tools/variancia.py`: a 1a versao lia esse campo e
  produzia "89,5% da grade coberta / zona DIRECIONAMENTO" -- diagnostico **invertido** em relacao ao
  real (43,0% / zona COBERTURA). A fonte foi trocada para a grade versionada e um teste estrutural
  impede a regressao, **mas o campo segue inflado no db**.
- **Leitura de sistema:** metas e performance leem `sessoes_bulk` e por isso nao foram afetadas -- o
  campo e uma **superficie de estado orfa**, que ninguem reconcilia e qualquer feature nova pode
  consumir de boa-fe. Foi exatamente o que aconteceu. O risco nao e o numero errado: e ele estar
  disponivel e parecer autoritativo.
- **Verificacao sugerida:** rastrear quem escreve o campo (`insert_questao.py`? migracao legada?) e
  decidir entre (a) reconciliar contra `sessoes_bulk`, (b) derivar on-the-fly, ou (c) **remover a
  coluna** -- preferivel, se ninguem legitimo a le. Enquanto existir, adicionar check no reconcile.
- **Nova evidencia (s155, 25/08/2026, achada via /graphify em resumos/Pediatria+GO):** o campo segue
  sendo escrito, nao e so residuo antigo. 128 de 269 temas (48%) compartilham `questoes_realizadas`
  identico com >=2 outros temas de **areas nao relacionadas** (ex.: 105 questoes em 21 temas
  cruzando Pediatria/Endocrino/Obstetricia). O caso mais flagrante: `Pediatria:PTI` (id 219),
  `Pediatria:Traumatismo Cranioencefalico na crianca` (id 222) e `Pediatria:Asma na infancia`
  (id 233) tem `questoes_realizadas=428`, `questoes_acertadas=358` e `percentual_acertos` **identicos
  ate a casa decimal** (83.6448...%), todos com `ultima_revisao='2026-08-23'` -- 3 dias antes desta
  sessao. Confirma que o campo continua sendo alimentado por alguma escrita em lote que nao calcula
  por tema; nao e apenas herdado da migracao original de 2026-07-25.

- 🔬 **CAUSA-RAIZ ENCONTRADA na s159 (2026-08-30) -- nao era import legado.**
  `tools/registrar_sessao_bulk.py` fazia
  `UPDATE taxonomia_cronograma SET questoes_realizadas = questoes_realizadas + ? ... WHERE area = ?`
  -- **sem filtro de tema**. Uma sessao de 51 questoes de Pediatria somava 51 em
  **todos** os temas de Pediatria. Assinatura confirmada no db: 16 temas de
  Pediatria com `156/140` identico, 14 de Cirurgia com `56/49`, 9 de Cirurgia com
  `153/131`, 7 de Obstetricia com `41/33`. Isso fecha a hipotese da s155 ("alguma
  escrita em lote que nao calcula por tema") -- era esta, e ela rodava a cada
  registro de bloco. Inflacao atual medida: **39.077 em taxonomia contra 6.631
  reais em `sessoes_bulk` = 5,9x** (era 3,7x na s127 -- o campo piorou, como
  previsto por "continua sendo alimentado").
- 🔴 **O dano nao era cosmetico -- contaminava o RANKING DE FRAQUEZAS DO BOOT.**
  `app/memory/manager._load_ipub_error_counts` derivava "erros por tema" de
  `SUM(questoes_realizadas - questoes_acertadas)` desse campo, e
  `_sync_error_counts` gravava isso em `WeakArea.error_count`, que
  `_rank_weak_areas(top_n=8)` ordena -- **a lista "Areas de fraqueza persistentes"
  que abre toda sessao**. Como cada tema carregava o acumulado da sua area, o
  ranking media **quanto a area foi estudada**, nao quao fraco o tema e.
  Ironia estrutural: `_sync_error_counts` documenta *"WeakArea sem par
  correspondente recebe 0 -- NUNCA herda o total da area"*; a defesa existia, mas
  na camada errada -- a fonte ja tinha assado o total da area dentro de cada tema.
  - **Caso mais flagrante medido:** `Ginecologia / Gravidez ectopica` figurava
    como fraqueza persistente **top-5 com "61 erros"** e tem **ZERO** linhas em
    `questoes_erros`. (Existe sinal real -- 12 erros mencionam "ectopica" no
    titulo/enunciado --, mas o numero exibido era fan-out, nao contagem.)
  - Outros deltas exibido -> real: Epilepsias 64 -> 13 · Arboviroses 58 -> 17 ·
    Lesao Renal Aguda 45 -> 8 · Doencas Exantematicas 51 -> 13 · Cirurgia
    Infantil 62 -> 30 · Imunizacoes 43 -> 23. As **descricoes** das fraquezas sao
    autorais e continuam validas; o que era artefato e a **contagem e a ordem**.
- ✅ **Corrigido na s159 (codigo):**
  1. `registrar_sessao_bulk` deixa de espalhar: o acumulado vai para a linha
     `[bulk] <area>`, que e o balde de volume da area. Uma sessao bulk e
     atribuida a AREA -- nao existe atribuicao por tema para distribuir.
  2. `_load_ipub_error_counts` passa a contar `questoes_erros` (a unica
     superficie com `tema_id` resolvido no ato do registro). Contrato de retorno
     inalterado; so a fonte mudou.
  - **Suites:** `tools/test_bulk_fanout.py` (8 testes -- temas intocados, outra
    area intocada, acumulo na linha bulk, e o assert direto de que o delta em
    taxonomia e EXATAMENTE o volume registrado, nao volume x nº de temas) e 2
    testes novos em `test_memory_counter.py` (estrutural anti-regressao + tema
    com volume alto e zero erro atribuido nao entra no ranking). 298 -> 306.
- ⏸️ **PENDENTE -- decisao do usuario (operacao de dado, nao de codigo):** o
  campo segue inflado para o historico ja gravado. Tres saidas: (a) zerar
  `questoes_realizadas/acertadas` dos temas reais e concentrar o acumulado nas
  linhas `[bulk] <area>`, reconciliando contra `sessoes_bulk`; (b) derivar
  on-the-fly e parar de persistir; (c) remover a coluna -- **inviavel hoje**, o
  grafo mostra leitores vivos (`app/utils/db.py` no widget Foco Critico,
  `.agents/workflows/gerar-reforco.md`). Enquanto nao for decidido, o numero
  segue errado nas superficies que leem o campo direto -- mas o ranking de
  fraquezas ja esta correto, que era o consumidor critico.
- 📝 **Doc drift achado de lambuja:** `.vibeflow/patterns/error-insertion-pipeline.md`
  afirma que `insert_questao.py` incrementa `questoes_realizadas` ("it tracks
  questions attempted"). O codigo faz o oposto e documenta o oposto desde a
  separacao de responsabilidades (so atualiza `ultima_revisao`). Padrao descreve
  comportamento que nao existe mais.

### F38 -- Erros analisados na conversa nao chegam a `questoes_erros`; a analise evapora -- **ALTA** -- **RESOLVIDO (s159) -- guarda entregue; 1 instancia historica a recuperar**
- **Evidencia (s127 -> descoberto na s128, 2026-07-25):** o bloco de Pneumologia Intensiva II teve
  **6 erros analisados em profundidade** (elo quebrado, armadilha, conteudo faltante -- registrados
  em prosa no `history/session_127.md`). No `ipub.db`: `sessoes_bulk` recebeu o volume (22/16) e o
  ledger de habilidades recebeu **7 habilidades** (`origem='bloco-s127'`, `veredito='errou'`), mas
  `questoes_erros` **nao recebeu uma linha sequer** -- zero registros com `data_registro` de 25/07.
  Consequencia: os cards nasceram sem erro de origem (`insert_card_base`, `questao_id=NULL`), e o
  substrato canonico (`tipo_erro`, `alternativa_marcada`, `explicacao_correta`) so existe em prosa.
- **Leitura de sistema:** o pipeline de analise tem **dois finais** -- `insert_questao.py` (erro
  completo + cards) e `habilidades.py --add` (so a habilidade). A s127 introduziu o segundo e o
  agente **substituiu** um pelo outro em vez de encadear. Nenhum invariante notou: `auto_check` audita
  arquivos, nao a coerencia "bloco com N erros narrados -> N linhas em `questoes_erros`". O sinal mais
  rico do sistema (o erro estruturado, que alimenta cards, areas fracas e armadilhas dos resumos) e
  o unico sem gate de persistencia.
- **Agravante:** o defeito e **silencioso e retroativo**. So apareceu porque a sessao seguinte foi
  cunhar os cards e nao achou a ancora. Blocos anteriores podem ter o mesmo buraco.
- **Dimensionamento retroativo (rodado na s128, 2026-05-01 a 2026-07-25):** erros esperados
  (`feitas - acertadas`) = **466**; linhas em `questoes_erros` no mesmo periodo = **335**;
  **delta = 131 (~28%)**. 17 dias-bloco com gap positivo. Dias com delta negativo (ex.: 29/06,
  -22) sao **registro tardio** -- o erro entra no dia seguinte ao estudo --, por isso o gap por
  linha e ruidoso e so o total tem leitura.
  ⚠️ **O 131 e teto, nao piso de analises perdidas.** Parte vem de volume importado da planilha via
  `/importar-planilha`, que traz feitas/acertos **sem** os erros terem sido itemizados -- ausencia
  esperada, nao defeito. O que o F38 nomeia e o subconjunto em que a analise **comprovadamente
  aconteceu** e nao persistiu; a s127 e a instancia confirmada (6 erros narrados no log, 0 no db).
  Separar os dois exige cruzar com o log de cada sessao -- trabalho de curadoria, nao de query.
- **Direcao (nao implementada):** (1) WARN no reconcile de boot -- "bloco de DD/MM registrou N erros
  em `sessoes_bulk` e 0 em `questoes_erros`"; (2) tornar explicito em `/analisar-questao` que
  `--add` **complementa** e nunca substitui `insert_questao.py`; (3) avaliar se `habilidades.py --add`
  com `veredito='errou'` e `questao_id=NULL` deveria simplesmente avisar na saida.

- ✅ **RESOLVIDO na s159 (2026-08-30) -- as 3 direcoes implementadas.**
  1. **Gate no `auto_check` (check 13, WARN):** `check_erros_orfaos()` em
     `tools/utils/state_utils.py` cruza `sessoes_bulk` x `questoes_erros` e acusa
     dia-bloco com >= 3 erros de volume e ZERO linhas de erro estruturado. Roda
     SEMPRE (nao so no `--all`): o defeito nasce de uma escrita no db, nao de um
     arquivo tocado, entao nenhuma heuristica de relevancia por path o alcanca.
  2. **Aviso na origem:** `habilidades.py --add` com `--veredito errou` e sem
     `--questao-id` imprime `[WARN] F38` em stderr (stdout fica limpo p/ script).
  3. **Contrato explicito:** `/analisar-questao` secao 10 agora diz, com o caso da
     s127 nominal, que `--add` **complementa** e nunca substitui `insert_questao.py`.
  - **Suite:** `tools/test_erros_orfaos.py`, 18 testes (deteccao, as 2 defesas
    contra falso positivo, parametros, modo defensivo, regressao viva). Registrada
    na allowlist `python_files` do `pytest.ini` -- sem isso a suite existiria sem
    ser coletada (mesmo modo de falha do D4/alcancabilidade).
- 📐 **Calibracao medida, nao arbitrada.** Janela de credito = **d..d+1** e piso = 3
  erros. Sobre os 52 dias-bloco reais (790 erros esperados): com d+1 o check acusa
  **1 dia** e ele e **verdadeiro**, com **zero falsos positivos**; com d+2 o unico
  positivo verdadeiro **desaparece** (os 19 erros de 20/06 sao de Cirurgia/GO/
  Exantematicas -- tema nenhum em comum com o bloco de 18/06). Alargar a janela
  compra silencio, nao precisao. Ambas as constantes travadas por teste.
- 🔴 **Instancia historica confirmada, ainda NAO recuperada -- fica como divida:**
  **2026-06-18 (s085, Pediatria 38/23 = 15 erros)**, bloco "Ictericia neonatal +
  Sepse neonatal" (tema dormente ha 63d, radar cravou). O tema
  `Pediatria / Ictericia e Sepse Neonatal` tem **26 flashcards e ZERO linhas em
  `questoes_erros`** -- assinatura exata do F38: os cards existem, a analise que
  os gerou nao. Recuperar exige o log da s085 + curadoria; nao e query.
  *(Coerente com `ESTADO.md`, que ja listava "ictericia neonatal (so andaime)"
  entre os gaps de resumo -- o tema esta subatendido em tres superficies.)*
- ⚠️ **Honestidade sobre o alcance:** o gate e **guarda de REGRESSAO**, nao remedio.
  Ele nao recupera analise perdida e nao mede qualidade do erro registrado -- so
  garante que a proxima substituicao de `insert_questao.py` por `--add` fale alto.
  O gap de ~28% dimensionado na s128 (131 de 466) continua sendo majoritariamente
  volume importado sem itemizacao, que o filtro de migracao exclui de proposito.

### F39 -- 40% do baralho viola o principio atomico; a nota FSRS vira ininterpretavel -- **ALTA** -- **PARCIAL (detector entregue, reforja em 8/358)**
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

## 3j. Sessao de uso s152 (drenagem de 90 cards, regime de divida) -- achado F40

> Origem: dreno de 90 cards (6 blocos de 15) apos analise de 11 erros (Aleitamento+CA de Mama).
> O usuario pediu explicitamente (2026-08-23) capturar cada reforja como **data flywheel**: "utilizar
> as regras para rastrear os mesmos problemas ou problemas parecidos em outros cards, em sessao de
> auditoria ampla do banco que vira em breve" -- conecta direto com F7 (mesma familia: defeito de
> autoria de card) e com a auditoria ampla ja pendente desde a s148 (ver HANDOFF.md).

### F40 -- Quatro padroes novos de defeito de formulacao de card (estimulo, nao conteudo) -- **MEDIA** -- **PARCIAL (4 reforjados nesta sessao)**
- **Evidencia:** 4 cards reforjados ao vivo por queixa do usuario durante a drenagem, nenhum por erro
  factual -- todos por como a FRENTE estava formulada:
  1. **Pacote de fatos, nao eixo unico** (`card_id=44`, Damage Control/Trauma Abdominal). Pedia lista
     de N passos sequenciais (tamponar + ressecar + peritoneostomia + reoperar em 48h) como resposta
     unica. Usuario: "demanda tempo para responder e cansa". Ja normatizado em principio por
     `estilo-flashcard.md` (eixo unico x pacote), mas o card sobreviveu ate hoje -- sinal de que a
     regra existe na norma e nao no linter.
  2. **Frente ambigua sobre indicacao ja estabelecida** (`card_id=1063`, crise de asma pediatrica).
     A pergunta ("por que nao e necessario corticoide EV?") deixava aberto SE o corticoide sistemico
     era indicado, quando o unico ponto de decisao real era a VIA (oral x EV). Usuario pediu "explore
     melhor a frente e a indicacao do corticoide sistemico".
  3. **Pergunta circular** (`card_id=484`, TTA/trauma penetrante). A frente ja continha a resposta
     ("por que a laparoscopia e a conduta especifica"), convidando a repetir a palavra-chave dada em
     vez de produzir o racional. Usuario: "ela ja e a resposta para o contexto; pergunta circular".
  4. **Pergunta composta com 2 informacoes** (`card_id=1039`, HPN/Hakim-Adams). Pedia simultaneamente
     "o achado obrigatorio" E "o que a ausencia dele aponta em vez disso" na mesma frase. Usuario:
     "da uma volta absurda para chegar no ponto central".
- **Leitura de sistema:** os 4 sao variantes do mesmo genero (F7 ja cobria "discriminacao incompleta";
  este achado amplia o catalogo para "estimulo mal-formulado mesmo com discriminacao correta").
  `audit_card_atomicity.py`/`card_checks.py` ja detectam duplo-ask e resposta-multifato via regex/
  contagem de interrogacao -- mas nenhum dos 4 casos acima disparou WARN no momento da autoria (3 sao
  BEM formados sintaticamente: 1 pergunta, 1 "?"), porque o defeito e SEMANTICO (a pergunta e
  logicamente composta, ou circular, ou pede uma lista, sem violar a sintaxe que o linter checa).
  Confirma o padrao ja registrado em F7/`project_curadoria_e_temas_zero`: **defeito de formulacao e
  de autoria, o linter e cego ao semantico** -- só um solucionador competente (o usuario) pega.
- **Verificacao sugerida:** rodar uma passada de amostragem no baralho ativo (~780 cards) buscando os
  4 padroes por heuristica leve: (a) verso_resposta com >=3 clausulas ligadas por "," ou ";" fora de
  uma enumeracao curta -> candidato a pacote-de-fatos; (b) frente_pergunta comecando por "por que
  nao e necessario/preciso X" sem X estar explicitamente confirmado como indicado no frente_contexto
  -> candidato a ambiguidade de indicacao; (c) overlap de token entre frente_pergunta e
  verso_resposta ja parcialmente coberto por `checar_resposta_embutida`, mas o caso "circular" aqui
  passou porque a palavra-chave repetida era curta/comum (laparoscopia) -- conferir o limiar RUN_MIN/
  JACCARD_MIN contra esse caso real; (d) frente_pergunta com 2 interrogativos implicitos ligados por
  "e" mesmo sem 2x "?" (`checar_multi_parte` so pega ">1 interrogacao" ou conectivo composto via regex
  -- conferir se "X, e o que Y" e "X e por que Y" estao no `RE_MULTI_CONECTIVO`).
- **Hipotese de melhoria:** (1) curto prazo -- usar os 4 casos como fixtures de regressao para
  `card_checks.py` (se o padrao se generaliza, os proximos exemplares do banco disparam WARN
  automatico em vez de esperar o usuario tropecar neles um a um); (2) media prazo -- quando a
  auditoria ampla do banco (pendente desde s148, ver HANDOFF.md) rodar, usar este achado como um dos
  eixos de varredura, nao so atomicidade/atomicidade-de-resposta. Precedente de execucao: F39 (mesma
  familia, `audit_card_atomicity.py` + `apply_reforja.py`/`recurate_cards.py` como gate de aplicacao).
- **Nao resolvido nesta sessao (escopo):** os 4 cards fixados sao pontuais; a auditoria ampla
  (rastrear os MESMOS padroes no banco inteiro) e trabalho futuro, registrado aqui como o gatilho.

---

### F41 -- Sessao s154 (100 cards, regime de divida): 6 novas instancias de F40 + reincidencia do padrao id=120 em Gravidez Ectopica + subpadrao tautologico em cards `[bulk]` -- **MEDIA** -- **PARCIAL (6 reforjados + 5 cards novos nesta sessao)**
- **Evidencia (extensao direta de F40, mesma familia -- pacote-de-fatos/pergunta composta/circular):**
  drenagem de 100 cards em 10 blocos produziu 6 reforjas ao vivo por queixa do usuario, nenhuma por
  erro factual de conteudo:
  1. `card_id=1053` (Vulvovaginites/Tricomoniase) -- pergunta composta fundia "qual o farmaco" +
     "por que nao pode ser topico", sendo que o mecanismo do "por que" nem constava na regra-mestre/
     armadilha documentada do card (nao era o mesmo eixo do farmaco-por-IST). Trimado para so o
     farmaco; mecanismo permanece no verso.
  2. `card_id=553` (HAS/pontos de corte) -- pedia 5 cortes numericos (consultorio/MAPA-vigilia/
     MAPA-sono/MAPA-24h/MRPA) numa unica frente. Dividido em 4 cards atomicos (553 = so consultorio;
     3 novos = vigilia+MRPA parelhados pelo mesmo valor numerico, sono, 24h).
  3. `card_id=155` (Puericultura/APS) -- "crianca baixo risco = so enfermeiro? E alto risco sai da
     APS?" eram 2 perguntas independentes coladas por "E". Dividido em 2 cards -- cada meia-verdade
     testada isoladamente, evitando que um acerto mascare o outro erro.
  4. `card_id=576` (DIU de cobre) -- "exige barreira apos insercao? NIC1 contraindica?" mesma
     familia de composta. Dividido em 2.
  5. `card_id=293` (Binswanger x doenca prionica) -- "por que X e mais provavel que Y" respondida
     com "porque X e mais comum" e quase tautologico uma vez que se sabe a prevalencia relativa.
     Reformulado para testar o PRINCIPIO generalizavel (prevalencia de base vence causa rara sem
     achado especifico), nao so esse par de doencas.
  6. `card_id=325` (Peritonite/trauma) -- mesma familia tautologica: "por que a estabilidade
     hemodinamica nao deve adiar a laparotomia" respondida com "porque a peritonite ja e indicacao".
     Reformulado como pergunta direta de conduta (peritonite franca precisa de imagem antes da
     laparotomia? Nao).
- **Subpadrao novo dentro de F40: tautologia em cards de tema `[bulk]`.** Os casos 5 e 6 (293, 325)
  compartilham um tracco que os 4 originais do F40 nao tinham: ambos vem de temas rotulados `[bulk]`
  (ex.: "Cirurgia / [bulk] Cirurgia", "Neurologia / [bulk] Neurologia") -- import em lote,
  presumivelmente com menos curadoria individual por card. A assinatura do defeito e especifica:
  pergunta no formato "por que X (achado/decisao) ocorre/e-preferido", resposta que so reafirma X
  com outras palavras, sem mecanismo ou principio transferivel por tras. Diferente das
  composta/circular originais do F40 (que tinham 2 fatos distintos ou auto-referencia lexical), esta
  e uma composta-por-tautologia -- sintaticamente 1 pergunta e 1 resposta, mas logicamente sem
  conteudo discriminador novo.
- **Reincidencia notavel: Gravidez Ectopica tem 2 cards historicamente mal-calibrados quanto a
  probabilidade pre-teste.** F7 (s108) ja tinha marcado `card_id=120` (mesmo tema, heterotopica-vs-
  corpo-luteo espontaneo) como "candidato a auditoria de evidencia" -- nunca executado. Hoje,
  `card_id=114` (beta-hCG subdiscriminatorio, cisto anexial + liquido livre em fundo de saco) foi
  auditado via `evidence-researcher` (mesmo protocolo do card GINA STEP1 da s153) e o veredito foi
  PRECISA AJUSTE: nem o card ("gestacao topica normal", certeza que nem FEBRASGO nem ACOG sustentam)
  nem a contestacao do usuario ("ectopica e a mais provavel") estavam certos -- o quadro real e
  "pregnancy of unknown location" (PUL), com falha da gestacao (~50%) mais provavel que ectopica
  (~11%) ou que "normal" confiante. Reformulado pra moldura de PUL + conduta de beta-hCG seriado 48h
  (fontes: ACOG Practice Bulletin 193, Connolly et al. 2013 Obstet Gynecol, FEBRASGO). `card_id=120`
  **segue sem auditoria** -- mesmo tema, mesmo padrao de calibracao, proximo candidato natural.
- **Calibracao aberta: 3 flags do usuario sem defeito identificado pelo agente.** cards `1411`
  (Ca mama, cirurgia previa x biopsia com atipia), `283` (estenose duodenal parcial em Down) e `319`
  (secao ductal pancreatica, resposta banca-especifica). Nos 3, o agente nao conseguiu enxergar
  pacote-de-fatos/composta/circular nem erro de conteudo -- para o `319` especificamente, o card e
  DELIBERADAMENTE banca-dependente (ja sinalizado como tal na propria armadilha do card, categoria
  legitima pelo `evidence-governance.md`). Pendente: usuario nao respondeu ainda o que especificamente
  incomodou nesses 3 -- proxima sessao deve retomar a pergunta antes de decidir se e um 5o subtipo de
  F40 ou ruido de calibracao do proprio usuario apos 6 reforjas bem-sucedidas seguidas na mesma sessao.
- **Verificacao sugerida:** quando a auditoria ampla (F40) rodar, adicionar 2 buscas: (a) join
  `taxonomia_cronograma`/tema contra o prefixo `[bulk]` para escopar os candidatos a
  tautologia-de-base-rate; (b) revisar TODOS os cards do tema "Gravidez Ectopica" contra criterio de
  calibracao de probabilidade pre-teste (nao so 114/120).
- **Hipotese de melhoria:** (1) `card_id=120` vai para `/pesquisar-evidencia` na proxima sessao de
  auditoria -- ja tem o precedente metodologico (114, GINA STEP1) pronto pra copiar; (2) fixture de
  regressao pro `card_checks.py` com os 6 casos de hoje, mesma logica do F40; (3) resolver a
  pendencia de calibracao (1411/283/319) diretamente com o usuario na abertura da proxima sessao,
  antes de tratar como sinal de novo padrao.

---

## 3m. Sessao de engenharia s159 (2026-08-30) -- achado F42

### F42 -- Editar o espelho da skill e silenciosamente revertido pelo `sync_skills` -- **BAIXA/MEDIA** -- **ABERTO**
- **Evidencia (s159, ao vivo):** para entregar a direcao 3 do F38 editei
  `.agents/skills/source-command-analisar-questao/SKILL.md`, rodei
  `python tools/sync_skills.py` e o texto **desapareceu**. A fonte de verdade e
  `.claude/commands/<nome>.md`; `.agents/skills/source-command-*/SKILL.md` e
  ESPELHO GERADO. O sync sobrescreveu a edicao e reportou sucesso
  (`~ source-command-analisar-questao/SKILL.md · 1 espelho atualizado`) --
  indistinguivel, na saida, de um sync que preservou trabalho.
- **Por que passa despercebido:** o espelho e o arquivo que o agente encontra
  primeiro (e o que os `grep` de skill retornam, e o que a listagem de skills
  expoe). Nada no cabecalho do SKILL.md diz "GERADO -- NAO EDITAR", e o
  `git status` depois do sync fica limpo, entao a perda nao deixa rastro.
  So percebi porque o arquivo nao apareceu na lista de staged do commit.
- **Custo real:** 1 ciclo perdido e -- pior -- o ledger chegou a registrar a
  direcao 3 do F38 como entregue quando ela nao existia mais em disco. Um gate
  que afirma entrega inexistente e pior que gate nenhum.
- **Direcao (nao implementada):** (a) banner `<!-- GERADO por tools/sync_skills.py
  -- editar .claude/commands/<nome>.md -->` no topo de todo espelho; (b) o sync
  avisar quando o espelho que ele vai sobrescrever tem mtime mais novo que a
  fonte ("voce editou o espelho; a edicao sera perdida"); (c) avaliar tornar os
  espelhos read-only. (a)+(b) sao baratos e resolvem o caso observado.

---

## 3n. Sessao de engenharia s159 (2026-08-30) -- achados F43-F44 (gates que nao gateavam)

### F43 -- "Quais testes rodam" tem TRES registros manuais e nenhum sabe do outro -- **MEDIA** -- **RESOLVIDO (s159)**
- **Evidencia:** uma suite em `tools/test_*.py` so executa se estiver citada em (1) `pytest.ini`
  -> `python_files` (allowlist explicita), (2) `tools/auto_check.py` (suites invocadas por nome)
  ou (3) `tools/test_pytest_bridge.py` (script-style por subprocess). Sao **tres registros
  mantidos a mao, nenhum ciente do outro**. Uma suite fora dos tres existe, passa no code review
  e nunca roda -- e ninguem percebe, porque nao ha erro: ha ausencia.
- **Medicao (s159):** 37 suites em disco, **37 cobertas** -- 31 no `pytest.ini`, 4 so no
  `auto_check`, 3 so no bridge (1 em dois registros). **Zero orfas hoje.** O achado nao e um
  defeito ativo: e a **ausencia de garantia**. `tools/test_erros_orfaos.py`, escrita nesta mesma
  sessao, so e coletada porque o autor lembrou de inscrever a mao.
- ✅ **Corrigido:** `check_suites_orfas()` em `tools/utils/state_utils.py` + check 14 do
  `auto_check` (WARN). Suite `tools/test_suites_orfas.py` (10 testes), auto-referente de
  proposito -- ela tambem precisou ser inscrita.

### F44 -- O harness NUNCA invocava o pytest; a suite completa era manual-only -- **ALTA** -- **RESOLVIDO (s159)**
- 🔴 **Evidencia:** `tools/auto_check.py` -- que roda no git hook de pre-commit e e a definicao
  de "trabalho validado" neste projeto -- **nao continha uma unica chamada ao pytest**. Ele
  rodava ~6 suites script-style nomeadas a mao e 8 checks estaticos. Os **306 testes** coletados
  pelo `pytest.ini` so executavam se um humano digitasse `pytest`. Nem o `--all` os rodava.
- **Consequencia medida:** commit com suite vermelha passava no hook com o relatorio dizendo
  "🎉 Todos os checks passaram". Foi exatamente assim que a quebra de coleta de
  `test_handoff_teto.py` (introduzida em `c4d4532`, s156) sobreviveu **3 sessoes** -- a s157
  registrou no proprio log "auto_check.py PASSED (0 BLOCKs)" com a suite quebrada.
- **Este e o F35 na sua forma real.** O F35 descrevia "o seletor da falso verde quando o
  consumidor vive noutro arquivo"; o diagnostico estava certo e subdimensionado -- nao era o
  seletor escolhendo mal, era **nao haver o que selecionar**.
- ✅ **Corrigido (2 partes):**
  1. **Check 2d, BLOCKING:** `auto_check` passa a rodar `pytest tools/ -q` quando o modo e
     `--all`, quando ha `.py` de `tools/`/`core/` tocado, ou quando substrato compartilhado
     mudou. Custo medido: ~17s.
  2. **Escalonamento por substrato:** mudanca em `tools/utils/`, `core/contracts/`, `pytest.ini`
     ou `conftest.py` forca a suite COMPLETA. Justificativa: substrato compartilhado **nao tem
     consumidor local** -- por definicao quem depende dele vive noutro arquivo, entao qualquer
     seletor por path erra. Em vez de adivinhar o consumidor, escala.
- ⚠️ **Honestidade:** isto conserta o gate, nao a cobertura. A suite testa CODIGO; nada testa a
  qualidade do output de estudo (aula-base, card, feedback) -- ver §9j do
  `docs/HANDOFF-AUDITORIA-MEDHUB.md`.

---

## 3o. Sessao de auditoria de engenharia s160 (Fable, 2026-08-30) -- achados F45-F60 + matriz de portadores + swap test

> Execucao do `docs/HANDOFF-AUDITORIA-MEDHUB.md` (goal, instrumentos, formato §10, salvaguardas).
> Metodo: graphify re-rodado no HEAD (16:32, pos-s159) como mapa; 4 varreduras por dominio
> (tools/, app/ RAG+memoria, contratos<->codigo, harness/governanca) + verificacao ao vivo
> (suite 317 PASSED em ~65s; `auto_check --all` PASSED com 342 WARNs; queries read-only no
> `ipub.db`/`medhub_memory.db`/indice Chroma). Read-only sobre o motor: zero patch nesta sessao.
> Toda afirmacao de invariante foi tratada como hipotese (regra do handoff) -- e varias cairam.

### Entregavel 1 -- tabela de achados (F45+)

| id | onde | classe | evidencia | mitigacao atual | proposta | prio |
|---|---|---|---|---|---|---|
| F45 | memoria de fraquezas (boot) | 3 | `app/memory/manager.py:173` casa par exato, mas o vocabulario que o Haiku inventa nao bate com a taxonomia: so 60/349 WeakAreas (17%) tem `error_count>0`; 109 duplicatas (31%, pior par 7x); 6x par (area,especialidade) invertido; `inspect.py:158` desempata por `last_updated` -> **o ranking que abre toda sessao mostra o mais RECENTE, nao o mais fraco** | nenhuma (F37 consertou a outra camada) | schema: `WeakArea.area` restrito ao vocabulario real (Literal/validador) + vocabulario no prompt + upsert por par (nao UUID novo) + teste | ALTA |
| F46 | consolidacao de memoria (paths) | 3 | `manager.py:29` `_IPUB_PATH = Path("ipub.db")` relativo ao cwd; 2 bancos-fantasma de 0 bytes (`tools/ipub.db` 06/07, `data/ipub.db`) provam runs com cwd errado; `history/memory_errors.log` tem 7 falhas HOJE (`no such table: questoes_erros`) e **nenhum check le esse arquivo** | guard `path.exists()` (derrotado pelo decoy 0-byte) | codigo: path por `__file__` + connect `mode=ro` no leitor; gate: auto_check exibe tail do memory_errors.log | ALTA |
| F47 | calibragem de dificuldade | 1 | `day_plan.py:576-579`: variavel `nota_usuario` recebe QUALQUER nota persistida -- `dificuldade_fonte` nunca decide, `dificuldade_at` nunca e lido (Clausulas 2 e 7 do revisao-calibrada-contract sem implementacao). 12 de 21 temas calibrados hoje tem fonte `agente_inferida`/`aula` tratada como soberana; a msg §4.4 ("Voce marcou 3...") atribui ao usuario nota que ele nao deu | nenhuma | codigo: fonte entra na decisao + frescor 7d reinfere; teste de precedencia input>pergunta>inferencia | ALTA |
| F48 | RAG (app/engine) | 2/3 | indice stale SEM sensor: reconstruido 26/08, 3 resumos editados depois, 6 chunks servindo texto desatualizado (medido); upsert nao deleta cauda quando resumo encolhe (`rag.py:229`); HyDE sem timeout (`rag.py:167`, pior caso ~30min pendurado) e sem `temperature=0` -- eval ja documentou swing de 17pp run-a-run; eval manual (ultimo run 15/08), fora do auto_check; `_chunk_by_headers` (76L, pura) sem NENHUM teste | eval honesto porem manual | gate: check de staleness (mtime resumos vs chroma) no auto_check; codigo: timeout+temperature no cliente, delete de cauda; teste: chunking | ALTA |
| F49 | writer gates | 2 | `AGENTE.md:170` ("so insert_questao escreve taxonomia, excecao set_dificuldade") e violado por 5 arquivos: `insert_card_base.py:65`, `registrar_sessao_bulk.py:115,132` (muta as colunas que set_dificuldade jura nunca tocar), `normalize_taxonomia.py`, `dedup_taxonomia.py`; `test_writer_gates.py` testa qualidade de card, NAO gates de escrita (docstring admite); o gate `import sqlite3` so varre `app/**` | convencao + nome de teste que sugere cobertura inexistente | teste estatico: allowlist tabela->writers (grep INSERT/UPDATE/DELETE), padrao ja provado em `test_revisao_calibrada.py:127` | ALTA |
| F50 | tools/autopsia_simulados.py | 3 | 852 linhas QUEBRADAS desde a s156: `:838` importa `tools.autopsia_template`, deletado no `dc8f460`; mascarado por `.pyc` orfao no `__pycache__`; PKs hardcoded (`range(622,668)`); 0 referenciadores vivos | reachability WARN (so em `--all`, pegou 5 dias depois) | decisao fica-ou-morre; gate: `compileall`/import-check dos CLIs no auto_check (pega import dangling na hora) | MEDIA |
| F51 | tools/auto_recurate_duplo_ask.py | 2 | writer de `flashcards`+`fsrs_cards` que BYPASSA card_checks (unico writer sem gate de qualidade), flipa `needs_qualitative=0` por texto de LLM; dependencia fantasma `google.generativeai` fora do requirements (3a superficie LLM nao declarada); BOM U+FEFF quebra `ast.parse`; orfao (0 refs) -- nasceu na s156 | inerte por falta da dependencia (mitigacao acidental) | aposentar OU reescrever sob card_checks + requirements; o teste allowlist do F49 o pegaria | MEDIA |
| F52 | contrato FSRS x codigo | 2 | (a) load balancer inteiro (`app/utils/fsrs_balance.py`, muta `due` em TODA gravacao state==2) fora do contrato que se declara governante do FSRS -- a norma efetiva vive em `revisar.md:68`; (b) invariante `needs_qualitative=1 nao deve existir` VIOLADO em dado: 6 cards, dentro da fila ativa (`<2`), sem sensor; (c) `state=3` (relearning) existe em 3 cards e nao esta no vocabulario do contrato | nenhuma p/ (b); (a) so doc de comando | contrato absorve o balanceador (params ja estaveis) + check `needs_qualitative=1` no auto_check + vocabulario state atualizado | MEDIA |
| F53 | HANDOFF/ESTADO derivacao | 2 | so o cap de 60 linhas fisicas segura (BLOCK real); TODOS os caps estruturais violados no HANDOFF atual (10 bullets onde cabem 3; 6 itens numa linha fisica p/ evadir o cap de 5; frente `Erros & Cards` ausente; vocabulario fora do canone); causa mecanica: `render_handoff_block` nao deriva `Erros & Cards`; `ESTADO.md:36` rotula "derivados" contadores digitados a mao (so resumos e derivado) | teste de linhas fisicas (evadivel por construcao) | codigo: estender render_handoff_block (vocabulario completo); gate: check estrutural de frentes | MEDIA |
| F54 | ledger-of-self (degrau 2) | 2 | 462 fingerprints, 279 abertos (263 `card_atomicidade`), mesmo WARN visto **102x em 36 dias**; nenhum codigo chama `ledger_self.abertos()`; auto_check nunca imprime o topo da divida; nao ha criterio de promocao WARN->BLOCK ("warning-first virou warning-only", D3 confirmado com numeros) | escrita fiel, leitura zero | codigo: auto_check imprime top-N de abertos + idade; regra de promocao (ex.: aberto ha >30d com >50 ocorrencias escala severidade) | ALTA |
| F55 | pre-commit --staged | 2 | `git_utils.py:47` colhe so NOMES staged; `auto_check.py:225` roda pytest contra o FILESYSTEM -- commit parcial (`git add -p`) e validado pelo codigo errado nas duas direcoes | nenhuma | codigo: validar o indice (stash -k -u ou worktree temporaria) | MEDIA |
| F56 | reconcile-contract | 2 | B2 declarada BLOCKING, implementada como WARN com `success=True` fixo (`auto_check.py:267`) -- e checa condicao aparentada (ponteiro>max+1), nao a escrita; B3/B4/W1/W3/W4 sem implementacao nenhuma (coluna "como checar" e prosa); mesma falha que o changelog v1.1 declarou consertada (consertou so B1) | B1 exemplar; resto convencao | promover B2 a BLOCK real OU re-ratificar contrato com o rebaixamento explicito; matriz condicao->instrumento | MEDIA |
| F57 | camada de memoria do harness | 2 | **o achado-tese, com caso provado**: 51 `feedback_*` fora do git/invisiveis p/ outros harness; a s156 (Antigravity) deletou `tools/autopsia_template.py` que a memoria-CONTRATO de s149 (`feedback_aula_base_artifact_design_contract`) aponta como modelo canonico -- a sessao nao via a memoria, a memoria nao detecta a delecao (3 arquivos de memoria apontam p/ o morto); 2 memorias fora do indice MEMORY.md (1 regra ATIVA invisivel: `feedback_fsrs_override_autoconfirm`; 1 morta de s044: `project_semantic_architecture`); ~2/3 das 51 duplicam portador versionado sem reconciliador (assinatura TETO_BASE aplicada a memoria) | AGENTS.md avisa (prosa) | migrar regra load-bearing p/ portador versionado (skill/contrato; vereditos por familia abaixo); check barato: grep de paths `tools/*.py` citados em `memory/*.md` contra o disco | ALTA |
| F58 | integridade de history/ | 3 | `session_156.md` corrompido NO SSOT: BOM + escapes comidos na escrita (`\t`ools -> tab literal, `pp/pages`, `uto_check`, `esumos/`, `srs-management`) -- nenhum gate olha history/; tabela do INDEX.md para na s144 (entradas novas so em prosa) | nenhuma | gate: check de encoding/estrutura minima de `session_NNN.md` novo no auto_check | BAIXA |
| F59 | permissoes do harness | 2 | `settings.local.json`: 166 entradas allow, ZERO deny/ask; `Bash(python:*)` = execucao arbitraria pre-aprovada; `pip install:*`; ~40% e lixo one-shot de sessoes antigas (seds de arquivo que nem existe) -- lista ilegivel = entrada perigosa futura passa despercebida | julgamento do agente | config: bloco deny minimo (rm -rf, git reset --hard, git clean, push --force) + poda das entradas mortas | MEDIA |
| F60 | robustez de exit code | 3 | `backup_db.py:104` imprime "BACKUP CORROMPIDO -- abortando" e sai **0**; `importar_sessoes.py` sai 0 com 100% das linhas rejeitadas; 18/45 CLIs nunca retornam !=0; 11 excepts silenciosos so no day_plan (plano pode sair sem zona/frieza/prescricao sem 1 aviso) | padrao certo ja existe (`insert_questao.py:474`, F27) e nao foi generalizado | codigo: exit simetrico nos writers + `[WARN]` impresso nas degradacoes do day_plan | MEDIA |

**Anexo -- menores (nao-F, para varreduras futuras):** `DB_PATH` redefinido 22x em 8 grafias (env `MEDHUB_DB` resolveria); `AREAS_VALIDAS` duplicada com divergencia (performance.py sem "Simulado"); 4a definicao de "card ativo" sobrevivente (`detect_clones.py:38` sem COALESCE); `resolve_tema_id` reimplementado 5x sem o desempate deterministico; PRAGMA foreign_keys em so 6/12 caminhos de escrita (dedup/normalize deletam taxonomia SEM FK ativa); 4 CLIs "read-only por docstring" abrem conexao gravavel (variancia, performance, review_radar, detect_clones -- `mode=ro` custa 1 linha); funcoes-monstro `auto_check.main` 488L e `insert_questao` 198L; `sync_skills --check` cego a drift de `description` e a espelho orfao; reachability conta mencao textual como alcance (lapide passa) e so roda em `--all`; `suites_orfas` valida por substring (mencionada != inscrita); README.md errado em 5 pontos verificaveis (BM25, generate_flashcards.py, two-tier, summarize_performance, metricas velhas); AGENTS.md diz "13 checks/2 BLOCK" vs medicao 19 unidades/8 BLOCK; frontmatter version != titulo em 4/9 contratos; `resumo_read` e kind fantasma; model id `claude-haiku-4-5-20251001` pinado e duplicado em 2 modulos; DeprecationWarning do datetime adapter (95 no run da suite); `pubmedmcp` caiu NESTA sessao e nenhum sensor distingue declarado de conectavel; graphify reporta "Import Cycles: None" mas rag.py<->get_topic_context tem ciclo real gerenciado por import lazy (limite do extrator); AUDITORIA_MEDHUB.md so cresce (99->115KB em 5 dias, 29 RESOLVIDOS no corpo) violando a auto-higiene binaria do AGENTE.md:63 -- e higiene de scratch/tmp nao tem sensor.

### Entregavel 2 -- matriz de portadores de regra (§10b, validada)

| # | portador | onde vive | enforcement real | se ninguem carregar | versionado? |
|---|---|---|---|---|---|
| 1 | CLAUDE.md -> AGENTE.md | repo | nenhum (prosa de boot) | swap test provou: parte ignorada por agente externo | sim |
| 2 | AGENTS.md | repo | nenhum | enquadramento p/ agente externo (entregue s159; ja com 1 drift de contagem) | sim |
| 3 | core/contracts/ (9) | repo | parcial -- so onde ha teste-espelho (LIMITE_HANDOFF sim; balanceador/precedencia nao) | drift silencioso (TETO_BASE 30x40 5 semanas; F47/F52 vivos) | sim |
| 4 | .claude/commands/ (11 skills) | repo | nenhum -- passo acontece se o agente ler | F42, override reprovado 3x | sim |
| 5 | .agents/skills/ (espelhos) | repo | sync_skills --check (WARN; cego a description/orfao) | espelho mente p/ Codex/Antigravity | sim (gerado) |
| 6 | .agents/workflows/ | repo | nenhum | orquestracao improvisada | sim |
| 7 | hooks (SessionStart, PostToolUse(Write), pre-commit) | .claude/ + .git | **REAL** | -- | parcial (.git/hooks reinstalavel) |
| 8 | tools/auto_check.py | repo | **8 BLOCK + 11 WARN** (medido; melhorou de 2 BLOCK na s159) | falso verde onde e WARN (F54) | sim |
| 9 | suite pytest (317) | repo | REAL **quando coletada** (allowlist manual; 6/38 suites so em branches condicionais) | suite fantasma (test_handoff_teto, 3 sessoes) | sim |
| 10 | schema/constraints ipub.db | db | REAL (UNIQUE, FK -- mas FK OFF em 6/12 caminhos de escrita) | orfaos p/ o check_fk_orphans achar depois | schema em init_db.py sim |
| 11 | memorias ~/.claude (77; 51 feedback_*) | FORA do repo | **nenhum + invisivel p/ outros harness** | F57 (caso provado autopsia_template) | **NAO** |
| 12 | medhub_memory.db (weak_areas) | fora do git | nenhum -- e 83% com error_count=0 (F45) | ranking do boot vira "mais recente" | NAO |

**Leitura confirmada com ajuste:** vinculantes de verdade = 7, 9-quando-coletada, 10, e o 8 subiu de 2/13 p/ 8/19 BLOCK na s159. As 51 memorias que mais governam o comportamento seguem 100% decorativas e nao-versionadas. Vereditos por familia (§8 do handoff): **conduta do /revisar (8)** -> passo/template da skill versionada (+ relearning intra-sessao vira codigo na fila); **aula-base (10)** -> contrato versionado + gate barato p/ ancorar-PDF + lint p/ width; **padroes de erro do usuario (10)** -> dado/schema (ja e o dominio do weak_areas/habilidades -- hoje ha DOIS SSOTs do mesmo fato); **numeros (2)** -> constante+teste (feito p/ TETO_BASE; memoria encolhe p/ o porque); **flashcards/curadoria (8)** -> regua ja vive em estilo-flashcard.md, memorias-duplicata encolhem p/ ponteiro; **processo (13)** -> prosa legitima MAS com portador repo (AGENTE.md/workflows), nao memoria de harness. "Permanece prosa" so se declarado onde e por que.

### Swap test retroativo (§11) -- s156-s158 (Antigravity/Gemini)

| check mecanico | s156 (3.1 Pro) | s157 (3.7 Flash) | s158 (3.7 Flash) |
|---|---|---|---|
| HANDOFF atualizado | sim | sim | sim |
| log criado + indexado | log sim; INDEX so no commit seguinte | sim | sim |
| auto_check | "PASSED" **falso verde** (coleta quebrada por ele mesmo -- F44) | "PASSED" falso verde herdado | idem |
| integridade do log | **corrompido** (F58: BOM + escapes comidos) | ok | ok |
| ipub.db coerente c/ narrativa | plausivel | coerente (F38 nao acusa) | coerente |
| contratos respeitados | **NAO**: TETO_BASE 30x40 mantido em commit "resolver ambiguidade"; quebrou coleta de suite (3 sessoes); criou CLI orfao com dep fantasma (F51); **deletou o alvo de memoria-CONTRATO invisivel (F57) e deixou o importador dangling (F50)** | ok mecanicamente | ok mecanicamente |

**Placar por classe:** s156 = 5 divergencias estruturais, TODAS classe 2/3, NENHUMA travou; s157/s158 = 0 divergencias mecanicas proprias (mas herdaram o falso verde). **Hipotese do handoff CONFIRMADA:** a divida e classe 2 (contrato implicito sem gate), nao classe 4 (capacidade) -- nenhum dos defeitos exigiria modelo mais forte para ser evitado, todos exigiam um gate que nao existia. Maturidade (criterio §11.4): != 0, e nada travou ruidosamente.

### O que esta solido (adicoes da s160 -- nao mexer sem motivo)

- **Suite 317 PASSED em ~65s** e, desde a s159, o auto_check RODA o pytest (check 2d BLOCK + escalonamento por substrato compartilhado -- correcao de causa-raiz, nao remendo).
- **Lock otimista no caminho FSRS** (`app/utils/db.py:420-481`): rowcount-check + rollback + revlog na mesma transacao. Concorrencia correta onde quase ninguem faria.
- **Watermark de dado** (auto_check cobre o ipub.db, nao so o git): tripla (MAX id, COUNT, MAX card_version), mode=ro, fail-open, selo pos-checks. As 3 decisoes dificeis certas.
- **`backup_db.py`**: copia -> integrity_check NA COPIA -> aborta sem tocar nada -> so entao rotaciona + COUNT-ASSERT. Ordem correta de operacao destrutiva (so falta o exit code, F60).
- **Eval do RAG com honestidade epistemica rara**: "misses sao dados", CI declarado, ruido run-a-run isolado e quantificado, folclore superseded explicitamente.
- **Meta-tooling de segunda ordem**: reachability + suites_orfas (auto-referente de proposito) atacam a classe "construido-e-nunca-conectado" que quase nenhum repo instrumenta.
- **Densidade de rationale nos comentarios** (incidente + sessao + porque): foi o que permitiu a auditoria distinguir decisao de acidente.
- **Zero SQL injection, zero bare except, zero path absoluto hardcoded, zero segredo vazado** (chave so via os.environ; .env/.db/.pdf fora do git -- verificado).

---

## 4. O que esta solido (nao mexer sem motivo)

Registrado para o PRD nao "consertar" o que funciona:
- **Camada de estado contract-driven** (HANDOFF operacional + ESTADO macro + contratos em `core/contracts/`). Arquitetura madura, portada do agente irmao.
- **Caminho de escrita unico do FSRS:** todo rating passa por `db.record_review()` via `fsrs_queue.py`; audit trail em `fsrs_revlog`. `import sqlite3` confinado a `app/utils/db.py`. Disciplina de SSOT respeitada.
- **Dados ja carregam `area`/`tema`** por card -- a clusterizacao de F3 e barata porque o campo existe.
- **Politica de severidade WARN->BLOCK** (s106/107): regra nova nasce advertindo, so bloqueia quando a base zera. Bom padrao anti-atrito para os invariantes propostos aqui (F1).
- **Harness autonomo staged-only + quotepath-safe** (`auto_check.py`) -- ja resolve o problema de caminhos acentuados no pre-commit.

---

## 5. Andaime de prompt para o agente de engenharia (anti-atrito)

Para o aprofundamento subsequente, estruturar o pedido assim (reduz a chance de o vocabulario de dominio disparar o classificador automatico, mantendo o foco em engenharia):

- **Enquadrar como engenharia de sistemas, nao clinica.** O sujeito do pedido e "camada de estado / fila / contrato / CLI / hook", nao a materia de estudo. O conteudo de dominio entra como *dado que as estruturas transportam*.
- **Verbos de engenharia:** auditar, reconciliar, derivar, versionar, invariante, idempotencia, ordenacao, cache, drift. Evitar centrar o pedido em termos de dominio quando o alvo real e a estrutura.
- **Referenciar este doc + os contratos** (`core/contracts/*.md`, `AGENTE.md`) como fonte, e pedir verificacao antes de mudanca.
- **Um achado por vez -> spec -> patch.** Priorizar por severidade (ALTA primeiro; aqui todas sao MEDIA/BAIXA, entao ordenar por custo/beneficio: F3 e F1 sao os melhores primeiros passos -- baratos e de alto retorno).

**Ordem sugerida de ataque para o PRD:**
1. **F1 + F6** (juntos) -- fechar o drift de estado e derivar os numeros do HANDOFF. Restaura confianca na camada de governanca antes de construir em cima dela.
2. **F3** -- ordenacao por cluster na fila. Barato, alto retorno pedagogico, observado direto do uso.
3. **F4** -- estrategia de drenagem de divida FSRS + metrica de divida no day_plan.
4. **F2** -- perfilar e enxugar a latencia de tooling/hooks.
5. **F5** -- PREPARAR proativo no fluxo DRENAR.

---

## 6. Log de observacao (sessao viva -- s108)

Materia-prima dos achados. Drenagem completa da fila de atrasados: **43 cards** em 9 clusters, ordem = cluster-a-cluster com PREPARAR calibrado.
- Boot correu limpo; hook de fraquezas + plano do dia + proximo ato funcionaram (Parte 1 do PRD de Autogovernanca confirmada em uso). Latencia de Bash (`git`/`ls`) estourou 120s -> F2.
- A fila veio clusterizavel, mas a ordem do CLI e por bucket, nao por tema; a conducao por cluster foi **manual** -> F3.
- **Contagem manual errou 3x** (Cardiopatias "7"->6, Ectopica "5"->4, Pancreatite idem): sintoma de F6 (numero digitado x derivado). Reforca a hipotese de `day_plan --review-plan` emitir os clusters do dia com contagem.
- PREPARAR so disparou por pedido do operador na 1a vez -> F5; depois passou a ser oferecido proativamente (dogfooding do proprio F5).
- **Dois cards mal-calibrados** (`id=95` HCE-vs-TGA; `id=120` heterotopica-vs-corpo-luteo) -> F7, com o `id=120` marcado para gate de evidencia.
- **Vies do PREPARAR** confirmado em 3 canais (vazamento direto, pre-resolucao de card de conduta, amplificacao de erro de ensino) -> F8; e a classe "card de fato puro" onde o refresh e contraindicado.
- **Override pos-record** (card `id=403`, Paget->Faget) expos a contradicao append-only x contrato -> F9.
- Distribuicao de notas final (43 cards): **22x nota 4 · 9x nota 3 · 9x nota 2 · 2x nota 1** (213 pneumotorax e 205 pentamidina; ambos re-drillados). Dominio de mecanismo forte; gaps pontuais de fato/discriminacao.

---

## 7. Aprendizados de processo (meta -- como esta etapa de iteracao funcionou)

O objetivo da sessao nao era so drenar cards: era **usar o MedHub para descobrir como melhorar o MedHub**. O que essa etapa ensinou sobre o *metodo* de iteracao:

1. **Dogfooding > leitura estatica para achar defeito real.** 4 dos 9 achados (F3, F7, F8, F9) so apareceram porque o ambiente foi *usado*, nao lido. Leitura de codigo pega arquitetura; uso pega friccao. Regra de processo: **toda sessao de uso e tambem uma sessao de auditoria** -- o agente-player e simultaneamente auditor, e cada atrito no fluxo e um achado candidato.
2. **Defeito de card so aparece quando um solucionador competente discorda do card.** F7 (`id=95`, `id=120`) exigiu que o operador desse a resposta *clinicamente melhor* e o card marcasse erro. Um linter sintatico nunca pegaria isso -- e um sinal semantico que emerge do desacordo humano-vs-gabarito. Implicacao: capturar sistematicamente os cards onde o operador "erra com razao" (candidatos a reforge/gate de evidencia).
3. **O agente que aquece e o mesmo que sabe a resposta -> vies estrutural.** F8 nao e descuido, e uma propriedade do arranjo. Qualquer mecanismo de "preparar antes de sondar" conduzido pelo mesmo agente precisa de uma clausula explicita de isolamento, senao contamina a metrica.
4. **Contradicoes de contrato so disparam sob uso especifico.** F9 (override x append-only) estava latente no contrato desde s075; so apareceu quando um operador *de fato* corrigiu uma nota ja gravada. Contratos precisam ser exercitados, nao so lidos, para revelar suas arestas.
5. **Enquadramento anti-atrito e parte do metodo, nao cosmetica.** O classificador automatico do modelo marca vocabulario clinico como sensivel. Conduzir o trabalho de engenharia com o dominio tratado como *payload* (e nao como assunto) foi o que manteve o fluxo produtivo. Este doc e escrito nesse registro **de proposito**, para que o Fable o consuma sem atrito (ver secao 8).
6. **Separar as duas trilhas de fechamento.** Achado de *conteudo* (ex.: o operador confundiu eponimo Faget/Paget; o padrao vivo do pneumotorax reincidiu) vai para o `history/session_NNN.md` e para os "padroes de erro vivos" do HANDOFF. Achado de *engenharia* vai para este doc. Nao misturar -- sao SSOTs diferentes.

**Como continuar a iteracao (para o proximo coordenador de sessao):** manter este doc como o **ledger vivo de engenharia** do MedHub. Cada nova sessao de uso adiciona achados numerados (F10, F11, ...) com o mesmo template. Quando o operador quiser, o Fable consome o ledger e emite o PRD. O ledger nunca "fecha" -- ele acumula ate virar backlog priorizado.

---

## 8. Para o Fable -- ponto de entrada (briefing pronto, registro de engenharia)

> Cole/adapte o bloco abaixo para iniciar a sessao de PRD com o Fable. Ele ja vem no registro que evita o atrito do classificador.

**Contexto:** O MedHub e um sistema de software de gestao de estudo (camada de estado contract-driven, filas de repeticao espacada, CLIs em `tools/`, hooks de validacao). Este arquivo (`AUDITORIA_MEDHUB.md`) e o ledger de engenharia: 9 achados verificaveis (F1-F9), cada um com evidencia, verificacao sugerida e hipotese de melhoria. O conteudo de dominio nos exemplos e apenas o *dado* que as estruturas transportam -- o alvo do trabalho e a estrutura (fila, contrato, CLI, hook, invariante de estado).

**Tarefa:** transformar este ledger em um PRD de melhorias, no fluxo `/vibeflow:discover` -> `/vibeflow:gen-spec`. Antes de especificar, **verificar cada achado** contra o codigo (coluna "verificacao sugerida"). Priorizar por custo/beneficio.

**Ordem de ataque recomendada (secao 5, reafirmada):**
1. **F1 + F6** -- invariante de ponteiro de sessao no `auto_check` + bloco numerico do HANDOFF derivado por `day_plan.py --handoff-block`. Fecha a classe inteira de drift de estado.
2. **F3** -- flag `--cluster`/`--by-tema` em `fsrs_queue.py` (+ eventual `day_plan --review-plan`). Barato, alto retorno, observado direto do uso.
3. **F9** -- mudar o protocolo do loop de `/revisar` para gravar `--record` so apos a janela de override (nao tocar schema).
4. **F8** -- clausula no contrato de `/revisar` isolando o conteudo do PREPARAR das respostas dos cards; distinguir card de raciocinio (refresh ok) de card de fato puro (refresh contraindicado).
5. **F7** -- rodar `/curar-cards` nos `id=95` e `id=120` (este ultimo pelo gate de evidencia); avaliar a heuristica de linter proposta.
6. **F4** -- estrategia de drenagem de divida FSRS + metrica de divida no `day_plan`.
7. **F2** -- perfilar e enxugar a latencia de tooling/hooks.
8. **F5** -- PREPARAR proativo no fluxo DRENAR (depende de F3 para o sinal de cluster frio).

**Restricoes de projeto a respeitar (nao violar):** `import sqlite3` so em `app/utils/db.py`; agentes nao fazem SQL direto (engine/CLI); FSRS escreve so via `record_review`; resumos seguem `/estilo-resumo`; encoding ASCII limpo (secao 4.5 do AGENTE.md); `ipub.db` local-only; armadilhas de resumo sao cumulativas.

---

*Este doc e o ledger vivo de engenharia. Nao "fecha" -- acumula achados a cada sessao de uso. O 1o ciclo Fable (PRD -> 5 ondas) foi ENTREGUE em 2026-07-05 (secao 3b). A s109 (coordenador-observador) adicionou **F16-F19** do uso vivo (forja da aula-base de apendicite; secao 3c) -- insumo do ciclo 2. A rodada 1 do ciclo 2 (Fable/ai-eng, paralela a s109; secao 3d) entregou F14/F15, validou o teto (F4/b), preparou a janela do expurgo (F11) e registrou F20. A s109 (1o lote de questoes; secao 3e) adicionou F21, e (2o lote; secao 3f) **F22-F26**. O **ciclo 2 rodada 2** (Fable/ai-eng, 2026-07-06; secao 3g) entregou o PRD ORQUESTRACAO completo (vibeflow 4/4 PASS): posicao SSOT (op-3), recomendador do dia, F22-F26 RESOLVIDOS; F21 segue aberto (contrato de aula); F27/F28 registrados pelos audits. A **s110 parte 2** (2026-07-06) verificou performance+cronograma a pedido do operador, achou e RESOLVEU **F29** (drift planilha-db de 76q, ao vivo, mesma sessao); no ciclo de Pre-Natal I (cold recall, tema-zero) registrou **F30** (material_indicado nao verifica existencia real do resumo), aberto. A **s113** (08/07, verificacao de cronograma a pedido do operador) achou e RESOLVEU **F33** (boot recomendava temas ja feitos, calendario-driven sem ler conclusao real da planilha) na mesma sessao via ciclo completo `/discover`->`/gen-spec`->`/implement`->`/audit` (PASS); F31/F32 registrados por uso vivo (s112). A **s115** (2026-07-09) auditou o boot e entregou o PRD **boot-cronograma-drive-confiavel** em 3 partes (vibeflow discover->gen-spec->implement->audit, audits PASS): achado novo **F34** (disparo+ordem do Drive) + **F30/F31 RESOLVIDOS**; **F21 segue aberto**. A reconciliacao de fechamento da **s125** (2026-07-19; secao 3i) registrou
retroativamente **F35** (reconcile de volume manual + seletor de suite do `auto_check` dando falso
verde) e **F36** (binario grande do Drive via MCP nao materializa em disco -> `--sync-drive` pulado
na s124 e na s125), ambos ABERTOS. A **s128** (2026-07-25) registrou **F37** (campo `questoes_realizadas` inflado, achado
na s127) e **F38** (erros analisados nao chegam a `questoes_erros` -- pipeline com dois finais), e
elevou **F36 para ALTA** com o modo de falha precisado (limite de transcricao, nao de acesso).
Ainda na **s128**, o dreno de 40 cards produziu **F39** (40% do baralho viola o principio atomico --
detector entregue, 8 cards atomizados, ~350 na worklist), achado **do usuario**, nao do agente.
A **s152** (2026-08-23, drenagem de 90 cards em regime de divida) registrou **F40** (4 padroes novos
de defeito de FORMULACAO de card -- pacote-de-fatos, frente ambigua, pergunta circular, pergunta
composta -- mesma familia do F7, gatilho para a auditoria ampla do banco ja pendente desde a s148),
**PARCIAL** (4 cards reforjados ao vivo; rastreio no banco inteiro fica para a auditoria ampla).
A **s154** (2026-08-24, drenagem de 100 cards em 10 blocos, regime de divida) registrou **F41**:
6 novas instancias de F40 (cards 1053/553/155/576/293/325, 2 delas -- 293/325 -- um subpadrao
tautologico novo em cards de tema `[bulk]`), a reincidencia do padrao de calibracao de probabilidade
do F7 na tema Gravidez Ectopica (`card_id=114` auditado via `evidence-researcher`, veredito PRECISA
AJUSTE -- moldura de PUL; `card_id=120` do F7 original segue sem auditoria) e 3 flags do usuario
(1411/283/319) sem defeito identificado pelo agente, calibracao em aberto pra proxima sessao.
~~**Proximos achados comecam em F42**~~ -> **proximos comecam em F87** (F82-F86 numerados na s171). Ultima atualizacao: s154 (2026-08-24). **Ciclo DESCOLAR
(Fable/ai-eng, 2026-09-01 — retorno do handoff `~/ai-eng/HANDOFF-MEDHUB-COLA.md`):** PRD
`descolar-motor-determinismo` (P1-P7 respondidas) + 7 specs + implementacao. RESOLVIDOS:
**F45** (vocabulario+upsert por par via `reconciliar_weak_areas`), **F46** (paths por __file__,
leitor ro, 2 decoys deletados), **F47** (precedencia de fonte implementada), **F48** (timeout+
temp0+cauda+RAG_STALE+testes do chunker), **F49** (allowlist tabela->writers TESTADA,
`test_writer_allowlist`), **F50** (deletado; check IMPORT_DANGLING mata a classe), **F51**
(aposentado sem substituto), **F52** (contrato FSRS v1.1 absorve balanceador + state=3 + sensor
needs_qualitative), **F53** (Erros&Cards derivado; matriz de verdade no reconcile v1.2 — o
derivado ja expos drift real: 922 erros vs 903 digitados), **F54** (painel de DIVIDA = leitor
obrigatorio em todo run), **F56** (B2 BLOCK real + matriz condicao->instrumento), **F61** (novo,
do discovery: duplas execucoes de suite mortas; tempo por bloco impresso). **F57** RESOLVIDO-parcial
(5 memorias nomeadas resolvidas + check `memory_pointers` vigiando; 2 ponteiros mortos restantes
= WARN no painel, migracao das demais 72 nas proximas sessoes), **F58** RESOLVIDO (check
`history_integrity`: session novo nasce integro ou e acusado; s156 fica como lapide), **F59**
RESOLVIDO (deny 0->4, allow 163->138 por poda mecanica), **F60** RESOLVIDO (exit simetrico em
backup_db/importar_sessoes + day_plan degrada audivel; ~15 CLIs restantes = candidatos no
painel). Suite 317->**358**. Ciclo verificado: audits em
`.vibeflow/audits/descolar-motor-cycle-audit.md` (PASS 7/7).
Anti-scope preservado: promocao automatica WARN->BLOCK (P2), golden de aula (P6, pos-ENAMED),
F55, rotacao deste doc (**F62** candidata — politica do dono), ipub.db/conteudo clinico. **Adendo 2026-07-12 (Fable/ai-eng, ciclo mecanismo-de-conhecimento):** F21 RECONCILIADO em dois planos (conduta RESOLVIDA no contrato v1.2; enforcement mecanico na spec `mecanismo-conhecimento-consolidacao-part-3`) -- ver secao 3e. Ciclo de consolidacao do mecanismo de RAG/conhecimento em andamento (part-1 audit PASS: MCP obsidian aposentado, scaffold LangGraph/BM25 removido; part-2: reconciliacao de drift documental).*

---

## 4o. Achado de uso vivo -- s162 (Claude Code/Opus 5, 2026-09-02)

### F63 -- a prioridade que governa o estudo nao viaja com o repo (o usuario e a camada de transporte)

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

### F64 -- o gatilho do regime de divida le `atrasados`, o dono le `vencidos`

**Classe:** gap de spec entre a formula e o modelo mental do operador.

**Observado.** `tools/day_plan.py::_teto_efetivo(atrasados)` sobe o teto do dia so quando
`atrasados > TETO_BASE` (60). Na s162 havia **45 atrasados + 22 p/ hoje = 67 vencidos**: o
operador leu "vencidos > teto, logo regime de divida" e o codigo leu "45 < 60, teto base".
O agente reportou o teto do codigo como se fosse fato pacifico e recomendou parar o estudo com
base nele. O operador contestou -- e a leitura dele e a mais defensavel: card vencido hoje e
divida igual a card vencido ontem.

**O defeito.** A politica declarada (memoria `feedback_politica_cards_diaria`, s159: "teto 60/dia,
CAP de divida 1,5x = 90") nao diz **qual contador** dispara o regime. `_teto_efetivo` decidiu por
`atrasados` sem que a escolha esteja escrita em nenhum portador. Consequencia pratica: numa
divida composta majoritariamente por cards de HOJE, o regime nunca dispara e o teto trava em 60
com a fila inteira vencida.

**Agravante medido na mesma sessao.** A sessao cruzou a meia-noite (02/09 -> 03/09). O teto e
por dia de calendario, e nenhum aviso existe quando a fronteira e cruzada no meio de uma
drenagem: o agente seguiu argumentando com o orcamento do dia anterior por 2 turnos. 02/09
fechou em 75 (sob o CAP 90) e 03/09 abriu limpo -- mas isso foi descoberto por `date`, nao por
sensor.

**Direcao (nao implementada).** (a) Decidir e **escrever** o contador do gatilho em
`fsrs-management-contract.md` (recomendacao: `vencidos = atrasados + hoje`, que e a leitura do
dono); (b) `_teto_efetivo` passa a receber o contador decidido, com teste; (c) `day_plan`
imprime o **consumo do dia** (`gravados_hoje / teto`) no bloco de FSRS -- hoje o teto aparece
sem o saldo, o que obriga o agente a derivar a conta a mao e errar.

**Severidade:** MEDIA (nao corrompe dado; distorce a prescricao de volume e ja produziu uma
recomendacao errada de parar).

### F65 -- o balde `[bulk] <Area>` esconde 72 cards do radar de dormencia

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

### F66 -- 45% da memoria de fraquezas e orfa por ABREVIACAO, e o log cresce sem teto

**Classe:** F45 nao terminou o servico (o input do boot ainda nao e verdadeiro) + sensor que
cresce sem limite. **Descoberto ao vivo:** o painel de DIVIDA saltou de 7 para **146 linhas**
durante o proprio fechamento da s162, disparado pelo hook que consolida o session log novo.

**Medido.** `reconciliar_weak_areas` (F45) roda em toda consolidacao e classifica cada WeakArea
contra o vocabulario de `taxonomia_cronograma`:

| | |
|---|---|
| WeakAreas no store | **244** |
| areas canonicas no vocabulario | **23** |
| **fora do vocabulario** | **111 (45%)** |
| linhas `wa_vocab/fora` geradas numa consolidacao | **139** |

**A causa NAO e alucinacao do modelo -- e abreviacao.** O vocabulario canonico usa forma curta
(`Infecto`, `Gastro`, `Hepato`, `Dermato`, `Pneumo`, `Endocrino`, `Hemato`, `Reumato`,
`Otorrino`) e o Haiku escreve a forma longa. As 8 areas invalidas mais frequentes sao todas
especialidades **legitimas** em forma nao-abreviada:

```
10x Infectologia     4x Oncologia        3x Gastroenterologia   3x Emergencias Pediatricas
 7x Dermatologia     4x Hepatologia      3x Atencao Primaria    3x Clinica Geral
```

`_norm` faz casefold + remocao de acento e declara na propria docstring: *"NAO faz substring:
dois rotulos so casam se forem o MESMO rotulo."* Logo `Infectologia` nunca casa `Infecto`. O
mismatch e de **forma lexical**, nao de conteudo -- o dado esta certo e e descartado.

**Duas consequencias, ambas na linha de mira do P3.**

1. **O ranking de fraquezas do boot sai enviesado.** O bloco "Areas de fraqueza persistentes
   (top 8)" -- o sinal mais importante que o agente le no primeiro turno -- e ordenado por
   `error_count`, que vem de um match **exato** do par `(area, tema)` contra `ipub.db`. Area orfa
   nunca casa, entao `error_count` fica 0 e a entrada **nunca sobe no ranking**, por real que
   seja a fraqueza. O top 8 e disputado por 55% do store; os outros 45% sao invisiveis por erro
   de grafia.
2. **O log cresce 111-139 linhas por consolidacao, para sempre.** O gate e *recall-safe* por
   desenho (nunca dropa: normaliza o que mapeia, loga o resto) -- correto como politica, mas
   ninguem fecha o ciclo, entao os mesmos 111 itens sao re-logados a cada sessao. Isso torna a
   linha `memory_errors.log: N linha(s)` do painel de DIVIDA **estritamente sem significado**:
   ela mede quantas vezes o sensor rodou, nao quanta divida existe. Confirma a falha (b) do
   veredito da s162 (painel conta linha, nao item aberto) com um caso de crescimento ilimitado.

**Sujeira no proprio vocabulario canonico.** As 23 areas incluem `Clinica Medica/Cardiologia`,
`Clínica Médica` **e** `Cardiologia` como entradas distintas -- a taxonomia tem drift proprio, e
qualquer mapa de alias tem de ser construido **depois** de sanear isso (`normalize_taxonomia.py`
e o portador).

**Direcao (nao implementada).** (a) Tabela de alias explicita area-longa -> area-curta em UM
portador versionado (candidato: `core/` ao lado da taxonomia, nao hardcoded no manager), com
teste que falhe quando uma area canonica nova entra sem alias; (b) `reconciliar_weak_areas`
consulta o alias antes de declarar `fora_vocab`; (c) o que sobrar fora do vocabulario apos o
alias e **divida real** -- vai para um sink idempotente (chave por `item.key`, nao append), para
o painel poder contar item aberto; (d) sanear as 3 entradas duplicadas do vocabulario primeiro.

**Severidade:** ALTA (degrada o sinal do primeiro turno de toda sessao e polui o unico painel de
divida que o harness tem).

> **Nota de processo.** A s162 declarou a des-colagem APROVADA e este achado nasceu **no
> fechamento da mesma sessao**, do painel que a reforma criou, disparado por um hook que a
> reforma consertou. Nao contradiz o veredito -- ilustra-o: o P1 entregou o orgao sensorial que
> viu isto, e o F66 e a prova de que o P3 ("o input do boot fica verdadeiro") ficou a meio
> caminho. F45 consertou o **mecanismo** de reconciliacao; faltou o **dicionario**.

### F67 -- taxonomia duplicada divide o sinal do FSRS e da dormencia (s165, Claude Code/Fable 5.1, 2026-09-05)
**Evidencia (db, read-only):** o mesmo tema vive em 2-5 linhas de `taxonomia_cronograma`: Rastreamento de colo x2 (`...do Câncer de Colo do Útero` 12 ativos/8 erros e `...do Cancer de Colo Uterino` 2/1), TH x2 (`Climatério e Terapia Hormonal` 6/2 e `Terapia Hormonal do Climaterio` 0/1), Asma x5 (`Asma`, `Asma - Crise Aguda`, `Asma na Infância`, `Asma na infância`, `Asma - Exacerbacao`), `Planejamento Familiar` x `Contracepção`, Ulceras x2, TCE x3 (Neuro, Cirurgia leve, Ped), `Cirurgia Infantil` x `Cirurgia Infantil I`, APS x2. **Efeito:** `review_radar`, `infer_nota` e `--cluster` leem metades; a dedup da s083 (`dedup_taxonomia.py`, merge MAX) nao pegou variantes por acento/caixa/sufixo. **Fix candidato:** normalizacao NFKD + casefold + tabela de alias em `normalize_taxonomia.py`, com `--dry-run`. **Re-medido em 2026-09-09 (s174, dry-run A6):** chave NFKD+casefold (sem sufixo romano/"na infancia") acha **10 grupos / 22 linhas / 193 cards + 104 erros**; 5 dos 10 sao a area fantasma `GO`/`Clinica Medica` de volta (F89). Decisao de fusao por grupo = operador (`docs/DRYRUN-F65-F67-2026-09-09.md` §4).

### F68 -- 15 temas de alta/media prevalencia ENAMED sem linha na taxonomia (s165)
**Evidencia:** `core/cronograma/prevalencia_enamed.json` (`tema_id: null`): SCA/dor toracica, DPOC, Derrame pleural, Crise hipertensiva, Parkinsonismo, Dermatoses infecciosas, SUA, Sindrome de Down, Dx nutricional, Choque em pediatria, TB na infancia, Vasculite IgA, SIMP, Saude do trabalhador, Doencas de vulva e vagina. Sem linha nao ha card, erro, dormencia nem nota -- o tema e invisivel ao motor. **Agrava F65:** `[bulk] Cirurgia` guarda **148 erros** sem tema (eram 72 cards na s162), `[bulk] Pneumo` 17. **Fix:** criar as linhas (via cunhagem/`insert_card_base`) e reclassificar os `[bulk]` pelo titulo do erro.

### F69 -- resumos com lacuna de diretriz nova = risco banca-dependente (s165)
**Evidencia (grep):** `[CIR] Trauma.md` ja tem X-ABCDE, torniquete, hipotensao permissiva, ABC score, pneumotorax oculto/3,5 cm, Beck, tranexamico; **falta** "sangue total > 1:1:1" e "Sellick contraindicada", e a classificacao do choque ainda cita "classe I" (11a ed = leve/moderado/grave). `Prevenção Secundária Pós-IAM (Dislipidemia).md`: 1 mencao a PREVENT/Lp(a)/bempedoico (diretriz 2025 rasa). `Sistemas de Informação em Saúde.md`: conferir SINAN 2026 (esporotricose, anomalias, Oropouche, parotidite). HAS Pt2 (130/80, MAPA) e Epilepsias (levetiracetam EV) ja atualizados. **Fix:** Revisao Direcionada com Regra de Acumulo; os `padroes_banca` do JSON sao a fonte.

### F63 -- atualizacao (s165)
O insumo `prevalencia_enamed` agora EXISTE (89 temas, 5 aulas EMED) e ja governa o bucket `novos` via `fsrs_queue --prevalencia`. Falta: `cronograma.py`/`day_plan.py` consumirem o mesmo arquivo para o eixo 4 do `infer_nota()` (contrato §7.7 previa "basta fornecer o campo") e para a prioridade roxa da grade.

## 4p. Sessao de uso s166 (Claude Code/Fable 5.1, 2026-09-05/06) -- achados F70-F72 + evidencias F40/F65/F67

Contexto: drenagem do bloco 1 (62 cards, 4 sub-blocos, 40x4 / 8x3 / 3x2 / 11x1), 5 reforjas in-place, 3 carimbos `review_log`, seguida de sessao de engenharia curta (README, drift doc-vs-codigo, hotfix).

### F70 -- informe do balanceador FSRS ia para stdout e quebrava o contrato JSON do `fsrs_queue --record` -- **MEDIA** -- **RESOLVIDO (hotfix s166)**
**Evidencia:** em 3 de 14 records do sub-bloco 1.1 (cards 788, 1187, 244) o `json.load` do consumidor falhou (`Expecting value: line 1 column 2`); a gravacao tinha persistido. No stdout cru dos sub-blocos seguintes: `[FSRS_BALANCE] due 2026-09-13 -> 2026-09-14 (+1d; carga 21 -> 8)` impresso ANTES do `{"recorded": true, ...}` em 12 cards (381, 823, 1101, 485, 122, 1404, 1475, 1476, 1354, 459, 1472, 1480). Sitios: `app/utils/db.py::_balancear_due` (informe) e o `except` de `_aplicar_review` (WARN). Os testes existentes ja embrulhavam `record_review` em `redirect_stdout` -- o ruido era conhecido e tolerado, nunca tratado como defeito de contrato.
**Fix (aplicado):** os dois `print()` -> `file=sys.stderr`; regressao `tools/test_fsrs_balance_stdout.py` (vermelho antes, verde depois; registrada no `pytest.ini`); trace em `.vibeflow/hotfixes/2026-09-06-fsrs-balance-stdout.md`. Verificado read-only sobre o `ipub.db` real (alvo 13/09, carga 22 -> 11): stdout vazio.

### F71 -- o balanceador de carga nao conhece o calendario de provas: empurrou cards para o dia SEGUINTE ao ENAMED -- **MEDIA** -- **RESOLVIDO (hotfix s174, `.vibeflow/hotfixes/2026-09-09-fsrs-balance-blackout-prova.md`)**
**Evidencia (records de hoje):** #381 e #823 tinham `due` 2026-09-13 (dia da prova, pico de 22 cards) e foram movidos para 2026-09-14 (+1d). Na janela de +-5% o balanceador escolhe o dia de menor carga sem saber que 13/09 e a prova e que 14/09 e o primeiro dia em que a revisao ja nao serve ao objetivo daquela semana. `app/utils/fsrs_balance.escolher_dia` recebe `(alvo, intervalo, carga, hoje, state)` -- nenhum sinal de `core/provas.json`, que ja existe e alimenta o `day_plan` (countdown).
**Fix candidato (S/M):** `escolher_dia` ganha um parametro opcional `dias_evitar: set[date]` (prova e o dia seguinte, derivados de `core/provas.json` pelo caller em `db._balancear_due`); dentro da folga, um candidato em `dias_evitar` so vence se for o unico. Regra continua pura e testavel (`tools/test_fsrs_balance.py`, BLOCKING). Ate la, na semana de prova o efeito e pequeno (deslocamento max +-1d), mas e um pico movido para o lugar errado.
- **Fechamento (s174, 2026-09-09, veredito A3 do `/ai-eng` com 3 ALTERAs):** (i) blackout lido de `core/provas.json` por `db.blackout_provas` (G4: teste prova que nenhuma data real esta no codigo); (ii) alvo em blackout vai para ANTES da prova, nunca depois -- sem vaga na folga = OVERFLOW em stderr, due mantido; (iii) re-rodada sobre a fila via `fsrs_load.py --blackout [--apply]` (dry-run + COUNT-ASSERT §10.7): **34 movidos** (23 de 13/09 -> 12/09), **17 overflow** em 14/09 (inclui #381/#823: o alvo original nao e recuperavel, folga +-1d nao alcanca antes da prova). 15 testes em `tools/test_fsrs_blackout_provas.py`, 11 nasceram vermelhos. Deferido: leitor de `provas.json` duplicado entre `db` e `day_plan`.

### F72 -- `day_plan` recomenda tema de um snapshot que ele mesmo declara nao confiavel (Drive 42d) -- **MEDIA** -- **ABERTO** (familia F34/F36/F63, W8 do reconcile)
**Evidencia (`python tools/day_plan.py`, 2026-09-06):** o cabecalho avisa `Drive desatualizado (42d atras) -- rodar --sync-drive antes de confiar na lista abaixo`, e no mesmo relatorio a "Recomendacao do dia" abre com `1. questoes 51 -- Atencao Primaria a Saude no Brasil` e lista `proximos temas: APS (extensivo), Diarreia, Cirurgia Vascular`. A ordem real (roxos da S17: Diarreia Teoria -> SUA -> APS Revisao -> Diarreia Revisao -> Urologia I -> Pneumonias I) vive so no HANDOFF, decidida pelo usuario (F63). O WARN existe, mas a recomendacao nao degrada: o agente que le so o plano recomenda o tema errado. O usuario percebeu a contradicao na propria sessao ("inconsistencias no seu motor").
**Fix candidato (S):** quando `cron.conclusao_desatualizada` (W8), o passo 1 da recomendacao deixa de nomear um tema do snapshot e passa a apontar o ponteiro textual do HANDOFF ("Grade S17 roxos", ou o campo equivalente em `preparacao_estado`), e a lista `proximos temas` sai rotulada `(snapshot de N dias, ordem manual do usuario nao capturada)`. Nao cria dado novo: reaproveita o WARN que ja e calculado.

### Evidencias novas para achados abertos
- **F40/F41 (defeito de formulacao de card): 9 defeitos em 62 cards (14,5%) nesta drenagem.** Reforjados in-place (id e FSRS preservados, `recurate_cards --apply`): #245 (frente circular "por que a SBP considera..." -> janela do Kasai), #667 (cor de vaginose na vinheta de tricomoniase + regra citando pH ausente da frente), #741 (contexto meta "o enunciado ja entrega..." -> vinheta real, par contrastante com #667), #577 (regra com erro de conteudo "primaria = anovulacao" + contexto vazio; banca-dependente registrado), #311/#313 (clones: o usuario deu a mesma resposta aos dois). Na fila de reforja: #792 (frente aberta, aceita varias respostas certas), #4 (pergunta composta farmaco + concentracao), #1117 (contexto "dor e sangramento" contradiz a pergunta "assintomatica").
- **F65 (`[bulk]` cego):** #297 (Esclerose Multipla, declinio cognitivo) vive em `[bulk] Cirurgia` -- conteudo de Neurologia arquivado na area errada; o radar de dormencia de Neuro nao o ve.
- **F67 (taxonomia duplicada):** os pares `Cirurgia Infantil` x `Cirurgia Infantil I` e `Rastreamento do Cancer de Colo Uterino` x `Rastreamento do Câncer de Colo do Útero` apareceram como clusters separados no `--list --cluster` de hoje.
- **Candidato de DIVIDA "mecanizar o redrill" (ja no painel):** os 10 cards que receberam nota 1-2 hoje voltaram ao `--list` como `vencido` (relearning, `state 3`, due no mesmo dia). O CLI nao distingue "ja gravado nesta sessao"; a unica guarda contra o duplo-record e o conjunto de ids mantido pelo agente. Evidencia de que a fila de redrill precisa viver no CLI.

### F73 -- `cronograma.py --check` (instrumento W5 do reconcile) morria em traceback: PDF-fonte vive em `data/`, codigo procurava na raiz -- **ALTA** -- **RESOLVIDO (hotfix s166)**
**Evidencia:** `python tools/cronograma.py --check` -> `FileNotFoundError: ...\medhub\Cronograma.pdf`; o arquivo esta em `data/Cronograma.pdf` (mtime 2026-03-24) ao lado dos outros PDFs de dados. `PDF_PATH` fixo em `ROOT/Cronograma.pdf` (`tools/cronograma.py:44`), `check()` sem teste de existencia. Como W5 e "manual, WARNING", ninguem rodava e o instrumento ficou morto por tempo indeterminado -- mesma classe de F56 (contrato declara instrumento que nao instrumenta).
**Fix (aplicado):** `resolve_pdf_path(root)` (raiz canonica -> fallback `data/` -> caminho canonico p/ a mensagem), `check()` degrada para `status: missing_pdf`; regressao `tools/test_cronograma_pdf_path.py`; skill `/cronograma` + espelho; trace em `.vibeflow/hotfixes/2026-09-06-cronograma-pdf-path.md`. `--check` real: `fresh` (sha256 do PDF == `_meta.fonte_sha256`). Nao investigado: quando/por que o PDF saiu da raiz.

### F74 -- README.md descrevia uma arquitetura que nao existe mais (Streamlit, RAG two-tier, "zero testes") -- **MEDIA** -- **RESOLVIDO (s166)**
**Evidencia:** README citava app Streamlit de 3 paginas + `streamlit run`, `summarize_performance`, RAG `gold/pdf_raw` + BM25 dormente + cadeia HyDE Anthropic->llama3, FSRS "simplificado ~75 LOC", "delete-after-extract", "test coverage effectively zero, no pytest.ini", "~18 CLIs", baseline 0.778/0.657 (que nem existe no REPORT.md). 30 afirmacoes obsoletas removidas (lista em `README.verification.md` da sessao, nao versionada). O usuario leu isso como "instabilidade arquitetural" -- o codigo esta estavel; o documento publico e que envelheceu em silencio (mesma familia de D2/F42: doc que ninguem gera nem checa).
**Fix (aplicado):** README reescrito por subagente com verificacao afirmacao-a-afirmacao contra o codigo (py-fsrs `fsrs>=6.3.1`, 365 testes coletados, 43 modulos em `tools/`, 9 contratos, 12 skills, hooks reais, eval 0.889/0.685 e sua nota de nao-determinismo). **Sem sensor:** nada acusa README stale; candidato a `drift-check` anotado nas afirmacoes numericas do README (contagens de suites/CLIs/contratos), como o ROADMAP ja faz.

### F75 -- Varredura de drift doc-vs-codigo (subagente, s166): 12 achados D1-D12, 6 ALTA -- **MEDIA (agregado)** -- **9 RESOLVIDOS na sessao, 3 ABERTOS**
Sensores existentes (`doc_drift.py`, `sync_skills --check`) reportavam 0 achados: escopo estreito (refs mortas + 12 anotacoes manuais + paridade de espelho), nao cobertura de alegacoes (D11). Metodo: `--help` de 16 CLIs x skills; grep de termos removidos; contradicoes entre docs.

| ID | Sev | Achado | Status s166 |
|---|---|---|---|
| D1 | ALTA | `fsrs-management-contract` diz que 120/dia foi REJEITADO; HANDOFF autoriza sprint de 120 ate 13/09 sem ponteiro no contrato | RESOLVIDO: excecao datada gravada no contrato (expira 14/09) |
| D2 | ALTA | AGENTE §7.4 "tabela GERADA" divergia do gerador em 5+ linhas (docstring de `backup_db`, contagens) | RESOLVIDO: tabela regenerada com `reachability_check --tabela` (41 linhas). Sem teste de paridade colada-vs-gerada (candidato) |
| D3 | ALTA | enum `veredito` citado de 2 formas em `analisar-questao.md`, nenhuma = `VEREDITOS` (5 valores) | RESOLVIDO: unificado (5 valores; `indefinido` = backfill) + espelho |
| D4 | MEDIA | 5 de 12 skills numeram passos, contra a letra do §7.2 | RESOLVIDO por clausula: §7.2 agora distingue orquestracao de CLI (workflow) de protocolo cognitivo numerado (permitido) |
| D5 | ALTA | CLIs sem assinatura canonica em skill: `day_plan.py` (4 de 10 flags em lugar nenhum: `--no-persist --plano-de --aderencia --semanas`), `recurate_cards`/`detect_clones`/`audit_flashcard_quality`/`normalize_taxonomia`/`backup_db`/`insert_card_extra` (so no workflow `curar-cards`), `registrar_sessao_bulk --acumular/--semana` | **ABERTO (M):** criar skill `day-plan.md` + skill `curar-cards.md` (ou anexar a `estilo-flashcard.md`) e deixar o workflow so com orquestracao |
| D6 | MEDIA | `cronograma.md` sem `--sync-drive`; `revisar.md` sem `--pre-bloco`/`--janela-horas` | RESOLVIDO + espelhos |
| D7 | ALTA | AGENTS.md: "13 checks, apenas 2 bloqueiam" vs ~20 checks e 7 pontos de bloqueio dinamicos | RESOLVIDO: frase fiel + ponteiro p/ matriz do reconcile |
| D8 | ALTA | workflow `registrar-sessao` manda escrever "Ultimas sessoes" no ESTADO -- padrao proibido pelo `estado-contract` (secao nem existe) | RESOLVIDO: passo 3 reescrito |
| D9 | BAIXA | ROADMAP cita R@5=0.778/MRR 0.657; REPORT.md diz 0.889/0.685 (0.778 e o R@3) | RESOLVIDO |
| D10 | BAIXA | `.vibeflow/index.md` Known Issues com 2 itens ja resolvidos | RESOLVIDO (tachados com data) |
| D11 | MEDIA | sensores de drift "verdes" nao cobrem D1-D9 por desenho; "0 achados" le como "sem drift" | **ABERTO (S):** documentar o escopo em `doc_drift.py --help`; (L) paridade skill-vs-`--help` como sensor novo |
| D12 | MEDIA | ROADMAP Linha 8 tratava remocao do player Streamlit como decisao em aberto | RESOLVIDO (tachado + FEITO) |

**Aberto tambem (desta sessao, fora da varredura):** F71 (balanceador x calendario de provas), F72 (`day_plan` recomenda tema de snapshot stale). **Padrao dos 12:** nenhum era bug de codigo; todos eram documento que envelheceu sem gerador nem sensor -- a mesma classe que motivou a tabela gerada do §7.4 e o `doc_drift`. O remedio estrutural e ampliar o que e GERADO (assinaturas de CLI a partir do argparse, contagens a partir do disco) em vez de digitado.

## 4q. Sessao de uso s167 (Claude Code/Fable 5.1, 2026-09-06 noite) -- drenagem de 90 + Simulado 7: evidencias F40/F41/F67 + achado F76

### Evidencias novas para achados abertos
- **F40/F41 (defeito de formulacao de card):** 12 defeitos em 90 servidos (13%; s166: 14,5%). Composta (5, todos flagrados pelo usuario no ato): #175 (indicador de gravidade + por que amilase nao), #1041 (por que nao avidez + conduta), #1424 (vacina + vigilancia), #572 (competencia da DO + papel do SVO), #581 (por que nao DIU + qual prescrever). Frente binaria sim/nao sem exigir o discriminador (2): #151 (transito x frota), #837 (progesterona). Contexto = pergunta reescrita (1): #526. Contexto contradiz a pergunta (1, padrao #1117): #1112 (DMG 28 sem x swab EGB). Tema arquivado errado (1): #258 (ileo pos-op sob "Pancreatite"). Frente aberta com multiplas respostas validas (1): #910 (condiloma: usuario deu podofilotoxina, valida no PCDT, verso so tem ATA). Frente truncada (1): #527 ("USG na"). Frente pede lista sem vinheta (1, usuario: "esse card precisa de fork"): #513. **Reforja pendente de todos os 12.** O lote da S7 nasceu com 1 composta (corrigida antes do insert) e 2 WARNs do lint (#1488 multi-parte, #1490 negativo-orfao) -- o lint pega parte, o usuario pega o resto.
- **F67 (taxonomia duplicada):** #1095 (GO/Endometriose) e #1446 (Ginecologia/Endometriose) sao o mesmo card (USGTV com preparo p/ endometriose profunda) em dois temas; o `--cluster` serviu os dois no mesmo bloco. Dedup de (GO, Endometriose) -> (Ginecologia, Endometriose) e o candidato imediato.
- **Leech candidato:** #245 (Kasai < 60 dias) caiu 4x em 2 sessoes antes de fechar; #1112 (swab EGB 35-37) oscilou 37/34/34-36 na mesma sessao; #567 (cefalohematoma) teve a coleção dita 3x e a conduta nunca. Os tres sao dado numerico/composto -- F40 e curva de esquecimento se tocam aqui.

### F76 -- `fsrs_queue --record --reason` aceita proveniencia divergente do card servido sem aviso -- **BAIXA** -- **RESOLVIDO (hotfix s174, `.vibeflow/hotfixes/2026-09-09-reason-divergente-gravado.md`)**
- **Evidencia (s167):** o bloco 7 misturava 1 card `vencido` (#559) com 8 `agendado`; o agente gravou os 9 com `--reason agendado`. O CLI aceitou e o revlog de #559 carrega proveniencia falsa. O contrato de apresentacao (`revisar.md` §4) diz "gravar SEMPRE com --reason igual ao selection_reason servido", mas nada verifica: o `selection_reason` e derivado (bucket) e o CLI poderia recomputa-lo no `--record` e avisar (ou corrigir) quando o argumento diverge.
- **Remedio (S):** em `--record`, recomputar o bucket do card na hora e emitir `[WARN] reason divergente: servido=vencido, recebido=agendado` em stderr (nao bloquear). Opcional: `--reason auto`.
- **Fechamento (s174, 2026-09-09; A4 do `/ai-eng`: WARN nao BLOCK + ALTERA "gravado, nao so impresso"):** `db.bucket_de` (puro) recomputa o bucket antes de aplicar; coluna nova `fsrs_revlog.reason_servido` (historico NULL); `reason_divergente` no retorno e no JSON do `--record`; `[WARN] reason divergente` em stderr; `--reason auto`. `pre_bloco` cobre `fresh_error`/`novo` (modo, nao bucket). Query do contador B1 fixada em `tools/test_reason_divergente.py` (9 testes, 9 vermelhos antes). `revisar.md` §4 atualizado + espelho regenerado.

## 4r. Sessao de uso s168 (Claude Code/Opus 5, 2026-09-07) -- precificacao da grade: achado F77

### F77 -- `grade.json` nao guarda questoes por tarefa, e o rateio igual que o contrato manda erra por ate 3x -- **MEDIA** -- **ABERTO**
- **Evidencia (s168):** o usuario pediu "quantas questoes somam estes temas?". `core/cronograma/grade.json` so tem `total_questoes` no nivel da SEMANA; o comentario do `parse_grade` (`tools/cronograma.py`, bloco do `wq`) instrui explicitamente: *"NAO atribuimos count por task: o PDF nao amarra link[i]<->task[i] de forma garantida (ultraplan §c.5) -> o consumidor rateia igual (total_questoes / n_tasks)"*. Na S17 o rateio daria **26,6q para toda tarefa**, quando as tarefas reais valem de **16q (Pneumonias Bacterianas) a 50q (APS Revisao)** -- erro de ate 3x, justamente na dimensao que o usuario usa para planejar o dia.
- **O dado ja existe e nao e gravado:** `_parse_detail()` **ja calcula** `questoes` por tarefa (soma dos `Link - NN questoes` dentro do bloco da tarefa). O valor e computado e descartado -- `parse_grade` monta o dict de task sem ele.
- **A desconfianca do contrato e testavel, e passou:** re-parseei S17-S20 e a **soma das tarefas bate exatamente com o total da semana nas quatro** (293/380/449/301). Nenhum link ficou orfao. Sobrou uma anomalia -- APS (Teoria III) da S17 com 0q -- que tinha a forma de atribuicao trocada e **foi resolvida por evidencia externa**: no xlsx do usuario essa linha esta **riscada**. Dois sinais independentes concordando.
- **Remedio (S):** gravar `questoes` por task no `grade.json` **com marca de confianca** (`questoes_fonte: "link_no_bloco"`) e um invariante no `rebuild`: se `sum(task.questoes) != total_questoes` da semana, emitir WARN e cair para o rateio igual naquela semana. Assim o dado bom viaja e o caso duvidoso degrada para o comportamento atual, em vez de o dado bom ser jogado fora preventivamente em 100% das semanas.
- **Remedio (M):** `cronograma.py --semana N` passar a imprimir a coluna de questoes por tarefa -- hoje o usuario nao tem CLI que responda "quanto vale esta tarefa?" sem re-parsear o PDF a mao.
- **Padrao de fundo:** e um primo do achado de alcancabilidade -- um dado **construido e deliberadamente descartado** por uma desconfianca que nunca foi medida. A desconfianca era razoavel em 2026-07; custou 3 sessoes de planejamento cego e nao tinha teste.

### F77b -- `_parse_detail` so reconhece `Livro Digital:` e perde o tema dos blocos "Revisao por Questoes" -- **BAIXA** -- **ABERTO**
- **Evidencia (s168):** ao montar o bloco de links do artifact, as 5 tarefas do tipo "Revisao por Questoes" (S18 t12/t13, S19 t11/t12/t13) sairam com `tema_detail` vazio. Causa: o regex de `_parse_detail` (`tools/cronograma.py`) exige o literal `Livro Digital:`, mas essas tarefas usam `Assunto:` -- ex.: *"Obstetricia Assunto: Pre-Natal; Assistencia ao Parto; Vitalidade Fetal (Revisao por Questoes)"*. Resultado: o `grade.json` grava essas 5 tarefas por ciclo com `tema` vazio.
- **Impacto:** e exatamente a familia do drift "Revisao por Questoes" ja registrado (tarefa multi-tema que cai em campo emprestado e fica subnotificada). O tema esta escrito no PDF e o parser o joga fora -- mesmo padrao do F77, um degrau abaixo.
- **Remedio (S):** trocar o literal por `(?:Livro Digital|Assunto):` no regex de `_parse_detail`. Uma linha; 5 tarefas por ciclo deixam de nascer sem nome.

### F78 -- Extracao de PDF descarta em silencio todo conteudo que vive em FIGURA, e nada no harness mede essa perda -- **MEDIA** -- **ABERTO (mitigacao demonstrada)**
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

### F79 -- `audit_resumos.py` era cego a 5 das proibicoes DURAS da spec; a conformidade vinha da disciplina manual, nao do gate -- **MEDIA** -- **RESOLVIDO (s169)**
- **Evidencia (s169):** ao auditar por fora o resumo de SUA depois de aplicar as licoes do bloco, meu lint ad-hoc acusou **emoji em header** e **bloco de codigo** -- as duas coisas proibidas em letra maiuscula no `estilo-resumo.md` -- num arquivo que o `audit_resumos.py` declarava "AUDITORIA PERFEITA". Inspecao do linter: ele checa seccao Armadilhas (BLOCK), tabela ASCII (BLOCK), marcadores (WARN), frontmatter §5.2 (WARN) e encoding proibido (WARN). **Nao checa**: emoji em header H1/H2/H3, bloco de codigo/fluxograma ASCII, bullet `✅`/`❌`, campo `estilo:` no frontmatter, rodape editorial em italico. Cinco proibicoes que a spec chama de duras e nenhum gate observava.
- **Por que so apareceu agora:** os 10 resumos do sprint sairam limpos, mas **nao por causa do gate** -- sairam limpos porque cada regra foi repetida a mao no brief de 10 subagentes e conferida por fora, num script meu. Disciplina de orquestrador nao escala e nao sobrevive a sessao. Medida do passivo real no acervo: **22 arquivos** violando (18 emoji em header, 4 bloco de codigo, 2 bullet proibido); zero com `estilo:` ou rodape editorial (esses ja tinham sido limpos a mao em sessoes anteriores -- e a limpeza manual nao deixou gate atras de si).
- **Remedio aplicado:** check 6 `[SPEC]` em `audit_resumos.py`, nascendo **WARN** conforme a politica warning-first (`regra nova nasce WARN, so vira BLOCK quando a base zerar`). Suite `tools/test_audit_resumos.py`, inscrita em `pytest.ini` (`python_files`) -- o F43 pegou a suite orfa na primeira tentativa, o que e o check funcionando.
- 🔴 **O bug dentro do conserto (vale mais que o conserto):** na primeira escrita do check, um caractere de **backspace literal (0x08)** entrou no regex do rodape editorial no lugar de ``. O linter continuava verde, a suite nao existia ainda, e o sub-check estava **MORTO** -- so casaria com um backspace, que nenhum resumo contem. Um teste do tipo "roda sem explodir" nao pegaria. Por isso a suite prova **cada sub-check disparando sobre um caso positivo sintetico**, e o caso do rodape esta anotado como regressao do 0x08. Padrao: *gate escrito, gate nunca disparado* -- primo do F78 (perda que ninguem mede) e do achado de alcancabilidade.
- **Dividas que ficam abertas:** os 22 arquivos com WARN. Nao foram corrigidos em massa nesta sessao (fora do escopo do que o usuario pediu); ficam visiveis no agregado do linter ate serem tratados, que e exatamente o que o modo WARN existe para fazer.

### F80 -- Writers do `ipub.db` discordam de FUSO: `fsrs_revlog`/`questoes_erros` gravam em UTC, `sessoes_bulk` grava em local -- **MEDIA** -- **RESOLVIDO (hotfix s174, `.vibeflow/hotfixes/2026-09-09-fuso-unico-writers.md`)**
- **Evidencia (s169):** as 21:30 do dia 07/09 (hora local), o `fsrs_revlog` carimbou `review_time = 2026-09-08 00:29` e o `questoes_erros` carimbou `data_registro = 2026-09-08 00:20`, enquanto as 3 linhas de `sessoes_bulk` da mesma sessao ficaram em `2026-09-07`. Confirmado com `select datetime('now')` (UTC 2026-09-08 00:30) x `datetime('now','localtime')` (2026-09-07 21:30). Nao e drift de relogio: sao writers diferentes escolhendo referenciais diferentes no MESMO banco, na MESMA sessao.
- **Custo ja pago nesta sessao:** o subagente que analisou os erros de APS concluiu, com toda razao aparente, que *"a sessao cruzou a meia-noite"* e reportou isso como observacao. A sessao nao cruzou nada -- eram 21:30. Ou seja, o defeito **produz uma conclusao factualmente errada em quem le o banco**, que e o pior tipo de defeito de dado: nao quebra, mente.
- **Onde isso morde de verdade:** (a) qualquer join erro<->volume por data ve um deslocamento fantasma de 1 dia entre 21h e 00h locais; (b) o check **F38 (ERROS_ORFAOS)** usa janela `d..d+1` e hoje **so nao acusa falso-positivo porque a janela e frouxa** -- a frouxidao esta encobrindo o bug, nao o resolvendo; (c) a regra do HANDOFF "os cards de relearning so regravam em sessao-calendario nova" depende de qual coluna se olha para decidir o que e "novo dia".
- **Remedio (S):** eleger UM referencial (proposta: **local**, porque e o que o usuario enxerga e o que `sessoes_bulk` -- a SSOT volumetrica -- ja usa) e passar todos os writers por um unico helper de timestamp em `app/utils/db.py`, em vez de cada um chamar seu proprio `now`.
- **Remedio (M):** teste de invariante que grave nas 3 tabelas na mesma chamada e asserte que as datas concordam. Sem isso a correcao volta a divergir no proximo writer novo.
- 🔴 **Nao corrigir retroativamente sem decisao explicita do usuario:** reescrever timestamps historicos e operacao destrutiva sobre SSOT (AGENTE §1.1) e distorceria o revlog que o FSRS usa para calibrar. O remedio e go-forward.
- **Fechamento (s174, 2026-09-09; GO do `/ai-eng` com zona canonica = LOCAL, revertendo a ALTERA "UTC no db" diante da evidencia de que o nucleo FSRS grava local por construcao):** relogio unico `db.agora()/carimbo()/hoje()`; 4 writers (nao 3: `review_log.reviewed_at` tinha o mesmo defeito) passam o carimbo explicito; `tools/test_fuso_unico.py` congela o instante nos 4, prova o leitor `realizado_do_dia` e varre `tools/`+`app/` -- writer novo que caia no DEFAULT falha nomeando o arquivo. **Commit-fronteira:** o commit deste hotfix (s174, `git log --grep F80`); linhas anteriores das 3 colunas seguem em UTC (shift constante -3h, Brasil sem horario de verao desde 2019). **Backfill = item separado**, dry-run + COUNT-ASSERT contando linhas que mudam de DIA, gatilho do operador. **Sub-achado aberto (F80b):** `get_cards_by_bucket` compara `fc.due` (local) com `datetime('now', '-48 hours')` (UTC) na janela de erro fresco -- 3h de erro em 48h; nao tocado (uma chamada, um bug).

### F79b -- `card_self_sufficiency.py` nao pega pergunta com DEIXIS sobre contexto vazio -- **MEDIA** -- **ABERTO**
- **Evidencia (s169):** o card **#367** tem `frente_contexto = ''` e pergunta *"Que elementos **do caso** (historico do paciente e circunstancia do achado) classificam **essa** morte como suspeita...?"*. O caso nao existe no card -- a pergunta e literalmente inrespondivel como posta, e o usuario a sinalizou no drill ("reforja"). Rodei `card_self_sufficiency.py --json`: 10 achados no banco inteiro, e **367 nao esta entre eles**.
- **O buraco:** o check procura auto-suficiencia por outros criterios, mas nao cruza **dexis** (`do caso`, `essa`, `esse paciente`, `nesse cenario`, `descrito acima`) com **contexto vazio ou minimo**. E justamente a combinacao que produz card impossivel: a pergunta faz referencia anaforica a um antecedente que foi descartado na cunhagem.
- **Familia:** e o mesmo padrao do **F79** -- gate existe, gate nao cobre o caso que ele foi criado para cobrir. Dois checkers cegos descobertos na mesma sessao, os dois por leitura humana e nao por gate.
- **Remedio (S):** predicado novo em `tools/card_checks.py` (a biblioteca UNICA de predicados de qualidade) -- `frente_pergunta` casa regex de dexis **E** `frente_contexto` vazio/< N caracteres -> achado. Nasce WARN, como o check 6 do F79.
- **Remedio (M):** varredura do banco com o predicado novo para dimensionar o passivo antes de decidir promocao a BLOCK.

### F81 -- `frente_contexto` DESALINHADO da `frente_pergunta`: 3 eixos de defeito que nenhum predicado de `card_checks.py` mede -- **MEDIA** -- **ABERTO**
- **Origem (s170):** achado do USUARIO durante o DRENAR, nao do harness. Depois de sinalizar "reforja" em 3 cards do mesmo bloco (#243, #792, #321), ele nomeou o padrao: *"note que todas as perguntas aparentam o padrao da de crise convulsiva do bloco anterior: parece que contexto e pergunta 'falam de coisas diferentes'"*. E o 3o caso consecutivo de defeito de card descoberto por leitura humana e nao por gate (familia F79 / F79b).
- **O buraco estrutural:** `checar_resposta_embutida` compara **frente x verso**. Nenhum predicado compara **contexto x pergunta**. O eixo inteiro do alinhamento interno da FRENTE esta fora de cobertura.
- **Varredura (read-only, 904 cards ativos com contexto+pergunta preenchidos), 3 eixos:**
  - **A -- contexto redundante** (`containment >= 0.70`: a pergunta reengole o contexto inteiro): **26 cards (2,9%)**. Casos extremos: **#673** (`contexto` == a pergunta, palavra por palavra), **#525** (idem, so muda "achado" -> "achado radiologico"), **#664** (`contexto` = "Gestante convulsionando por eclampsia; **pergunta a PRIMEIRA medida**" -- artefato de pipeline vazado para dentro do campo). O contexto nao faz trabalho nenhum: nao adiciona dado, so ocupa a tela antes da pergunta repetir tudo.
  - **B -- conclusao asserida no enunciado** (`^Por que ...` + proposicao NEGADA: "por que X **nao pode/nao deve/nao entra**"): **10 cards** de 67 perguntas "Por que" com contexto. O aluno nunca precisa **produzir** a conclusao -- ela ja esta afirmada -- so justifica-la. Vira reconhecimento, nao recall. Exemplares: **#321** (`Por que um FAST com figado conservado nao deve afastar a indicacao cirurgica quando a TC mostra ar retroperitoneal?`), **#365** (`Por que uma etapa causal condensada nao pode ser recuperada colocando-a na Parte II?`), **#1537** (na fila de hoje). 🔴 **Nao e defeito automatico:** quando o alvo cobrado E o mecanismo, "por que X nao deve" e card legitimo (**#1375**, daptomicina no VRE, e bom). O defeito e quando a proposicao asserida e ela propria a coisa testada. Exige triagem humana -> nasce WARN.
  - **C -- contexto CONTRAFACTUAL** (vinheta descreve o cenario A, pergunta cobra o achado que apontaria para nao-A): **#792** -- vinheta de crise inequivocamente epileptica, pergunta cobra "qual achado apontaria para crise NAO epileptica". O contexto trabalha **contra** a pergunta. Nao e capturado por nenhuma das duas metricas (containment 0.0, run 0) -- e semantico. Eixo nomeado e **nao medido**; dimensiona-lo exige leitura, nao regex.
- **Por que os eixos A/B nao pegam o que o usuario viu:** os 4 cards que ele flagrou dao `containment` 0.467 / 0.095 / 0.2 / 0.0. Ou seja, a metrica de sobreposicao encontrou uma **classe real e diferente** (A) e a de proposicao asserida encontrou **parte** do que ele viu (B, pega #321 e #365 mas nao #243 nem #792). A intuicao humana agregou 3 defeitos distintos sob um mesmo sintoma percebido ("falam de coisas diferentes"). Registrar os 3 separados evita corrigir o passivo errado.
- **Remedio (S):** predicado `checar_contexto_desalinhado` em `tools/card_checks.py` cobrindo A (containment sobre `_norm_tokens`, reusando `_maior_run_comum` que ja existe) -- WARN, com o corte a calibrar sobre os 26. Eixo B entra como predicado separado, tambem WARN, porque tem falso-positivo legitimo.
- **Remedio (M):** os 26 do eixo A sao passivo de **reforja de FRENTE** (memoria `feedback_reforja_mira_frente`): ou o contexto vira vinheta com dado concreto, ou vira vazio de verdade. Fila via `cards_regen_queue.py`.
- **Nao fazer:** promover a BLOCK antes de zerar o passivo (convencao warning-first, AGENTE §6). E nao tentar medir o eixo C com regex -- e leitura.

## 6o. Achados da s170 numerados na s171 (2026-09-08, Claude Code/Opus 5 + audit do `/ai-eng`)

> Os quatro nasceram na s170 e foram entregues/deferidos SEM F-id -- o `§10.6` cumprido pela metade
> (achado tratado, achado nao registrado). Numerados aqui a pedido do `/ai-eng` (G2 da colheita de 09-08).
> **F82-F84 ja estavam RESOLVIDOS quando ganharam numero**; o registro existe para que o ledger tenha
> a evidencia da CLASSE, nao para reabrir trabalho.

### F82 -- Reforja executada nao deixava rastro: `event_log` so existia no caminho de CRIACAO -- **ALTA** -- **RESOLVIDO (hotfix s170, `c4ce1db`)**
- **Evidencia:** unico chamador de `event_log.registrar` no repo era `tools/insert_questao.py:39-41` e `:296-301`, e so para card NOVO (tipos `generation`/`reincidencia`). `app/utils/db.py::update_flashcard_fields` reescrevia o card, incrementava `card_version` e commitava **sem emitir evento**. Como `flashcards` nao tem timestamp de update, a reforja era a **unica operacao do pipeline que muda o SSOT sem deixar registro**.
- **A prova que forcou o hotfix:** o card **#321** estava em `card_version=2` com o texto do defeito **INTACTO** -- a versao subiu sem fix e nada registrava isso. Corolario duro: **`card_version` nao e evidencia de reforja feita**, e por isso o fechamento de marca nunca pode ser inferido dele (vira fixture do spec da fila de reforja).
- **Fix:** evento `reforja` emitido **so pos-commit** nos 2 writers, com `card_id`, writer, version antes/depois, reason e nomes de campo -- **zero texto clinico** (contrato do `event_log`). No `recurate_cards.aplicar` os eventos acumulam em `pendentes` DENTRO da transacao e so saem em `_flush_eventos` apos o commit: emitir no laco daria evento-fantasma no rollback, e o lote e all-or-nothing.
- **Regressao:** `tools/test_reforja_event_log.py`, 6 testes, **vermelho antes do fix**. Os 2 caminhos que commitam -> exatamente 1 evento; os 3 que NAO commitam (card inexistente, gate levantando, rollback do lote) -> ZERO; falha de log nao derruba a escrita do card.
- **Classe:** *Reachability-Debt variante 1* -- a auditoria de reincidencia lia uma populacao que o pipeline nunca populou.

### F83 -- Nada media CRESCIMENTO do verso, e o 2o writer nao tinha gate de atomicidade nenhum -- **MEDIA** -- **RESOLVIDO (s170, `d2026a1`)** + 1 sub-achado **DEFERIDO**
- **Evidencia:** cards em `card_version=4` acusam **46,8%** de defeito, **20/47** por verso estourado. Cada rodada de reforja adiciona frase ao verso -- **a reforja mira a frente e engorda o verso** (memoria `feedback_reforja_mira_frente`), sem ninguem medir. 🔴 **Claim causal fica [MEDIUM]**, confundidor de selecao declarado: card com 3 rodadas E o card dificil que continua falhando. A evidencia DIRETA e o estouro de `LIMITE_CHARS`.
- **O gate que faltava nao era "verso longo"** -- esse ja existia, **ABSOLUTO**, em `audit_card_atomicity.checar_verso`. Era **CRESCIMENTO**: um verso de 100 -> 219 chars passa limpo pelo absoluto e mesmo assim inchou 2x.
- **Fix:** `medir_verso()` + `checar_ratchet_verso()` puros, ao lado da fonte unica `LIMITE_CHARS` (nao duplica a constante). Teto = `max(LIMITE_CHARS, len(antes))` -- card que ja nascia longo pode ser reescrito no mesmo tamanho: o gate mede crescimento, **nao pune heranca**. Gate 5 em `recurate_cards.validar` entra em `erros` (BLOCK), nao em `avisos`. Telemetria `len`/`n_frases` antes e depois no evento `reforja`: **o mesmo caminho que mede para bloquear grava para medir**, e e o que converte o [MEDIUM] em medicao.
- 🔴 **O achado tem TRES partes, nao uma** (correcao do `/ai-eng` no audit): **(a)** parametro morto `permitir_atomicidade` em `validar()` -- **DEFERIDO**, segue aberto; **(b)** nada media crescimento -- resolvido; **(c)** `db.update_flashcard_fields` **nao rodava gate de atomicidade nenhum** -- resolvido. Sem (c) a guarda do recurate seria contornavel pelo outro writer: seria o F79/F79b/F81 (gate que nao cobre o caminho real) se repetindo pela quarta vez.
- **Regressao:** `tools/test_ratchet_verso.py`.

### F84 -- O gate novo era fail-open: `ImportError` virava WARN e a escrita passava SEM ratchet -- **MEDIA** -- **RESOLVIDO (s170, `06634b6`)**
- **Origem:** achado do **audit do `/ai-eng`** sobre o `d2026a1` -- nao do harness, nao da sessao que escreveu o fix.
- **Evidencia:** em `db.update_flashcard_fields`, `ImportError` de `audit_card_atomicity` virava `[WARN]` e a escrita seguia sem ratchet. 🔴 **E a regra de ouro do repo ("aviso que nao bloqueia nao existe -- vira gate") sendo violada DENTRO do proprio fix que existe para aplica-la.**
- **Fix:** gate que nao pode rodar => **escrita RECUSADA** (`RuntimeError`). A recusa vale so quando a escrita **toca o verso** -- bloquear edicao de frente por causa do ratchet do verso seria gratuito; nesse caso so a telemetria degrada, com WARN. Ressalva aceita pelo `/ai-eng` no mesmo turno.
- **Regressao:** 2 testes com `sys.modules` monkeypatchado para forcar o `ImportError`: escrita de verso recusada com `card_version` intacto; edicao de frente segue passando. O caminho do `recurate` ja era fail-closed -- confirmado no audit, o fix nao herdou o bug.
- **Licao transferivel:** *o fix que introduz a classe que ele conserta*. Custo de deteccao: um audit externo entre parts. Sem ele o repo teria um gate BLOCK com porta dos fundos.

### F85 -- Justificativa ORFA governando um `except`: a premissa morreu, o `except` continua -- **MEDIA** -- **RESOLVIDO (hotfix s174, `.vibeflow/hotfixes/2026-09-09-justificativa-orfa-card-gate.md`)**
- **Evidencia:** `app/utils/db.py:760-765` (comentario) e `:773-775` (o `except`). O 2o gate fail-open da MESMA funcao -- o import de `card_checks` -- carrega a justificativa escrita: *"indisponivel -> WARN e segue (a camada CLI ja valida; **o app nao pode quebrar sem tools/** -- degradacao anunciada)"*. Esse "app" era a **UI Streamlit, REMOVIDA** (AGENTE.md secao 6). **A justificativa sobreviveu ao seu proprio motivo** e segue autorizando escrita sem gate de qualidade.
- **Por que nao foi corrigido junto:** observado durante o `06634b6` e deixado no ledger de proposito -- mudar blast radius alheio no mesmo commit de um fix de audit e o anti-padrao. *Uma chamada, um bug.*
- **Varredura da assinatura (s170):** 4 ocorrencias brutas, triadas pelo discriminador **"a premissa esta no caminho de decisao?"** -- **Classe 1** (premissa governando codigo) **N=1**: este. **Classe 2** (claim envelhecido em docstring, nao governa): `db.py:9` ("Callers acima: `app/pages/*.py`") e `fsrs_queue.py:9` ("o player Streamlit local") -- correcao de **documentacao**, sem teste. `get_topic_context.py:19` = lapide em preterito, **NAO tocar**.
- **Remedio (S) -- hotfix, item (7) da fila s171:** teste com `sys.modules` **ANTES** do fix (escrita recusada quando `card_checks` nao importa) -> fail-loud -> remover o comentario. Mesma forma do F84, que e o irmao gemeo desta funcao.
- **Classe:** *Reachability-Debt variante 3* -- **le uma razao que ja nao existe**. Fecha a taxonomia das tres: (1) le o nada [F82] · (2) ninguem le [G1, graphify] · (3) le razao morta [F85].
- **Fechamento (s174, 2026-09-09; GO do `/ai-eng` nos termos do ledger):** `except` vira `RuntimeError(... RECUSADA)`, `if _cc is not None` e o `print` em stdout morrem, comentario orfao substituido por lapide. Classe 2: `fsrs_queue.py:9` reescrito; `db.py:9` ja reescrito pelo F80 na mesma sessao. `get_topic_context.py:19` intocado. 4 testes em `tools/test_card_gate_fail_loud.py` (3 vermelhos antes). Smell que fica: `app/utils/db.py` importa `tools/card_checks.py` por `__file__` (mover = spec).

### F86 -- O gate do F43 validava por SUBSTRING: mencao contava como inscricao -- **ALTA** -- **RESOLVIDO (hotfix s171, `.vibeflow/hotfixes/2026-09-08-suite-mencionada-nao-inscrita.md`)**
- **Origem:** achado DENTRO do hotfix `clausula-revogada-em-vigor`, na mesma sessao. Nao veio de varredura -- veio de um numero que nao subiu.
- **Evidencia:** `tools/test_contrato_revogado.py` nasceu com 12 testes e **fora do `python_files` do `pytest.ini`** (que e allowlist explicita, nao glob). **12 testes escritos, ZERO executados** -- a suite ficou em `395 passed` antes e depois de acrescentar 12 testes. E o `SUITES_ORFAS` **passou verde o tempo todo**: `check_suites_orfas` fazia `blob = "".join(corpus)` e testava `nome not in blob`, entao o nome bastava aparecer em QUALQUER lugar dos 3 registros -- e ele aparecia numa **mensagem de WARN** dentro do proprio `auto_check.py`, escrita no mesmo commit pelo autor do gate novo.
- 🔴 **A falha e auto-infligivel por construcao:** quem escreve um gate novo naturalmente cita o nome da suite na mensagem de erro desse gate. A mencao que satisfez o verificador foi produzida pelo proprio ato de verificar. Um gate inteiro (`CONTRATO_REVOGADO`) esteve a um `git commit` de entrar sem nunca ter rodado, com o harness dizendo PASSED.
- **O erro tinha DOIS sentidos.** Falso-negativo (mencao = inscricao) e falso-positivo simetrico: `python_files` sao **padroes** casados por fnmatch, e com `python_files = test_*.py` uma suite realmente coletada seria acusada de orfa, porque o nome nao e substring do padrao. Mesma causa unica: ignorar a estrutura.
- **Ja estava registrado, sem caso e sem fixture:** anexo dos menores da s160 -- *"`suites_orfas` valida por substring (mencionada != inscrita)"*. Ficou como observacao por 9 dias. 🔴 **Observacao sem fixture nao e cobertura** -- e a mesma licao do D3 ("warning-first virou warning-only") aplicada ao ledger em vez do painel.
- **Fix:** cada registro lido pela sua ESTRUTURA. `pytest.ini` -> campo `python_files` casado por **fnmatch** (como o pytest decide). `auto_check.py` e `test_pytest_bridge.py` -> `ast.parse` recolhendo nomes `test_*.py` passados a um **verbo de execucao**, inclusive via lista montada em variavel antes da chamada (formato real do `auto_check`). Registro ilegivel = nao cobre, nunca levanta.
- **Contrafactual verificado:** `_suites_executadas(auto_check.py)` = `['test_card_self_sufficiency.py', 'test_day_plan_telemetria.py', 'test_fsrs_balance.py']` -- o nome do caso real NAO esta la, embora exista no arquivo como texto. Sem a inscricao no `pytest.ini`, o predicado novo o acusa.
- **Serie gate-miss (§10.8), classe TOOLING** -- distinta da classe CONTEUDO (F79/F79b/F81, que e `card_checks` cego a defeito de card). Decisao do `/ai-eng` na s171: o contador de gate-miss carrega o campo `classe` e conta **por classe**; misturar as duas mata o numero. F86 e a **1a fixture da classe tooling**; o filtro `quality_source='heuristic'` da fila de reforja e o predicado que so vivia em `avisos` sao os casos historicos sem fixture.
- **Classe:** *"le o nada" aplicado ao proprio verificador* -- um gate que valida por presenca TEXTUAL em vez de por EXECUCAO vigia uma populacao que ele mesmo pode fabricar.

---

---

## 6p. Sessao de uso s172 (Claude Code/Opus 5, 2026-09-09) -- 1o teste em producao do 6o principio: achado F87

> A fila de engenharia segue CONGELADA por decisao do operador. F87 e **registro**, nao agendamento --
> existe para que a classe tenha evidencia quando a fila descongelar.

### F87 -- O harness de flashcard verifica FORMA e e cego a RENDIMENTO: os 13 cards que o operador reprovou passam em TODOS os predicados -- **MEDIA** -- **ABERTO**

- **Como apareceu:** o 6o principio do `estilo-flashcard` (alternativa errada = no) foi aplicado ao Simulado 8 e rendeu **85 candidatos para 17 erros**. O agente triou para 45; o operador julgou os 85 um a um numa bancada dedicada e **inverteu 25 vereditos (29%)**, fechando em 44. Veredito literal dele: *"ampliou os pontos de conteudo passiveis de expansao, mas cunhou bastante ruido -- o que eu justamente temia. nesse sentido, os cards realmente precisam de juizes de qualidade ate mesmo pedagogica."*
- 🔴 **A evidencia dura:** os **13 cards que ele cortou passam** no `audit_card_atomicity.py`, no `card_self_sufficiency.py` e nos predicados de `tools/card_checks.py`. Sao atomicos, tem UM criterio de acerto, frente gerativa, verso curto, contexto alinhado. **Nenhum predicado do repo mede se o card vale a pena.** O harness responde "esta bem formado?" e nunca "isto acrescenta recall?".
- **O sinal, medido:** o que ele RESGATOU (12 cards) era `conteudo` em 8 dos 12 -- fato arbitrario que nao se deduz (janela de 48-72 h; resolucao em 7-10 dias; SIRI em 4-8 semanas; bilirrubina > 0,2 mg/dl/h; diabetes = 25% dos polidramnios; "grao de cafe"; doxiciclina 100 mg 12/12 h por 7 d; reforco faltante da febre amarela). O que ele CORTOU (13 cards) era `discriminador` (5), `mecanismo` (2) e `nuance` (2) -- resposta **regeneravel** a partir do card-nucleo mais o mecanismo, ou o proprio raciocinio da questao reescrito como pergunta.
- ⚰️ **O caso que derruba a intuicao do agente:** *"por que insuficiencia uteroplacentaria, RCF e pos-datismo cursam com oligoamnio?"* foi celebrado na s171 como o melhor achado do 6o principio (um card resolvendo tres alternativas pelo mesmo mecanismo). **O operador cortou.** Resolver tres alternativas de uma vez e o sintoma, nao a virtude: se um mecanismo unico explica as tres, o aluno as reconstroi e o card nao mede nada.
- **O nucleo nunca oscilou:** dos 85 candidatos, os **12 `elo_quebrado` sobreviveram sem uma unica inversao**. O criterio "nucleo do erro intocavel" esta validado; o que falhou foi tudo o que orbita.
- 🔎 **O unico predicado que reagiu -- e reagiu no lugar certo.** Apos aplicar o corte dele, o `insert_questao.py` emitiu `[AVISO-CARD] distrator-perdido` em exatamente **2 dos 17 erros** (Liquido Amniotico e HIV): sao os dois em que os cards cortados eram justamente os que carregavam a alternativa marcada. **Existe UM predicado adjacente a rendimento no repo, ele funciona, e ele nao bloqueia** -- ele marca a tensao real entre o 6o principio (ler as alternativas) e o filtro de regenerabilidade (cortar o que se deduz). Candidato natural a fixture de qualquer predicado futuro de rendimento.
- **Remedio aplicado agora (documental, nao codigo):** `estilo-flashcard.md` ganhou o §Triagem com o **teste de regenerabilidade** e o corolario que inverte a heuristica (`conteudo` rende mais que `discriminador` derivado da mesma questao). A triagem fica **humana e antes do `insert_questao.py`**, com a lista integral guardada em disco para o operador derrubar o corte.
- **Classe:** familia CONTEUDO (com F79/F79b/F81 -- `card_checks` cego a defeito de card), mas num eixo novo: os anteriores sao **defeito de forma que o gate nao ve**; F87 e **ausencia de forma defeituosa em card que nao deveria existir**. Um gate de rendimento, se algum dia existir, nao e um predicado sobre o texto do card -- e sobre a relacao entre o card e o resto do conjunto.

## 6q. Sessao de engenharia s174 (Claude Code/Fable 5.1 + `/ai-eng` orquestrando, 2026-09-09) -- ciclo A do destilado: F71 · F88 (novo) · F80 · F85 · F76

Protocolo `AGENTE.md §10.6` (D71): implement E audit aqui, vereditos do `/ai-eng` por item (GO com ALTERAs: ordem F71 -> F80 -> A5 -> F85 -> F76; A6 so dry-run). Traces em `.vibeflow/hotfixes/2026-09-09-*.md`.

### F88 -- `cronograma --gap` e o boot reportavam pares DIFERENTES de acumulado/meta lidos do mesmo banco (duas contas, G4) -- **MEDIA** -- **RESOLVIDO (hotfix s174, `.vibeflow/hotfixes/2026-09-09-gap-volume-fonte-unica.md`)**
- **Evidencia (s173, numerado aqui -- regra G2):** `--gap` = `meta 10000 / acumulado 6305`; `day_plan` do mesmo instante = `10400 / 7036`; db = 7.036. Causa: `--meta default=10000` literal de argparse (marco ENAMED revogado na s126, nunca re-medido -- D67) + `escopo="cronograma"` excluindo o Simulado (contra a decisao s126). So o `day_plan` lia `MARCOS`.
- **Remedio (ALTERA do `/ai-eng`):** UMA funcao `performance.volume_vs_marco(conn, hoje)` chamada por `day_plan.build` e por `cronograma.gap_payload`; `--meta` vira what-if (`default=None`). Teste: mesma fixture, dois comandos, mesmo par + AST sem default literal >= 1000. **Absorveu os 2 riders do F71:** (a) overflow do blackout no painel do boot via `db.overflow_blackout` (estado do banco, nao log); (b) leitor UNICO de `core/provas.json` em `app/utils/provas.py` (`day_plan` re-exporta, `db` delega).
- **Classe:** Claim-Aging (D67) em literal de CLI -- numero em canonico que nenhum leitor re-mede. 5 testes em `tools/test_volume_fonte_unica.py`, 5 vermelhos antes.

### F89 -- Areas fantasma `GO` e `Clinica Medica` VOLTARAM apos a dissolucao da s097: nenhum writer de taxonomia valida `area` -- **MEDIA** -- **ABERTO (so-dado; remedio = spec)**
- **Evidencia (dry-run A6, 2026-09-09, `docs/DRYRUN-F65-F67-2026-09-09.md`):** a RODADA 1 do `normalize_taxonomia.py` (s097) dissolveu as areas `GO` e `Clinica Medica`; hoje existem de novo, com ids novos: `GO` 299, 301, 347, 348, 417 · `Clinica Medica` 285, 286 -- 7 linhas, 39 cards + 33 erros. `AREAS_VALIDAS` vive so em `registrar_sessao_bulk.py`; `insert_questao.py` e `insert_card_base.py` criam a linha `(area, tema)` que receberem.
- **Por que e gate-miss (§10.8, tooling):** a normalizacao foi operacao unica sem gate de retorno; o defeito reentrou pela porta dos writers. Mesma familia do F65/F67 (taxonomia que corrompe sensor): o `review_radar`/`infer_nota` leem metades.
- **Remedio (spec, nao hotfix):** `AREAS_VALIDAS` vira fonte unica (em `app/utils/` ou `core/`), validada nos 3 writers de `taxonomia_cronograma` (F49 allowlist) com fail-loud; WARN no `auto_check` para linha com area fora da lista (nasce WARN, vira BLOCK quando a base zerar). Entra na RODADA 3 do normalizador (decisao do operador).
- **Achado-irmao (A6):** o `normalize_taxonomia.py` esta VAZIO para o problema -- suas operacoes declaradas ja foram aplicadas (perdedores 230/225 inexistentes) e simula 286 -> 286. Reachability-Debt variante 1 (le o nada). Medicao completa: F67 = 10 grupos / 22 linhas / 193 cards + 104 erros; F65 = 35 cards ativos presos em `[bulk]` (eram 72 na s162) + **201 erros** em balde (nao medido antes).

## 6r. Sessao de ESTUDO s175 (Claude Code/Opus 5, 2026-09-10) -- F90

### F90 -- `revisar.md` carrega DUAS linhas revogadas que contradizem o Invariante F e a regua de lote; o agente as obedeceu -- **MEDIA** -- **RESOLVIDO (s176, 10/09/2026 -- (i)+(ii) no mesmo commit)**

- **Como apareceu:** correcao direta do usuario no 3o turno da s175, apos o 1o bloco do DRENAR: *"Voce saiu completamente do padrao. Esta dando feedback de card nota 3 e 4, dividindo os blocos em 'menores' e ainda colocando esse trem no cli: `<sub>...</sub>`. Voce deu o boot direito, mestre?"*
- **Evidencia (as duas linhas, no canonico `.claude/commands/revisar.md`):**
  1. **§Protocolo do loop conversacional, passo 4:** *"**Informar a nota proposta** ('-> 3') + justificativa em 1 linha."* -- contradiz o **Invariante F** (mesma skill, secao superior): *"Durante o DRENAR o agente entrega verso + nota + tally, e nada mais. Zero prosa explicativa entre blocos, inclusive para nota 1 e 2."*
  2. **§Modo conversacional padrao:** *"Apresentar N frentes de uma vez (default ajustavel -- o usuario pediu 3, depois 5, depois 6)."* -- a regua real e **10-15**: s130 pediu blocos de 10 (memoria `feedback-revisar-apresentacao-cards`, que corrige explicitamente "isso NAO e pedido para reduzir o tamanho do bloco") e a s152 rodou 90 cards em blocos de 15 (`feedback_revisar_pipeline_blocos`).
- 🔴 **Por que e gate-miss DE VERDADE (§10.8), e nao so drift documental:** o gate que deveria ter pego **existe, esta aceso e mira este arquivo**. `auto_check.py:100-119` implementa o **`CONTRATO_REVOGADO` (G12/G11, s171)**, que varre `_PORTADORES_NORMA` -- lista que inclui **`.claude/commands/revisar.md` nominalmente** -- procurando prescricao ativa de mecanismo revogado fora de lapide. Ele rodou nesta sessao e reportou **PASSED, zero achados**.
  - **Por que passou:** o registro `_TERMOS_REVOGADOS` (`:104-108`) tem **exatamente 3 entradas** -- `PREPARAR`, `Camada 0`, `Camada 1` -- todas da mesma revogacao (Clausula 11, s170). O gate so ve o que alguem lembrou de cadastrar.
  - 🔴 **E o proprio comentario do codigo declara a premissa que falhou** (`:102-103`): *"Extensivel: revogacao nova entra aqui e o gate passa a vigiar o termo em TODOS os portadores. O registro e a fonte unica -- ninguem enumera a mao."* O registro **e** enumerado a mao, e ninguem enumerou as revogacoes do **Invariante F** (prosa no meio do DRENAR) nem a regua de lote **10-15** (s130/s152). O mecanismo esta certo; a alimentacao dele nao tem gatilho.
  - **Classe real:** *gate cujo alcance depende de um registro manual sem ritual de alimentacao* -- irma do F89 (`AREAS_VALIDAS` que so existe num writer) e do D4/G5 (tabela gerada mantida a mao). O defeito nao e a ausencia do gate; e a **ausencia do passo "cadastrar o termo" no rito de revogacao**.
- **Custo medido:** 1 bloco inteiro entregue no formato reprovado + 1 turno do usuario gasto em correcao, numa janela de estudo de ~1h antes do ENAMED. O 3o furo (`<sub>` HTML) e adjacente: o contrato P3 part-3 manda mostrar o preview "junto das opcoes", mas sob override passivo (s123) **nao existem opcoes** -- o usuario nao escolhe a nota. A clausula ficou orfa da sua premissa.
- **Remedio -- NAO executado nesta janela (era de estudo). Duas metades, e a segunda e a que importa:**
  - **(i) o conserto pontual (barato):** (a) lapide (`⚰️` + data + motivo) nas duas linhas, no formato ja usado para o PREPARAR e a Camada 0/1 na mesma skill; (b) default de lote **10-15** com a proveniencia (s130/s152); (c) requalificar o preview -- exibir so quando notavel, no tally, como ja permite o passo 5 ("reportar o proximo `due` so quando notavel"); (d) `sync_skills.py` no mesmo commit (§10.3).
  - **(ii) o conserto do GATE (o que impede a proxima):** cadastrar em `_TERMOS_REVOGADOS` os termos que o Invariante F e a regua de lote revogaram (`justificativa em 1 linha`, `lote de 3`/`5`/`6`, `preview junto das opcoes`) **e** dar ao registro um ritual de alimentacao -- toda revogacao futura entra la no mesmo commit que a declara. Sem (ii), (i) conserta uma instancia e o gate continua cego para a proxima.
- ✅ **Remedio APLICADO (s176, 10/09/2026, item 0.0 da ordem do `/ai-eng` N=78 -- as duas metades no mesmo commit, como ele decidiu na bifurcacao 6.3):**
  - **(i)** tres lapides `⚰️` em `.claude/commands/revisar.md`: passo 4 do loop (a "justificativa em 1 linha" morta pelo Invariante F), Modo conversacional (o lote de 3/5/6 -> **default 10-15** com a proveniencia s130/s152 escrita na linha, e o fallback "sem lote explicito, usar 1 por vez" corrigido para o mesmo default) e o **preview P3** requalificado para "so quando notavel, no tally" com a premissa orfa nomeada. `sync_skills.py` no mesmo commit (secao 10.3).
  - **(ii)** os quatro termos cadastrados em `_TERMOS_REVOGADOS` (`tools/auto_check.py`) -- `justificativa em 1 linha`, `justificativa de 1 linha`, `depois 5, depois 6`, `junto das opcoes` -- e o **ritual de alimentacao** escrito em dois lugares: o comentario do proprio registro (que passou a dizer a verdade sobre si) e **`AGENTE.md` secao 10, item 10** (revogar = declarar + lapidar + cadastrar, tres passos no mesmo commit).
  - 🔴 **Alcance declarado, nao maquiado:** o gate casa **substring literal**. Ele pega a reintroducao verbatim de uma redacao morta; **nao** pega a mesma regra reescrita com outras palavras nem o eixo semantico "bloco menor que 10". Esse eixo fica declarado **nao-verificavel por este check** (secao 10.8, *verification-stack*) -- a derivacao do registro a partir do ledger, que mataria a enumeracao manual, e o item **1.8 (ii')** do `11` de `docs/MEMORIA-AUDITORIA.md`.
- **Corolario de processo (o que este achado ensina):** revogar uma clausula tem **tres** passos, nao um. (1) declarar a revogacao; (2) **lapidar a clausula revogada** no portador que o agente le; (3) **cadastrar o termo no gate que vigia lapides**. O `revisar.md` fez os tres para PREPARAR/Camada 0/Camada 1 e **nenhum** para estes dois -- a mesma skill carrega o padrao certo e o errado lado a lado, e o gate so protege a metade cadastrada.
- **Como foi descoberto (vale como metodo):** nao por varredura -- por **uso real**. O usuario bateu no comportamento, e a autopsia da causa (nao do sintoma) chegou no registro do gate. Reforca D67: *ler o mecanismo atual > ler o ledger*. O `auto_check` desta mesma sessao imprimiu `✅ PASSED - Clausula revogada em vigor (CONTRATO_REVOGADO)` **enquanto o defeito estava em curso**.
- **Classe:** gate-miss de **alcance** (registro manual sem ritual de alimentacao) -- familia do F89 e do G5. Distinto do F79/F79b/F81, que sao gates cegos por **poder expressivo**; este e cego por **inventario**.

## 6s. Sessao de ESTUDO s175, 2o bloco (autopsias de Diarreia e Urologia) -- F91 e F92

### F91 -- `rag.search()` devolve `[]` com o motor OFFLINE e o consumidor le isso como "nao existe conteudo": honest-negative violado na camada `local` -- **ALTA** -- **ABERTO (remedio = spec)**

- **Como apareceu:** durante a autopsia de Urologia (s175), o subagente `evidence-researcher` concluiu e escreveu num relatorio de evidencia que *"nao ha resumo indexado sobre HPB/LUTS"* e registrou o item como lacuna de cobertura do corpus. **A afirmacao e falsa:** `resumos/Cirurgia/Urologia.md` tem **39 chunks** indexados no ChromaDB (colecao com 2.353 chunks).
- **Reproducao (medida por mim, 10/09/2026, nao herdada do subagente):**
  ```
  from app.engine.rag import search
  search('hiperplasia prostatica benigna indicacao cirurgica', n_results=3)  ->  []
  ```
  Zero resultados, **zero excecao, zero WARN**. Ollama fora do ar (`WinError 10061` em `localhost:11434`).
- 🔴 **Por que e pior do que "faltou um fallback":** o fallback **existe e foi bem desenhado**. `_textual_fallback()` (`app/engine/rag.py`) tem docstring explicita -- *"Fallback lexico quando o RAG semantico esta indisponivel (Chroma/Ollama offline)"* -- e marca a proveniencia em `metadata['source'] == 'fallback_textual'` justamente para o consumidor distinguir o degradado do curado. **A salvaguarda esta certa; ela e que falha em silencio.** O `except Exception: return []` no fim do proprio fallback (`:333-334`) colapsa "o motor caiu E o fallback tambem nao achou" no MESMO valor de retorno de "o indice nao tem isso": `[]`.
- **O invariante violado:** `evidence-governance.md §7` (honest-negative) exige que ausencia de evidencia seja **declarada como ausencia de busca** quando a busca nao aconteceu. Aqui a busca **nao aconteceu** (motor offline) e o retorno e indistinguivel de **busca feita sem achados**. Um agente leu o `[]` como fato e o escreveu num relatorio.
- **Classe:** falha silenciosa de degradacao em superficie de EVIDENCIA -- pior que a familia F79/F81 (gate cego), porque nao e um gate que deixa passar: e um **leitor que produz um fato falso**. Irma do F80 (relogio que mente sem avisar), mas com raio maior: o consumidor e um agente que escreve conclusao.
- **Remedio (spec):** `search()` distingue tres estados e o **tipo de retorno carrega a distincao** -- (a) `hits` (semantico), (b) `hits` degradados (`source='fallback_textual'`, ja implementado), (c) **`engine-indisponivel`**: levantar, ou devolver um sentinela que o chamador nao consiga confundir com lista vazia. O `except Exception: return []` do fallback vira `except` que **registra e propaga o motivo**. Teste: Ollama derrubado + query on-topic **nao pode** retornar `[]` silencioso.
- **Corolario de processo (vale alem do bug):** um subagente afirmou "nao existe X no corpus" a partir de um retorno vazio. A regra que faltou e simetrica a de nao fabricar fonte: **nao afirmar ausencia a partir de um retorno vazio sem confirmar que a busca rodou.** Candidato a clausula em `evidence-governance.md`.

### F92 -- resumo com duas afirmacoes OPOSTAS sobre a mesma conduta, sem rotular fonte, PRODUZIU um erro de prova -- **MEDIA** -- **RESOLVIDO (s175, conteudo)**

- **Evidencia:** `resumos/Cirurgia/Urologia.md` listava, na §1.6, "Alteracoes vesicais: calculos vesicais ou divertículos" entre as indicacoes cirurgicas da HPB (linha 107) e, **5 linhas abaixo** (linha 112) + na secao Armadilhas (linha 460), afirmava que *"calculo vesical deixou de ser indicacao absoluta isolada (mudanca AAU 2019); hoje a cirurgia e reservada a calculos de repeticao; um calculo unico pode ser tratado com extracao associada a terapia clinica."*
- 🔴 **A segunda redacao E a alternativa C da questao que ele errou** (Urologia T I, Q3, 09/09). O aluno marcou o que o proprio material dele ensina -- e o material ensina na **secao Armadilhas**, que e a feita para ser memorizada.
- **Causa:** as duas afirmacoes nao sao erro de conteudo -- sao **duas sociedades**. EAU 2026 lista "bladder stones or diverticula" sem qualificador; AUA 2023 (statement 26) escreve "**recurrent** bladder stones". O defeito e nao rotular a fonte de nenhuma das duas, deixando o leitor escolher a errada para a banca brasileira.
- **Agravante de claim-aging (D67):** a datacao "mudanca AAU 2019" **nunca foi verificada** e nao foi possivel confirmar; foi removida com lapide.
- **Remedio aplicado (10/09/2026):** as duas passagens reescritas com atribuicao explicita por sociedade + o principio que organiza as 7 indicacoes (nenhuma e complicacao a consertar isoladamente; todas sao prova de que bexiga ou rim ja pagaram o preco da obstrucao) + IPP > 10 mm como desempate (PMID 34561198) + lapide na redacao antiga.
- **Classe:** familia CONTEUDO, eixo novo -- **material que produz o erro que depois e diagnosticado como lacuna do aluno**. Se a autopsia tivesse parado no "ele nao sabia o criterio n. 4", o remedio teria sido reforcar um card contra um resumo que ensina o contrario. Corolario: **ao diagnosticar erro em tema com resumo, ler o que o resumo diz sobre a alternativa MARCADA, nao so sobre a correta.**

---

## 6t. Reforma remota pos-s175 (item 0.0, ordem do `/ai-eng` N=78, 2026-09-10) -- F93

### F93 -- a regua de proporcionalidade de subagents vivia SO na memoria do harness: regra load-bearing sem portador versionado -- **MEDIA** -- **RESOLVIDO (s176, 10/09/2026)**

- **Como apareceu:** feedback duro do operador no fechamento da s175, verbatim: *"achei, no entanto, que voce deu uma volta muito grande para entregar algo simples. sumonou subagents que sumonaram outros subagents, para checar uma informacao. como os blocos eram curtos, voce mesmo poderia ter checado, que seja via websearch. absorva este feedback e atualize a preferencia por mais eficiencia no uso de subagents."*
- **Custo medido (s175, com o comando na mao -- D72):** 3 spawns para **15 erros de questao**; **~673k tokens de subagente** e **~66 min** de wall-clock. O pior deles cobriu **3 erros** e gastou ~24,7 min numa cadeia de **2 niveis** (`evidence-researcher` invocado por subagente, 2x via SendMessage).
- 🔴 **O que torna o caso um achado de MECANISMO e nao so um deslize de conduta:** a delegacao **nao poupou a verificacao**. O principal re-mediu a mao toda afirmacao load-bearing antes de repassar ao operador e **rejeitou duas**: (a) "772 cards nunca vistos" -> o numero honesto e **647** (125 sao aposentados por contrato, `needs_qualitative >= 2`, bancarrota FSRS s075) -- reportar 772 teria inflado a frente de alcancabilidade em ~19%; (b) *"nao ha resumo indexado sobre HPB/LUTS"* -> **falso**, 39 chunks no ChromaDB -- essa virou o **F91**. Ou seja: pagou-se o overhead da cadeia **e** fez-se a checagem de qualquer jeito, com retorno **integral** (relatorios de 15-20k chars) em vez de destilado.
- **Por que e F (classe PORTADOR, secao 10.5):** a regua de 5 clausulas foi gravada na s175 **so na memoria do harness** -- que nao e versionada, e decorativa para qualquer outra IDE e nao viaja com o repo. A propria secao 10.5 do `AGENTE.md` diz: *"regra load-bearing nao mora na memoria do harness"*. Uma regra que so existe la nao tem gate, nao tem lapide e nao sobrevive a troca de harness -- e a mesma familia de alcance do F90 (mecanismo certo, alimentacao sem gatilho) e do Reachability-Debt.
- **Decisao (`/ai-eng` N=78, bifurcacao 6.1, 10/09/2026):** opcao **(a)** -- o portador e a **skill que o agente le no ato da tarefa**, nao o `AGENTE.md`. NAO espera janela de engenharia: e edicao de skill/docs e e o que impede a recorrencia na proxima sessao de ESTUDO.
- **Remedio aplicado (s176, 10/09/2026):** `.claude/commands/analisar-questao.md` ganhou a secao **`0. Orquestracao`** -- as **10 clausulas canonicas** (1-5 medidas no MedHub/s175; 6-10 do `/ai-eng`: retorno destilado <= 3k + arquivo, numero do filho so com o comando que o produziu, `D(x)` em brief >3 itens, `model` explicito no spawn, custo em tokens+minutos no selo), com a origem e o custo medido escritos na propria secao. `sync_skills.py` no mesmo commit.
- **O que ainda NAO tem gate (declarado, secao 10.8):** nada verifica que a secao existe nem que ela foi obedecida. O CHECK proposto pelo `/ai-eng` -- *grep que falha se a skill perder a secao `Orquestracao`* -- **mede em vez de lembrar** e e o fechamento natural deste achado; entra na varredura 1.8 junto com os demais checks de portador. Ate la, a clausula 10 (custo por spawn no selo) e a unica coisa que torna a regua **falsificavel**.
- 🔴 **Limite de alcance conhecido:** a regua e mais ampla que a analise de questao (vale para varredura de engenharia, auditoria de docs, curadoria de cards), mas o portador escolhido so e lido em tarefa de questao. As outras superficies continuam sem portador versionado -- registrado aqui, nao resolvido.
- **Classe:** **portador ausente** (regra load-bearing so na memoria do harness, secao 10.5), com um eixo de **proporcionalidade de delegacao** que ate agora nao tinha nome no ledger.

---
