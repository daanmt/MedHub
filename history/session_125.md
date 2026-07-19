# Session 125 — Sepse (Revisão) + drenagem FSRS maratona (80 cards) + passada de curadoria (20 reforjados + 3 no gate de evidência)
**Data:** 2026-07-19
**Ferramenta:** Claude Code (Opus 4.8 [1M])
**Continuidade:** Sessão 124

---

## O que foi feito

### Boot + correção de rota
- Boot ofereceu Colecistite/Imunizações (ancorado em `grade.json`/HANDOFF do PDF); **usuário corrigiu com a ordem REAL da S13** (Sepse Revisão → DII → Pneumo II → Transtornos de Humor → Hepato → Arbovirose/Meningite/Sepse por questões). Instância viva do **dual-SSOT do cronograma** (`project_cronograma_dual_ssot`): o `--sync-drive` não rodou (base64 grande do xlsx não materializa em disco à mão) → ledger **F36**.

### Sepse (Revisão) — item 1 da S13
- Nota resolvida via `day_plan --difficulty "Infecto" "Sepse"` = **6 (D5, `fonte=usuario`)**, propósito exercícios → aula **ampla + mecanismo aberto, prosa comprimida**, ancorada no resumo gold `Sepse.md`. `review_log` carimbado (`directed_review`, tema 266).
- Bloco: **37q / 31a (83,8%)**. 6 erros → 6 cards (840-845) via `insert_questao --errors-file` (deck EMED de Sepse consultado).
- **Achado-mestre:** 4/6 erros bateram na **camada LEGADA** (SIRS, EGDT/SvcO2, "sepse grave", protocolo-por-ano SSC 2016) que o resumo Sepsis-3-forward omitia → **`Sepse.md` expandido** (mediadores IL-10/NO, SIRS, "sepse grave" abolido, âncora-por-protocolo, escalonamento de ATB, metas EGDT/SvcO2, +6 armadilhas). auto_check PASS.

### Reforja pré-drenagem (fluxo EMED-fed, s124)
- 350/398/757/759 reforjados atômicos (recurate) + splits 838 (ADE dengue) / 839 (DTN hipertermia); 760 marcado p/ gate. Validados ao vivo depois (398/757/759 → 4 a frio).

### Drenagem FSRS — 80 cards em 14 blocos (DRENAR)
- Pull 1 (50): 26 atrasados + 16 hoje + 8 novos (dívida real). Extensão (30, a pedido do usuário "até 80"): fraco-primeiro/casado (Sepse Neonatal, Cirurgia Infantil, SdHG, **LRA**, Hemostasia, DM Agudas).
- **65 avaliados: 34×4 / 9×3 / 9×2 / 13×1 (66% sólido)** num pool ~60% inédito. Reforjados de hoje validaram a frio; **Pré-Natal cru 4/4/4** (medo do HANDOFF infundado); #419 resistiu à ancoragem no fármaco.

### Passada de CURADORIA (durante a extensão)
- Usuário articulou a régua **"resposta grande = reforja automático"** (= minimum-information principle) e flagou 18 cards. **Todos os 18 resolvidos** por **recast in-place** (recall vira 1 fato/discriminador; o resto desce pra regra-mestre — não explode o pool). Distinção ensinada: reforja é p/ card **mal escrito**, não p/ card que se **errou** (segurei o #356, que é bom).

### Gate de evidência (subagente `evidence-researcher`, PMID-ancorado)
- **760 ferro 1º tri:** timing/dose canônicos ✓ (MS/FEBRASGO: ferro 40mg elementar da 20ª sem; folato 400µg pré-concepção), mas o mecanismo "estresse oxidativo trofoblástico" é **framing** (hipótese contestada) → corrigido.
- **420 Ringer/K hiperK:** mecanismo **REFUTADO** (SMART, PMID 33503391 — balanceado não piora hiperK e reduz TRS; a salina é que pode piorar) → corrigido + armadilha banca-dependente.
- **423 bicarbonato/rabdo:** "previne LRA" superestimado (RS PMID 23324509 — quem previne é a hidratação) → corrigido + banca-dependente.

## Padrões de erro identificados
- **PADRÃO-MESTRE consolidado** (nova memória `feedback_bug_discriminador_exclui`): ancora no achado saliente/frequente e **ignora o discriminador que EXCLUI** o dx óbvio. Provas: #338/#342/#280/#498/#322/#507/#348/#340/#422. Ritual: "qual dado EXCLUI o que eu ia marcar?".
- Inversão de direção (#416 K), pergunta composta (auto-reconhecida), enunciado negativo (Sepse Q6).

## Artefatos criados/modificados
- `resumos/Clínica Médica/Infectologia/Sepse.md` — expandido (camada legada + 6 armadilhas). **[commit]**
- `HANDOFF.md`, `ESTADO.md`, `history/session_125.md`, `history/INDEX.md`. **[commit]**
- Memória: `feedback_bug_discriminador_exclui.md` (síntese do bug nº1). **[user memory, fora do repo]**
- `ipub.db` (local-only): 6 erros + cards 840-845; 20 cards reforjados (recurate); 65 FSRS records. **[não commitado]**

## Decisões tomadas
- **Recast in-place > split** na curadoria em massa — respeita "matar os cards"/teto; o recall vira atômico sem inflar o pool.
- **Nenhum dos 3 cards do gate aposentado** — todos valem como **banca-dependentes** (ensinam a resposta da prova + fixam a divergência com a evidência atual).
- 80 cards drilados a pedido explícito do usuário (override consciente do teto de 30; extensão fraco-primeiro).

## Próximos passos
- **S13 item 2: Doença Inflamatória Intestinal (Teoria)** — aula-base ancorada no PDF EMED → questões → cards.
- Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Card #828 (último WARN de auto-suficiência).
- Ledger: F36 (materialização de binário MCP no boot), F35, F8.
