## Audit Report: fila-de-reforja-como-estado (B2 / F40+F41+G7, item 0.3)

**Verdict: PASS**

Spec: `.vibeflow/specs/fila-de-reforja-como-estado.md` · Suite: **496 passed** (baseline 485; +11)
· `auto_check --changed`: PASSED · Data: 2026-09-10 (s176).

---

### DoD Checklist

- [x] **1. `reforja_marks` e APPEND-ONLY e o estado e DERIVADO.**
  - 3 marcacoes do mesmo par = **3 linhas**, e a fila reporta `n_marcacoes: 3`
    (`test_marcar_tres_vezes_produz_tres_linhas_e_a_fila_conta`). O #792 deixa de ser anedota de
    HANDOFF e vira COUNT.
  - **Nao existe coluna de status.** `test_nao_existe_coluna_booleana_de_status` varre o
    `PRAGMA table_info` e reprova `status`/`resolvido`/`fechado`/`done`/`ativo`. E a licao do F82
    aplicada ao schema: qualquer campo que alguem possa "virar" reproduziria o engano num lugar
    novo.
  - O `CHECK (evento IN ('marcada','fechada','descartada'))` fecha o enum no proprio schema.

- [x] **2. 🔴 Fechamento VERIFICADO, nao declarado** -- o coracao do item.
  `fechar_reforja` re-roda o predicado nomeado no motivo sobre o card **como esta no banco agora**
  e levanta `ReforjaAindaDefeituosa` se ele ainda acusar. Fixture obrigatoria cumprida:
  **#1568**, com `card_version = 2` no proprio fixture, tem o fechamento **RECUSADO**
  (`test_fechar_e_recusado_enquanto_o_predicado_ainda_dispara` e
  `test_card_version_2_nao_fecha_nada`). O caminho feliz tambem esta coberto: reescrever a
  pergunta com o condicional e depois fechar grava
  `evidencia = "predicado contrafactual_mal_formado re-rodou limpo"`.
  `--forcar` exige justificativa escrita, que fica **gravada na linha** (`forcado: ...`).

- [x] **3. `descartada` e estado de primeira classe.** Testado que produz `aberta: False` **sem**
  incrementar `fechada` (`test_descartar_e_diferente_de_fechar`), e que exige justificativa. Sem
  esse estado, marca falsa fecharia como conserto e a metrica de passivo mentiria **para cima**.

- [x] **4. A cifra sai de ferramenta.** `python tools/reforja.py --fila` e a unica fonte citavel;
  `--json` para consumo programatico. O cabecalho da saida diz literalmente "a UNICA cifra citavel
  do passivo (G7)" -- os quatro numeros historicos (12/13/15/38) eram leitura humana.

- [x] **5. Backfill = dry-run + COUNT-ASSERT, execucao do OPERADOR.**
  `python tools/reforja.py --backfill --dry-run` ->
  ```
  COUNT-ASSERT declarado ANTES de escrever: 9 linha(s) a criar (de 9 marcas com proveniencia).
  [DRY-RUN] nada foi escrito. Rodar com --apply e decisao do OPERADOR.
  ```
  Cada linha carrega a proveniencia (`HANDOFF s175: ...`), verificado por
  `test_backfill_so_migra_marcas_com_proveniencia`. O `--apply` compara o escrito com o declarado
  e falha se divergir. **Nao foi executado** -- e Tier 2.

- [x] **6. Craftsmanship gate.** `auto_check --changed` PASSED; suite 496; `sqlite3` so em
  `app/utils/db.py` (o CLI e camada fina); allowlist F49 ganhou `reforja_marks` **conscientemente**
  (o diff denuncia, como a docstring dela exige); `sync_skills --check` exit 0.

---

### Pattern Compliance

- [x] **Camada de acesso unica (`AGENTE.md §6`)** — `tools/reforja.py` nao abre `sqlite3`; os tres
      writers e o leitor vivem em `app/utils/db.py`.
- [x] **Assinatura canonica em UMA skill (§7.2)** — a tabela de comandos do CLI novo vive em
      `.claude/commands/estilo-flashcard.md §Fila de reforja`; a spec referencia, nao duplica.
- [x] **Schema idempotente** — `CREATE TABLE IF NOT EXISTS` + indice, padrao do `init_db.py`;
      rodado sobre o `ipub.db` real sem efeito colateral.
- [x] **Warning-first respeitado** — nenhum WARN dos predicados vira marca sozinho. O anti-escopo
      declara e a skill repete: *o CLI oferece candidatos, quem marca e gente* (licao do F87).

---

### Critical Gate

**Limpo.** O diff acrescenta uma tabela (`CREATE TABLE IF NOT EXISTS`), tres funcoes de INSERT,
um leitor e um CLI. Zero `DROP`/`TRUNCATE`/`DELETE`, zero UPDATE, zero operacao em massa, zero
segredo. A tabela nova e **append-only por construcao**: nao ha caminho de escrita que apague ou
altere linha existente.

---

### Achado colateral, corrigido e declarado

Ao regenerar a tabela `AGENTE.md §7.4` (obrigatorio: entrou um CLI novo), o `tools/reforja.py`
apareceu com **`—`** na coluna "O que faz" -- que a propria legenda da tabela define como
*"modulo sem docstring, lacuna a fechar"*. **Falso:** o modulo tem docstring completa.
`_resumo_docstring` ancorava a regex no inicio do ARQUIVO e nao tolerava o **shebang**, entao todo
CLI executavel perdia a descricao; e docstring que abre com quebra de linha devolvia string vazia.
Dois `re` ajustados -> os `—` da tabela caem de **14 para 6**, e os 6 restantes sao docstrings
genuinamente ausentes -- que e o sinal honesto que a tabela existe para dar.

Classe: **claim-aging em tabela gerada** (familia G5/D4). O gerador estava certo; o extrator
afirmava uma lacuna inexistente em 8 linhas. `tools/test_reachability.py` segue verde (8 passed).

---

### Ponto cego DECLARADO

O fechamento verificado so alcanca marcas cujo motivo nomeia um **predicado existente**
(`card_checks.PREDICADOS_VERIFICAVEIS`, 8 hoje). Motivo fora do registro -- *pacote de fatos*,
*pergunta circular*, o eixo C semantico -- fecha por palavra humana e a linha grava
`evidencia = 'humana'`, testado em
`test_motivo_sem_predicado_fecha_como_humana_e_a_linha_diz_isso`. A propria `--fila` imprime a
lista dos motivos sem predicado sob `[DECLARADO]`. Fronteira escrita, nunca maquiada.

Igualmente declarado: o **"passivo ~37"** do HANDOFF **nao foi migrado** -- existe o numero e nao
existe a lista. Fabricar 37 linhas a partir de um numero sem nomes seria inventar estado, a propria
doenca que esta fila cura. Entra por `--marcar` quando alguem produzir os nomes.

---

**Ready to ship.**

2 hotfix docs not yet consolidated (`.vibeflow/hotfixes/2026-09-10-*.md`) —
ver `audit --consolidate-hotfixes`.
