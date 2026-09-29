# Spec: rotação do ledger -- part 1 (mover e enxergar)

> Decisão do operador (28/09/2026): *"ainda fico na dúvida: o que já foi resolvido e o que está em aberto? [...] não devemos acumular um backlog infinito; o que resolvermos, sai da frente."*
> É a decisão que o anti-escopo "rotação do ledger = política do dono" (F62) esperava.

## Objetivo

Abrir `AUDITORIA_MEDHUB.md` e ver só o que está em aberto, com um índice no topo; o que foi resolvido mora em `history/auditoria/resolvidos.md`.

## Contexto

O ledger tem 124 achados, 2.400 linhas e 395 KB; 105 estão resolvidos e ficam misturados aos 19 abertos. `tools/selo.py` deriva o status do cabeçalho, mas a saída padrão não imprime as classes GATE e DECLARADO: 12 achados ficavam invisíveis. Na s204 o F140 foi escrito sem que o F32, já no ledger, fosse achado.

## Que fricção esta spec remove -- e ela é virtuosa ou viciosa?

Remove a procura do item aberto no meio de 105 resolvidos: **viciosa**. Nenhuma fricção de estudo é tocada.

## Definition of Done

1. `tools/test_selo_rotacao.py::test_rotacao_move_so_os_resolvidos_e_conserva_cada_bloco` escrito ANTES: em ledger sintético, só os blocos com terminal FEITO, SUPERADO ou RETRATADO saem da frente, e o sha256 de cada bloco é o mesmo antes e depois.
2. `test_rotacao_e_idempotente`, `test_dry_run_nao_escreve` e `test_expect_errado_recusa_sem_escrever` passam.
3. `test_continuacao_viaja_com_o_pai` e `test_mitigado_e_parcial_ficam_na_frente` passam.
4. `test_selo_lista_todo_item_em_aberto`: a saída padrão do selo imprime todo achado não resolvido, com severidade e status literal, incluindo GATE e DECLARADO.
5. Migração do ledger real com prova de conservação: a união dos blocos F (frente + histórico) é idêntica, por sha256, à do arquivo de partida; nenhum texto fora de bloco F se perde.
6. Suíte completa verde e `auto_check --changed` PASSED; nenhuma violação dos Don'ts.

## Escopo

- `tools/selo.py`: leitura dos dois arquivos; `--rotacionar` (dry-run por padrão), `--apply`, `--expect N`, `--onde FID`; índice gerado entre marcadores no topo da frente; lista completa dos abertos.
- `tools/test_selo_rotacao.py` (novo) e o registro em `pytest.ini`.
- `AUDITORIA_MEDHUB.md` (frente) e `history/auditoria/resolvidos.md` (novo).
- `tools/_archive/migrations/rotacao_ledger_s204.py`: a migração de partida, one-shot.

## Anti-escopo

- Reescrever, resumir ou apagar o texto de qualquer achado.
- Decidir o destino dos itens abertos: isso é do operador e do /ai-eng.
- Leitores (`consistencia_check`, `auto_check`): part 2. Portadores: part 3.
- Índice manual `docs/MEMORIA-AUDITORIA.md` §3 e §3b: fica como retrato datado.

## Decisões técnicas

- **Histórico em `history/`, não em `archive/`.** `history/` é o SSOT do que aconteceu; a regra "sem archive" vale para cópia órfã, e aqui o texto é movido, não copiado.
- **Resolvido = FEITO, SUPERADO, RETRATADO.** MITIGADO e PARCIAL ficam na frente: têm resíduo declarado.
- **Bloco = do `### F<n>` até o próximo cabeçalho de nível 1 a 3.** Cabeçalho de continuação (`### F63 -- atualizacao`) segue o status do pai.
- **Migração de partida separada do rotacionador.** O arquivo antigo tem 38 seções narrativas; elas vão inteiras para o histórico, na ordem original. Depois dela, o rotacionador só move blocos F para o fim do histórico.
- **Índice gerado, com marcadores.** Tabela digitada envelhece (G5); a part 2 acusa índice velho.
- **COUNT-ASSERT.** `--apply` exige `--expect N` igual ao número medido no dry-run.

## Padrões aplicáveis

- `patterns/warn-first-check.md`: o selo deriva, nunca digita.

## Riscos

- **Perder texto na migração.** Mitigação: prova por sha256 de bloco e contagem de bytes fora de bloco; o arquivo de partida fica no git.
- **Citação por número de linha** (`AUDITORIA_MEDHUB.md:68`) quebra. Já estava defasada antes; tratada na part 3.

## References

- `tmp/f140_auditoria/S3-relatorio.md` -- varredura dos consumidores do ledger.
