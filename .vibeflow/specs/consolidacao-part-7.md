# Spec: consolidacao-part-7 — filesystem, rotação embutida e auto-higiene no rito

> PRD: `consolidacao-alcancabilidade.md` · Mapa do auditor de filesystem + regra nova do operador: auto-higiene é passo do protocolo de ENCERRAMENTO.

## Objective
O filesystem local para de acumular; o protocolo de fechamento passa a limpar o que foi absorvido — para sempre, não uma vez.

## Definition of Done
1. [ ] Limpeza física (lista do auditor): `__pycache__/` do projeto (raiz+app+tools) · `.pytest_cache/` · `tmp/` EXCETO `redrill42.json` (dívida ativa no HANDOFF) · backups raiz `ipub_backup_202607*.db` (4 de julho; 13/08 e 14/08 FICAM) · `artifacts/backups/` rotacionado keep-5 · 6 dirs UUID órfãos do chroma (se a part-2 não pegou).
2. [ ] **Rotação EMBUTIDA**: `tools/backup_db.py` grava em `artifacts/backups/` (fix do path que gerava backup na raiz) e após cada backup bem-sucedido purga além dos 5 mais recentes POR local; teste com fixture (6 backups fake → sobram 5).
3. [ ] `medhub-backup-pre-expurgo.git` (19MB, externo) DELETADO (aprovação explícita do operador nesta sessão; expurgo validado há 39d).
4. [ ] PDFs harvested: com a lista da part-2 — se marcadas como cópias-para-índice-morto, saem fisicamente; senão, ficam com o motivo registrado. PDFs-fonte EMED INTOCÁVEIS (s086).
5. [ ] **Auto-higiene no protocolo**: `AGENTE.md` (seção de fechamento de sessão) ganha o passo permanente: "arquivo absorvido/integrado em doc mais estável SAI no mesmo commit do selo; relatório incorporado por outro mais fresco SAI; veredito binário, sem archive/" + 1 linha no checklist do rito; `handoff-contract.md` alinhado.
6. [ ] `.gitignore` cobre o que sempre reacumula (`__pycache__/`, `.pytest_cache/` — se ainda não cobre com padrão recursivo).
7. [ ] `pytest` verde; `git status` limpo de lixo conhecido; peso recuperado reportado no commit (~25MB núcleo + 19MB mirror).

## Scope
Filesystem (deleções) · `tools/backup_db.py` + teste · `AGENTE.md` (fechamento) · `core/contracts/handoff-contract.md` · `.gitignore`.

## Anti-scope
NÃO tocar `.venv/` (pycache interno regenera; remoção opcional fica FORA — mexer no venv em uso é risco desnecessário) · NÃO tocar `resumos/*.md` nem PDFs-fonte · NÃO tocar `data/chroma` do gold.
