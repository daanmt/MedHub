# HANDOFF — Auditoria do MedHub: gaps determinísticos preenchidos pelo modelo

> **Este documento é o OBJETIVO de uma sessão dedicada, com contexto limpo — disparada pelo
> usuário, não automaticamente.** A s160 abre com a autópsia do simulado ENAMED; a auditoria vem
> depois, em janela própria (`HANDOFF.md` itens 4 e 5).
> Escrito em 2026-08-30 (s159) a partir de `~/ai-eng/HANDOFF-AUDITORIA-PERICIA.md`, que
> consolidou a tese "modelo como cola" no pipeline `pericia`. **A tese não se re-litiga aqui**
> — ler a Parte I daquele documento primeiro. Este é o *guia de execução para o alvo MedHub*,
> com o experimento natural, os instrumentos e os suspeitos que são deste repo.

## 🎯 GOAL da sessão de auditoria

1. **Absorver a tese** (Parte I do handoff do `pericia`) e a taxonomia de 4 classes — ela é o
   instrumento central, e este documento assume que ela já está na cabeça.
2. **Re-rodar o graphify no HEAD** (§5): o grafo atual é de 25/08, anterior às 3 sessões
   Antigravity e a tudo que a s159 mexeu.
3. **Executar a auditoria** (§6-§9): caçar onde harness/modelo/operador ainda preenchem gaps
   determinísticos no MedHub.
4. **Entregar a tabela de achados** (§10), numerada como **F43+** no `AUDITORIA_MEDHUB.md`.
5. **Rodar o swap test retroativo** (§11) — o MedHub já tem 3 amostras gravadas.

> **Numeração dos achados:** F43+ no `AUDITORIA_MEDHUB.md`, sem renumerar F1-F42.

---

# PARTE I — A VARIANTE MEDHUB DA TESE

A tese do `pericia`: *o modelo forte vira um componente de RUNTIME não especificado; ao trocar
de modelo ou de IDE você não troca o cérebro, remove uma dependência que nunca foi declarada.*

**No MedHub a cola tem uma segunda perna, e ela é pior.** Além do modelo, existe uma camada de
**77 memórias** em `~/.claude/projects/C--Users-daanm-medhub/memory/`, das quais **51 são
`feedback_*`** — contratos de comportamento ("aula-base é escada de degraus", "nunca perguntar
confirma as notas?", "feedback só nas notas 1-2", "reforja mira a frente, não o verso"). Essas
memórias:

- **estão fora do repositório e fora do git** — não versionam com o código que governam;
- **são específicas do harness** — nenhuma outra IDE as carrega;
- **não têm enforcement** — nenhuma é gate, teste ou schema; todas são prosa injetada no
  contexto do Claude Code;
- **não constam da arquitetura**: `AGENTE.md` §8 chama-se "Modelo de Memória (2 camadas)" e
  diagrama **Camada 1** e **Camada 3**. A camada do meio — justamente estas 51 — não está
  desenhada. A cicatriz na numeração sugere que ela existiu no documento e saiu; da realidade
  não saiu.

Então a formulação MedHub é: **"funciona no Claude Code" = "funciona com um modelo forte MAIS
51 contratos não-versionados que só existem dentro de um harness".** O corolário do `pericia`
vale intacto: você nunca compara modelos, compara sistemas.

Um segundo agravante, específico deste repo: `AGENTE.md` §8 afirma que `error_count` "vem de
`ipub.db` por match exato do par (area, tema); par sem correspondência fica em 0 — **nunca
herda o total da área**". Essa garantia era **falsa na prática** desde a s127 e só caiu na s159
(F37): a defesa existia na camada de match, enquanto a fonte já tinha assado o total da área
dentro de cada tema. **A arquitetura documentava um invariante que o dado violava há meses, e
nada detectou.** Ao auditar, tratar toda afirmação de invariante em `AGENTE.md` e
`core/contracts/` como *hipótese a verificar*, nunca como fato.

---

# PARTE II — O ALVO (MedHub em 1 minuto)

Sistema agêntico de preparação para prova de residência médica. O agente é o cérebro; o código
faz FSRS, derivações do cronograma e gates (`project_pivot_agent_first`). Superfícies: `ipub.db`
(12 tabelas — `sessoes_bulk` é o SSOT de volume, `questoes_erros` o de erro estruturado,
`fsrs_cards`/`fsrs_revlog` o do baralho), `resumos/` (128 .md + PDFs do EMED para RAG),
`core/contracts/` (8 contratos em prosa), `tools/` (~50 CLIs), `.claude/commands/` (11 skills,
espelhadas em `.agents/skills/`), `AUDITORIA_MEDHUB.md` (ledger F1-F42) e o harness
`tools/auto_check.py` (13 checks, rodado por git hook). Boot: `AGENTE.md` → `HANDOFF.md` →
`ESTADO.md` → hook `SessionStart` (que já roda `day_plan.py`).

Diferença relevante em relação ao `pericia`: **não há golden-set nem gabarito homologado.** O
ratchet do `pericia` (61 casos) não tem equivalente aqui — o que o MedHub tem é a suíte (306
testes), o `auto_check` e o ledger. Isso muda o desenho do swap test (§11).

---

# PARTE III — O EXPERIMENTO NATURAL (já aconteceu, e está gravado)

O `pericia` teve um incidente. O MedHub teve **três sessões inteiras**:

| Sessão | Data | Ferramenta |
|---|---|---|
| s142-s155 | 12/08 - 25/08 | Claude Code (Sonnet 5 / Opus 5) |
| **s156** | 25/08 | **Antigravity (Gemini 3.1 Pro)** |
| **s157** | 26/08 | **Antigravity (Gemini 3.7 Flash)** |
| **s158** | 28/08 | **Antigravity (Gemini 3.7 Flash)** |
| s159 | 30/08 | Claude Code (Opus 5) |

**Três defeitos silenciosos nasceram ou sobreviveram nessa janela — todos achados na s159, nenhum
por gate:**

1. **`c4d4532` (s156, "Refactor: Extrair utilitários do auto_check")** moveu `LIMITE_HANDOFF`
   para `tools/utils/state_utils.py` e deixou `test_handoff_teto.py` importando de
   `tools.auto_check`. **A coleta daquele módulo quebrou e ficou quebrada por 3 sessões.** O
   `auto_check` reportou PASSED o tempo todo (o log da s157 diz literalmente "auto_check.py
   PASSED (0 BLOCKs)") porque ele seleciona suíte por arquivo tocado — é o **F35 acontecendo ao
   vivo**: falso verde no gate barato. Classe 2.
2. **`ee45e9d` (s156, "docs(fsrs): resolve ambiguidade de formula do teto")** editou exatamente
   as linhas do teto em `fsrs-management-contract.md`, nomeou `CAP_MULTIPLICADOR`... e manteve
   `TETO_BASE = 30` **enquanto o código dizia 40 desde a s126 (25/07)**. Um commit cujo título é
   "resolver a ambiguidade" passou por cima do número errado. O sensor `DOC_DRIFT`: verde.
   Classe 2 — contrato em prosa sem ligação executável com a constante.
3. **F37** (`registrar_sessao_bulk` somando volume em TODOS os temas da área) atravessou a
   janela crescendo — 3,7x na s127, **5,9x na s159** — corrompendo o ranking de fraquezas que
   abre toda sessão. Classe 3: escrita sem contabilidade, item some sem sinal.

E na própria s159, com modelo forte: **F42** — o agente editou o espelho
`.agents/skills/.../SKILL.md`, o `sync_skills` sobrescreveu em silêncio, `git status` ficou
limpo, e o ledger chegou a registrar uma entrega que não existia mais em disco. **Nem o modelo
forte cobre tudo** — ele só percebeu depois, por acaso (o arquivo não apareceu na lista de
staged do commit).

> **Leitura**: o MedHub não precisa provocar o experimento. Precisa **auditar retroativamente**
> o que já rodou (§11).

---

# PARTE IV — O GUIA DE AUDITORIA

Critério de achado (idêntico ao do `pericia`): *"este comportamento load-bearing vive na
discricionariedade de um modelo/operador, sem contrato executável"* — não "código feio".

## 5. Instrumentos

| Instrumento | O quê | Cuidado |
|---|---|---|
| `graphify-out/` | 1.344 nós · 2.408 arestas · 75 comunidades (68 nomeadas, 7 finas omitidas) · **90 arestas INFERRED, confiança média 0,84** | **Construído em 2026-08-25** — antes das 3 sessões Antigravity e de toda a s159. É o snapshot "antes". **Re-rodar no HEAD antes de qualquer conclusão estrutural**; o build velho vale como termo de comparação |
| `~/.claude/projects/C--Users-daanm-medhub/memory/` | 77 memórias · **51 `feedback_*`** | O alvo principal (§8). Fora do git |
| `AGENTE.md` (295 linhas) | Contrato canônico do agente | §8 numera Camada 1 e 3 e omite a do meio; §2 passo 3 manda rodar reconcile "BLOCKING" que nenhum código impõe |
| `core/contracts/` (8) | Normas em prosa | Ligação com o código é por convenção; ver assinatura "constante duplicada" (§6) |
| `tools/auto_check.py` | 13 checks | **Só 2 são BLOCKING** (B1 do HANDOFF, integridade FK). Os outros são WARN — D3/s144 já nomeou: "warning-first virou warning-only". `--changed` seleciona suíte por path tocado |
| `pytest.ini` | `python_files` = **allowlist manual** | Suíte nova NÃO é coletada até ser inscrita à mão. Mesmo modo de falha do D4/alcançabilidade |
| `AUDITORIA_MEDHUB.md` | Ledger F1-F42 | Já é o instrumento. Achados novos entram como **F43+**, sem renumerar |
| `history/INDEX.md` + `session_*.md` | Registra **qual ferramenta rodou cada sessão** | É o log do experimento natural. Preservar o campo `Ferramenta:` |
| Suíte: 306 testes + git hook pre-commit | O ratchet possível | Sem golden-set: cobre código, não a QUALIDADE do output de estudo |

## 6. Assinaturas do padrão (o que grepar/perguntar)

- **Constante duplicada entre código e prosa**: um número que existe em `tools/*.py` E em
  `core/contracts/*.md`. Pergunta: *o que garante que os dois batem?* (Hoje: nada. Foi assim que
  `TETO_BASE` ficou 30×40 por 5 semanas.) Cruzar os números de `core/contracts/` com as
  constantes nomeadas de `tools/`.
- **Contrato comportamental na memória**: qualquer `feedback_*.md` com "sempre", "nunca",
  "não perguntar", "🔴". Pergunta: *se o próximo agente não carregar esta memória, o que quebra
  e quem percebe?*
- **Aviso sem gate**: `[WARN]`, `⚠️`, `pendente`, `conferir`, `revisar`, `backlog`, `TODO` em
  código e em skills. *Quem é OBRIGADO a consumir? O que acontece se ninguém consumir?*
- **Espelho gerado sem banner**: arquivo produzido por script que não se declara gerado (F42).
  `tools/sync_skills.py`, e procurar outros geradores.
- **Allowlist/registro manual**: `pytest.ini` `python_files`, listas de suítes no `auto_check`,
  `MEMORY.md` (índice mantido à mão), `core/provas.json`. *O que acontece com o item que alguém
  esqueceu de inscrever?* — ele existe e não roda.
- **Campo de estado sem reconciliador**: coluna escrita por alguém e lida por outro, sem check
  de coerência (F37 era exatamente isso). Inventariar as 12 tabelas: para cada coluna, *quem
  escreve, quem lê, o que reconcilia?*
- **Pipeline com dois finais**: dois CLIs que podem ser tomados um pelo outro (F38:
  `insert_questao` × `habilidades --add`). Procurar outros pares.
- **Passo "o agente faz"**: etapa cujo executor é o modelo lendo uma skill. É a maioria do
  MedHub por design (`project_pivot_agent_first`) — o achado não é a existência, é a **ausência
  de detector** quando o passo não acontece.

## 7. Método com o knowledge graph

O grafo é obrigatório, não opcional — sem ele a auditoria vira grep na sorte (o F37 só fechou
porque o grafo devolveu o conjunto de escritores incluindo migrations arquivadas que nenhuma
busca por nome teria alcançado).

1. **Costuras entre comunidades** do fluxo (Boot/Plano do Dia → Cronograma → Análise de Questão
   → Flashcards/FSRS → Auditoria/Gates → Memória): o artefato trocado na fronteira tem schema
   validado? A falha ali é ruidosa?
2. **Nós-ponte**: ponte que é FUNÇÃO é boa; ponte que é CONVENÇÃO (nome de arquivo, ordem de
   execução, "o espelho espelha a fonte") é candidato — F42 é uma ponte-convenção que quebrou.
3. **90 arestas INFERRED**: se o extrator estático só infere, um modelo fraco também só infere.
   Listar todas; cada uma vira código explícito ou contrato.
4. **7 comunidades finas omitidas do report**: mortas, ou conectadas só por prosa/operador — as
   segundas são achados (é a frente `project_alcancabilidade_auditoria`, que é a MESMA tese por
   outro ângulo: *"os gates verificam correção e nada verifica alcance"*).
5. **Delta 25/08 × HEAD**: re-rodar e diffar. As arestas que a s159 criou (`questoes_erros` →
   contador de fraquezas; `[bulk] area` → taxonomia) são o desenho do que "codificar um gap" faz
   com o grafo. Procurar fluxos análogos que ainda não têm a aresta equivalente.

## 8. Os 51 contratos da memória como alvos (o análogo dos "gotchas")

Este é o coração da auditoria do MedHub. Auditar **um a um**: *dá para converter em código,
gate ou teste? Se não, por quê?* Amostra do que espera lá dentro:

| Memória | Natureza | Pergunta de auditoria |
|---|---|---|
| `feedback_revisar_override_passivo` ("nunca perguntar 'confirma as notas?'" — reprovado 3×) | regra de conduta reincidente | 3 reincidências é sinal de que prosa não segura. Vira passo da skill com default explícito? |
| `feedback_revisar_feedback_so_1_2` | regra de formato do output | o `/revisar` pode impor por template em vez de confiar? |
| `feedback_politica_cards_diaria` | número (teto 60/dia) | **triplicado**: memória + `day_plan.py` + contrato FSRS. Zero reconciliador |
| `feedback_aula_base_ancorar_pdf_emed` ("🔴 buscar o PDF-fonte antes de QUALQUER aula-base") | passo obrigatório sem gate | nada verifica se o PDF foi lido. Detector barato? |
| `feedback_artifact_width_alignment` ("checar com `grep max-width` antes de publicar") | verificação manual pré-entrega | por que não é lint? |
| `project_cronograma_dual_ssot` | armadilha de ordem | o `--sync-drive` está quebrado há 6 sessões (F36) e a norma manda confiar nele |
| `feedback_subagent_unico_analise_questoes` | política de orquestração | invisível para qualquer outro harness |

Saída esperada: para cada uma, um veredito em **{vira código · vira gate · vira teste · vira
schema · permanece prosa com justificativa}**. "Permanece prosa" é resposta legítima — mas
precisa do *porquê*, e conta como dívida declarada.

## 9. Inventário de suspeitos residuais (partida, não lista fechada)

a. **[2] Os 51 `feedback_*`** — §8. O maior bloco por volume e o mais invisível.
b. **[2] `AGENTE.md` §2 passo 3** — manda rodar o reconcile e chama de BLOCKING; nenhum código
   bloqueia. Contrato que se autodeclara gate sem ser.
c. **[2] Constantes duplicadas código × contrato** — `TETO_BASE`/`CAP_MULTIPLICADOR` (já bateu),
   `LIMITE_HANDOFF` (60, em 2 lugares — travado por teste, é o modelo a seguir),
   `PISO_ERROS_ORFAOS`, `JANELA_CREDITO_DIAS`, marcos de `performance.py`. Inventariar e travar
   por teste.
d. **[2] `pytest.ini` allowlist** — quantas suítes existem em `tools/test_*.py` e NÃO estão na
   lista? Rodar o diff. Cada ausente é um D4 vivo.
e. **[3] WARNs não-bloqueantes do `auto_check`** — hoje: 313 de atomicidade, 9 de
   auto-suficiência, 3 de cobertura, 2 de alcançabilidade, 1 de erro órfão. *Qual é o critério
   para um WARN virar BLOCK?* Sem critério, WARN é ruído com carimbo de qualidade.
f. **[1/2] `auto_check --changed`** — seleção de suíte por path é a causa provada do falso verde
   de 3 sessões. Propor: mudança em `tools/utils/` ou `core/contracts/` força suíte completa.
g. **[2] Espelhos `.agents/skills/`** — F42. Banner de "gerado" + aviso do sync quando o espelho
   tem mtime mais novo que a fonte.
h. **[3] Colunas de `ipub.db` sem reconciliador** — F37 fechou uma. Fazer o inventário das 12
   tabelas (escritor × leitor × reconciliador) é provavelmente o item de maior rendimento.
i. **[2] F36 (`--sync-drive`)** — 6 sessões sem rodar, e o ledger já concluiu que **só código
   resolve**. O modo degradado (`read_file_content` devolve a planilha inteira como texto) está
   documentado e não implementado. Enquanto isso a ordem do cronograma vem do PDF, não do que o
   usuário reordenou à mão.
j. **[meta] Pontos cegos do ratchet** — a suíte cobre código. **Nada** cobre a qualidade do
   output de estudo (aula-base cumpriu o escopo? card é atômico? feedback seguiu a política?).
   O `pericia` resolveu com golden-set; o MedHub não tem análogo. Decidir se cria um (ex.: 5
   aulas-base homologadas pelo usuário como referência) ou aceita a lacuna declarada.
k. **[4] Piso de capacidade** — qualidade clínica da explicação, calibragem da descompressão.
   Não confundir com 1-3; não é alvo desta auditoria.

## 10. Formato do achado (entregável)

Tabela única, um achado por linha, numerada a partir de **F43**:

`| id | onde (módulo/fronteira) | classe (1-4) | evidência (arquivo:linha / aresta / memória) | mitigação atual (código/gate/teste/doc/nenhuma) | proposta | prioridade |`

**Regra de ouro** (herdada, não negociável): a proposta converte sempre para (a) código,
(b) gate bloqueante, (c) teste/fixture, ou (d) schema validado. **Documentação é complemento,
nunca a mitigação** — este documento inclusive.

## 11. Swap test do MedHub — retroativo, porque as amostras já existem

O `pericia` roda o pipeline headless com modelo fraco. O MedHub não é pipeline: é sessão
interativa. Adaptação:

1. **Amostras**: os commits das sessões **s156, s157 e s158** (Antigravity/Gemini), listados na
   Parte III, contra os contratos vigentes na época.
2. **Para cada sessão**, verificar mecanicamente: HANDOFF atualizado dentro do teto? log de
   sessão criado e indexado? `auto_check` rodado? escritas no `ipub.db` coerentes com o que o
   log narra (o gate F38 já responde parte disso)? contratos de `core/contracts/` respeitados?
3. **Classificar cada divergência nas classes 1-4.** A hipótese a testar: a maioria é classe 2
   (contrato implícito que o Claude Code cumpria por leitura espontânea), não classe 4.
4. **Maturidade**: divergência estrutural (1-3) = 0, ou a sessão TRAVOU ruidosamente. Hoje
   sabemos que o placar é ≥ 3 divergências não travadas.
5. A contagem por classe, por sessão, vira a série temporal da dívida de harness do MedHub — e o
   campo `Ferramenta:` do log é o que torna a série possível. **Não remover esse campo.**

## 12. Salvaguardas

- **Read-only sobre o motor**: a auditoria produz **achados**, não patches. Conserto é sessão
  própria, com teste antes. (A s159 fez as duas coisas juntas e funcionou, mas porque o escopo
  era pequeno — numa varredura ampla isso vira commit gigante sem revisão.)
- **Não renumerar o ledger**: F1-F42 são referências vivas em memórias, logs e commits.
- **Não confundir classe 4 com 1-3** — o erro comum é atribuir tudo à capacidade do modelo.
- **Editar a FONTE, nunca o espelho** (F42): `.claude/commands/` é fonte, `.agents/skills/` é
  gerado.
- **Não tocar no `ipub.db`** durante a auditoria. Reconciliação de dado é operação separada, com
  o usuário no loop (a de F37 está pendente de decisão dele).
- **Tratar invariante documentado como hipótese**, não como fato: `AGENTE.md` §8 afirmava uma
  garantia que o dado violava há meses.
- **Este documento é prosa e sabe disso.** Pela própria regra de ouro do §10 ele não vale como
  mitigação de nada — vale como plano. O que o torna alcançável é o `HANDOFF.md` apontar para
  ele como próximo ato; se isso sair do HANDOFF, este arquivo vira mais um artefato que funciona
  e ninguém alcança — a definição exata do problema que ele descreve.
