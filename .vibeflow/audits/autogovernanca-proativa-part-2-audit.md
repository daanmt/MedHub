## Audit Report: autogovernanca-proativa-part-2

**Verdict: PASS**

Auditado em 2026-07-04 contra `.vibeflow/specs/autogovernanca-proativa-part-2.md`.
Testes: suíte central + harness de autonomia verdes; `auto_check --all` exit 0.
Critical Gate: limpo (1 WARNING resolvido como override spec-documentado).

### DoD Checklist
- [x] **1 — Duas severidades no linter** — `tools/audit_resumos.py:31` define `BLOCK, WARN`; cada achado é uma tupla `(sev, msg)`; `block_total` (só BLOCK) governa o exit code (`audit_resumos.py:169`). BLOCK preserva as regras vigentes: "Armadilhas de Prova" ausente (`:113`) e tabela ASCII 3+ pipes (`:118`). WARN cobre as regras novas: frontmatter §5.2 (`:127`) e encoding proibido (`:132`). Verificado num resumo de teste: 2 BLOCK + 2 WARN reportados corretamente.
- [x] **2 — Encoding deixa de ser mascarado** — `errors='ignore'` removido da leitura (`audit_resumos.py:97`, `open(..., encoding='utf-8')`); `UnicodeDecodeError` vira BLOCK com nome do arquivo + mensagem (`:99-105`). Testado com byte 0xff → exit 1, `[BLOCK] [ENCODING] UnicodeDecodeError`.
- [x] **3 — Nenhuma regra vigente rebaixada** — `python -X utf8 tools/auto_check.py --all` → **exit 0** na base atual (0 BLOCK, 3 WARN agregados: ENCODING 1 + FRONTMATTER 2). As duas regras que já eram BLOCK seguem BLOCK; as novas nascem WARN, sem quebrar o débito legado.
- [x] **4 — Suíte isolada do db real** — `test_revisao_calibrada.py::test_roundtrip` (`:80-108`) copia o `ipub.db` para `%TEMP%/ipub_test_roundtrip.db`, faz `db.DB_PATH = tmp`, opera na cópia e restaura/remove no `finally` (padrão de `test_barreiras_preparar`). Rodada a suíte 2x + `auto_check --all`: `ipub.db` real **byte-idêntico** (Get-FileHash conferido antes/depois).
- [x] **5 — Craftsmanship (guard + convenções)** — guard de `fsrs` no import de `app.utils.db` (`test_revisao_calibrada.py:23-32`): `ModuleNotFoundError` com `e.name=='fsrs'` imprime "rode com o python global que tem py-fsrs; o .venv não tem" e `sys.exit(2)`, re-levantando o resto. Testado bloqueando o módulo `fsrs` → mensagem clara + exit 2. Nenhum `import sqlite3` novo (gate `test_craftsmanship_sqlite` verde; writes de teste só na cópia temp via `db.py`). `auto_check` distingue visualmente WARN de BLOCK: badge `⚠️ N WARN (não bloqueia)` no relatório final (`auto_check.py:170`).

### Pattern Compliance
- [x] **clinical-summary-format** — segue. As regras BLOCK (Armadilhas, sem tabela ASCII) são a materialização executável do padrão; frontmatter §5.2 e encoding entram como WARN conforme a spec, sem enrijecer a base.
- [x] **db-access-layer** — segue. Os writes de teste ocorrem só na cópia temp via funções de `db.py` (`set_dificuldade`/`get_dificuldade` roteadas por `db.DB_PATH`); nenhum `import sqlite3` novo introduzido (o de `test_revisao_calibrada.py` é pré-existente e o de `store.py` é backend separado).

### Convention Violations
Nenhuma. Idioma pt-BR; `snake_case`; degradação graciosa (`try/except` com default seguro no frontmatter/leitura); `finally` restaura estado.

### Critical Gate
- 🟡 WARNING [SEC108] `tools/auto_check.py:64` — `subprocess.run` (dynamic exec). **Resolvido como override:** o comando é lista estática (`[sys.executable, "tools/audit_resumos.py"]`, sem `shell=True`, sem input do usuário), é **padrão pré-existente** do próprio `auto_check` (cujo papel é orquestrar sub-checks por subprocess) e é **explicitamente documentado na spec** (Scope + Technical Decisions: "o exit code continua vindo dos sub-processos; auto_check não reimplementa a regra"). Não rebaixa o veredito.
- ✅ `shutil.copy`/`os.remove(tmp)` operam só sobre a cópia temporária do db — sem gatilho de mass-delete (DAT101) nem de banco. Nenhuma operação destrutiva, secret ou PII no diff.

### Nota de desvio (resolvido, não é gap)
A DoD 1 lista "emoji em header" entre as regras BLOCK "vigentes", mas o `audit_resumos.py` **nunca** enforçou essa regra — as únicas BLOCK vigentes eram Armadilhas + tabela ASCII. A base tem 28+ headers com emoji legítimos (`⭐`/`⚠️`/`🔴`), então promovê-la a BLOCK quebraria a DoD 3 (`auto_check --all` deixaria de ser exit 0), que é o invariante testável e binding. Seguindo o princípio explícito da própria DoD 3 ("as que já eram BLOCK seguem BLOCK; as novas nascem WARN"), emoji-em-header **não** foi introduzida (nem BLOCK — quebraria a base — nem WARN — está fora da enumeração da DoD 1). Recomendação ao arquiteto: se lintar emoji-em-header for desejado, nasce WARN numa parte futura, junto de uma decisão sobre os `⭐`/`⚠️`/`🔴` que a base usa de propósito. DoD 1 marcada PASS porque seu núcleo testável (2 severidades + regras vigentes preservadas como BLOCK) está cumprido.

### Próximos passos
**Ready to ship.** Sugestão: seguir para a Parte 3 do PRD (paridade de skills + drift no auto_check) e commitar ao final, como o usuário pediu.
