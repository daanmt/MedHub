# Spec: Engenharia Ledger — Part 3: Contratos de Medida (F9 + F8)

> Gerada via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/engenharia-ledger-f1-f13.md` (Onda 3)

## Objetivo

O contrato de `/revisar` deixa de corromper a própria métrica: o rating só é gravado após a janela de override (F9, elimina o re-record sobre estado mutado) e o PREPARAR é isolado das respostas dos cards do bloco (F8, preserva a validade do trial de recall).

## Contexto

Caso real s108: card 403 gravado com nota 2, corrigido para 4 depois do `--record` — o re-record recalculou FSRS a partir do estado já mutado e deixou 2 linhas de revlog. A contradição ("usuário pode sobrepor" vs "nunca --record duas vezes") dormiu no contrato desde s075. No mesmo dia, o PREPARAR contaminou o trial por 3 canais verificados: vazamento direto de resposta, pré-resolução de cards de conduta, e erro de ensino amplificado. Correção é 100% protocolo/texto — `record_review` e schema ficam intocados (decisão do ledger, mantida no PRD).

## Definition of Done

1. [ ] Contrato de `/revisar` (passos 4-5 do loop): o agente apresenta a nota proposta + justificativa, **espera a janela de override** (confirmação, correção ou silêncio-que-avança no modo lote), e só então roda `--record` — **uma vez por card, sempre**. A cláusula "usuário pode sobrepor" passa a referenciar a janela (antes do record), não o pós-gravação.
2. [ ] Regra anti-duplo-registro reescrita sem contradição: override intencional acontece ANTES do record; pós-record não há amend (se acontecer erro de gravação real, registrar em history/ e seguir — o caso vira achado de ledger, não re-record).
3. [ ] Cláusula de isolamento do PREPARAR: aquece conceitos/mecanismos, NUNCA o par pergunta-resposta dos cards do bloco; o refresh é montado sem abrir os versos; formulações como tendência ("geralmente X, mas considerar Y se Z"), nunca absolutos.
4. [ ] Distinção de classe de card no PREPARAR: cards de raciocínio/conduta → refresh do framework legítimo (nota mede "pegou o framework", sinalizar); cards de fato puro → refresh contraindicado (só orientação de entorno; a resposta específica é retida para o recall).
5. [ ] `python tools/sync_skills.py --check` passa (paridade command↔skill) e `auto_check.py --all` continua verde.
6. [ ] Craftsmanship: `git diff` restrito a `.claude/commands/revisar.md`, `core/contracts/revisao-calibrada-contract.md` e espelho gerado em `.agents/skills/` — zero mudança em `*.py`, zero mudança de schema; estilo/formatação dos arquivos preservados (pt-BR, emojis de invariante 🔴 mantidos).

## Escopo

- `.claude/commands/revisar.md` — passos 4-5 do protocolo do loop + Camada 0 (cláusulas F8) + regra anti-duplo-registro.
- `core/contracts/revisao-calibrada-contract.md` — norma correspondente (janela de override; isolamento do PREPARAR; classes de card).
- `.agents/skills/` espelho — regenerado via `sync_skills.py` (nunca editado à mão).

Budget: 3 arquivos (≤6 OK).

## Anti-escopo

- **Nenhum `--amend` no CLI nem rollback no `record_review`** — alternativa pesada explicitamente descartada pelo ledger (F9 hipótese preferida).
- Nenhuma mudança em `fsrs_queue.py`, `db.py`, `fsrs.py` ou schema.
- Não redesenhar o modo lote (N frentes por vez) — a janela de override se encaixa nele (propor notas do lote → confirmar → gravar lote).
- Não tocar o gatilho proativo do PREPARAR (F5, Onda 5).
- Não editar `estilo-flashcard.md` nem workflows de curadoria.

## Decisões Técnicas

1. **Protocolo > schema**: mover o record para depois da janela elimina a classe inteira de corrupção sem tocar o banco — zero risco de regressão em código. Trade-off: depende de disciplina do agente (texto), mas é exatamente o tipo de cláusula que o contrato existe para carregar, e o custo do caminho alternativo (amend com rollback de estado FSRS) é desproporcional.
2. **Janela no modo lote**: apresentar notas propostas do lote inteiro, aguardar 1 turno de confirmação/correção, gravar o lote — mantém a eficiência do lote e dá ao operador um ponto único de override.
3. **Fato puro vs raciocínio sem novo campo no schema**: a classificação é do agente na condução (heurística textual do card), documentada como critério no contrato; o campo `tipo`/altura formal fica para quando o sinal recorrer (anti-máquina-antes-do-sinal).
4. **Edição canônica + espelho gerado**: editar só o canônico e rodar `sync_skills.py` — a paridade é verificada pelo auto_check (WARN).

## Patterns Aplicáveis

- `agent-workflow-protocol.md` — mudanças de contrato seguem o rito (documentar em history/ no fechamento).
- `fsrs-review-flow.md` — a regra "1 record por card por sessão" é reforçada, não alterada.

## Riscos

- **Janela de override adicionar atrito por card** → mitigação: no modo lote a janela é por LOTE (1 turno para N cards), não por card; no modo 1-a-1 a confirmação já era natural do diálogo.
- **Agente esquecer a janela em sessão longa** → mitigação: a cláusula entra como 🔴 invariante no topo do protocolo (mesmo peso dos invariantes A/B do PREPARAR); candidato futuro a check executável se recorrer (ledger).
- **Drift entre canônico e espelho** → mitigação: DoD 5 (sync_skills --check) + paridade já monitorada pelo auto_check.

## Dependencies

- Nenhuma técnica. Recomendado após part-2 apenas para o contrato poder citar `--cluster`/`--review-plan` se útil (opcional, não bloqueante).
