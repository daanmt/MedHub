# HANDOFF PRD: Sensor de drift doc-vs-código no auto_check (degrau 1/4 — auto-evolução)

> Gerado via M-HAND on 2026-07-12 — Fable/ai-eng (arquiteto observador).
> **Destinatário: o agente INTERNO do MedHub.** O MedHub toca isto internamente:
> `/vibeflow:gen-spec` → `/implement` → `/audit` sobre este PRD. O arquiteto NÃO implementa.
> Série: degrau 1 de 4 do plano de auto-evolução (origem: sessão N=65 do ai-eng,
> `ai-eng/brain/interactions/2026-07-12-handoff-medhub-autoevolucao.md`).

## ⛔ Fronteira clínica (invariante da série toda)

Engenharia pura. O sensor compara **docs ↔ código/schema/estado** — paths, símbolos,
contadores, constraints. Ele **NUNCA lê ou julga conteúdo médico**: o texto de
`resumos/**/*.md`, pergunta/resposta de cards, dose/conduta/critério clínico estão fora.
Se uma verificação exigir interpretar mérito médico, ela não pertence a este sensor.

## Problema

A dívida dominante do MedHub hoje é **drift documental**: docs afirmam coisas que o
código/schema/estado desmentem. Evidência (auditoria 2026-07-12,
`docs/AUDITORIA-MECANISMO-CONHECIMENTO-2026-07-12.md`): 3 das 4 dores investigadas eram
drift doc-vs-código, não bugs. Casos concretos reconciliados À MÃO nessa sessão:

- ROADMAP marcava "FSRS fiel" como TODO — já estava implementado (`46df800`).
- ROADMAP mandava corrigir `get_next_due_card()`/`frente`/`verso` em `db.py` — já removidos.
- Contadores narrativos no HANDOFF divergindo do derivável (padrão F6 do ledger).

O sistema já detecta duas formas pontuais de drift (checks 4 e 5: `SESSION_POINTER_DRIFT`,
`POSICAO_DRIFT`), mas a classe geral — *"o que o doc afirma vs o que o repo é"* — só é
detectada quando um humano/arquiteto audita na unha. Padrão `Drift-as-Primary-Debt` (N=1,
registrado em `ai-eng/brain/observed-systems/2026-07-12-medhub-mecanismo-conhecimento.md`).

## Público-alvo

O harness do MedHub (autogovernança) e o operador — que hoje só descobre doc stale quando
uma sessão de auditoria externa acontece.

## Solução proposta (WHAT, não HOW)

Um **check 7** no `auto_check.py`, WARN-first (padrão exato dos checks 4/5/6: função
retorna achados ou vazio → `[WARN] DOC_DRIFT: ...` → `success=True`, não rebaixa o
veredito), cobrindo **duas classes de drift mecanicamente verificáveis**:

1. **Contador declarado ≠ derivado.** O HANDOFF já marca números com a proveniência
   `[derivado: day_plan --handoff-block]`. O sensor re-executa a derivação declarada e
   compara com o número escrito no doc. Divergência → WARN com os dois valores.
2. **Claim de existência ≠ repo.** Afirmações do tipo "X existe / não existe / tem a
   constraint Y" em ROADMAP/HANDOFF/ESTADO, verificáveis por inspeção mecânica (símbolo em
   arquivo, coluna/índice no schema do `ipub.db`, arquivo em path). Como claims em prosa
   livre não são parseáveis com honestidade (anti-fabricação: NÃO prometer NLP), o PRD
   propõe uma **convenção de anotação machine-readable** nos docs — ex.: comentário
   `<!-- drift-check: <tipo> <alvo> <esperado> -->` ao lado do claim. Sintaxe exata: decisão
   do gen-spec. **Seed obrigatório**: anotar os claims reconciliados em 2026-07-12 (FSRS
   fiel FEITO; `get_next_due_card` removido; `UNIQUE(area,tema)` ABERTO — este último deve
   emitir WARN até o handoff de integridade fechá-lo, e calar depois: é o teste vivo do sensor).

A regra de comparação mora num módulo próprio (ex.: `tools/doc_drift.py`); o `auto_check`
só orquestra — mesmo padrão do check 3 ("a regra mora no gerador; o auto_check orquestra").

## Critérios de sucesso (o gen-spec transforma em DoD binário)

1. `auto_check --all` executa o sensor e o relatório final mostra a linha do check 7 com
   contagem de WARNs; nenhum WARN altera o exit-code (WARN-first preservado).
2. Falsificação deliberada de um contador `[derivado: ...]` no HANDOFF → WARN apontando
   doc-valor vs derivado-valor. Restaurado → silêncio.
3. Os claims-seed anotados são verificados: o claim `UNIQUE(area,tema)` ABERTO emite WARN
   enquanto a constraint não existe; após o handoff de integridade criá-la, o mesmo run cala.
4. O sensor não abre nenhum arquivo de `resumos/` nem lê texto de cards (verificável no
   código: allowlist de docs-alvo = ROADMAP.md, HANDOFF.md, ESTADO.md, AUDITORIA_MEDHUB.md).
5. `pytest` verde; suíte nova para o módulo do sensor (casos: derivado-diverge,
   claim-existe, claim-não-existe, anotação malformada → WARN de sintaxe, nunca crash).

## Anti-escopo

- **NÃO** auto-corrigir docs (detecção apenas; correção é humana ou de ciclo futuro).
- **NÃO** escrever achados no ledger automaticamente — isso é o degrau 2 (auto-instrumentação);
  aqui o achado vive no output do run.
- **NÃO** parsear prosa livre / claims não-anotados (anti-fabricação).
- **NÃO** transformar WARN em bloqueio.
- **NÃO** tocar conteúdo clínico (fronteira acima).
- **NÃO** duplicar os checks 4/5 existentes — o check 7 cobre as classes novas.

## Contexto técnico (para o gen-spec interno)

- `tools/auto_check.py` (341 ln): checks 4/5/6 nas linhas ~281-320 são o template exato
  (função pura testável + print `[WARN] TAG:` + `success=True`).
- **Coordenação de merge**: o handoff `HANDOFF-integridade-harness-taxonomia.md` também
  edita `auto_check.py` (cobertura de suítes). Sequenciar: integridade primeiro OU manter o
  check 7 autocontido (função + 1 bloco no `main()`) para merge trivial. Decisão do agente interno.
- Derivação de contadores: `day_plan --handoff-block` já existe (F6 é o precedente do padrão).
- Schema-check: `ipub.db` via `PRAGMA index_list`/`table_info` — leitura, nunca DDL.
- Budget: ≤4 arquivos (`doc_drift.py` novo · `auto_check.py` · teste novo · anotações-seed nos docs).

## Handoff — como o MedHub toca isto

1. `/vibeflow:gen-spec .vibeflow/prds/HANDOFF-sensor-drift-doc-codigo.md`
2. `/vibeflow:implement` + `/vibeflow:audit`, gate de PASS.
3. Ao fechar: registrar no `AUDITORIA_MEDHUB.md` (à mão, ainda — o degrau 2 automatiza isso)
   e reconciliar a linha correspondente do ROADMAP.

## Questões abertas

- Sintaxe da anotação drift-check (comentário HTML vs bloco YAML vs tabela dedicada) — gen-spec.
- Rodar o sensor também no `--changed` (só quando docs-alvo mudam) vs só no `--all` — custo/latência, gen-spec.
- O ledger (551 ln, prosa) entra como doc-alvo de anotações já no degrau 1 ou só após o degrau 2 — gen-spec.
