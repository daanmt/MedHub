# Spec: medhub Fase 0 · Lote 1 — Part 1.1a: a captura declara a figura perdida e as figuras entram por mescla (código)

> Gerada: 2026-10-11 ~12:15 (medhub, s223, `/vibeflow:gen-spec`) | Origem: P5 do ai-eng = **M-042** (`docs/BACKLOG-UNICO-MEDHUB.md:79`): recapturar as figuras da t40 Q5/6/18/21/22, declarar `sem_figura` na captura, varrer S4-S7. Fontes: `history/session_222.md:40`, `history/session_220.md:33`, captura de figura da s221 (`tools/emed_api.py:142`, `:218-221`).
> Repo-alvo: medhub. HEAD de partida: `081ca1b`. Irmã: **1.1b** (a operação de recaptura e o aviso no hub), que só começa com esta em PASS.

## Objective

Toda questão do banco que cita uma imagem ausente passa a ser DECLARADA (`sem_figura`), em vez de sumir calada. A figura recapturada entra no banco por mescla junto do `emed_id`, sem reescrever enunciado, gabarito, solução nem resposta.

## Context

Medido em 11/10, só leitura:
- **Origem da perda, em 3 camadas.**
  - (1) A captura pelo Chrome (26/09; `claude-in-chrome` 91 linhas, `claude-code-chrome` 240) perdia a imagem: a t40 inteira é dessa época.
  - (2) A captura pela API até a s220 nunca marcava figura, porque lia o `statement_text`, que é texto puro (0 de 2.322 docs).
  - (3) Desde a s221 (08/10), a URL da `<img>` do ENUNCIADO viaja em `figuras`. Mas as listas capturadas em 07/10 (a maioria da S4-S7) são anteriores a isso.
  - No `ipub.db` são 212 de 3.040 linhas de `emed_questoes` com `figuras` em `extras`. Nas capturas locais (`tmp/emed_*`), 91 de 2.569 docs.
- **Nenhum sensor.** Não existe check de "enunciado cita figura/tabela/gráfico e o doc não tem `figuras`". Quem acusou foi o subagente das Soluções v3 (`sem_figura` no `PRONTO.json`; brief `tmp/brief_v3_lote_s222.md:8`). Varredura grosseira por regex nas capturas locais: 150 suspeitos em 58 listas (t734 9, t325 7, t393 7, t110 6, t1 6, t40 5...).
- **Alternativa-imagem:** `extrair` guarda só o booleano (`emed_api.py:228-236`). O parser já coleta `srcs`, mas a URL da alternativa não sai.
- **Ingestão:** `emed_banco.py --ingerir` -> `db.emed_upsert_questoes` (`app/utils/db.py:2498`). O `ON CONFLICT DO UPDATE` (`:2553-2568`) troca TODAS as colunas de conteúdo. Para uma linha do Chrome, reingerir a captura da API reescreveria o enunciado e as alternativas de uma lista já resolvida: é por isso que esta part cria uma mescla estreita. `figura`/`figuras` moram em `extras`, que entra no hash (`:2283-2290`); `figuras_img` fica fora do hash (`:2296-2298`).
- **Hub:** o doc `questoes/<lista>_<num>` leva `figuras_img` (data URI WebP, `emed_banco.py:400`, `:463-469`). O 1º publish é `batch set`, e a solução entra depois por `batch update` com `if_version` (`.claude/commands/banco-emed.md:197-198`). Não existe caminho de update só de figura. Limite do doc: 256 KiB (maior medido: 100 KB).

**Fricção que esta spec remove, virtuosa ou viciosa?** Viciosa: o operador resolve uma questão cuja tabela não está na tela, e a análise do erro sai genérica (t832 Q30/Q35, `session_220.md:33`). Nenhuma fricção de estudo é tocada.

## Definition of Done

1. [ ] **A captura declara.** `extrair` (`tools/emed_api.py`) marca `sem_figura: True` quando o ENUNCIADO cita um objeto visual e a questão não tem `figuras`.
   - O padrão é uma constante nomeada (`CITA_FIGURA`, regex por termo: figura, imagem, tabela, quadro, gráfico, radiografia/tomografia/ECG "a seguir|abaixo|apresentad[ao]", "a seguir:" no fim do enunciado).
   - O resumo da captura lista `sem_figura: [nums]`, e `montar_docs` leva a chave ao doc só quando verdadeira.
   - Testes em `tools/test_emed_api.py`, vistos VERMELHOS antes, com os textos reais da t40 Q6 ("está demonstrada na tabela a seguir:") e de 1 caso com `<img>` (sem `sem_figura`).
   - Um negativo explícito: "tabela periódica" ou um termo do padrão citado sem objeto visual. Declare no relatório qual dos dois virou teste.
   - **Recall no conjunto conhecido:** rodar o `CITA_FIGURA` sobre os enunciados da t40 Q5, Q6, Q18, Q21, Q22 (lidos do `ipub.db` em `mode=ro`) dá 5 de 5. Se der menos, o padrão está errado; a falha não pode ir para o anti-scope.
2. [ ] **A URL da alternativa-imagem viaja.** `extrair` passa a levar `figuras_alt: {letra: [urls]}` (só https, sem repetir, do `sanitized_body` ou do `body`) quando houver. A chave entra em `CHAVES_EXTRAIDAS`/`CHAVES_META` e no doc. Teste com o shape real da t833 Q34 (alternativa com `sanitized_body` vazio e `<img>` no `body`).
3. [ ] **Mescla estreita no banco.** Nova função em `app/utils/db.py`, `emed_mesclar_figuras(mapa, conn=None)`, com `mapa = {emed_id: {figura?, figuras?, figuras_alt?, sem_figura?}}`.
   - Atualiza SÓ as chaves de figura dentro de `extras` (e o `hash`, que depende de `extras`) das linhas cujo `emed_id` já existe.
   - Não cria linha. Não toca `enunciado`, `alternativas`, `gabarito`, `solucao`, `emed_solucoes` nem `emed_respostas`.
   - Retorna `{atualizadas, iguais, ausentes: [emed_id]}`.
   - Testes no banco sintético (sentinela do Lote 0): (a) linha do Chrome ganha `figuras` e o enunciado fica byte a byte igual; (b) `emed_id` desconhecido vai para `ausentes`, sem INSERT; (c) rodar 2 vezes dá `atualizadas` 0 na 2ª (idempotente); (d) `sem_figura` some quando a recaptura traz `figuras` (a figura chegou e a declaração cai).
4. [ ] **CLI com rito.** `emed_banco.py --figuras <pasta da recaptura>` lê os `questoes/*.json` do `emed_api --apply` e chama a mescla.
   - Sem `--apply`, é dry-run com a contagem. `--apply` exige `--expect N`, segue o `_upsert_com_rito` (COUNT-ASSERT + backup fixado quando `atualizadas` > 0) e imprime `ausentes`.
   - `emed_banco.py --exportar ... --so-figuras` escreve `OUT/upd/<lista>_<num>.json` só com `figura`, `figuras`, `figuras_alt`, `figuras_img`, `sem_figura` e `emed_id` (este para o join na 1.1b), e só dos docs com alguma dessas chaves.
   - Falha de download segue a regra de hoje (item listado, sem `figuras_img` parcial). O `figuras_img` das alternativas fica para a 1.1b só se o limite de 256 KiB couber (ver Riscos); aqui, só as URLs.
   - Testes em `tools/test_emed_banco.py`: dry-run não escreve; `--apply` sem `--expect` recusa; `--so-figuras` não leva `solucao_medhub`, `enunciado` nem `alternativas`.
5. [ ] **Norma lida no ato acompanha.** O parágrafo **Figura** da skill `banco-emed` (`.agents/skills/source-command-banco-emed/SKILL.md:154`, espelho `.claude/commands/banco-emed.md:162`) passa a dizer que a perda é declarada (`sem_figura`), que a alternativa leva URL (`figuras_alt`) e qual é o caminho de recaptura (`--figuras` + `--so-figuras` + `batch update`). O terminal `NAO-VERIFICAVEL` existente vira `CHECK:` apontando os testes novos, onde couber. `python tools/sync_skills.py --check` exit 0.
6. [ ] **Suíte e craftsmanship:** `python -m pytest tools/ -q` verde, sem violação dos Don'ts de `.vibeflow/conventions.md`. Nenhuma chamada à API do EMED nesta part (os testes usam fixtures). O orquestrador regenera a §7.4, se acusar, fora do budget.

## Scope

`tools/emed_api.py`, `tools/test_emed_api.py`, `app/utils/db.py` (só a função nova), `tools/emed_banco.py`, `tools/test_emed_banco.py`, `.agents/skills/source-command-banco-emed/SKILL.md` (o espelho em `.claude/commands/` vem pelo `sync_skills`, se for gerado; se for manual, conta como 7º arquivo e é declarado). **Budget: 6 arquivos (+1 espelho).**

## Anti-scope

- Nenhuma chamada real à API, nenhuma escrita no `ipub.db` real, nenhum `ArtifactData`: tudo isso é a 1.1b.
- Não mudar o `emed_upsert_questoes`, o hash das colunas de conteúdo, o `--ingerir` nem o `--exportar` sem a flag nova.
- Não tocar no `core/templates/hub.html` (o aviso no hub é a 1.1b).
- Não regenerar Soluções MedHub / cadeias das questões que ganham figura: a 1.1b só LISTA quais são.
- Não mexer no filtro de spoiler UERJ (`_algum_exame_spoiler`) nem no `--sem-figuras`.

## Technical Decisions

1. **Mescla por `emed_id`, não por `(lista, num)`.** A numeração do Chrome (t40, t1) não tem garantia de bater com a ordem da API. O `emed_id` é a chave estável dos dois lados.
2. **Regex declarando com falso positivo aceito, em vez de exigir precisão.** `sem_figura` é suspeita declarada (alça fechada): o custo de um falso positivo é um aviso a mais, e o de um falso negativo é a tabela sumir calada. O recall no conjunto conhecido é o DoD; a precisão vai ao relatório da 1.1b.
3. **Mescla nova, em vez de reingerir.** Reingerir a captura da API sobre uma linha do Chrome trocaria o texto de uma lista já resolvida e analisada. Custo: uma função a mais no `db.py`.

## Applicable Patterns

- `whitelist na fronteira` do `emed_api.py` (`CHAVES_EXTRAIDAS`/`CHAVES_META`): chave nova entra pela whitelist, nunca solta.
- `_upsert_com_rito` (`emed_banco.py:115-139`): COUNT-ASSERT + backup fixado.
- Banco sintético + sentinela do Lote 0 (parts 2a/2c).
- Lição F108: HTML por parser, nunca regex (vale para as URLs da alternativa; a regex do DoD 1 é sobre o TEXTO já extraído).

## Risks

- **"O padrão marca demais."** -> Decisão 2. A 1.1b mede a precisão sobre as listas reais e pode apertar o padrão.
- **"`figuras_alt` com `figuras_img` estoura 256 KiB."** -> Aqui só as URLs; quem embute a alternativa decide a 1.1b, medindo o tamanho.
- **"Mudar `extras` muda o hash e algum leitor compara hash."** -> O DoD 3 (c) prova a idempotência. O hash já mudava quando `figuras` entrou na s221 (precedente).

## References

- `tools/emed_api.py:105-145` (`_Texto`, `html_para_texto`, `figuras_do_html`), `:213-245` (`extrair`), `:381-389` (`montar_docs`).
- `tools/emed_banco.py:115-139`, `:217-227`, `:400`, `:441-485`.
- `app/utils/db.py:2283-2298`, `:2498-2568`.
- `history/session_220.md:33`, `history/session_222.md:40`, `tmp/brief_v3_lote_s222.md:8`.
