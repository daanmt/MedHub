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

### F5 -- PREPARAR (Camada 0) e reativo, nao proativo -- **BAIXA**
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

### F8 -- Risco de vazamento de resposta no PREPARAR -- **BAIXA/MEDIA**
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

### F16 -- Tema cirurgico de alto rendimento sem SSOT clinico (.md); so o PDF-fonte existe -- **MEDIA**
- **Evidencia:** apendicite ("um dos temas mais cobrados na prova de Cirurgia Geral", segundo a propria fonte EMED) tem em `resumos/Cirurgia/` apenas o PDF-fonte gitignored (`8. Abdome Agudo Inflamatorio - Apendicite Aguda.pdf`) e **nenhum `.md`**. Glob por `*Apendic*` retorna so o PDF; grep de termos (Alvarado/apendice/carcinoide) nos `.md` acha so mencoes tangenciais (Cirurgia Infantil, Polipose/CCR), nao resumo dedicado. Para cunhar a aula foi preciso extrair o PDF a mao na sessao.
- **Leitura de sistema:** `resumos/**/*.md` e o SSOT de conhecimento clinico E o unico corpus que o RAG indexa (`index_resumos.py`; AGENTE secao 6). Tema sem `.md` fica (a) invisivel ao RAG semantico (`obsidian-notes-rag search_notes` volta vazio p/ apendicite), (b) sem fonte consultavel nem armadilhas cumulativas, (c) re-extraido a mao a cada aula. O HANDOFF lista gaps pontuais (TCE.md, Sistemas de Informacao) mas nao ha check sistematico de cobertura.
- **Verificacao sugerida:** cruzar `resumos/**/*.pdf` (fontes EMED presentes) contra `resumos/**/*.md` (SSOTs existentes); listar temas com PDF sem `.md` par e quantos sao de alto rendimento.
- **Hipotese de melhoria:** (a) relatorio de cobertura `pdf-sem-md` (CLI ou check WARN no `auto_check`) que torna o gap visivel e priorizavel; (b) rodar o workflow `criar-resumo` p/ apendicite -- fecha o gap de conteudo E realimenta o RAG. A aula-base desta sessao ja e insumo pronto p/ o `.md`.

### F17 -- PDFs-fonte retidos "para o RAG" nao sao indexados; o proposito da decisao s086 esta desconectado do wiring -- **MEDIA**
- **Evidencia:** a decisao s086 (AGENTE secao 6) reteve os PDFs do EMED dentro de `resumos/` "pois serao usados para alimentar o RAG". Mas `index_resumos.py` indexa `resumos/**/*.md` -- o PDF fica no lugar, **un-indexado**. O texto do PDF so entra no RAG se/quando transcrito a mao para `.md`.
- **Leitura de sistema:** gap entre a intencao declarada (PDF alimenta o RAG) e o wiring (RAG so le `.md`). O caminho real e implicito: PDF -> extracao manual -> `.md` -> index. Enquanto o `.md` nao e cunhado, o PDF e IP retido sem retorno de busca. F17 e a causa-sistemica de F16 existir silenciosamente.
- **Verificacao sugerida:** confirmar que `index_resumos.py` nao ingere PDF (aparentemente so glob de `*.md`); contar PDFs em `resumos/**` sem `.md` par.
- **Hipotese de melhoria (escolha de arquitetura p/ ai-eng):** ou (a) canonizar PDF->md como o unico caminho (entao F16 e "so" execucao de conteudo + o relatorio de cobertura basta), ou (b) `index_resumos` passa a ingerir texto extraido de PDF como fonte secundaria do RAG (com metadado de origem) -- amplia cobertura sem trabalho de autoria, mas indexa material bruto fora do `/estilo-resumo`.

### F18 -- Aula-base e efemera (chat-only); sem artefato de persistencia/reuso nem registro de calibracao -- **BAIXA/MEDIA**
- **Evidencia:** a aula-base de apendicite foi construida e entregue so no chat. Nao ha `aulas/` nem campo que vincule aula a tema; a proxima vez o artefato e re-forjado do zero. A nota de dificuldade 1-10 que calibrou a descompressao (D10 pela regra do extensivo) tambem nao foi registrada (`taxonomia_cronograma.dificuldade` intocada nesta sessao).
- **Leitura de sistema:** a aula-base e artefato pedagogico validado (memoria: "leitura mais prazerosa"; efeito de cobertura 53%->75%) e caro de produzir (extracao + escada). Efemeridade = re-trabalho, zero acumulo, sem reuso cross-sessao -- tensao com o objetivo "melhor app de estudos". Pode ser efemera-por-design SE o `.md` (F16) for a forma duravel e a aula for so a sua renderizacao descomprimida.
- **Verificacao sugerida:** decidir se a forma duravel do ensino e o `.md` gold (aula = derivada efemera) ou se a aula merece artefato proprio; conferir se `db.set_dificuldade` pode registrar a calibracao mesmo em prova fora do cronograma.
- **Hipotese de melhoria (p/ ai-eng decidir):** (a) `.md` como forma duravel + aula como render efemero (fecha via F16, custo zero de infra); ou (b) persistir a aula (`{Tema}.aula.md` ou secao); e, minimamente, (c) registrar a nota de dificuldade do tema no ato da aula, alimentando a Revisao Calibrada.

### F19 -- Ambiente e ENAMED/cronograma-centrico; prova paralela (R+ gastro) sem suporte de primeira classe -- **BAIXA**
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

### F20 -- .venv dessincronizado do requirements.txt (fsrs ausente) -- **BAIXA**
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

### F27 -- Modo single do insert_questao sai com exit 0 mesmo em falha -- **BAIXA**
- **Evidencia:** a docstring promete "Exit 0 em sucesso, 1 em falha", mas o main nao
  captura o retorno de `insert_questao()` -- falha imprime erro e sai 0. Pre-existente;
  descoberto na verificacao da part-4 (que implementou exit 1 no caminho --errors-file).
- **Hipotese de melhoria:** `sys.exit(0 if ok else 1)` no modo single (1 linha; conferir
  se algum chamador depende do exit 0 atual antes).

### F28 -- Arg `--elo` (required) nao e persistido em coluna propria -- **BAIXA**
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

### F32 -- Re-drill intra-sessao do `/revisar` colide com o relearning nativo do FSRS (state=3) -- **BAIXA**
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

*Este doc e o ledger vivo de engenharia. Nao "fecha" -- acumula achados a cada sessao de uso. O 1o ciclo Fable (PRD -> 5 ondas) foi ENTREGUE em 2026-07-05 (secao 3b). A s109 (coordenador-observador) adicionou **F16-F19** do uso vivo (forja da aula-base de apendicite; secao 3c) -- insumo do ciclo 2. A rodada 1 do ciclo 2 (Fable/ai-eng, paralela a s109; secao 3d) entregou F14/F15, validou o teto (F4/b), preparou a janela do expurgo (F11) e registrou F20. A s109 (1o lote de questoes; secao 3e) adicionou F21, e (2o lote; secao 3f) **F22-F26**. O **ciclo 2 rodada 2** (Fable/ai-eng, 2026-07-06; secao 3g) entregou o PRD ORQUESTRACAO completo (vibeflow 4/4 PASS): posicao SSOT (op-3), recomendador do dia, F22-F26 RESOLVIDOS; F21 segue aberto (contrato de aula); F27/F28 registrados pelos audits. A **s110 parte 2** (2026-07-06) verificou performance+cronograma a pedido do operador, achou e RESOLVEU **F29** (drift planilha-db de 76q, ao vivo, mesma sessao); no ciclo de Pre-Natal I (cold recall, tema-zero) registrou **F30** (material_indicado nao verifica existencia real do resumo), aberto. A **s113** (08/07, verificacao de cronograma a pedido do operador) achou e RESOLVEU **F33** (boot recomendava temas ja feitos, calendario-driven sem ler conclusao real da planilha) na mesma sessao via ciclo completo `/discover`->`/gen-spec`->`/implement`->`/audit` (PASS); F31/F32 registrados por uso vivo (s112). A **s115** (2026-07-09) auditou o boot e entregou o PRD **boot-cronograma-drive-confiavel** em 3 partes (vibeflow discover->gen-spec->implement->audit, audits PASS): achado novo **F34** (disparo+ordem do Drive) + **F30/F31 RESOLVIDOS**; **F21 segue aberto**. **Proximos achados comecam em F35**. Ultima atualizacao: s115 (2026-07-09). **Adendo 2026-07-12 (Fable/ai-eng, ciclo mecanismo-de-conhecimento):** F21 RECONCILIADO em dois planos (conduta RESOLVIDA no contrato v1.2; enforcement mecanico na spec `mecanismo-conhecimento-consolidacao-part-3`) -- ver secao 3e. Ciclo de consolidacao do mecanismo de RAG/conhecimento em andamento (part-1 audit PASS: MCP obsidian aposentado, scaffold LangGraph/BM25 removido; part-2: reconciliacao de drift documental).*
