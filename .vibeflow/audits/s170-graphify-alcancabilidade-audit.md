# Auditoria de Alcançabilidade — /graphify (MedHub)

Data da auditoria: 2026-09-08. Modo: READ-ONLY (nenhum arquivo editado, grafo não regenerado).

## 0. Correção de premissa

A tarefa presumia **dois** `graphify-out/` (repo + `~/.claude/skills/graphify/`). Falso:
`~/.claude/skills/graphify/` contém só `SKILL.md` (43.292 bytes), `references/*.md` (8 arquivos)
e `.graphify_version` (`0.9.49`) — é a **instalação da skill**, não um output. Não há
`graphify-out/` lá dentro. `find /c/Users/daanm -iname graphify-out` só acha três, um por
projeto: `medhub/graphify-out`, `Daktus/daktus-hub/graphify-out`, `pericia/graphify-out` —
irrelevantes entre si. Não existe divergência de "duas cópias do mesmo grafo" — existe um
único `graphify-out/` no repo, e **dentro dele** dois grafos distintos e não sobrepostos
(ver §3).

## 1. Frescor do índice

- `graph.json` / `GRAPH_REPORT.md` / `manifest.json` / `graph.html` / `cost.json`: todos com
  mtime **2026-08-30 16:32:08–16:32:43 -03:00** (mesmo lote — a última regeneração completa).
- `graph.json["built_at_commit"] = 9e3785a` → `git cat-file -t 9e3785a` = commit real,
  mensagem "feat: alvo de cobertura do conteudo vira decisao declarada (01/11)".
- HEAD atual = `5b1f682` (2026-09-08 12:19:19, sessão s170).
- `git rev-list --count 9e3785a..HEAD` = **36 commits** de defasagem (9 dias corridos,
  30/08→08/09).
- `git diff --name-status 9e3785a..HEAD` = **114 arquivos mudaram** desde a regeneração
  (46 A / 66 M / 2 D).
  - **70 desses 114** caem dentro do próprio escopo que o grafo alega cobrir
    (`tools/`, `core/`, `.agents/`, `.claude/`, `.vibeflow/`, `app/`, `docs/`, `.md` de raiz):
    26 A / 42 M / 2 D — **35% do escopo indexado (198 arquivos no manifest) mudou em 9 dias**
    sem o grafo saber. Entre os 26 novos: um comando inteiro novo
    (`.claude/commands/aula-base.md` + espelho em `.agents/skills/`) e **9 arquivos de teste**
    novos (`tools/test_boot_verdadeiro.py`, `test_contrato_reconcile.py`,
    `test_cronograma_pdf_path.py`, `test_exit_codes.py`, `test_fsrs_balance_stdout.py`,
    `test_fsrs_queue_prevalencia.py`, `test_painel_divida.py`, `test_rag_sensores.py`,
    `test_writer_allowlist.py`) — inexistentes como nós.
  - **27 dos 114** são mudanças em `resumos/` — área que o grafo nunca cobriu (§2).
- Histórico de regenerações: só **2 na vida do artefato** (`cost.json`): 25/08 (124 arquivos,
  escopo `tools/+core/`) e 30/08 (88 arquivos, escopo ampliado mas ainda sem `resumos/`).
  Nenhuma desde então, apesar da regra que manda rodar `graphify update .` a cada sessão
  que mexe em código (§4).

## 2. Cobertura

- `GRAPH_REPORT.md` (30/08): **"88 files · ~820.509 words"** extraídos — de
  **685 arquivos rastreados pelo git** no repo hoje (`git ls-files | wc -l`). **~13% de
  cobertura** do repo, mesmo antes de contar a defasagem do §1.
- `manifest.json` (cache incremental, acumula as 2 rodadas) tem 198 chaves; `graph.json`
  tem 182 `source_file` únicos. Breakdown do manifest por topo de diretório: `tools/` 104,
  `core/` 23, `.agents/` 18, `.claude/` 14, `app/` 13, `.vibeflow/` 10, `docs/` 5,
  8 `.md` de raiz, `history/INDEX.md`, `requirements.txt`, `conftest.py`.
- **`resumos/`: 0 de 136 arquivos `.md` rastreados indexados no grafo raiz.** Isso
  contradiz o próprio `.gitignore:56` — `"# /graphify output — regenerável a partir do
  source (tools/, resumos/, etc.)"` — que lista `resumos/` como fonte esperada. A promessa
  documentada no comentário nunca foi cumprida.
- Dentro do próprio escopo alegado (as pastas acima), **195 arquivos** existem no repo mas
  não viraram nó (`comm -23` entre `git ls-files` dessas pastas e os 182 `source_file`):
  164 são `.vibeflow/{audits,prds,specs}/*.md` (documentação de trace efêmera — plausível
  exclusão deliberada, mas não documentada em lugar nenhum), e **31 são código/dados reais
  não-triviais**: 12 em `tools/` (9 deles os `test_*.py` novos do §1, mais
  `tools/data/competidores_categorias.json`, `tools/eval/queries.json`), 15 em `core/`
  (JSON de cronograma/simulados — provavelmente excluídos por serem dados, não código, mas
  sem confirmação no `SKILL.md`), 3 em `.claude/` (`settings.json`, `settings.local.json`,
  `commands/aula-base.md`), 1 em `.agents/` (`skills/source-command-aula-base/SKILL.md`).

## 3. Os dois grafos dentro de `graphify-out/`

Não é "canônico vs. cópia" — são **dois experimentos de escopo diferente da sessão 155
(25/08, MVP do `/graphify` no MedHub)**, confirmados por `history/session_155.md`:
- **Raiz** (`graph.json`): escopo `tools/+core/` → depois ampliado (25/08→30/08) para
  incluir `.agents/.claude/.vibeflow/docs/`+`.md` de raiz. 1940 nós, 3374 arestas,
  construído por último em 30/08.
- **`pediatria-go/`**: escopo `resumos/Pediatria/`+`resumos/GO/` (42 arquivos, fundido
  deterministicamente com overlay de `ipub.db` — erros/flashcards/FSRS). 1258 nós,
  construído em 25/08 e **nunca mais tocado**. Rótulos de comunidade ficaram no genérico
  ("Community 0", "Community 1"...) — o Passo 5 do `SKILL.md` (nomear comunidades em
  linguagem natural) nunca foi concluído para este grafo, ao contrário do grafo raiz, que
  tem nomes reais ("Camada de acesso ao DB", "Auto-suficiência de card" etc.). É um piloto
  abandonado a meio caminho, isolado do grafo raiz — não fala com ele, não é atualizável
  junto (comandos diferentes, escopos diferentes).

## 4. Uso real

- `git grep -il graphify` no repo rastreado: `.agents/rules/graphify.md`,
  `.agents/workflows/graphify.md`, `.gitignore`, `AUDITORIA_MEDHUB.md`, `README.md`,
  `docs/HANDOFF-AUDITORIA-MEDHUB.md`, `history/INDEX.md`, `history/session_155.md`,
  `history/session_156.md`, `tools/auto_check.py` (só um comentário de nome de missão de
  refactor, "Graphify Missão 3" — não é uso da ferramenta).
- **`AGENTE.md` — o documento canônico de boot ("leia antes de qualquer ação") — tem ZERO
  menções a graphify.** Não está na tabela de CLIs §7.4, não está em nenhuma seção.
- `.agents/rules/graphify.md` (`trigger: always_on`) instrui: *"Após modificar arquivos de
  código nesta sessão, rode `graphify update .`"* — mas **nada no repo lê `.agents/rules/`**
  (`git grep ".agents/rules"` só bate no próprio arquivo). Não faz parte da sequência de
  boot descrita em `AGENTE.md` (HANDOFF→ESTADO→reconcile→Plano do Dia→workflow→log→
  memória→RAG). É formato de frontmatter de outro framework de agente (estilo Windsurf/
  Cascade), colado no MedHub e nunca conectado.
- `.claude/settings.json` tem só 2 hooks: `SessionStart` (`memory_boot.py`) e
  `PostToolUse[Write]` (`memory_session_log.py`). **Nenhum hook chama `graphify update`.**
- `tools/reachability_check.py` — o próprio gate de alcançabilidade — tem
  `ALVOS = ["tools/*.py", "app/**/*.py"]` (linha ~44): verifica se scripts Python têm
  chamador vivo. **`graphify-out/` e a skill `/graphify` não são alvo do check — o
  instrumento que existe para pegar exatamente este tipo de problema não tem este
  artefato no radar.**
- Único uso substantivo documentado na vida do artefato: a auditoria de engenharia s159
  (`AUDITORIA_MEDHUB.md:964`, `docs/HANDOFF-AUDITORIA-MEDHUB.md:20,178`), que **regenerou o
  grafo ad hoc só para aquela tarefa** e cujo próprio handoff já registrava, antes de usar:
  *"o grafo atual é de 25/08, anterior às 3 sessões Antigravity e de toda a s159 [...]
  Re-rodar no HEAD antes de qualquer conclusão estrutural"* — ou seja, os próprios
  auditores já tratavam o índice como não-confiável por padrão. Essa mesma auditoria
  também documentou um falso-negativo do extrator: *"graphify reporta 'Import Cycles:
  None' mas rag.py↔get_topic_context tem ciclo real [...] (limite do extrator)"*
  (`AUDITORIA_MEDHUB.md:991`).

## 5. Custo de regeneração

- `cost.json`: 2 rodadas na vida do artefato. 25/08: 200k tokens de entrada / 11,4k saída
  (124 arquivos). 30/08: 680k entrada / 0 saída (88 arquivos — extração semântica via
  subagentes, sem tracking de output nesse modo).
- Por `SKILL.md`: extração AST de código é grátis/local/determinística (sem LLM, sem rede).
  Extração semântica de `.md`/docs **exige despachar subagentes Claude em paralelo**
  (~20-25 arquivos por chunk, ~45s por lote) OU uma `GEMINI_API_KEY`/`GOOGLE_API_KEY`
  (não configurada aqui) — ou seja, **não é um comando de CLI barato**: precisa de uma
  sessão interativa do Claude Code orquestrando Agent tool calls.
- Existe `--update` incremental (só reextrai arquivos novos/mudados, AST grátis para
  código) — mas **nunca foi invocado** apesar da regra `always_on` mandando isso a cada
  sessão. A parte incremental barata (código via AST) poderia em tese rodar num hook
  `post-commit`; a parte cara (semântica, que é a única forma de indexar `resumos/`, o
  conteúdo clínico que mais importa para este usuário) não tem caminho barato de
  automação — sempre vai exigir uma sessão de agente ativa.

## Veredito: MORRE

**Justificativa em 3 linhas:** (1) o grafo cobre 88/685 arquivos do repo (13%) e nunca
indexou `resumos/` (0/136) apesar do próprio `.gitignore` prometer isso — a fatia que mais
importaria para o usuário (conteúdo clínico) está ausente por design, não por atraso; (2)
mesmo dentro do escopo que cobre, 35% dos arquivos indexados mudaram nos últimos 9
dias/36 commits sem regeneração, e a regra `always_on` que deveria manter isso fresco não
é lida por nada no repo, não tem hook, e não aparece em `AGENTE.md`; (3) o próprio gate de
alcançabilidade (`reachability_check.py`) não tem este artefato no radar (`ALVOS` só cobre
`tools/*.py`/`app/**/*.py`), e o único uso real em 14 dias de vida foi um regen manual ad
hoc para uma auditoria pontual, cujos autores já desconfiavam do índice antes de usar.
Manter "por enquanto" significa continuar pagando ciclos de sessão para rodar um pipeline
de subagentes cujo output ninguém consulta entre regenerações — sem hook nem menção em
`AGENTE.md`, é indistinguível de morto entre uma auditoria e a próxima.

**O que deletar:**
- `C:\Users\daanm\medhub\graphify-out\` inteiro (nunca foi versionado — `git status
  --ignored` confirma; apagar é `rm -rf`, zero perda de histórico git).
- `.agents/rules/graphify.md` (regra órfã, nada a lê).
- `.agents/workflows/graphify.md` (workflow que só existe para uma skill que não vai
  mais rodar aqui).
- Não editar `history/session_155.md`/`session_156.md`/`AUDITORIA_MEDHUB.md` — são log
  histórico, não referência viva; deixar como registro do experimento.
- `README.md:136` menciona `graphify-out/` na lista de local-only — ajustar quando o
  usuário aprovar a remoção (fora do escopo READ-ONLY desta auditoria).

**Se o usuário preferir FICA em vez disso**, o mínimo para deixar de mentir por omissão
seria: (a) trocar `.agents/rules/graphify.md` por uma linha real em `AGENTE.md` §7 citando
o comando e quando rodar; (b) hook `post-commit` chamando `graphify update .` (cobre só a
metade AST/código, grátis); (c) um check de frescor em `auto_check.py`/
`reachability_check.py` que WARN quando `built_at_commit` está a mais de N commits do
HEAD; (d) decidir e documentar explicitamente se `resumos/` entra ou fica de fora — hoje
é uma lacuna silenciosa, não uma decisão.
