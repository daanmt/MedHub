## Audit Report: sprint-final-uerj part-3 (Painel = backlog único por dia)

Commits: 4c14f21 (implementação), d132ece (título do bloco "Hoje" -> "Plano de hoje"). Auditado em 13/10/2026 (s226).

**Verdict: PASS** (com 4 achados não bloqueantes, abaixo)

### Testes
`python -X utf8 -m pytest tools/test_plano.py tools/test_painel.py -q` -> 152 passed (7,6 s).
`python -X utf8 tools/ui_capturas.py --cenas painel --larguras 390,768,1280 --out tmp/audit_p3/cap` -> 3x `ok` (sem rolagem horizontal; painel do build v109, com "Plano de hoje").
`python -X utf8 tools/painel.py --html --out tmp/audit_p3/painel.html` -> 2,4 s; no HTML real: "Plano de hoje", "Próximos dias", "Fora do sprint · 37"; zero "Atrasadas", "Desta semana", "Semana N do plano", "Até a prova".

### DoD Checklist
- [x] 1. `plano.agenda_sprint` PURA, lê só `dia_plano`; pendente de dia passado entra no `hoje` com `atrasada: False`; `None` sem sprint. Evidência: tools/plano.py `agenda_sprint`/`_item_sprint`/`motivo_fora_do_sprint`; `test_agenda_sprint_hoje_rola_proximos_e_fora`, `test_agenda_sprint_sem_dia_plano_e_none`, `test_motivo_fora_do_sprint_le_a_marca_do_compor`.
- [x] 2. Painel: Hoje (tarefas via `_tarefa`/`_html_tarefa` = mesma linha-alvo, total de questões, "+ N cards" = `restantes` ou teto, RD não assinada mais antiga) + Próximos dias (`details` recolhido, "qui 24/09 · 1 lista · 60 q") + Fora do sprint · N (recolhido, agrupado pelo motivo); sem sprint, `_html_semana`. Evidência: tools/painel.py `_bloco_sprint`, `_html_sprint`, `render_html`; 3 testes novos. Desvio justificado: o h2 é "Plano de hoje" (d132ece), não "Hoje", para não repetir o título do bloco `dia`.
- [x] 3. `test_painel_sprint_sem_semana` proíbe "Atrasadas", "Desta semana", "Semana ", "Até a prova" e as classes de atraso.
- [x] 4. `<li class="tarefa[ proxima]" data-tarefa="N">` preservado (regex no teste; `data-bloco="semana"` mantido de propósito).
- [x] 5. Sem cor literal no diff (só `var(--...)`); capturas 390/768/1280 `ok`; suíte do escopo verde.

### Pattern Compliance
- [x] Função pura + fonte única (plano.py), tela só renderiza (painel.py) — segue o padrão `plano.panorama`.
- [x] Degradação declarada (None -> bloco antigo) testada.
- [x] Tokens do tema.css; nada de cor literal.
- [ ] docs/UI.md §6 ainda chama o bloco de **Hoje** (o código diz "Plano de hoje") — drift de doc, baixa.

### Critical Gate
Clean — nenhuma operação destrutiva ou regra do catálogo disparada (o `subprocess` do `git log` é pré-existente em `hub.data_de_criacao`, não adicionado).

### Achados (não bloqueantes)
1. **MÉDIA (confiança alta) — leitura de `tmp/hub_db/quadro` é frágil, falha para o lado errado.** tools/painel.py:59 (`QUADRO_ESTADO`) e `_rd_nao_assinada` (~l.180-196): pasta ausente = "nenhuma assinada". Numa máquina/clone sem o espelho do tique, ou antes do 1º `ArtifactData list` do dia, TODAS as RDs com arquivo (25 hoje) viram candidatas e o Painel publica a mais antiga como pendente — falso pendente, contrário à alça fechada. Também: o espelho só anda no tique (RD assinada entre tiques segue listada no painel estático; o hub pinta "assinado" ao vivo, então o dano é visual e curto); doc apagado no db deixa arquivo velho no espelho (rglob lê tudo). E o HTML do Painel passa a depender de estado gitignorado (`painel.py --html` dá resultados diferentes por máquina). Sugestão: pasta ausente = não mostrar RD (fail-closed) + aviso no JSON; ou o tique passar o estado explicitamente (`--quadro-estado`, como o `hub.py`).
2. **BAIXA (confiança alta) — custo de `hub.data_de_criacao` no build.** `_data_da_aula` roda 1 `git log --follow --diff-filter=A` por candidata (todas, só para tirar o `min`). Medido: 5 candidatas = 1,0 s dos 2,4 s do `painel.py --html`; no pior caso do achado 1 (25 candidatas, sem espelho) ~5 s. Aceitável hoje; barato de cortar: uma única chamada `git log --diff-filter=A --name-only --format=%as -- artifacts/` (ou a data no `core/hub_quadro.json`).
3. **BAIXA (confiança média) — pendente sem `dia_plano` e sem a marca `sprint: fora` some do Painel** (nem hoje, nem próximos, nem fora). tools/plano.py `agenda_sprint`. Por desenho da spec, mas tarefa criada depois do último `--sprint` fica invisível até recalcular; vale um contador "sem dia · N" ou cair em "Fora".
4. **BAIXA — drift docs/UI.md §6** ("o bloco das tarefas é **Hoje**") vs "Plano de hoje" no código/teste. (UI.md está sendo editado pela part-4; corrigir lá.)

### Gaps / Incremental Prompt Pack
Nenhum gap de DoD. Follow-ups opcionais:
- painel.py `_rd_nao_assinada`: `if not Path(QUADRO_ESTADO).exists(): return None` (fail-closed) + teste "sem espelho = sem RD".
- `_data_da_aula`: uma chamada de git para todas as aulas (dict slug->data), injetável como hoje.
- UI.md §6: "Hoje" -> "Plano de hoje".
