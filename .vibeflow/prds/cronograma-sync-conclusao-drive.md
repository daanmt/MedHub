# PRD: Sync de conclusão real do cronograma (xlsx do Drive → boot)

> Gerado via /vibeflow:discover em 2026-07-08

## Problem

O boot diário (`day_plan.py`, consumido pelo SessionStart hook e por `AGENTE.md §2 passo 4`) recomenda "próximos temas" a partir de `core/cronograma/grade.json` — uma derivação puramente **calendário-driven** do `Cronograma.pdf` estático (posição = semana nominal por data). Ele nunca lê o marcador de conclusão real que o usuário mantém na planilha `Cronograma de Reta Final.xlsx` do Drive (tema riscado/recolorido = concluído — mecânica já documentada em `.claude/commands/importar-planilha.md` e em `core/contracts/reconcile-contract.md §Absorção de dados de performance`, mas nunca automatizada).

Consequência: o boot erra sistematicamente para quem estuda fora de ordem ou em ritmo diferente do calendário nominal — que é exatamente o caso do usuário (execução por trilha temática, não estritamente sequencial). Materializou-se ao vivo em 2026-07-08 (sessão corrente): o boot recomendou MFC/Imunizações/Apendicite como pendentes quando já estavam riscados como feitos, enquanto o pendente real (DITC II, Distúrbios do Potássio, Cefaleias+Epilepsias, HAS Pt.2 + 2 blocos de Revisão por Questões) ficou invisível. Registrado como achado **F33** em `AUDITORIA_MEDHUB.md` (irmão do **F29**, já resolvido, que era o mesmo problema aplicado a volume/planilha `Dashboard EMED 2026` em vez de conclusão de tema).

**Causa raiz:** o contrato `cronograma-contract.md` já documentava isso como fora de escopo v1.0 (Cláusula 1 + item **R8**: "Reconciliar PDF × xlsx do Drive"). O `reconcile-contract.md` já tem a condição **W6** ("Próxima = SNN desatualizada vs trabalho real") e a seção "Absorção de dados de performance" já prescreve em prosa que o marcador riscado deveria alimentar a priorização — mas nada mecaniza essa leitura. Ela só acontece quando o agente lembra manualmente ou quando o usuário contesta o boot (como hoje). Sem gatilho mecânico, o erro é estruturalmente recorrente, não um lapso pontual.

**Restrição arquitetural chave:** o Google Drive só é acessível via MCP, que só existe no contexto do agente (sessão interativa) — nunca dentro do hook `day_plan.py`, que roda como script Python puro no SessionStart. Logo, a leitura do xlsx nunca pode acontecer dentro do próprio hook; precisa ser feita pelo agente e cacheada para o hook consumir.

## Target Audience

O próprio usuário (operador/estudante) como beneficiário direto — recebe um boot confiável. O consumidor técnico imediato é o agente MedHub (Claude Code), que executa o boot e precisa de um sinal mecânico em vez de depender de memória/atenção para lembrar de checar a planilha.

## Proposed Solution

1. **Novo subcomando em `tools/cronograma.py`** que recebe os bytes já baixados do xlsx (o agente busca via MCP `download_file_content`, já que o script não tem MCP) e produz um snapshot estruturado da conclusão real por task (`area_norm`/`tema`/semana, flag `concluido` via `cell.font.strike`), cruzando com `grade.json` pelo mesmo `area_norm`/`tema` já usado no join cronograma↔desempenho.
2. **Snapshot cacheado em `core/cronograma/conclusao_drive.json`** (gitignored — decisão do discovery): grava o resultado + timestamp de quando foi lido do Drive.
3. **Gatilho de refresh: 1× por dia-calendário** (decisão do discovery). No boot (`AGENTE.md §2 passo 4`), o agente verifica a idade do snapshot; se for de um dia calendário anterior (ou não existir), busca o xlsx via MCP e regenera o snapshot antes de prosseguir. Nos demais boots do mesmo dia, reusa o cache — zero chamada MCP extra.
4. **`day_plan.py` passa a consumir o snapshot** (quando existir e não estiver mais que 1 dia desatualizado) para calcular "próximos temas" pela **fronteira real de conclusão** (tasks sem `concluido=true`), não mais pela posição sequencial calendário. Sem snapshot (primeira sessão, ou MCP indisponível/headless) cai no comportamento atual (calendário) — nunca bloqueia.
5. **Nova condição de reconcile `W8`**: "posição calendário de `grade.json` diverge da fronteira real marcada no xlsx" — WARNING, nunca BLOCKING (mesma família de W5-W7, `cronograma-contract.md` Cláusula 6). Resolução W8 = rodar o refresh do passo 3 e atualizar o ponteiro textual `Próxima = SNN` (único write permitido, Cláusula 5) com a semana real **e a lista de pendentes dentro dela** (não só o número da semana — lição de hoje: semanas ficam parcialmente concluídas).
6. **Fallback headless/sem auth:** se o MCP do Drive falhar (ambiente sem OAuth interativo, ex. cron/schedule), o agente reporta WARNING (não bloqueia) e segue com o cache existente ou com o calendário puro, igual ao comportamento W5-W7 já estabelecido.

## Success Criteria

- O boot do dia (mensagem "Plano do Dia") nunca mais recomenda como "próximo tema" algo já riscado como concluído no xlsx, salvo quando o snapshot estiver desatualizado (>1 dia) por falha de MCP — e nesse caso o boot **avisa explicitamente** que está em modo calendário-fallback.
- O ponteiro `Próxima = SNN` em `HANDOFF.md`/`ESTADO.md` reflete a fronteira real (não a posição calendário) sem precisar de correção manual do usuário — o incidente de hoje (usuário contestando o boot) não deveria se repetir.
- Achado F33 pode ser marcado RESOLVIDO em `AUDITORIA_MEDHUB.md` após a implementação, nos mesmos moldes do F29.

## Scope v0

- Subcomando novo em `tools/cronograma.py` (ex.: `--diff-drive <path-para-xlsx-baixado>`) que gera/atualiza `core/cronograma/conclusao_drive.json`.
- Passo explícito no boot (`AGENTE.md §2 passo 4`): checar idade do snapshot → se >1 dia-calendário ou ausente, buscar xlsx via MCP (`download_file_content`, id já registrado em `importar-planilha.md`) → salvar bytes em temp → chamar o subcomando novo.
- `day_plan.py`: ler `conclusao_drive.json` quando presente e fresco; calcular "próximos temas" pela fronteira real de conclusão em vez da posição calendário; fallback silencioso para o comportamento atual quando o snapshot não existir/estiver velho.
- Nova condição **W8** documentada em `reconcile-contract.md` (tabela + resolução), reaproveitando a mecânica de W5-W7 (nunca BLOCKING).
- `.gitignore`: adicionar `core/cronograma/conclusao_drive.json`.
- Fechar F33 em `AUDITORIA_MEDHUB.md` referenciando a implementação, nos moldes do fechamento de F29.

## Anti-scope

- **Não** criar cron/daemon — viola Cláusula 3 (`cronograma-contract.md`, sync read-on-demand, coerente com Zero-DB no Cloud). O gatilho é sempre um boot de sessão do agente.
- **Não** alterar `Cronograma.pdf`/`grade.json` como SSOT estrutural — o xlsx continua sendo só a **camada de conclusão**, nunca substitui o PDF como fonte da grade (Cláusula 1).
- **Não** escrever em `taxonomia_cronograma`, `sessoes_bulk`, FSRS (`fsrs_cards`/`fsrs_revlog`) a partir dessa feature — fronteiras duras da Cláusula 5 continuam valendo integralmente; o único write novo é o próprio `conclusao_drive.json` (fora do `ipub.db`) e o ponteiro textual já permitido.
- **Não** resolver o alinhamento fino `questoes_por_lista[i] ↔ tasks[i]` (já fora de escopo v1.0 do cronograma-contract, não é o problema deste PRD).
- **Não** tentar tornar o hook `day_plan.py` capaz de MCP — arquiteturalmente não é o papel dele; ele só lê o cache.
- **Não** reimportar automaticamente volume (`sessoes_bulk`) a partir do xlsx — isso já é o fluxo W1/F29 (`/importar-planilha`), este PRD cobre só o marcador de conclusão de tema, não questões/acertos.

## Technical Context

- **Mecânica de leitura já prototipada ad-hoc nesta sessão** (2026-07-08): `download_file_content` (MCP, fileId `157JEKQA9O49JxQHApOutKrVn7jW8JdIY`) → base64 → `openpyxl.load_workbook` → `cell.font.strike` por task, cruzado por `area_norm`/`tema`. Reaproveitar essa sequência, só formalizando em `tools/cronograma.py` em vez de script solto.
- **Estrutura do xlsx** (aba `Plan1`): linha 2 = datas por semana (colunas 1-28), linha 3 = trilha, linhas 4-16 = slots de task (`"Tema\n(Tipo)"`, quebras de linha internas — normalizar whitespace antes de casar com `grade.json`). Encoding: `read_file_content`/`download_file_content` retornou acentuação corrompida (mojibake) nos testes desta sessão — normalizar ou casar por substring tolerante a isso.
- **Contratos a atualizar:** `cronograma-contract.md` (mover R8 de "fora de escopo" para "implementado", adicionar Cláusula sobre o snapshot); `reconcile-contract.md` (nova linha W8 na tabela + passo de resolução); `AGENTE.md §2 passo 4` (passo explícito de refresh do snapshot).
- **Precedente idêntico já resolvido:** F29 (drift planilha↔db de volume) seguiu o mesmo padrão — leitura ad-hoc via MCP+openpyxl, script de fix, documentação do achado. Este PRD generaliza o mesmo padrão para a camada de conclusão de tema, fechando a "família" de drifts Drive↔local de uma vez (volume já resolvido, conclusão de tema é o que falta).
- **Decisões do discovery:** gatilho = 1×/dia-calendário com cache; `conclusao_drive.json` gitignored (mesmo tratamento de `ipub.db` — estado pessoal mutável, sem valor de auditoria em diff diário).

## Open Questions

- Formato exato do `conclusao_drive.json` (schema) — decidir no `gen-spec`, não bloqueia o PRD.
- Onde exatamente no fluxo do `AGENTE.md §2` o passo de refresh entra (antes ou depois do reconcile check padrão) — resolver no `gen-spec`/planejamento técnico.
- Se falhas de MCP devem virar uma condição própria (ex. W9) ou só um log silencioso dentro da resolução de W8 — decidir na spec técnica.
