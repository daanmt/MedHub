## Audit Report: feedback-cadeia-declarada part-1 (contrato da cadeia v3)

> Auditado em 2026-10-02 (s211), subagente de implementação. Spec: `.vibeflow/specs/feedback-cadeia-declarada-part-1.md`,
> **versão emendada no commit `cb31dae`**.

**Verdict: PASS** (contra a spec emendada).

### Histórico: 1ª auditoria PARTIAL -> emenda -> re-auditoria

A 1ª auditoria deu **PARTIAL**: o DoD 3 original (`emed_api.py --comentario NUM`) foi BARRADO pelo classificador de
permissões do harness, e com ele a revogação de "sem ler o comentário do professor". Nenhum contorno foi tentado. O autor das
specs (agente principal) emendou a part-1 em `cb31dae`: a conferência pela API e aquela revogação foram para a spec nova
`feedback-cadeia-declarada-part-1b.md`, BLOQUEADA à espera do operador; `docs/MEMORIA-AUDITORIA.md` entrou na lista de arquivos.
Esta re-auditoria mede o que já estava feito contra a spec emendada.

**Registro das negações (mantido):** duas edições em `tools/emed_api.py` foram negadas pelo classificador do auto mode --
(1) o bloco do `main()` que acrescentava `--comentario NUM` (argparse, erro de uso, chamada e `print`), motivo `[PII Data Handling]`;
(2) a troca da `description` do argparse citando o flag, motivo `[Instruction Poisoning]`. Duas edições anteriores no mesmo
arquivo tinham passado (lápide na docstring, `comentario_do_item()`, `buscar_comentario()`) e foram **revertidas**
(`git checkout -- tools/emed_api.py`, só mudanças minhas) para não deixar mecanismo pela metade nem docstring descrevendo
flag inexistente. A REGRA DURA "sem ler o comentário do professor" segue em vigor no brief.

### DoD Checklist

- [x] **1. Validador v3.** `db.solucao_v3_problemas(doc, catalogo=None)` em `app/utils/db.py:2982` (vocabulário `TIPOS_ELO_V3`, `:2522`).
  Um teste por defeito em `tools/test_emed_banco.py:698-791`: `test_solucao_v3_valida_nao_tem_problema`,
  `..._cadeia_com_menos_de_2_ou_mais_de_4_elos`, `..._elo_sem_campo_obrigatorio[elo|chave|habilidade|tipo]`, `..._tipo_fora_do_vocabulario`,
  `..._primeiro_elo_nao_e_identificar`, `..._sem_nenhum_recordar`, `..._ordem_violada`, `..._descartar_sem_letra`,
  `..._descartar_letra_inexistente`, `..._descartar_a_letra_certa`, `..._alternativa_sem_porque`,
  `..._numero_de_certas_diferente_de_1`, `..._pede_vazio`, `..._objetivo_fora_da_lista_fechada`. O exemplo do brief devolve `[]`
  (`test_exemplo_do_brief_passa_no_validador`, `:825`).
- [x] **2. Convivência v2/v3.** `db.solucao_problemas` despacha pela `versao` (`:3045`); `solucao_estruturada` aceita 2 e 3 (`:3063`);
  `emed_upsert_solucoes` chama o despachante (`:3084`) e grava v3 sem o `elo` herdado nas alternativas. Testes:
  `test_solucao_problemas_despacha_pela_versao`, `test_solucao_v3_grava_e_v2_continua_gravando`. Testes v2 existentes sem alteração, verdes.
- [x] **3. (emendado) `tools/emed_api.py` e `tools/test_emed_api.py` INTOCADOS.** `git diff HEAD --stat -- tools/emed_api.py tools/test_emed_api.py`
  -> vazio. `test_propriedade_nada_alem_da_whitelist_chega_a_disco_ou_saida` verde na suíte.
- [x] **4. Brief v3 + rito de revogação de "cuja falha leva a ela".** `docs/SOLUCAO-MEDHUB-BRIEF.md` reescrito (exemplo v3 validado por
  teste; fonte da dúvida não fechada = `divergente` + `conferir`, como pede a spec emendada). Rito de 3 passos no mesmo commit:
  (1) declarado no brief (lápide `⚰️ 02/10/2026` em §Regras do conteúdo), (2) lapidado em `.claude/commands/banco-emed.md` §Solução MedHub
  (lápide de 1 linha com o termo), (3) cadastrado em `docs/MEMORIA-AUDITORIA.md:304` (`<!-- TERMO-REVOGADO: cuja falha leva a ela | ... -->`).
  `auto_check --changed`: `✅ PASSED - Clausula revogada em vigor (CONTRATO_REVOGADO)`.
- [x] **5. Harness.** `python -X utf8 tools/sync_skills.py --check` -> exit 0; `python -X utf8 tools/auto_check.py --changed` -> exit 0,
  "Todos os checks passaram"; `python -X utf8 -m pytest tools/ -q -p no:cacheprovider` -> `1311 passed` (linha de base 1291 + 20).
- [x] **6. Craftsmanship.** Nenhum `import sqlite3` novo (grep no diff: 0); nenhum valor de comentário em código, recusa ou arquivo;
  português com acentos e pontuação ASCII no brief, na skill e nas docstrings novas.

### Pattern Compliance

- [x] `patterns/db-access-layer.md` -- validador e despachante PUROS em `db.py`; writer único segue `emed_upsert_solucoes`; sem SQL nova.
- [x] `patterns/warn-first-check.md` -- nenhum check novo; o termo entrou pelo registro derivado (§12), não por enumeração.
- [x] Skill canônica + `sync_skills` -- espelho regenerado, `--check` 0.

### Convention Violations

Nenhuma. Arquivos: os 5 da spec emendada + espelho gerado + este relatório.

### Decisões onde a spec deixava aberto

- `objetivo` vazio na v3 = ok (mesma régua da v2); só o objetivo FORA da lista fechada é defeito.
- Limite de 0 a 2 `descartar` sem check próprio: com 2-4 elos, 1º `identificar` e ao menos um `recordar`, sobram no máximo 2.
- Mais de um `identificar` ou `recordar` é aceito; só a ordem não pode voltar.
- A v3 grava as alternativas SEM o `elo` herdado ("presente = ignorado" -> não gravado, nenhum leitor futuro o usa).
- `<BASE>` do brief e da skill passou a `tmp/solucoes_v3_<lista>`.

### Critical Gate

Clean -- sem DDL de remoção, `DELETE`, segredo ou `eval/exec` no diff. O `git checkout -- tools/emed_api.py` reverteu só mudanças
minhas não commitadas.

### Não verificado

- `emed_banco.py --erros` com solução v3 gravada imprimiria "cai no elo None" (leitura nova = part-5, DoD 2 dela).

### Prompt pack -- agora da part-1b (BLOQUEADA; não executar sem o operador configurar o classificador)

1. `tools/emed_api.py`: `comentario_do_item(item)` (lê `solution.sanitized_complete` por `html_para_texto`; ausente = `Recusa` com o
   NOME da chave e `--esquema`), `buscar_comentario(caderno, headers, num, per_page, pausa)` (páginas em ordem até a posição NUM, checa
   `emed_id` repetido, para ali), `--comentario NUM` (`--apply`/`--out`/NUM < 1 = erro de uso, exit 1, antes da rede; imprime só o texto).
   Lápide `⚰️` na docstring.
2. `tools/test_emed_api.py`: `test_comentario_sai_so_em_stdout_e_nada_em_disco`, `test_comentario_recusa_com_apply_ou_out`,
   `test_comentario_sem_o_campo_e_recusa_nomeada` (fixture `_item`, `_fake_get`, sentinela `PROF`).
3. Brief (REGRA DURA) e `banco-emed.md` §Solução MedHub e §`emed_api.py`: lápide + o flag na tabela; marcador
   `<!-- TERMO-REVOGADO: sem ler o comentário do professor | ... -->` em `docs/MEMORIA-AUDITORIA.md` §12 -- no mesmo commit.

14 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
