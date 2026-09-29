# Spec: rotação do ledger -- part 2 (leitores e o gate)

## Objetivo

Os sensores que leem o ledger enxergam os dois arquivos, e um gate impede que item resolvido fique na frente.

## Contexto

`tools/consistencia_check.py` (G14, G14b) lê só `AUDITORIA_MEDHUB.md`: item movido sumiria do dicionário em silêncio. `tools/auto_check.py` e `tools/habilidades.py` emitem avisos que citam `AUDITORIA_MEDHUB.md F38` e `F89`, ambos resolvidos.

## Que fricção esta spec remove -- e ela é virtuosa ou viciosa?

Remove a disciplina de lembrar de rotacionar: **viciosa**. O gate faz "resolvido sai da frente" ser mecanismo.

## Definition of Done

1. `tools/test_consistencia_registros.py::test_resolvido_na_frente_e_achado` e `test_aberto_no_historico_e_achado` escritos ANTES, em repo sintético.
2. `test_indice_velho_e_achado`: índice do topo diferente do derivado vira achado.
3. `test_status_le_os_dois_arquivos`: G14 e G14b acham o cabeçalho de item que mora no histórico.
4. `test_repo_real_consistente` segue verde no repo real depois da migração.
5. Os avisos de `auto_check.py` e `habilidades.py` apontam o arquivo onde o achado mora.
6. Suíte completa verde e `auto_check --changed` PASSED.

## Escopo

- `tools/consistencia_check.py`: leitura dos dois arquivos; check novo `frente`.
- `tools/test_consistencia_registros.py`.
- `tools/auto_check.py`, `tools/habilidades.py`: texto dos avisos; gatilho por caminho.
- ~~`tools/doc_drift.py`: o histórico entra na lista de alvos.~~ Retirado na implementação: `test_allowlist_e_exatamente_os_4_docs_de_estado` prende a lista do sensor de propósito.

## Anti-escopo

- Docstrings e comentários que citam F-id resolvido (`day_plan.py`, `db.py`, `state_utils.py`): a frente aponta o histórico, a citação segue resolvível.
- `tools/ledger_self.py`: o tamanho da frente em KB cai, que é o efeito desejado.

## Decisões técnicas

- **O check `frente` entra em `CHECKS`** e, por `test_repo_real_consistente`, bloqueia: a base nasce zerada.
- **Uma função de leitura**, `selo.achados_do_ledger`, consumida pelo `consistencia_check`: duas leituras do mesmo cabeçalho divergiriam.

## Riscos

- **Import circular** (`selo` importa `consistencia_check` dentro de função). Mitigação: import tardio nos dois sentidos.

## Dependencies

- `.vibeflow/specs/ledger-rotacao-part-1.md`
