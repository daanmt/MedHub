# Session 144 -- Auditoria de arquitetura dos 7 sistemas não-flashcard (7 subagents + verificação adversarial)
**Data:** 2026-08-14
**Ferramenta:** Claude Code (Opus 5, 1M)
**Continuidade:** Sessão 143
**Tipo:** ENGENHARIA (sessão de estudo não aconteceu -- volume do dia = 0)

---

## Como a sessão começou: o boot caro

Abertura normal de sessão de estudo. O boot consumiu **~15 chamadas de ferramenta** para produzir um plano
que o `day_plan.py` já imprime, incluindo uma tentativa de transcrever ~40KB de base64 do xlsx do Drive que
falhou. O usuário interrompeu com a crítica que originou toda a sessão:

> "Esse boot foi extremamente longo e ineficiente, heim? Esse mecanismo de gestão de cronograma, das tasks
> que já foram, comunicação com o mcp do drive, etc., estão bem ruins. (...) Fizemos uma baita auditoria e
> sessão de engenharia na criação e auditoria dos flashcards, mas essa tentativa de boot cheio de
> contrapartidas me preocupa."

E a diretriz de política que governou todos os veredictos:

> "O que estiver obsoleto no medhub deve sair -- essa mania de ficarmos arquivando coisas mortas, é
> basicamente acumulação desnecessária, que inclusive depois sobrecarrega outros agentes futuros que tentem
> operar o sistema."

**Regra derivada, aplicada a toda a auditoria:** arquivar não é resposta. Veredito é binário -- fica ou morre.
`MATAR` exige prova de zero referência viva.

---

## O loop de auditoria (5 fases, reprodutível)

| Fase | O quê | Executor |
|---|---|---|
| F0 | Scout: inventário bruto (árvore, tamanhos, recência de commit por arquivo) | agente principal, inline |
| F1 | Fan-out: 7 auditores paralelos, 1 sistema cada, contrato de saída fixo | subagents Sonnet 5 |
| F2 | Cross-check: reconciliar conflitos entre veredictos | agente principal |
| F3 | Verificação adversarial: tentar REFUTAR cada `MATAR` por grep direto | agente principal, inline |
| F4 | Síntese: relatório (Artifact) + handoff técnico ao ai-eng | agente principal |

**O que fez a diferença na qualidade** foi o contrato imposto a cada auditor: veredito de conjunto fechado
(`MATAR`/`FUNDIR:<alvo>`/`CONSERTAR`/`MANTER`), proibição explícita de propor "arquivar", e prova obrigatória
para toda proposta de morte (comando de grep + resultado, sobre o repo inteiro incluindo `.md`,
`.claude/settings.json`, hooks e `.agents/`). Especulação foi rejeitada na origem.

**Nota operacional:** 5 dos 7 auditores morreram no limite de sessão e foram relançados após o reset. No
relançamento os fatos já apurados entraram nos prompts como "não re-verifique" -- cortou trabalho duplicado
e impediu a propagação de uma premissa falsa minha (ver "Correções" abaixo).

**Particionamento:** cronograma/plano-do-dia · camada de conhecimento (RAG/resumos/PDF) · apresentação
(Streamlit) · superfície de CLIs · governança documental · memória e telemetria · higiene de repo e dados.

---

## A tese que saiu

A hipótese de entrada era acumulação por desleixo. **A evidência não sustenta.** O git tem 2,55 MiB / 360
commits, o expurgo de julho foi executado e validado, nenhum PDF ou `.db` jamais foi commitado, 182 testes
passam sem falha, e as 12 tabelas do `ipub.db` têm todas escritor ativo. O `.vibeflow/` (155 arquivos) que
parecia entulho é o mecanismo de engenharia mais ativo do repo, com custo de boot zero.

O que o MedHub acumulou é outra coisa: **artefatos que funcionam e que nenhum caminho de execução alcança.**

- **192MB** de índice vetorial (`pdf_raw`, 14.216 chunks) construído, testado, com audit PASS, desconectado
  do único consumidor por **uma linha** (`get_topic_context.py:177` chama `search()` e não `search_two_tier()`).
- **514 registros** de `session_insights` gerados por Haiku a cada sessão; `load_context()` consulta 4
  namespaces e nunca esse. Write-only há meses.
- **11 normas** descrevendo sistemas que não existem mais.
- **2 scripts** com nome de auditor que corrompem dado se executados.
- `check_fk_orphans.py`: sensor pronto, nascido no mesmo commit dos checks 8/9 do `auto_check`, deixado
  fora do wiring.

Nada disso é bug. Tudo passou pelos gates. **Os gates verificam se está correto; nada verifica se alguém
chega lá.** Essa é a hipótese central entregue ao ai-eng: falta um check de *alcançabilidade*, e ele é
provavelmente reusável nos outros projetos do usuário.

---

## Os 6 defeitos estruturais (detalhe no handoff)

- **D1 -- Decisão tomada e não propagada.** MCP `obsidian-notes-rag` descomissionado em 12/07; **10 arquivos
  vivos** ainda instruem chamá-lo, incluindo o frontmatter `tools:` de `evidence-researcher.md` (quebra o
  subagente). Um deles foi editado 5 dias *depois* do descomissionamento sem correção.
- **D2 -- Norma que mente.** 11 instâncias com `arquivo:linha`. Uma delas destrutiva (ver abaixo).
- **D3 -- Sensores calibrados para não incomodar.** `doc_drift.py` reporta "0 achados" e só olha 4 arquivos
  allowlisted, nenhum deles onde as 11 normas de D2 vivem. `reconcile` B1 (HANDOFF > 60 linhas) estava
  ativo e não bloqueou. `sync_skills --check` falha agora, WARN-only, sem ação desde 17/07.
  **Padrão: warning-first virou warning-only.**
- **D4 -- Construído, testado, auditado PASS, nunca conectado.** (a tese acima)
- **D5 -- Protocolo que duplica o harness.** O hook `SessionStart` já roda `day_plan.py` e injeta o plano
  antes do primeiro turno; `AGENTE.md §2 passo 4` manda rodar de novo E declara obrigatório o sync do Drive
  por um caminho impossível. O bullet tem 272 palavras que duplicam verbatim o W8 do `reconcile-contract.md`.
  **Este é o defeito que produziu o boot caro desta sessão.**
- **D6 -- Documentação por acreção.** Boot obrigatório medido: **9.134 palavras / ~70KB** antes de qualquer
  trabalho. `ESTADO.md:46` tem 604 palavras num campo que o contrato define como 1 linha.

---

## Estancamento já executado (ai-eng, commit `49c5512`)

Os 3 itens de perda irreversível foram mortos ainda nesta sessão, pelo ai-eng, a partir do handoff:

1. **`.claude/commands/extrair-pdf.md`** -- "Política Zero PDF" (revertida na s086, seguia no ar) substituída
   pela política de retenção. Obedecê-la apagava IP-fonte do EMED não-reconstruível.
2. **`tools/audit_db_state.py` REMOVIDO** -- nome de auditor, corpo de fix one-shot (`DELETE id=22` +
   subtração fixa -44/-40); re-rodar corrompia `taxonomia_cronograma`.
3. **`tools/seed_dificuldade.py` REMOVIDO** -- re-rodar reverteria 3/8 notas já recalibradas por uso real,
   forjando `fonte='usuario'` sobre valor vindo de inferência.

O resto da lista de morte e dos consertos aguarda GO do operador.

---

## Correções a afirmações minhas (registradas para não reincidirem)

- **O cálculo de ritmo do cronograma NÃO tem bug.** Eu afirmei ao usuário que o `day_plan` tratava 25/10
  como deadline de prova. `day_plan.py:508-509` documenta que medir a grade contra o fim da grade (e não
  contra o ENAMED, 13/09) foi a **correção deliberada da s126**. O ENAMED aparece à parte, "sem alvo de
  volume". Injetei essa correção nos prompts do relançamento para o auditor não perder tempo.
- **`history/legacy/` não é lixo.** `AGENTE.md §9` usa "ignorar" no sentido de não citar como fonte viva,
  não de `.gitignore`. Está corretamente versionado.
- **O hook `consolidate_session` "não existe" estava errado.** O grep em `settings.json` estava certo, a
  conclusão não: quem escreve é `tools/hooks/memory_session_log.py` (`PostToolUse(Write)`), que dispara
  `python -m app.memory.manager` em background. A memória está viva; a doc é que aponta para o nome errado.

---

## Bug diagnosticado e ainda aberto: o contador "(1250 erros)"

O boot exibiu 8 fraquezas distintas, todas com `(1250 erros)`. Causa em `app/memory/manager.py:91-128`:
a query agrega com `GROUP BY area` sozinha (`('Cirurgia', 1250)` = total da especialidade inteira) e o loop
de matching usa substring bidirecional com `break` no primeiro acerto. Medido no banco: **25 registros com
`error_count == 1250`** em 8 áreas distintas que só compartilham a substring "cirurgia". O campo
`especialidade`, que desambiguaria, nunca é consultado. `inspect.py:121-123` já tinha um `TODO(R1b)`
registrando o mesmo bug quando o número era 241 -- cresceu com o corpus e nunca foi corrigido.
Conserto: `GROUP BY area, tema` + casar por `especialidade` + **somar** em vez de `break`. ~15 linhas.

---

## Fork aberto (precisa de decisão do operador, não de conserto)

**Collection `pdf_raw`: conectar ou deletar.** 14.216 chunks, ~192MB, 93% do peso de `data/`. Os auditores
de RAG e de higiene chegaram a veredictos opostos por caminhos independentes, mas **concordam que o status
quo é a pior das três opções**. Pré-requisito para decidir com dado: `tools/eval/REPORT.md` tem 1 único
commit (27/05), anterior ao two-tier -- re-rodar `tools/eval/run_eval.py` antes de escolher.

---

## Saída aproveitável: tirar o Drive do caminho crítico

A planilha **Dashboard EMED 2026** (Google Sheets nativo) já tem coluna `Realizada?` **por tarefa**, legível
em texto puro via `read_file_content`, sem base64. Isso separa dois sinais hoje acoplados:
**conclusão** migra para o Dashboard e fica acessível ao agente; **ordem** (reordenação manual, sem
substituto textual) vira ritual do usuário, que tem o xlsx local e roda `cronograma.py --sync-drive <path>`
sem MCP nenhum.

---

## Dívida de sessão anterior, registrada aqui

A sessão de engenharia de hoje mais cedo (reforma de flashcards, commits `8006471`..`cb5d9e2`, 16h56-18h14:
partes 1-6 de integridade + p3 partes 1-4) **não foi selada em `history/`** e o `HANDOFF.md` seguia apontando
para a s143. Por `AGENTE.md §5.3` ("não criar sessões retroativas") não criei sessão para trabalho que não
fiz -- fica o registro aqui para o rastro não se perder. O ponteiro do HANDOFF foi corrigido nesta sessão.

> **Resolvido na consolidação part-4 (mesma data):** o selo dos três ciclos do dia está agora na seção
> **"Os três ciclos de engenharia do mesmo dia"** abaixo, com hashes reais. Nenhuma sessão retroativa foi
> criada -- o trabalho do dia 14/08 vive todo no log do dia 14/08.

---

## Entregáveis

- **Relatório navegável (Artifact):** https://claude.ai/code/artifact/5d536604-c098-404d-ba95-4db45e785893
- **Handoff técnico ao ai-eng:** `C:\Users\daanm\ai-eng\HANDOFF_MEDHUB_SISTEMAS.md` -- inclui os 6 defeitos
  com `arquivo:linha`, lista de morte verificada em F3, 3 fusões com o que absorver antes, 11 consertos
  ordenados por dano-evitado÷esforço, o fork aberto, e a seção "o que NÃO está quebrado" para o ai-eng não
  gastar ciclo.
- **Nota cross-projeto** (pedido explícito do usuário): varredura rasa de `C:\Users\daanm\` -- 2 projetos
  ativos sem versionamento (Daktus 9.120 arquivos, NOS 155), 4 cascas de ideias abandonadas, o backup de
  expurgo de 3.271 arquivos nunca limpo, e **11 markdowns na raiz do próprio ai-eng** (o MedHub tem 12).

---

## Não executado nesta sessão, deliberadamente

- **`tools/reflect.py` (AGENTE.md §3 passo 5).** A auditoria mediu que ele **cumpriu o próprio gate
  anti-decorativo**: 3 execuções reais (12/07 ×2, 16/07), 0 decisões mudadas -- a única proposta gerada
  (`card_autosuficiencia`) nunca aparece em nenhuma sessão posterior. Rodá-lo uma 4ª vez seria exatamente
  o comportamento decorativo que a regra proíbe. Está na lista de morte do handoff; matar exige editar
  `AGENTE.md §3 passo 5` junto.
- **Nenhuma remoção.** A auditoria inteira foi read-only. As 3 remoções do dia são do ai-eng (`49c5512`).

---

## Os três ciclos de engenharia do mesmo dia (selo, hashes reais)

O 14/08 teve **três ciclos** de engenharia além da auditoria narrada acima. Volume de estudo do dia = 0.
Nenhum deles tinha selo em `history/`; ficam registrados aqui (`AGENTE.md §5.3`: sem sessão retroativa --
é tudo o mesmo dia-calendário). O `ad1ccde` (16h20) é o selo da **s143**, não deste dia de engenharia.

### Ciclo 1 -- `flashcards-integridade` (16h56-17h19) · 35 arquivos, +2.724/-144

PRD `.vibeflow/prds/flashcards-integridade-geracao.md` + 6 specs, resposta do ai-eng ao handoff (`8006471`).

| Parte | Commit | Entrega |
|---|---|---|
| 1 | `01f6a14` | mata o fallback heurístico + fecha vazamentos + FK enforcement |
| 2 | `b139764` | Invariante C vira **trava técnica** em `record_review` |
| 3 | `cec30bf` | biblioteca `card_checks` + gate nos writers principais |
| 4 | `7fa90cc` | gate nos writers restantes + fim do no-op disfarçado |
| 5 | `1fd670d` | definição canônica de "card ativo" + detectores cross-field no batch + calibração 68/68 |
| 6 | `e011066` | **watermark de dado** no harness -- o dado ganha gate (não só o arquivo) |

Fecho: `34d712e` -- audit **PASS 6/6** (`.vibeflow/audits/flashcards-integridade-parts-1-6-audit.md`) + decisões do ciclo.

### Ciclo 2 -- `flashcards-p3` fila e proveniência (18h02-18h14) · 19 arquivos, +1.082/-32

| Parte | Commit | Entrega |
|---|---|---|
| 1 | `12188c0` | proveniência no revlog -- vista `card_version` + `selection_reason` |
| 2 | `f83fd87` | banda prioritária de erros frescos no dreno padrão |
| 3 | `6443753` | preview dos 4 intervalos + contrato de apresentação codificado |
| 4 | `d860f16` | eventos de geração/reincidência + eficácia + fim do bypass |

Fecho: `cb5d9e2` -- PRD `flashcards-p3-fila-proveniencia.md` + 4 specs + audit **PASS 4/4**.

### Ciclo 3 -- `consolidacao-alcancabilidade` (21h53-em curso) · 45 arquivos, +1.029/-2.128

Nasce da auditoria narrada acima: PRD `.vibeflow/prds/consolidacao-alcancabilidade.md` + 7 specs (`6d89637`).
É o único ciclo do dia com **saldo negativo de linhas** -- o objetivo era remover, não somar.

| Parte | Commit | Entrega |
|---|---|---|
| 1 | `47aad80` | lista de morte de código -- 13 arquivos, 0 referências vivas |
| 2 | `293b973` | fork `pdf_raw` resolvido (morto) + eval honesto regenerado |
| 3 | `7fb673e` | memória radical -- contador veraz + purge do write-only |
| 4 | *(sem commit -- entregue no working tree)* | **boot barato + entidade multi-prova** (abaixo) |

**Part-4 (esta entrega).** Fecha os consertos 3/7 do handoff (D5/D6) e a decisão "entidade multi-prova":
- `AGENTE.md §2 passo 4` reescrito de **272 para 56 palavras** -- o Plano do Dia vem injetado pelo hook
  `SessionStart` e não se re-roda; `day_plan.py` só sob demanda (`--difficulty`/`--tempo`); W8 vira ponteiro
  para o contrato (zero duplicação verbatim). O "~94q/dia p/ ENAMED" (referencial misturado) sai.
- **Sync do Drive deixa de ser impossível** (`cronograma-contract.md` Cláusula 5b nova + `reconcile-contract.md`
  W8): **conclusão** passa a ser lida do `Realizada?` do Dashboard EMED 2026 (Sheets nativo, texto puro via
  `read_file_content`) -- ação que o agente pode fazer; **ordem** vira ritual do usuário com o xlsx local
  (`--sync-drive`, sem MCP). Proibido exigir binário via MCP em passo de boot; caveat honesto quando faltar.
- **`core/provas.json`** (novo, versionado): ENAMED 13/09 (`tipo: prova`) × fim-grade-EMED 25/10 (`tipo: grade`).
  `day_plan.py` ganha countdown no cabeçalho (`ENAMED em 30d · grade fecha em 72d`), parser tolerante
  (arquivo ausente/ilegível -> WARN, plano segue). 🔴 O **ritmo continua medido contra a grade** (correção
  deliberada da s126) -- há teste que cai se o countdown encostar na fórmula.
- **B1 promovida a BLOCKING de fato** (`auto_check.check_handoff_len`, check 10): a condição existia em prosa
  desde a s075 e nunca teve check -- era exatamente o D3 ("warning-first virou warning-only") aplicado a si mesmo.
- **Poda de acreção:** `ESTADO.md` e `HANDOFF.md` trazidos aos próprios contratos; a narrativa acumulada
  migrou para o Anexo abaixo. Suíte: **174 -> 194 testes**.

---

## Anexo -- narrativa migrada de `ESTADO.md` e `HANDOFF.md` (poda da consolidação part-4)

> **Nada foi apagado: mudou de endereço.** O `estado-contract.md` proíbe narrativa acumulada na linha do
> indicador e exige 1 linha por frente; o `handoff-contract.md` proíbe narrativa de mais de uma sessão.
> Os dois arquivos violavam isso (`ESTADO.md:10` = 309 palavras num campo de 1 linha; `ESTADO.md:29` = 604;
> `ESTADO.md:38-46` = 9 frentes com blow-by-blow de s121-s142). O texto **original, verbatim**, fica aqui --
> é história, e história vive em `history/`. Quem procura "o que a s128 achou" acha aqui, não no boot de
> toda sessão. Marcação `[origem: ARQUIVO:linha]` preserva a proveniência.

### A1 -- Header narrativo do ESTADO `[origem: ESTADO.md:10-11]`

*Atualizado: 2026-08-14 (sessão 144 -- ENGENHARIA: auditoria de arquitetura dos 7 sistemas não-flashcard, via 7 subagents + verificação adversarial. **Frente nova e prioritária: ALCANÇABILIDADE.** A acumulação do repo não é desleixo (git 2,55 MiB, expurgo validado, 182 testes verdes, 12/12 tabelas vivas, `.vibeflow/` ativo) -- é artefato que funciona e que nenhum caminho de execução alcança: 192MB de índice RAG desconectado por 1 linha, 514 `session_insights` write-only, 11 normas descrevendo sistemas mortos, 2 scripts que corrompiam dado, 1 sensor pronto e não plugado. Tudo passou pelos gates, porque os gates verificam correção e nada verifica alcance. 6 defeitos estruturais D1-D6; D5 explica o boot caro (o hook `SessionStart` já roda o `day_plan` e o `AGENTE.md §2 passo 4` manda rodar de novo, além de exigir sync do Drive por caminho impossível); D3 mostra que warning-first virou warning-only. ai-eng estancou os 3 itens de perda irreversível no mesmo dia (`49c5512`: política Zero PDF morta em `extrair-pdf.md`, `audit_db_state.py` e `seed_dificuldade.py` removidos). Handoff completo em `ai-eng/HANDOFF_MEDHUB_SISTEMAS.md`; relatório navegável como Artifact. Resto da lista de morte/consertos **aguarda GO do operador**; fork aberto sobre a collection `pdf_raw`. Detalhe em `history/session_144.md`) | Ferramenta: Claude Code (Opus 5, 1M)*

*Anterior: 2026-08-12 (sessão 142 -- bloco Hanseníase+PLECT (41q/33 acertos, fecho S14) + DRENAR de 69 cards + redrill de 24; usuário identificou aula-base sequencial falhando em cluster de dx diferencial (pediu tabela comparativa) e cards double-barreled em escala, inclusive uma reforja feita minutos antes pelo próprio agente -- nasceu o teste "eixo x pacote" em `estilo-flashcard.md`, refinando a régua "um critério de acerto" da s128; achado em escala via `audit_card_atomicity.py`: 280 cards não-atômicos no baralho inteiro (WARN, fila futura); 2 padrões de erro confirmados no ledger de habilidades em 4 temas cada (discriminação por epidemiologia solta; escalonar intervenção além do protocolo -- cruza família bug nº1); detalhe operacional completo em HANDOFF.md) | Ferramenta: Claude Code (Sonnet 5)*

### A2 -- Narrativa da linha "Indicador Atual" `[origem: ESTADO.md:29]`

> A parte numérica corrente (6.019 / 63,7% / ritmo ~47,7q/dia) permanece no ESTADO, em 1 linha. O que segue
> é a acreção histórica que estava colada nela.

*(atualizado na s144; estava em 5.919 -- o reconcile B4 do boot pegou a divergência contra `sessoes_bulk`.)* *(corrigido no reconcile da s140 -- estava em 5.535 desde a s125, o HANDOFF já tinha o número certo, só o snapshot macro ficou pra trás.)* 🆕 **Leitura de ritmo corrigida (s128):** o "20,9 q/dia real" do `day_plan` mistura dias vazios. Por **dia trabalhado**, julho deu **56,9 q/dia** (853q em 15 dias) -- já **acima** da meta a 6 dias/semana. **O gargalo é FREQUÊNCIA (15 de 26 dias = 58%), não capacidade.** A 6 dias/semana o marco de 9.454 cai (~9.745 projetado). **O que não fecha:** cobrir a grade EMED inteira exigiria ~75q/dia trabalhado -> ~76% da grade até 25/10. Fork registrado (cobertura parcial priorizada por banca × esticar a data), **não decidido**. ⚙️ **Gatilho de recalibração S13 RESOLVIDO:** acúmulo 5.026 < 5.200 -> **confirma meta-prova 10.000** (12k segue teto/stretch). Detalhe por sessão vive em `history/` (**s121** (15/07) -- drenagem FSRS (26 vencidos → dívida 0) + auditoria do baralho (425 pool nunca introduzidos, 66/105 temas nunca drilados) + 2 features vibeflow (`card_self_sufficiency.py` + telemetria pool×dívida, audit PASS ×2) + M1 reforja de 27 cards (worklist 24→0); estratégia M1-M4 "matar os cards"; **s120** (12-15/07) -- S13 conversacional SUS/Imunizações/Colecistite, 65q, 15 cards (811-825), resumo SUS gold novo, Imunizações recalibrado D10, lição "ancorar aula no PDF do EMED"; **s116** -- HAS Pt.2 + Distúrbios do Potássio cold, 42q, 12 cards (776-787), 3 resumos gold; **s115** engenharia -- PRD `boot-cronograma-drive-confiavel` fecha a costura headless/Drive, F30/F31 RESOLVIDO + F34 no ledger; **s114**, 09/07 -- S12 avança 2/6; marco ENAMED corrigido nos scripts p/ 10k meta-prova + 12k teto; achado dos **dois SSOTs do cronograma** -- ordem no xlsx do Drive vs detalhamento no `Cronograma.pdf`, memória `project_cronograma_dual_ssot`).

### A3 -- "Estado por frente (macro)" narrativo `[origem: ESTADO.md:38-46]`

- **Volume & Metas:** **5.535 / 9.454 (grade completa @ 25/10)**. Perf. geral **~78,9%**. Ritmo-alvo **~47,2q/dia corrido** (83 dias). 🆕 **Diagnóstico de zona (s127):** zona **COBERTURA** -- desempenho alto (77,6% média de blocos) sobre **43,0% da grade percorrida**; prescrição = avançar a grade, não refinar. 🔴 **Variância entre blocos = 11,9 pp (alta)** -- prescreve simulado, independente da zona; é o gargalo isolado nº1 hoje, acima da média. Cluster fraco (volume + %): Oftalmo, Dermato, Cardiologia, Otorrino, Nefrologia, Hemato. **Gargalo nº1 = execução de prova** (bug nº1: não fechar a conduta / exame lido por dado parcial / ancoragem no fármaco).
- **Conteúdo:** **70 resumos** (`Sepse.md` expandido na s125 com a camada legada -- SIRS, EGDT/SvcO2, "sepse grave" abolido, escalonamento de ATB; auto_check PASS). **🆕 s124 -- Corpus EMED de flashcards (275 decks / 7565 cards atômicos)** colhido em `resumos/**/Flashcards - <Tema>.pdf` (gitignored, IP EMED), consultável por `tools/emed_flashcards.py --query --tema "<tema>"` (match exato/fuzzy). Alimenta a cunhagem: `analisar-questao §8.3` consulta o deck + **seleciona por contexto** (nunca import em massa); padrão de autoria atômico em `estilo-flashcard §Formato atômico` (targeting metacognitivo mantido, formulação trocada). **Gaps:** reescrever `TCE.md` + `Sistemas de Informação em Saúde.md`; aula-base de Pré-Natal I (cluster frio). PDFs EMED p/ aula-base mantidos (gitignored).
- **🔴 s128 -- ATOMICIDADE MEDIDA (F39):** o pivô atômico da s124 foi contratual, não aplicado ao acervo. `tools/audit_card_atomicity.py` (novo, read-only, **check 9 do `auto_check`**, WARN-first) mediu: **358 de ~900 cards ativos (~40%)** violam o princípio -- **227 duplo-ask** (a frente cobra duas respostas) + **259 resposta-multifato**; 122 com ambos. **Por que é ALTA:** card com 2 critérios de acerto admite "acertei metade" e **a nota FSRS deixa de significar algo** -- o defeito corrompe a *medida* que governa a repetição espaçada, não só a experiência. Achado **do usuário**, que formulou a régua melhor que o contrato: cláusula **"UM CRITÉRIO DE ACERTO por card"** agora em `estilo-flashcard.md` (+ espelho). Demanda composta se treina em **questão**, nunca em card. Entregue: 8 cards atomizados (reescrita in-place com FSRS preservado + 12 desmembramentos); **~350 na worklist** (duplo-ask primeiro, em lotes por tema).
- **🆕 Padrão de flashcards (s124) -- pivô atômico:** a safra auto-cunhada violava o *minimum information principle* (paragraph card). Novo contrato: 1 fato/card, frente gerativa, resposta 1 frase, "porquê" fora do recall, card discriminador p/ interferência, sem sets, fonte+data. EMED = biblioteca de referência + fonte de cobertura; cunhagem error-driven seletiva. Demo: Endometriose 831-835 reforjados (FSRS preservado) + splits 836/837.
- **Erros & Cards:** **760 erros; 950 cards ativos**. Backlog FSRS: dívida 36 atrasados + 10 p/ hoje · **pool 612 nunca introduzidos** (entram ≤40/dia).
- **🆕 s142 -- Teste "eixo x pacote" (refina a régua de atomicidade da s128) + 2 padrões de erro cross-tema confirmados no ledger.** Durante DRENAR de 69 cards, o usuário identificou double-barreled em escala -- inclusive numa reforja feita minutos antes pelo próprio agente (corrigiu o conteúdo errado do card, mas empacotou um fluxograma inteiro na resposta, ficando mais double-barreled que o original). Formalizado em `estilo-flashcard.md`: **eixo único** (um discriminador do qual várias manifestações decorrem automaticamente -- ex. "calibre do conduto" define hérnia/hidrocele/cisto de cordão) recebe nota cheia sem exigir as vitrines derivadas; **pacote** (nós de decisão diferentes, cadeia causal de 3+ elos, fatos independentes) é defeito real -> split. Reforja de conteúdo não corrige atomicidade sozinha -- os dois testes rodam sempre. Achado em escala: `audit_card_atomicity.py` no baralho inteiro aponta **280 cards não-atômicos** (WARN, fila futura, fora do escopo desta sessão). Ledger de habilidades (`tools/habilidades.py`) confirmou 2 padrões cross-tema (4 ocorrências/4 temas cada, cruzam o limiar de família do bug nº1): discriminar por achado específico em vez de epidemiologia compartilhada (Cromomicose/Hanseníase/Leishmaniose/Esporotricose); escalonar para intervenção mais agressiva além do que o protocolo pede (Diverticulite/Apendicite/Pólipos-Neoplasias x2). Nova memória sobre epidemiologia-como-conteúdo (dado numérico solto sem âncora de raciocínio, sempre vira card dedicado) distinta de epidemiologia-como-discriminador-fraco.
- **🆕 s140 -- Loop reforjar + split + consolidação validado em escala (78 cards drenados, 15 reforjados, 1 aposentado, 2 desmembrados).** Durante o drill, o usuário sinalizou cards "mal produzidos" (não conteúdo errado -- forma: contexto vaza a resposta, pergunta e contexto não batem, ou raciocínio longo demais pro formato atômico). Mapeados 3 defeitos de autoria distintos; corrigidos in-place via `recurate_cards.py` (preserva `card_id`/estado FSRS) e, nos 2 casos de árvore de decisão densa (`Gravidez ectópica`), desmembrados em cards novos via `insert_card_base.py` (`tipo='conteudo'`). Fechamento pediu **re-drill de consolidação**: mesma fila (pool <4 + reforjados) reapresentada até nota 4 honesta, **sem novo `--record`** por rodada de consolidação -- só a 1ª tentativa grava FSRS (Invariante C estendida a rodadas de reforço). 3 de 27 gaps reincidiram na mesma lacuna após a 1ª correção (candidatos reais a leech, não erro pontual). Auditoria de evidência (`evidence-researcher`) usada inline para resolver 1 disputa card x usuário sobre protocolo de hanseníase -- usuário estava invertido, card original mantido.
- **FSRS:** backlog grande -- mas a **curva finally comeu na s084 (35/50 revisados)**. `/revisar` (PREPARAR/DRENAR) ataca o backlog. **Andaime validado em tempo real:** Hemostasia destravou após 3 cards-base. Clusters frios andaimados: Hemostasia (fatores), Cardiopatias (T4F/shunt).
- **Infraestrutura -- NOVA capacidade (s083): gestão da curva de esquecimento** -- `review_log` (SSOT do tempo-de-revisão) + radar de dormência (`review_radar.py`) + `/refrescar` (`dormant_refresh.py`, **não toca o FSRS**) + **boot proativo** "Plano do Dia" (`day_plan.py`, AGENTE §2 passo 4) + **autonomia codificada** (AGENTE §1.1) + contrato `core/contracts/forgetting-curve-contract.md`. Mantém: cards de altura graduada (s082), governança de evidência (s076), Camada 2 do `/revisar` (s078). **5 padrões metacognitivos vivos** (+ palpite-abandonado-por-palavra). **Tier-3 (schema de altura) pendente.** **🆕 s094 -- 2 frentes de método (aprovadas, a implementar):** (1) **Revisão Calibrada** (PRD `docs/plans/s094-revisao-calibrada-PRD.md`) -- escala 1-10 calibra a descompressão, **aglutina `/revisar` + `/refrescar`**, integra cronograma + `/performance`; memória `project_revisao_calibrada`; (2) **Registro onboarding fundacional** p/ temas de iniciante; memória `feedback_registro_onboarding_iniciante`. **🆕 s095 -- sync do cronograma LIVE (F1-F4):** derivador único `tools/cronograma.py` (read-only) + `core/cronograma/grade.json` versionado + `--radar` (cobertura × performance) + `day_plan.py` lê a grade (conteúdo×calendário, 2 ritmos) + contrato `core/contracts/cronograma-contract.md` + skill `/cronograma` + reconcile W5-W7. **🆕 s096 -- Revisão Calibrada IMPLEMENTADA (frente A):** schema `dificuldade*` + `db.set/get_dificuldade` + `infer_nota()` (`day_plan --difficulty`, read-only) + fusão `/revisar` (sub-modos PREPARAR/DRENAR, Invariantes A/B) + `/refrescar` deprecado + contrato `revisao-calibrada-contract.md` (pending-ratification) + 4 specs vibeflow + **63 testes verdes**; `_find_resumo` corrigido (indexa stem). **Política de cards: teto 30/dia (agendados + 15 backlog)** (`feedback_politica_cards_diaria`). Modelo FSRS auditado: agendados (119, têm due) × novos (290, pilha sem due, entram por `--new-limit`). **🆕 s097 -- Curadoria de flashcards (capacidade nova):** workflow `.agents/workflows/curar-cards.md` (5 fases: sanear taxonomia -> diagnóstico -> triagem multi-agente -> curar -> blindar) + `normalize_taxonomia.py` + `insert_card_extra.py` + `detect_clones.py` + linter endurecido (`orfao_sem_andaime`). Achado-mestre: defeito de card é de **autoria** (gerador não valida; linter cego ao semântico) -> **reforjar ancorado no erro > aposentar**; o linter complementa o olho, não substitui. **🆕 s106 -- Harness autônomo + frente de Autogovernança:** `tools/auto_check.py` (modos `--changed`/`--staged`/`--all`, **quotepath-safe**) + `tools/setup_hooks.py` (pre-commit **staged-only** instalado) + `test_autonomia_hooks.py` (test_03 hermético). **PRD `.vibeflow/prds/autogovernanca-proativa.md`** (aprovado): R1 corrige a âncora de fraquezas cega (formatter lê chave plana x envelope LangMem), R2 boot 2 fases estilo ai-eng, R3 harness warning-first, R4 paridade de skills (`.claude/commands` canônica + espelhos gerados), R5 defeitos da frente extensivo, R6 governança AGENTE.md. Frente extensivo `material_indicado` LIVE (`grade.json` + `day_plan`), com defeitos conhecidos (C1/C4/G5) mapeados no PRD. **🆕 s107 -- PRD de Autogovernança 100% IMPLEMENTADO (Partes 1-4, R1-R6; 4 auditorias vibeflow PASS; commit e13ee0b):** **P1 (R1+R2)** -- `app/memory/inspect.py` desembrulha o envelope LangMem `{kind,content}` + dedup/ranking top-8 (fim dos `[? / ?]`); `memory_boot.py` v2 injeta fraquezas + day_plan (subprocess/timeout) + flag de drift + próximo passo + contrato Presença->Expansão. **P2 (R3)** -- `audit_resumos.py` em 2 severidades BLOCK/WARN (encoding deixou de ser mascarado; frontmatter §5.2 + encoding proibido = WARN); `test_roundtrip` isolado em cópia temp; guard de `fsrs`. **P3 (R4)** -- `tools/sync_skills.py` (gerador determinístico, fonte canônica `.claude/commands`, `--check` acusa drift); `revisar` destalado, `estilo-resumo` sem perda, `cronograma` espelhado; WARN de paridade no `auto_check`. **P4 (R5+R6)** -- C1 matching normalizado + G5 precedência (nota explícita vence; extensivo sem nota -> D10 + `deep_research`); heurística `material_indicado` recalibrada (79%->44%); regra D10 única nos 3 artefatos; AGENTE.md §1.3 real + §7.4 (auto_check/setup_hooks/sync_skills) + §6 (2 decisões). **🆕 s121 -- Auto-suficiência de card + telemetria de fila (2 features vibeflow, audit PASS):** `tools/card_self_sufficiency.py` = check WARN no `auto_check` (bloco 8) que detecta cards não-respondíveis-a-frio (opção-anafórico/deítico/pct-fake), com guarda de contexto anafórico (regex cru do audit dava ~30% FP); cospe a worklist de reforja. `day_plan.telemetria_fila` separa **pool** (nunca introduzidos) de **dívida** (vencidos), encerrando o rótulo enganoso "backlog". **M1 executado:** 27 cards reforjados (`recurate_cards`, worklist 24→0). **Estratégia "matar os cards" (M1-M4):** o pool de 425 é dívida de consolidação sobre temas já estudados (não temas futuros); intake fraco-primeiro (Imunizações 18 casado com a task S13), ~20/dia, card fresco entra em ≤2 dias.

### A4 -- Narrativa da s144 no HANDOFF `[origem: HANDOFF.md:28-55, seção "Última sessão"]`

> Substituída no HANDOFF por ≤5 bullets (limite do `handoff-contract.md`). O corpo completo já está narrado
> nas seções acima deste mesmo arquivo -- o que segue é o texto que estava no HANDOFF, preservado verbatim.

Auditoria de arquitetura dos 7 sistemas não-flashcard, disparada pela crítica do usuário ao boot caro.
Loop de 5 fases: scout inline -> 7 subagents Sonnet 5 em paralelo -> cross-check -> verificação
adversarial dos `MATAR` por grep -> síntese. Regra imposta: **arquivar não é resposta; fica ou morre,
e morrer exige prova de zero referência viva.**

**Tese:** a acumulação não é desleixo. O git tem 2,55 MiB, o expurgo de julho foi validado, 182 testes
passam, 12/12 tabelas do `ipub.db` estão vivas e o `.vibeflow/` é mecanismo ativo. O que se acumulou são
**artefatos que funcionam e que nenhum caminho de execução alcança**: 192MB de índice RAG desconectado
por 1 linha, 514 `session_insights` write-only, 11 normas descrevendo sistemas mortos, 2 scripts que
corrompiam dado, 1 sensor pronto e não plugado. Tudo passou pelos gates -- **os gates verificam se está
correto, nada verifica se alguém chega lá.**

**6 defeitos estruturais (D1-D6)**, com `arquivo:linha` no handoff ao ai-eng. Os dois que importam aqui:
**D5** -- o hook `SessionStart` já roda `day_plan.py` antes do primeiro turno e o `AGENTE.md §2 passo 4`
manda rodar de novo, além de exigir um sync do Drive por caminho impossível; 272 palavras do passo
duplicam verbatim o W8 do `reconcile-contract.md`. **D3 -- warning-first virou warning-only:**
`doc_drift.py` reporta "0 achados" olhando 4 arquivos onde as normas mortas não estão; B1 do reconcile
estava ativo e não bloqueou; `sync_skills --check` falha desde 17/07 sem ação.

**Bug aberto:** o `(1250 erros)` do boot vem de `app/memory/manager.py:91-128` (`GROUP BY area` sozinho +
substring com `break`); 25 registros com o mesmo número em 8 áreas. Conserto ~15 linhas, sem schema.

**Correções registradas:** o ritmo medido contra 25/10 e não contra o ENAMED **não é bug** (correção
deliberada da s126, `day_plan.py:508-509`); `history/legacy/` não é lixo; a Camada 3 da memória está viva,
e quem escreve é `tools/hooks/memory_session_log.py`, não o nome citado no `AGENTE.md §8`.

---

*Próximo passo: novo boot, para aferir se a arquitetura melhorou -- é o teste que o usuário pediu.*
