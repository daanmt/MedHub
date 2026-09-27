# Session 202 -- lista do EMED pela API (script sem LLM), F137 fechado, lote5/lote6 do /ai-eng lidos, CA de Mama corrigido

**Data:** 2026-09-26 (sábado, noite) -> 2026-09-27 (selo) - **Ferramenta:** Claude Code (Opus 5.5 1M) - **Continuidade:** `session_201.md` - **Observada pelo /ai-eng** (`ai-eng-59`; presença, checkpoints e ordens no `history/exchange-log.jsonl`)

---

## O que foi feito
1. **Item 0 (golden EMED) -- a fonte do gabarito virou a API.** O /ai-eng repassou a decisão do operador: *"extrair a questão, alternativas e gabarito, que é dado público"*, sem re-export com "Ver solução" (traria o comentário do professor para o disco). Como revertia a recusa registrada na s199, **confirmei com o operador no meu canal** (AskUserQuestion: "Sim, API por script") antes de escrever código. `tools/emed_api.py` (`c81156c`): whitelist na fronteira (`extrair()` é a única leitura do item; doc = `emed_id num banca ano enunciado alternativas gabarito tags` + metadados do pipeline), 2a trava antes do 1o byte, token só em `.emed_token` (gitignored) ou env, recusa se rastreado ou fora do `.gitignore`, discursiva declarada (achadas = gravadas + declaradas = `--expect`), tudo ou nada, dry-run default, `--esquema` só chaves. `tools/test_emed_api.py`: 24 + golden t3 (skip sem a saída real); mutação 2/2. Skill `/banco-emed` com a assinatura e a lápide da lista EMED em PDF; AGENTE 7.3/7.4; nota s202 no F135.
2. **F137 parte 2 -- RESOLVIDO** (`f43ad24`): `backup_db.fixar_antes_do_ato` (cópia + sha256 da cópia == do banco no mesmo instante + integrity + manifesto com o ato) no 1o write de `cards_prune`, `recurate_cards`, `dedup_taxonomia`, `normalize_taxonomia` e do `--apply` do `emed_banco` que SOBRESCREVE; sem fixado = recusa. `--desfixar ID --motivo` devolve à rotação; nenhuma flag apaga fixado; a rotação recusa o prefixo; fixar o `ipub.db` real dentro do pytest = recusa. `tools/test_fixado_ato.py`: 16, vermelhos antes; mutação 2/2.
3. **(ii) advisories do /ai-eng lidas contra o repo** (`fd24ce4`, `d987a9c`), 1 linha por ato no ROADMAP 9: lote5 (2 entraram, 1 só no cronograma, 2 não); lote6 = o D66 dele de 10/09 (5 entraram, 3 parciais, 1 não) -- declarados, sem spec.
4. **UX** (`fd24ce4`): a leitura com 3 letras vira "ficou entre A, C e D" no `--erros` e na página; teste + golden `provisoria` antes do fix. Vai ao ar no próximo publish do hub.
5. **CA de Mama** (`8fe6142`): supraclavicular ipsilateral = cN3c = estádio IIIC (AJCC 6a ed. em diante), não estádio IV -- 4 trechos do resumo + cards #1346/#1347 pelo `recurate_cards --apply` (dry-run antes). 1o uso real do F137-2: fixado `ipub_fixado_20260926_181614_antes-de-recurate-cards-apply-2-refeitos.db`, sha256 `468e0009c36dce84f89ee8df5adae20ede2a7d9054a1cd2f2370cdad721dd25b`. A resposta da banca da questão de origem (#860, quimioterapia primária) segue certa: sem conflito banca x evidência.

## Decisões
- Operador (26/09, no meu canal): lista do EMED pela API por script sem LLM; o risco da conta é dele; o agente nunca lê o token do navegador.
- Operador (27/09, via /ai-eng): "não tenho um token" -- o item 0 fica ABERTO até ele escolher entre copiar o `authorization` pelo DevTools, liberar a ferramenta ao /ai-eng ou testar o PDF exportado depois de responder. Nada de engenharia nova no item 0 até lá.
- Decisão repassada por par que reverte decisão registrada do operador = confirmar com ele no próprio canal (virou linha do HANDOFF e da memória).

## Achados de engenharia (ledger)
- F137 PARCIAL -> **RESOLVIDO** (limites declarados: lista explícita de 5 writers; `fsrs_load --blackout` fora; `normalize_taxonomia` por lente estática; fixados acumulam ~6,7 MB cada; path + sha256 no ledger segue conduta).
- Nenhum F novo. Golden t3 = item aberto por falta de token, não defeito.

## Erros meus
- Um heredoc longo com Python partiu no shell (`unexpected EOF`); refeito por script no scratchpad, o padrão da s201.
- A tabela 7.4 do AGENTE.md teve de ser re-gerada 3 vezes: arquivo novo em `pytest.ini`/`tools/` muda o "Alcançado por" de outros CLIs; o gate de consistência pegou as três.
- No texto ao operador contei o lote6 como "2 parciais"; eram 3 -- corrigido na mensagem seguinte.

## Custo dos subagentes
Nenhum subagente nesta sessão (0 filhos; tudo no principal).

## Pendências
- **Item 0:** golden t3 aguardando `.emed_token` (decisão do operador); com ele: `--esquema` -> dry-run `--expect 31 --conferir` -> `--apply`.
- **Estudo:** UERJ 2021 no hub (0 respostas em 27/09) = `--registrar` idempotente na abertura; semana 2 fechou com #49, #40, #100 em aberto.
- `questoes_erros` #860 guarda o racional antigo (supraclavicular = IV); sem writer.
- Hub não republicado nesta sessão (Version 33); o fix de UX sai no próximo tique.

banco-emed: nenhuma lista ingerida · respostas do hub 37 = 37 iguais (t26 19 + t96 18), t1793 sem respostas
