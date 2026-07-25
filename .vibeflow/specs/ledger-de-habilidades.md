# Spec: Ledger de Habilidades

> Gerado via /vibeflow:gen-spec em 2026-07-25
> PRD: `.vibeflow/prds/ledger-de-habilidades.md`

## Objetivo

Promover **habilidade** de string em prosa a entidade consultável do `ipub.db`, permitindo responder "quais habilidades eu falho repetidamente, através de temas diferentes" -- a granularidade que o platô dos 75-80% exige.

## Contexto

`questoes_erros.habilidades_sequenciais` está preenchido em **593/593** registros no formato `A -> B -> C`, mas como TEXT. O sistema narra a cadeia de uma questão e não agrega nada. As "áreas fracas" reportadas hoje são **temas**, granularidade útil na faixa dos 60% e inútil na faixa dos 79% em que o usuário está.

Além disso, `questoes_erros` só é alimentado por questão **errada**: aprendizados colhidos em questão acertada (e o estado "acertei na dúvida") não têm onde morar.

## Definition of Done

1. **Schema idempotente:** `tools/init_db.py` cria `habilidades` e `questao_habilidades`; rodar 2x seguidas não duplica linhas nem levanta exceção.
2. **Backfill não-destrutivo:** `python tools/habilidades.py --backfill` popula o ledger a partir dos 593 registros e **`questoes_erros` permanece inalterada** -- verificável por contagem de linhas + checksum das colunas antes/depois. Zero `UPDATE`/`DELETE` sobre a tabela.
3. **Reincidência consultável:** `--reincidentes` devolve habilidades ordenadas por nº de ocorrências e nº de **temas distintos**, sinalizando explicitamente as que aparecem em **>= 3 temas distintos** (candidatas a padrão de raciocínio, não lacuna de conteúdo).
4. **Enum de veredito fechado:** `veredito` aceita exatamente `acertou | incerteza | errou | indefinido`; valor fora do conjunto levanta `ValueError` com mensagem nomeando os válidos.
5. **Ingestão de questão ACERTADA:** `--add` registra habilidade avulsa **sem** criar linha em `questoes_erros` nem em `sessoes_bulk` -- provado por asserção de contagem nas duas tabelas.
6. **Craftsmanship gate:** `python -X utf8 tools/auto_check.py --changed` sai verde (0 BLOCK); `import sqlite3` apenas em `app/utils/db.py` e no CLI standalone `tools/habilidades.py` (conforme `db-access-layer.md` e conventions.md §Don'ts); arquivos novos em ASCII limpo, sem setas Unicode nem LaTeX (`AGENTE.md §4.5`).

## Escopo

- `tools/init_db.py`: +2 tabelas (`CREATE TABLE IF NOT EXISTS`, padrão do arquivo).
- `tools/habilidades.py` (novo): CLI com `--backfill`, `--report`, `--reincidentes`, `--add`.
- `app/utils/db.py`: helpers de leitura (`get_habilidades_reincidentes`, `registrar_habilidade`) para a camada app/agente.
- `.claude/commands/analisar-questao.md`: passo de emissão de habilidades estruturadas + assinatura canônica do novo CLI (§7.2 do AGENTE: assinatura vive em UMA skill).
- `tools/test_habilidades.py` (novo): suíte cobrindo parser, dedup, enum, barreira de não-escrita.

## Anti-escopo

- 🔴 Clonar Prisma: sem banco de questões, sem SRS por questão, sem "algoritmo sugere próxima questão". O MedHub não possui as questões.
- Integração no `day_plan.py` -- fica para o spec de variância/zona.
- Métrica de variância entre provas e diagnóstico de zona (vídeo 1) -- spec separado.
- Qualquer toque em FSRS, agendamento ou estabilidade.
- Migração destrutiva de `habilidades_sequenciais` -- o campo em prosa permanece como está.
- Taxonomia hierárquica de habilidades (parent/child, árvore).
- Inferência por LLM em lote sobre o histórico -- backfill é parser determinístico.
- UI Streamlit.

## Decisões técnicas

- **Duas tabelas, não uma.** `habilidades` (catálogo, `texto_norm` UNIQUE) + `questao_habilidades` (ocorrência). Trade-off: um JOIN a mais em toda leitura, em troca de dedup real e contagem de reincidência barata. Uma tabela só exigiria agrupar por string a cada query e não sobreviveria a variação de grafia.
- **Normalização para dedup:** lowercase + strip + colapso de espaços + remoção de acentos. Deliberadamente **simples**; sem stemming nem similaridade fuzzy. Trade-off: "afastar C. difficile" e "afastar C.difficile" podem não colapsar. Aceito em v0 -- fuzzy merge é curadoria, não parsing, e falso-merge é pior que duplicata.
- **`questao_id` nullable.** Habilidade de questão acertada não tem erro de origem. Espelha exatamente a decisão já tomada em `insert_card_base.py` (cards de andaime nascem com `questao_id=NULL`) -- padrão existente, não invenção.
- **Backfill marca `indefinido` por default.** Os 593 registros são de questão errada, mas **nem toda habilidade da cadeia falhou** -- tipicamente quebra-se numa só. Inventar `errou` para toda a cadeia envenenaria a métrica de reincidência, que é o produto. `indefinido` é honesto e curável incrementalmente.
- **Parser determinístico com fallback explícito.** Separador ` -> ` (garantido pela convenção ASCII). Registro que não separa vira **uma única** habilidade com o texto inteiro e flag `precisa_curadoria=1` -- nunca descartado silenciosamente.

## Padrões aplicáveis

- `.vibeflow/patterns/db-access-layer.md` -- `sqlite3` só em `db.py` + CLIs standalone de `tools/`.
- `.vibeflow/patterns/error-insertion-pipeline.md` -- o ledger pendura-se no pipeline, não o substitui.
- `.vibeflow/patterns/agent-workflow-protocol.md` -- harness antes de reportar conclusão.
- **Padrão NOVO introduzido:** *ledger normalizado sobre campo de prosa legado* -- extrair estrutura sem migrar destrutivamente a fonte. Documentar em `.vibeflow/patterns/` se repetir.

## Riscos

- **Backfill corromper `questoes_erros`.** Mitigação: DoD-2 exige checksum antes/depois; CLI abre a conexão para escrita apenas nas 2 tabelas novas; teste dedicado.
- **Explosão de duplicatas por grafia.** Mitigação: normalização + `--report` expõe o catálogo para inspeção; falso-merge é evitado por design (preferir duplicata a merge errado).
- **Métrica virar teatro.** Se todo backfill fica `indefinido`, `--reincidentes` nasce vazio e a feature parece inútil no dia 1. Mitigação: `--report` deve mostrar a distribuição de vereditos e dizer explicitamente quantos aguardam curadoria. Honestidade > número bonito.
- **Ledger competir com a memória `weak_areas`.** Mitigação: escopos disjuntos -- `weak_areas` continua por **tema**, o ledger é por **habilidade**. Não sincronizar; são camadas diferentes.
