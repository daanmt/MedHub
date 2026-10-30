# Pendências do MedHub — inbox no formato comum

> Store do medhub (PD-20261030-03 do ai-eng), no mesmo formato do inbox do ai-eng (`C:/Users/daanm/ai-eng/brain/pendencias/README.md`, que veio do `daktus-hub:qa/pendencias/README.md`). Primeiro consumidor: a **folha de decisão** do banco de evidências (`evidence-bank`, contrato `core/contracts/evidence-governance.md` v1.5 §8). Nasceu vazio em 30/10/2026 (s236).

## Schema

Um arquivo `PD-AAAAMMDD-NN.md` por pendência. Cabeçalho entre `---`, um campo por linha, valor em JSON, nesta ordem: `id`, `estado`, `tipo`, `criado_em`, `sessao`, `frente`, `dono`, `gatilho`, `origem`, `ponteiros`, `triagem`, `card`, `resolvido_em`, `resolucao`, `resolucao_ponteiros`, `assinatura`. Depois do `---` de fechamento vem o texto.

- `id` = `PD-<dia UTC>-<NN>`; todo `em` é UTC do relógio, gerado por comando, nunca digitado.
- `estado`: `aberta` → `resolvida` | `descartada` | `promovida`; só `aberta` transiciona.
- `tipo`: `achado` (sai por triagem assinada) · `decisao` (sai só com a assinatura do operador) · `tarefa` (sai com prova em `resolucao_ponteiros`).
- Assinatura = `{nome, papel, fonte, em}`, uma por item, nada pré-assinado.
- Fora daqui, cite `medhub PD-…`: o ai-eng e o hub usam a mesma forma de id.

## Folha de decisão do banco de evidências

- Gerada pelo pacote, nunca à mão: `python -m evidence_bank folha --db C:/Users/daanm/medhub/evidencias.db --out C:/Users/daanm/medhub/pendencias/ --dono medhub` (na raiz de `C:/Users/daanm/evidence-bank`). Ela só existe com itens `pesquisada` triados na fila (`triar` antes).
- O corpo é a tabela `fila_id · afirmação · veredito · fontes · proposta · motivo`. O operador assina a folha inteira ou edita a coluna `proposta` (`incluir` | `rejeitar` | `adiar (data:AAAA-MM-DD|evento:<slug>)`).
- Aplicar: `python -m evidence_bank decidir --folha PD-… --assinada --por "Daniel Martins" [--arquivo <a folha editada>] --db C:/Users/daanm/medhub/evidencias.db --ipub C:/Users/daanm/medhub/ipub.db` — com o hub parado (sem tique): não há atomicidade entre o `evidencias.db` e o `ipub.db` em WAL (README do pacote).
- `incluir` liga a ponte `card_evidencia`/`questao_evidencia` da origem (`card:<id>` sai da quarentena e volta ao FSRS); `rejeitar` exige motivo; `adiar` exige gatilho.

## Regras da casa

- O repo é público (D-01 pendente): folha com texto de terceiros (enunciado do EMED, apostila) não entra no git sem decisão do operador.
- O `INDEX.md` deste store ainda não existe (o núcleo executável do inbox é o porte PD-20261029-28 do ai-eng).
