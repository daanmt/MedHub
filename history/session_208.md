# Session 208 -- Engenharia quitada: frente do ledger 10 -> 3 (so as do operador)

**Data:** 2026-09-30 (quarta, 00h-02h) - **Ferramenta:** Claude Code (Opus 5.5) - **Continuidade:** `session_207.md`

---

## Pedido

O operador deu /clear e pediu ao /ai-eng (ai-eng-40) que ajudasse a quitar TUDO de engenharia. O /ai-eng mandou a ordem com DoD por item: F39 medir; F129+F113; F114; F63; F16+F78; F2; 17 cards do overflow. O canal ficou com 1 mensagem por fecho. Não houve pedido direto do operador nesta sessão.

## O que foi feito

1. **F39 MEDIDO, sem reescrita (a decisão é dele).** Sensor `audit_card_atomicity.run_checks`, rodado no backup de antes da s206 (`ipub_fixado_20260929_175639`) e no banco atual:
   - Violadores caíram de **277/1594 (17,4%)** para **74/1692 (4,4%)**.
   - Duplo-ask: 121 -> 38.
   - 0 violadores novos.
   - Os 24 marcados são exatamente as 24 marcas do lote vivo 30a. Dos 50 sem marca, a maioria é da safra 1677-1728.
   - Das 25 frentes duplo-ask sem marca, lidas: ~23 são defeito real.
   - Pergunta fechada para ele no chat.
2. **F129 + F113 RESOLVIDOS (`2c126ee`).**
   - Lente léxica independente (`tmp/varredura_s206/pt_sensor.py`): 32 -> 14 cards, e os 14 são falso-positivo triado ou lote vivo.
   - `recurate_cards --apply` de **18 cards só-acento**: COUNT-ASSERT 18, FSRS idêntico, FIXADO `ipub_fixado_20260930_002427`. O diff achou 1 cópula (#838).
   - Lente contextual de e/é: 0.
   - Canário: 20 aleatórios, 0 erros.
3. **F114 RESOLVIDO (`2c126ee` + `42cd187`).**
   - `regua.proveniencia` mede ajustado/default pelo valor, o otimizador grava o campo e o carregador recusa default declarado ou medido.
   - 5 testes escritos antes do fix.
   - Prova no arquivo real: remap -> w3, w16.
   - Nota de borda do /ai-eng aplicada: a recusa nomeia o remédio.
4. **F63 RESOLVIDO (`42cd187`).**
   - `plano.faixa_uerj` + `panorama(prevalencia=)`: o boot mostra `UERJ alta|media` por tarefa, e a autoridade é o arquivo.
   - Eixo 4 do `infer_nota` ligado (estava 'media' cravado desde a s096); Cláusula 8 do contrato lapidada.
   - 4 testes.
   - Prova: o hook roda o CLI em subprocesso.
5. **F16 RESOLVIDO / F78 LIMITE / F2 RESOLVIDO (`45d9611`).**
   - Novo resumo `resumos/Cirurgia/Abdome Agudo Inflamatório - Apendicite Aguda.md`: 31 páginas renderizadas e lidas; a seção de lacunas tem 15 entradas de figura.
   - A tabela laparoscopia x laparotomia (p. 22) foi recuperada da página.
   - Cobertura 68 -> 69.
   - F78 fica como limite (revisar 02/11).
   - F2: bateria de 8 comandos x 3 execuções, git/ls ~0,04 s, boot 2,3 s. Não reproduz.
6. **17 cards do overflow (F71): conferidos.**
   - A lista nunca foi persistida. Reconstruí pelo revlog 32 cards com due 14/09 (superconjunto dos 17).
   - Os 32 foram revistos em 16-17/09 e hoje estão em state 2 com due futuro.
   - `fsrs_load --blackout`: 0 overflow para 01-02/11.

**Selo:** frente **10 -> 3** (F39, F69, F111, todos do operador); 5 limites conhecidos; 118 resolvidos. Suíte 1286.

## Tropeços

- 🔴 **Afirmei que `index_resumos.py` saía com exit 0 quando o Ollama estava fora.** O 0 era do `| tail -5` do meu comando em background. Sem pipe, exit=1. O /ai-eng chegou a dar GO num hotfix que não era necessário. Retratado no ledger (lápide no fecho do F16) e no canal. **Lição:** código de saída se mede sem pipe.
- Fixture de teste com "Tema 2"/"Tema 9": `trilha.casa` ignora dígitos, então tudo casava. Troquei por nomes reais.
- A lente contextual inicial contava `glicemia`, `agudo` e `rim` como palavras que precisam de acento. Erro meu na lista; descartado antes de qualquer escrita.

## Próximo

- **F39:** resposta dele à pergunta fechada (fecha · reescreve os 50 sem marca por lote · limite conhecido).
- RAG sem reindexar desde 09/09 (25 resumos mais novos; `RAG_STALE`). Reindexar pede o Ollama no ar.
- Resto: o "ABRIR A s209" do `HANDOFF.md`.
