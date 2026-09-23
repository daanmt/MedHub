---
type: spec
projeto: MedHub
feature: medhub-hub-v0
part: 4
slug: medhub-hub-v0-part-4
status: ready
relates_to:
  - .vibeflow/prds/medhub-hub-2026-09-22.md
  - .vibeflow/specs/medhub-hub-v0-part-3.md
---

# Spec -- MedHub HUB v0, parte 4: medir o hub em uso (sessao nova, celular, 2 fechamentos)

> Passos (v)+(vi) da ordem do `/ai-eng`. Nao ha codigo: e a verificacao empirica do que o papel nao
> prova. Roda nas sessoes SEGUINTES a s192 e com o operador. Enquanto nao fechar, o audit do v0 e PARTIAL
> por construcao -- e isso e o resultado honesto, nao um defeito.

## Objective
Provar em uso real que o hub sobrevive, que o rito funciona numa sessao que nao criou o artifact e que o
drill no celular grava -- com numero no session log, nao com afirmacao.

## Context
As partes 1-3 entregam o montador, a idempotencia, o rito e o 1o publish. Tres coisas so se medem depois:
(a) o contrato recusa publish/`files` em artifact nao lido -> o rito tem de funcionar pos-`/clear`;
(b) navegar do index para um arquivo secundario e voltar pode ou nao manter o `db` da pagina (nao
documentado); (c) humano pode apagar o hub mesmo fixado.

**Friccao (F110):** nenhuma removida aqui; esta parte mede se a das partes 1-3 foi removida de fato.

## Definition of Done
1. **Sessao nova (pos-`/clear`), rito completo:** `Artifact read url` -> `Artifact list scope=files url` ->
   `painel.py --html` -> `hub.py --build --lote <vivo> --publicado <lista>` -> `Artifact publish url + files`
   aceito; `Artifact list` (limit 50) antes e depois sem URL novo; os dois numeros e o custo do `read` em
   contexto (inline ou arquivo) no session log.
2. **Celular (so o operador prova):** drill de >= 20 cards pelo hub; no meio, abre 1 aula e volta; as notas
   de antes E de depois da navegacao estao no `db` (`ArtifactData list`) e gravam por `--record-lote
   --apply --expect N` com COUNT-ASSERT batido. Se a nota de depois nao cair: plano B da parte 1
   (`target=_blank`) e re-teste.
3. **Sobrevivencia:** 2 fechamentos seguidos republicam na MESMA URL (sem `artifact-deleted`), registrado
   no selo de cada um.
4. **Idempotencia em uso:** uma releitura da mesma sessao depois de gravada imprime `ja_gravadas = N` e
   grava 0.
5. Resultado de cada item vai para o HANDOFF como DADO (SIM/NAO + numero) e para o canal do `/ai-eng`.

## Scope
Atos do agente nas sessoes s193+ e do operador no celular; `history/session_NNN.md`, `HANDOFF.md`.

## Anti-scope
Qualquer mudanca de codigo que nao seja o plano B declarado (`_blank`). v1a/v1b.

## Technical Decisions
- **Medir no uso real, nao em artifact de teste:** artifact novo de spike e exatamente a poluicao que o hub
  mata (regra do `/ai-eng`: spike so no proprio hub).

## Risks
- **Operador sem tempo para o drill antes de 01/11:** o drill e o proprio estudo dele (cards do dia); a
  medicao pega carona, nao custa sessao extra.

## Dependencies
- .vibeflow/specs/medhub-hub-v0-part-3.md
