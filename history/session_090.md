---
type: session
sessao: 090
data: 2026-06-24
area_foco: Gastro (Pólipos/CCR) + Neurologia (TCE+Demências) + Cardiologia (HAS)
---

# Sessão 090 — Dia tríplice da Semana 09 (T9+T10+T11) + 20 flashcards

## Contexto
Dia gigante e em modo rush a pedido do usuário. Fechados **três temas** da Semana 09 do `Cronograma.pdf` — T9, T10 e T11 — intercalados com uma rodada de drenagem do FSRS. Reconcile de boot limpo (B1–B4 OK). Acumulado cruzou **31% do marco ENAMED**.

## O que foi feito
- **T9 — Pólipos Intestinais e Câncer Colorretal (Gastro, Teoria):** aula-base "escada" COMPLETA (escopo inteiro do PDF EMED: pólipos → síndromes hereditárias → CCR clínica/rastreio/estadiamento/tto cólon e reto/metástase hepática → delgado). Bloco **23q / 18 (78%)**. 5 erros → 5 cards (#534–538) + 1 andaime de AAA na Preventiva (#539).
- **Flashcards FSRS:** **20 cards drenados** (4 lotes de 5; curva de notas subindo 2,0→3,6 — aquecimento pós-pausa). 20 dos 36 atrasados zerados.
- **T10 — TCE + Demências (Neuro, Revisão):** aula-base **descomprimida** nos dois (a pedido explícito do usuário, apesar do resumo de Demências já ser gold). Bloco **40q / 29 (72,5%)**. 11 erros → 6 cards (#540–545) + **2 andaimes de Glasgow** (base + mecanismo, #546–547).
- **T11 — HAS Pt1 (Cardio, Teoria):** **SEM aula-base** — o usuário resolveu as 13 questões por conta antes de retomarmos. Bloco **13q / 8 (61,5%)**. 5 erros → 5 cards (#548–552) + 1 andaime da grade de HAS (#553).
- **Volume:** `sessoes_bulk` s090 → Gastro 23/18, Neurologia 40/29, Cardiologia 13/8 = **76q / 55 (72%)**.

## Padrões de erro identificados
- **🔴 Eixo do dia — bug nº1 (ancoragem / leitura por dado parcial):** reapareceu forte. Pólipos: PSO×colonoscopia (Q2 sangramento + Q4 anemia = mesmo erro, 2×). HAS: ignorou a **hipocalemia** (Q1 → foi a renovascular em vez de hiperaldo), não leu a **MAPA contra o cutoff** (Q2, 136≥135), aplicou critério de **consultório a valor de MAPA** (Q3 estágio I). 5 dos 21 erros do dia são essa assinatura.
- **🔴 Reincidente — hiperventilação no TCE:** errada no flashcard #78 **e** no bloco (Q2/Q10). Hiperventilação é resgate, nunca rotina (isquemia).
- **Glasgow (cluster fraco, 3 erros):** Q1 (não pegou a MELHOR resposta motora), Q3 (componente ocular), Q4 (verbal confuso×sem sentido). → 2 andaimes (escala+regra / 3 discriminações).
- **CJD (2 lados):** não reconheceu quando era (Q6, marcou Lewy) e aceitou "priônica comum" quando era distrator (Q9).
- **Decoreba pontual:** Korotkoff fase III×II (Q4 HAS), metas de PA por risco (Q5 HAS, banca-dependente).

## Artefatos criados/modificados
- **20 cards novos:** 16 de erro (#534–538, 540–545, 548–552) + 4 andaimes (#539 AAA · #546–547 Glasgow base+mecanismo · #553 grade HAS).
- Temas novos na taxonomia: "Hipertensão Arterial Sistêmica" (Cardiologia).
- Contadores: **327 erros · 354 cards ativos · 41 andaimes.**
- Nenhum resumo `.md` editado (só leitura de TCE.md e Demências.md).

## Decisões / pendências
- **`resumos/Clínica Médica/Neurologia/TCE.md` precisa de reescrita** — conteúdo correto, mas estilo coloquial/erros de digitação que violam o gold standard (AGENTE §4). Reescrever em sessão dedicada (escopo grande → confirmar com usuário).
- **Ectópica sem resumo `.md`** (só andaime) — gap de matéria confirmado na Revisão Direcionada dos flashcards (par #116/#118 invertido).
- **Curadoria de cards:** #104 (CIA — falta critério de repercussão), #70 (sulfonilureia 1ª ger.), #116 (MTX×curva, banca-dependente).
- HAS Pt1 ficou **sem aula-base** — oferecer consolidação narrativa se o usuário quiser.

## Meta de junho
- Meta acumulada: **4.500**. Acumulado atual: **3.739**. Déficit: **761** em **6 dias** (25–30/06) → **~127 q/dia**.

## Próximo (s091)
Fechar a Semana 09: **T12 (Dependência Química + Intoxicações, Rev) → T13 (cluster Pediatria)**. Drenar o FSRS restante (16 atrasados + os cards/andaimes de hoje, que vencem cedo — Glasgow e grade HAS state 0). Aula-base escada COMPLETA antes de cada bloco novo.
