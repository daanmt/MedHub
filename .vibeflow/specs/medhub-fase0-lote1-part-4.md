# Spec: medhub Fase 0 · Lote 1 — Part 1.4: cópia off-machine do `ipub.db` e dos 48 fixados

> Gerada: 2026-10-10 ~23:58 (medhub, s223, `/vibeflow:gen-spec`; commit `260cdfb`) | Origem: GO do Lote 1 do ai-eng (10/10 23:32), que pôs a 1.4 **primeiro** no lote por causa do M-129; os 5 pontos de conferência dele (10/10 23:55). Revisada em 11/10 00:01 com as adições (A) e (B) do ai-eng, no GO da spec. PRD: `.vibeflow/prds/medhub-fase0-preparar-ambiente.md` (linha 4 da tabela de lotes: "backup off-machine").
> Repo-alvo: medhub. HEAD de partida: `bdae7bc`. Ids: fecha a condição do **M-129** (o G-op da 0.4b só depois desta part, com md5 dos 48 conferido).

## Objective

O `ipub.db` atual e os 48 backups fixados que a 0.4b vai devolver à rotação ganham uma cópia carimbada, com md5 conferido de volta no destino, numa pasta fora do repo público. A partir dela, o operador sobe a cópia para um git privado e para o Drive.

## Context

- **Não existe cópia fora desta máquina** (decisão iii do operador: "drive e git"). O apply da 0.4b (G-op) faria a rotação keep-5 apagar 49 arquivos de uma vez, e no disco ficariam só pontos de 09/10 e 10/10 (M-129, medido no dry-run da 0.4b: 53 fixados ativos, K=48, 341,7 MB; os 5 de rotação são de 26/09 a 07/10).
- **O que existe e deve ser reusado, não reescrito:**
  - `tools/backup_db.py::plano_desfixar_lote(5)["sair"]` dá a lista exata dos 48, a mesma que o apply vai soltar;
  - `_fixar()` é o modelo do snapshot consistente (`shutil.copy2` + sha256 da cópia == sha256 do banco + `PRAGMA integrity_check`);
  - `_sha256()` e `_ler_manifesto()` fazem a conferência contra `FIXADOS.json` (campos `arquivo`, `sha256`, `motivo`, `criado_em`).
- **Não há pasta do Google Drive para desktop nesta máquina** (procurado em `G:/`, `~/Google Drive`, `~/My Drive`, `~/Meu Drive`, em 10/10). O Drive é passo manual do operador.
- **Repo público** = `https://github.com/daanmt/MedHub.git`, em `C:/Users/daanm/medhub`. Hoje nenhum `.db` está rastreado (`git ls-files` medido em 10/10). O `.gitignore` cobre `ipub.db`, `ipub_backup_*.db` e `artifacts/backups/`, mas **não** `*.db` genérico: um `ipub_fixado_*.db` copiado para fora de `artifacts/backups/` entraria. E nenhum gate do pre-commit barra binário de banco: `git add -f` passa pelo gitignore.
- O `ipub.db` contém conteúdo do EMED (IP de terceiro): só pode ir ao destino privado.

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: não haver ponto de retorno fora da máquina trava a poda local (0.4b) e deixa o banco inteiro dependente de um disco. A fricção virtuosa fica intacta: o fixado continua sem CLI que o apague (F137), e o upload segue ato humano.

## Definition of Done

1. [ ] **Dry-run por padrão, sem escrita.** `python tools/backup_offmachine.py --dest DIR` lista os N = 1 + 48 arquivos (o snapshot do banco + os de `plano_desfixar_lote(5)["sair"]`), com MB, e o carimbo da pasta que seria criada. Não cria `DIR`, não escreve nada e não toca `artifacts/backups/`. Teste em `tools/test_fixado_ato.py`, sobre diretório sintético (8 fixados + manifesto + banco sintético): a impressão digital da origem (sha256 de cada arquivo + do manifesto) fica igual e `DIR` não existe depois. Vermelho visto antes do código.
2. [ ] **Apply com COUNT-ASSERT e md5 de volta.** `--apply` exige `--expect N`; N diferente recusa e nada muda. **Precondição (A, ai-eng):** o banco está em `journal_mode=delete` (lido em `mode=ro` em 10/10). ANTES de copiar, o apply recusa se existir `ipub.db-journal` ao lado do banco (hot journal = transação em curso ou queda) ou `ipub.db-wal`/`-shm` com bytes, com a mensagem "banco em uso: pare o tique e feche conexões" e nada escrito. Teste: um `-journal` sintético ao lado do banco sintético -> recusa, `DIR` não existe. Com o N certo e o banco quieto, a cópia vai para `DIR/<carimbo>/`:
   - o snapshot `ipub_<carimbo>.db`, feito como no `_fixar` (sha256 da cópia == do banco, `integrity_check` ok; senão recusa e não deixa cópia meia-feita);
   - cada fixado com o sha256 conferido contra `FIXADOS.json` ANTES de copiar (um divergente ou sumido recusa o lote inteiro);
   - `MD5SUMS` (formato `md5sum`: `<md5>  <caminho relativo>`) e `manifest.json` (origem, bytes, sha256 do manifesto, motivo do fixado).
   Depois de copiar, o script RELÊ cada arquivo no destino e confere o md5 contra o da origem; se divergir, sai 1 e diz qual. `DIR/<carimbo>/` já existente = recusa (nunca sobrescreve). Testes no mesmo arquivo, inclusive um que prova que nada foi apagado na origem.
3. [ ] **O destino nunca é o repo público.** Recusa, sem escrever nada:
   - `--dest` dentro de `C:/Users/daanm/medhub` (subpasta e variação de caixa incluídas);
   - `--dest` dentro de uma árvore git que tenha QUALQUER remote igual ao público (normalizar `.git` final, barra final e caixa).
   O script só roda git de leitura (`rev-parse`, `remote -v`): nunca `init`, `add`, `commit` nem `push`. Teste: um `subprocess.run` gravador registra os subcomandos git chamados no apply sintético, e só os de leitura aparecem.
4. [ ] **Conferência de volta reutilizável.** `python tools/backup_offmachine.py --conferir DIR/<carimbo>` relê os arquivos contra o `MD5SUMS` da própria pasta: tudo bate = exit 0; arquivo adulterado ou ausente = exit 1 com o nome. É o comando que o orquestrador roda depois do clone fresco do repo privado (G-op). Teste com um byte alterado.
5. [ ] **Nada de banco no repo público (gitignore + gate).**
   - O `.gitignore` ganha `*.db`, `*.sqlite` e `*.sqlite3`, cada um também com `-wal`, `-shm` e `-journal`. Adição (B) do ai-eng: o Chroma usa `chroma.sqlite3`, o mesmo tipo de arquivo e o mesmo risco.
   - O `auto_check` ganha, no conjunto "sempre" da part-1 (sem early-return, sem gatilho por extensão), o check `[BLOCK] BANCO_NO_RECORTE`: todo arquivo staged (ACMR) cujo nome casa `\.(db|sqlite3?)(-wal|-shm|-journal)?$` bloqueia o commit, mesmo com `git add -f`. Nasce BLOCK porque a base é zero por construção: 0 arquivos `.db|.sqlite|.sqlite3` rastreados (`git ls-files`, medido em 11/10), a mesma razão do `gate_inexistente`.
   - A regra é uma função PURA em `backup_offmachine.py` (`bancos_no_recorte(caminhos)`), e o `auto_check` só orquestra. Regressão in-process em `tools/test_fixado_ato.py`.
   - Prova no fluxo real, feita pelo orquestrador: `git add -f` de um `.db` sintético -> commit BLOQUEADO, HEAD intacto, revertido.
6. [ ] **Dry-run real (orquestrador).** Sobre `artifacts/backups/` real, com `--dest` numa pasta do scratch fora do repo, o dry-run imprime N = 49 e o total em MB (esperado ~352 MB = 341,7 + o banco). A impressão digital da pasta de backups (sha256 do manifesto + nome/tamanho/mtime de cada entrada) fica idêntica antes e depois, e `--dest` não é criado. O md5 do `ipub.db` também fica igual.
7. [ ] **Assinatura e craftsmanship:** as flags novas (`--dest`, `--apply`, `--expect`, `--conferir`) estão em `.claude/commands/engenharia-cli.md` (seção nova do `backup_offmachine.py`), com o espelho regenerado (`python tools/sync_skills.py`; `--check` exit 0). `python tools/cli_signature_check.py` dá 0 flags órfãs, e `python -m pytest tools/ -q` fica verde. Nenhuma violação dos Don'ts de `.vibeflow/conventions.md`: `sqlite3` só no CLI standalone de `tools/`, nada em `app/`. A §7.4 do `AGENTE.md` é regenerada pelo orquestrador (CLI novo = linha nova), fora do budget.

## Scope

`tools/backup_offmachine.py` (novo), `tools/test_fixado_ato.py` (testes da família backup; arquivo existente, para não exigir o `pytest.ini`), `.gitignore`, `tools/auto_check.py` (só o check `BANCO_NO_RECORTE` no conjunto "sempre"), `.claude/commands/engenharia-cli.md` e `.agents/skills/source-command-engenharia-cli/SKILL.md` (gerado). **Budget: 6 arquivos.**

## Anti-scope

- **O script não cria repo, não autentica, não faz `git add`/`commit`/`push`, não fala com o Drive e não apaga nada**, nem na origem nem no destino. Upload e push são G-op do operador (ou ato do orquestrador com autorização dele, fora do script).
- **Não roda o apply da 0.4b** nem chama `desfixar`/`purge`/`backup()`. A F137 não muda.
- Nada de agendamento ou recorrência (cópia periódica = Lote 4 / Fase 1). Esta part é a cópia única que destrava o M-129. Limite conhecido **M-136**: cada cópia pesa ~352 MB no repo privado, e a política de retenção dele (ex.: 1 cópia por semana depois de 30 dias) vai para o Lote 4 / Fase 1.
- Nada de Git LFS, criptografia ou compressão (decisão do operador sobre o destino privado; fica para a Fase 1 se pesar).
- Nenhuma escrita no `ipub.db`, em `FIXADOS.json` ou em `artifacts/backups/`.
- Não mexer em `tmp/` (M-130/M-131) nem em `medhub_memory.db`.

## Technical Decisions

1. **Reusar `backup_db`** (`plano_desfixar_lote`, `_sha256`, `_ler_manifesto` e a receita do `_fixar`) em vez de recalcular a lista ou o snapshot: os 48 da cópia são, por construção, os 48 que o apply vai soltar.
2. **md5 no `MD5SUMS`, sha256 no `manifest.json`.** O md5 é o que o Drive expõe (`md5Checksum` na metadata) e o que o `md5sum -c` lê; o sha256 continua sendo a identidade do fixado (F137). Custo: dois hashes por arquivo (~352 MB lidos duas vezes); aceitável numa cópia única.
3. **Gate no pre-commit além do `.gitignore`.** O gitignore não segura `git add -f` nem cobre um nome novo; o BLOCK `BANCO_NO_RECORTE` no conjunto "sempre" segura os dois. A regra pura mora no módulo novo porque é a fronteira do que pode sair da máquina.
4. **Sem LFS.** Cada arquivo tem ~7-11 MB (abaixo do aviso de 50 MB do GitHub), ~352 MB no total. O repo privado cresce a cada cópia, mas recorrência está fora desta part.
5. **Pasta por carimbo, nunca sobrescrever.** `DIR/<carimbo>/` já existente = recusa: duas cópias nunca se misturam e o `MD5SUMS` de cada pasta é autossuficiente para o `--conferir`.

## Applicable Patterns

- `tools/backup_db.py` `purge`/`plano_desfixar_lote`/`desfixar_lote`: dry-run por padrão, `--apply --expect N` (COUNT-ASSERT), recusa = `Recusa` com "nada mexido".
- `.vibeflow/patterns/warn-first-check.md`: função pura no módulo, o `auto_check` só orquestra. A exceção "nasce BLOCK com base zero" é a do `gate_inexistente` (check 29).
- `tools/test_fixado_ato.py` (fixture `lote`, diretório sintético de fixados + manifesto): modelo dos testes.
- `AGENTE.md §10.7`: operação em lote com o número declarado antes, dry-run que confirma, só então o apply.
- Lote 0 part-1 / 0.3: checks "sempre" sem early-return; repo sintético com a fixture `git_isolado` (ambiente `GIT_*` limpo) para o teste do gate.

## Risks

- **"A cópia mora no mesmo disco."** -> Sim: até o push/upload ela é staging local. A condição do M-129 é o md5 conferido **depois** do clone fresco do repo privado (G-op), não o apply desta part.
- **"O banco muda durante a cópia."** -> Duas travas. Antes de copiar, a precondição (A) recusa com journal, WAL ou SHM presentes. Depois, o sha256 da cópia diverge do banco e o script recusa sem deixar cópia, como o `_fixar`. Nos dois casos, repetir com o tique parado.
- **"O push para o repo privado é negado pelo classificador."** -> O push é do operador (`! git -C <dir> push`); o script não depende dele.
- **"O gate novo bloqueia um `.db` legítimo de teste."** -> Nenhum `.db` é rastreado hoje. Fixture de banco sintético nasce em `tmp_path`, fora do índice.
- **"O destino herda credencial ou remote errado."** -> A recusa por remote igual ao público roda antes de qualquer escrita; criar o remote privado é ato do operador.

## G-op depois desta part (não é DoD; ordem para o operador e o orquestrador)

1. O operador cria o repo git PRIVADO (conta e credencial dele) e o clone local fora de `C:/Users/daanm/medhub`.
2. O orquestrador roda o apply real com `--dest <clone>`, e o operador faz commit + push no repo privado.
3. O orquestrador faz clone fresco do privado em scratch e roda `--conferir`: exit 0 = md5 dos 49 conferido. Se o classificador negar o clone na sessão do orquestrador, quem roda `! git clone` é o operador, nunca outro agente.
4. Drive: o operador sobe a pasta `<carimbo>/`. O orquestrador confere o `md5Checksum` de cada arquivo pela metadata do Drive (conector, só leitura) contra o `MD5SUMS`, ou o operador roda `md5sum -c` numa cópia baixada.
5. Com 3 e 4 conferidos, o apply da 0.4b (M-129) fica liberado para o operador.

## References

- `tools/backup_db.py` — `_fixar` (receita do snapshot), `plano_desfixar_lote` (a lista dos 48), `_sha256`/`_ler_manifesto`.
- `tools/test_fixado_ato.py` — fixture `lote` e testes do desfixar-lote: o modelo dos testes novos.
- `tmp/lote0/part-4b-implement.md` e o dry-run real da 0.4b (K=48, 341,7 MB): o número que o DoD 6 deve reproduzir.

## Dependencies

- `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-4b.md` (o `plano_desfixar_lote` vem de lá).
