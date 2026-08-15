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

*Próximo passo: novo boot, para aferir se a arquitetura melhorou -- é o teste que o usuário pediu.*
