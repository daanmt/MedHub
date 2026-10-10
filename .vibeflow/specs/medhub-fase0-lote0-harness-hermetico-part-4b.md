# Spec: medhub Fase 0 · Lote 0 — Part 4b: peso local (gc agora; fixados e `tmp/` com dry-run e apply só com GO)

> Gerada: 2026-10-10 | PRD: `.vibeflow/prds/medhub-fase0-preparar-ambiente.md` (ai-eng) | Evidência: `brain/observed-systems/medhub-reforma-2026-10-10/D1-git-housekeeping.md` §Objetos e peso, §Raiz e segredos
> Parte 4b (de 7) — a última. Depois da part-4a (o `gc` empacota já sem o código removido).
> Repo-alvo: medhub (implement + audit no loop vibeflow dele). Código conferido em leitura @ `6d0239a`. `git count-objects -v` lido em 2026-10-10: `count: 6737` soltos, `size: 59997` KiB.

## Objective

O `.git` é empacotado agora, e a poda dos backups fixados e a limpeza de `tmp/` ficam prontas como dry-run com contagem — o apply só roda depois do GO do operador.

## Context

- **`.git`:** 6.737 objetos soltos (~58,6 MiB) contra 3.185 empacotados (2,5 MiB); nunca houve `gc`. Os `.jsonl` de `history/` reescritos a cada commit são o maior custo do histórico (D1).
- **Backups:** `artifacts/backups/` com 436 MB / 62 arquivos, sendo 53 `ipub_fixado_*` (D1). Por desenho (F137), **nenhuma CLI apaga fixado**: `tools/backup_db.py:227-257` (`desfixar`) exige `--motivo`, confere o sha256 do manifesto `FIXADOS.json` e devolve o arquivo à rotação (`ipub_backup_<carimbo>_desfixado.db`); quem apaga é a rotação keep-5 (`purge`, `:60-97`, com COUNT-ASSERT antes e depois) no próximo backup. Travado por `tools/test_fixado_ato.py` (`test_rotacao_com_20_falsos_nunca_remove_fixado_e_recusa_o_prefixo`, `test_cli_desfixar_exige_motivo_e_nao_existe_flag_de_apagar`). Hoje desfixar 48 exigiria 48 chamadas.
- **`tmp/`:** 382 MB / 32.959 arquivos (D1), mas **não é lixo homogêneo**: o código usa `tmp/` como estado de trabalho — `tools/emed_banco.py:48,364` (`tmp/emed_export`, `tmp/emed_figuras`, cache de figuras), `tools/emed_api.py:67` (`tmp/emed_api`), `tools/hub.py:1973,2084` (`tmp/hub`), lotes `tmp/player_<sessao>.json`; e `tools/test_emed_api.py:446` usa `tmp/emed_api/t3` como golden. 87 arquivos rastreados citam caminhos de `tmp/`. Tirar as figuras de `tmp/` é o Lote 4.
- Não existe backup fora desta máquina (Lote 4). Desfixar antes disso reduz os pontos de retorno locais.

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: 48 chamadas manuais para devolver fixados à rotação, e peso local sem inventário. A proteção do fixado (motivo + sha256 + nenhuma CLI apaga) é fricção **virtuosa** e fica intacta.

## Definition of Done

1. [ ] **`gc` executado** (não depende de GO): `git count-objects -v` antes e depois de `git gc` (sem `--prune=now`, sem `--aggressive`) colados no audit; `count` depois < antes; `git fsck --connectivity-only` sai 0.
2. [ ] **Desfixar em lote, dry-run por padrão.** `python tools/backup_db.py --desfixar-lote --manter 5 --motivo "<texto>"` lista os fixados ativos que sairiam (todos menos os 5 mais recentes pelo carimbo), com quantidade K e MB, e **não altera nada**. Teste em `tools/test_fixado_ato.py` (diretório sintético com 8 fixados + manifesto): depois do dry-run, arquivos e `FIXADOS.json` têm o mesmo sha256.
3. [ ] **Apply com COUNT-ASSERT.** `--apply` sem `--expect K` → recusa; `--expect` diferente de K → recusa e nada muda; com o K certo, cada um dos K passa pelo `desfixar()` existente (sha256 conferido, `desfixado_em` + motivo no manifesto) e os 5 mais recentes continuam fixados. Testes no mesmo arquivo; `test_cli_desfixar_exige_motivo_e_nao_existe_flag_de_apagar` continua verde (a flag nova não apaga, devolve à rotação).
4. [ ] **Dry-run real registrado, apply gated.** O audit cola a saída do dry-run sobre o `artifacts/backups/` real (K, MB). O apply real **não** faz parte deste DoD: roda só depois do GO do operador. <!-- TODO(operador, Q2 do PRD): desfixar os fixados antigos (manter 5) antes do backup off-machine do Lote 4? default = nao, esperar o Lote 4 -->
5. [ ] **Inventário de `tmp/` (read-only).** O audit traz, por subpasta de 1º nível de `tmp/` (e pelos arquivos soltos na raiz de `tmp/`): nº de arquivos, MB e classe — **VIVO** (caminho é default em código: `git grep -n "tmp" -- tools app`), **CITADO** (nome aparece em arquivo rastreado: `git grep -l -F <nome>`), **SOLTO** (nenhum dos dois). A remoção da classe SOLTO acontece só depois do GO, com a contagem declarada antes e recontada depois. <!-- TODO(operador, Q3 do PRD): apagar de tmp/ so a classe SOLTO? default = sim, apos o GO -->
6. [ ] **Assinatura e craftsmanship:** a flag nova está em `.claude/commands/engenharia-cli.md` (seção do `backup_db.py`) e o espelho foi regenerado (`python tools/sync_skills.py`; `--check` exit 0); `python tools/cli_signature_check.py` → 0 flags órfãs; `python -m pytest tools/ -q` verde; nenhuma violação dos Don'ts de `.vibeflow/conventions.md`.

## Scope

`tools/backup_db.py` (flag `--desfixar-lote` + `--manter` + `--apply`/`--expect`, reusando `desfixar()`), `tools/test_fixado_ato.py`, `.claude/commands/engenharia-cli.md`, `.agents/skills/source-command-engenharia-cli/SKILL.md` (gerado). `git gc` e o inventário de `tmp/` não editam arquivo. **Budget: 4 arquivos.**

## Anti-scope

- **Fronteiras:** design no ai-eng, implementação no medhub.
- **Nada que mude conteúdo clínico, FSRS ou o hub publicado.** Nenhuma escrita no `ipub.db`.
- Nenhuma flag nem caminho que apague fixado diretamente; a regra F137 ("nenhuma CLI apaga fixado") não muda.
- Não rodar o apply real do desfixar-lote nem apagar nada de `tmp/` sem GO.
- Nunca tocar as subpastas VIVO de `tmp/` (`emed_figuras`, `hub`, `emed_api`, `emed_export`, `bancada`, `player_*.json` do lote corrente) — elas saem de `tmp/` no Lote 4.
- Não mexer em `Medcards 2022/`, `data/chroma/`, PDFs da raiz (`AGENTE.md §6`: PDFs-fonte retidos), `.venv/`, `graphify-out/`.
- Não usar `git gc --prune=now`, `--aggressive`, `git reflog expire` nem reescrever histórico.
- Backup off-machine → Lote 4.

## Technical Decisions

1. **Desfixar em lote reusa `desfixar()`** em vez de apagar: mantém o contrato F137 (motivo + sha256 + quem apaga é a rotação). Custo: os arquivos só somem no próximo `backup()`; ganho: um rastro por item no manifesto.
2. **`--manter 5` pelo carimbo do nome**, mesma ordem que a rotação usa (`purge` ordena pelo carimbo do nome).
3. **`tmp/` sem CLI nova:** limpeza é ato único e humano; um script novo seria peso para manter. O inventário com classes e a contagem declarada antes do `rm` cumprem o "COUNT-ASSERT + dry-run" do `AGENTE.md §10.7`.
4. **`git gc` padrão:** respeita reflog e o prazo de 2 semanas para objetos inalcançáveis — empacota sem perder nada recuperável.

## Applicable Patterns

- `tools/backup_db.py:60-97` (`purge`): COUNT-ASSERT antes e depois, `dry_run=True` sem escrita.
- `tools/backup_db.py:227-257` (`desfixar`) e o teste `test_desfixar_exige_motivo_e_devolve_o_arquivo_a_rotacao` (`tools/test_fixado_ato.py:91`): modelo de teste em diretório sintético.
- `AGENTE.md §10.7`: operação em lote com número esperado declarado, dry-run que confirma, só então o apply.
- `AGENTE.md §3.4`: scratch de `tmp/` e backups fora da rotação "SAEM" — com veredito binário, mas aqui sob GO.

## Risks

- **"O `gc` rodou com o tique commitando."** → O `git gc` toma lock; se falhar por lock, repetir depois do tique (o audit registra).
- **"Desfixar apagou o ponto de retorno de um ato recente."** → `--manter 5` guarda os mais recentes; o apply só roda com GO, e o default do PRD é esperar o backup off-machine.
- **"A classe SOLTO tinha algo vivo."** → VIVO é derivado do código, CITADO dos rastreados; o que sobra não tem leitor. Mesmo assim, só com GO e contagem declarada.

## Dependencies

- `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-4a.md` (o `gc` empacota depois das remoções).
