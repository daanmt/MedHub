# Audit Report: espelho-gerado (F42, item 1.4)

**Verdict: PASS**

> Spec: **o proprio ledger** (`AUDITORIA_MEDHUB.md` F42, direcoes a/b/c) -- classe *quick*.
> Sessao **s176 janela 2** (2026-09-10). Suite **578 passed** (baseline 572; +6).
> `auto_check --changed` -> **PASSED**, 0 BLOCK; `sync_skills --check` exit 0.

## DoD (as tres direcoes do achado)

- [x] **(a) Banner de artefato gerado.** Todo espelho nasce com
  `<!-- 🔴 ARQUIVO GERADO por tools/sync_skills.py -- NAO EDITE AQUI ... -->`, **nomeando o
  canonico daquele slug** (`.claude/commands/<slug>.md`), nao um texto generico. 12 de 12
  espelhos regenerados e verificados por teste que varre o diretorio.
- [x] **(b) Aviso ANTES de sobrescrever.** `_edicao_perdida()` -> `[WARN] ESPELHO_EDITADO_A_MAO`
  em **stderr**, com **a 1a linha divergente** na mensagem. O momento importa: depois da escrita
  nao ha o que reconhecer -- o disco volta ao gerado e o `git status` fica limpo, que e
  exatamente por que a perda da s159 nao deixou rastro.
- [x] ⚰️ **(c) Espelho read-only: avaliado e DESCARTADO, com razao escrita.** Os espelhos sao
  **commitados** (o Codex os consome); travar arquivo versionado briga com `git checkout` e com o
  proprio `sync` em toda maquina -- o custo recairia sobre o fluxo **correto** para punir o
  incorreto. O achado ja dizia *"(a)+(b) sao baratos e resolvem o caso observado"*.
- [x] **Craftsmanship.** 578 passed; suite inscrita no `pytest.ini`; banner fica no **wrapper**,
  fora do corpo comparado pela paridade (`check()` segue verde -- teste proprio).

## O desenho que evita o falso-positivo

O criterio e **CONJUNTO**, e isso e a decisao central do item:

| sinal sozinho | por que nao basta |
|---|---|
| mtime do espelho > fonte | `git checkout` mexe na data sem mexer no conteudo -- viraria ruido em toda maquina |
| corpo divergente | e o **fluxo normal**: "a fonte mudou, o sync vai alinhar" |
| **os dois juntos** | assinatura de *"alguem editou o espelho depois"* -- o caso da s159 |

Os **dois negativos tem teste**: `test_fonte_editada_normalmente_NAO_acusa` e
`test_criterio_e_CONJUNTO_mtime_sozinho_nao_acusa`. Um gate que grita no fluxo correto e um gate
que sera ignorado -- e ignorar o WARN era metade do defeito original.

## Pattern Compliance

- [x] **Sensors WARN-first** -- avisa e segue; nao bloqueia o sync (bloquear travaria o fluxo
  legitimo de todo commit que edita skill).
- [x] **stderr para diagnostico**, stdout para o relatorio do sync (mesma disciplina do
  `_warn_degradacao` do `day_plan`).
- [x] **Artefato de build se declara** -- alinhado ao `AGENTE.md §10.3` e ao
  `.vibeflow/conventions.md` ("nunca editar `.agents/skills/` a mao").

## Convention Violations

Nenhuma.

## Critical Gate

Clean — no destructive operations detected. O diff adiciona um banner ao texto gerado, uma funcao
pura de comparacao e um `print` em stderr. Nenhuma escrita nova, nenhum SQL, nenhum caminho
destrutivo. Os 12 espelhos foram reescritos pelo gerador -- que e a operacao normal dele.

## Fronteiras DECLARADAS

1. **O aviso depende de mtime, e mtime nao e historico.** Um `git checkout` que traga um espelho
   editado **e** a fonte no mesmo instante pode empatar os tempos e nao acusar. O sinal e
   heuristico por natureza; o **banner** e a camada que nao depende de relogio nenhum.
2. **Nada impede a edicao** -- o WARN informa, o sync sobrescreve. Tornar isso BLOCK travaria o
   fluxo legitimo (todo commit que edita skill roda o sync) e foi rejeitado junto com (c).
3. **Nao cobre o outro agente.** Se outro harness gerar espelhos por conta propria, o banner e o
   aviso desta ferramenta nao o alcancam -- e a mesma classe *sem perimetro* do F95, declarada.
