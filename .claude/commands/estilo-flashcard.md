---
description: "Contrato de autoria de flashcards do MedHub — os 5 princípios para cunhar cards ancorados no erro metacognitivo. Consultar antes de gerar ou regenerar qualquer card."
type: skill
layer: commands
status: canonical
---

# Skill: Estilo Flashcard

> Consultar este arquivo SEMPRE antes de cunhar ou regenerar um flashcard.
> É a régua de qualidade dos cards, assim como `estilo-resumo.md` é a dos resumos.
> A análise do erro (habilidades sequenciais, elo quebrado) vive em `analisar-questao.md`; aqui está **como o card é escrito**.

---

## Princípio central

O flashcard do MedHub não enuncia um fato genérico sobre um tema — ele **reforça o conteúdo exato onde o raciocínio rompeu** quando o usuário errou a questão. O substrato vem de `questoes_erros` (`tipo_erro`, `o_que_faltou`, `habilidades_sequenciais`, `alternativa_marcada` vs `alternativa_correta`, `armadilha_prova`) cruzado com o resumo correspondente (via RAG local). O card é a costura entre o ponto de ruptura e a rede de conhecimento.

---

## Os 5 princípios

1. **Conteúdo clínico atômico.** Um conceito por card. Decompor em vez de combinar: se o erro toca duas listas (ex.: agentes de úlcera *e* de corrimento), são **dois cards**, não um. O card é **recall de conteúdo**, nunca um card sobre "o hábito de raciocínio".
2. **O erro define o alvo.** `tipo_erro` + `o_que_faltou` apontam *qual* conteúdo drilar e *qual distinção/sobreposição* tornar central. O card é específico ao erro do aluno — não uma varredura genérica do tema.
3. **Pergunta direta, sem vazar a resposta.** A `frente_pergunta` é uma pergunta clínica real terminando em "?". **Nunca** colar o `habilidades_sequenciais` cru, **nunca** embutir a resposta no contexto, **nunca** usar template tipo "Qual o distrator típico em...?".
4. **Regra-mestre = a distinção/sobreposição** que previne a confusão. É o princípio transferível que costura este erro a outros (ex.: *Chlamydia* L1-L3 = úlcera vs D-K = corrimento).
5. **Armadilha = o distrator específico** que pegou o usuário, ancorado no resumo (que carrega o alerta de incidência em prova). Não um distrator hipotético — o que de fato induziu o erro.

---

## Granularidade

- **1 a 3 cards por erro.** A maioria dos erros rende 1-2. Acima de 3, o erro provavelmente mistura conceitos — reanalisar.
- **Armadilha: linha vs card próprio.** O distrator vai como `verso_armadilha` dentro do card de conteúdo. Só vira **card separado** se for ele mesmo um conceito recall-ável e distinto (raro). Não criar card de armadilha por padrão.
- **Atômico ≠ raso.** Atômico é *um conceito*, mas a resposta deve ser completa (agentes com seus nomes, doses, critérios) — densidade clínica como nos resumos.

---

## Exemplo-âncora: erro #211 (Úlceras Genitais)

**Erro real:** validou a alternativa por reconhecer 3 de 4 agentes corretos numa questão de lista, sem conferir o 4º (*Trichomonas* — corrimento, não úlcera).

### ❌ Ruim (geração heurística atual)

> **P:** "1) Classificar IST por síndrome: úlcera (...) vs corrimento (...); 2) Em questões de lista, conferir cada item; 3) Saber que Chlamydia tem dois comportamentos conforme sorotipo?"
> **R:** "Trichomonas vaginalis é protozoário..."

Por que falha: colou o `habilidades_sequenciais` cru (não é pergunta, vaza tudo); viola os princípios 1 e 3.

> **P:** "Qual o distrator típico do examinador em: IST por síndrome — armadilha do agente intruso em lista?"

Por que falha: template genérico; não força recall de conteúdo. Viola 1, 2, 3.

### ✅ Bom (atômico, ancorado)

**Card 1 — Úlcera**
> **P:** Quais agentes causam **úlcera** genital?
> **R:** *Treponema pallidum* (sífilis) · HSV · *Haemophilus ducreyi* (cancro mole) · *Klebsiella granulomatis* (donovanose) · *Chlamydia trachomatis* **L1-L3** (LGV).
> **Regra-mestre:** *Chlamydia* entra aqui só nos sorotipos **L1-L3**; os **D-K** dão corrimento — mesma bactéria, dois quadros por sorotipo.
> **Armadilha:** *Trichomonas* **não** causa úlcera — é o intruso clássico enfiado em listas de úlcera.

**Card 2 — Corrimento**
> **P:** Quais agentes causam **corrimento/cervicite**?
> **R:** *Trichomonas vaginalis* · *Neisseria gonorrhoeae* · *Chlamydia trachomatis* **D-K** · *Gardnerella vaginalis* · *Candida*.
> **Regra-mestre:** *Chlamydia* **D-K = corrimento**; **L1-L3 = úlcera (LGV)** — a pegadinha da sobreposição.
> **Armadilha:** *Trichomonas* aparece como distrator em listas de "úlcera" — confira: é corrimento.

A distinção (dois grupos) e a sobreposição (*Chlamydia* por sorotipo) ficam reforçadas nos dois cards; o erro específico (*Trichomonas* mal-agrupado) vira a linha de armadilha — sem meta-card.

---

## Os 5 campos estruturados (output)

```
frente_contexto:    [cenário clínico em 1-2 frases, OU vazio se a pergunta é conceitual direta — nunca vaza a resposta]
frente_pergunta:    [pergunta clínica direta, termina em "?"]
verso_resposta:     [resposta completa e densa — nunca uma letra isolada]
verso_regra_mestre: [a distinção/sobreposição que previne a confusão]
verso_armadilha:    [o distrator específico que pegou o usuário, ancorado no resumo]
```

Persistir via `insert_questao.py` (go-forward) ou via o caminho de UPDATE/`--cards-file` (regeneração) — ver `analisar-questao.md` §9 e a spec da Onda B.

---

## Backfill — regenerar cards legados

Os cards cunhados pela heurística antiga (`needs_qualitative = 1`) devem ser refeitos pelo agente, um erro por vez:

1. **Puxar a fila:** `python tools/cards_regen_queue.py [--area X] [--limit N] [--questao-id ID]` — emite, em JSON, cada erro com seu substrato metacognitivo (`tipo_erro`, `habilidades_sequenciais`, `o_que_faltou`, `alternativa_correta`/`marcada`, `armadilha_prova`) + os `cards_atuais` (com `card_id`).
2. **Ancorar no resumo:** buscar o resumo correspondente via RAG local (`app.engine.rag.search`) para os critérios/alertas de incidência.
3. **Cunhar** 1-3 cards atômicos pelos 5 princípios acima.
4. **Persistir, preservando o FSRS:**
   - Reescrever um card existente (mantém `card_id` → estado FSRS):
     ```python
     from app.utils.db import update_flashcard_fields
     update_flashcard_fields(card_id, {"frente_pergunta": "...", "verso_resposta": "...",
                                        "verso_regra_mestre": "...", "verso_armadilha": "...",
                                        "tipo": "conteudo"})
     ```
   - Adicionar cards novos ao mesmo erro: `python tools/insert_questao.py --cards-file <json>` (ver `analisar-questao.md §9`).
5. **Priorizar áreas fracas** (`--area`) e processar em lotes — não big-bang. Revisar a qualidade pela régua antes de seguir.

> A geração heurística (`regenerate_cards.py`) foi **aposentada** — a geração é do agente, o código só persiste.

---

## Fronteira com `estilo-resumo.md`

- **Resumo** = documento técnico de referência, didática 80/20, cumulativo, por tema.
- **Flashcard** = recall atômico de um ponto de ruptura específico, ancorado no resumo.

O card consome o resumo; não o substitui nem o duplica.
