---
type: session
sessao: 091
data: 2026-06-26
area_foco: Psiquiatria (Dependência Química + Intoxicações) + Pediatria (revisão 4 clusters) + revisão FSRS
---

# Sessão 091 -- Fecha a Semana 09 (T12 + T13) + revisão FSRS + 2 refreshes

## Contexto
Dia épico (atravessou 24-26/06 numa conversa contínua). Boot com reconcile limpo (B1-B4 OK; HANDOFF 31 linhas). Fechada a **Semana 09 inteira** do `Cronograma.pdf` -- T12 e T13 --, intercalando uma sessão pesada de `/revisar` (fila vencida zerada) e 2 refreshes de tema dormente. Acumulado cruzou **32% do marco ENAMED**. **100 questões no dia** (meta diária batida).

## O que foi feito
- **T12 -- Dependência Química + Intoxicações Exógenas (Psiquiatria, Revisão):** duas aulas-base "escada" **descomprimidas e COMPLETAS** (Ato 1 Dep. Química -> Ato 2 Intoxicações), tapando dois **gaps de escopo dos resumos** (drogas perturbadoras; quadro clínico das "outras drogas" das intoxicações). Bloco **51q / 44 (86%)**. 7 erros -> **10 cards (#554-563)** + 2 resumos turbinados.
- **Refreshes dormentes (`/refrescar`):** Hanseníase (review_log #51) + Síndromes Hipertensivas da Gestação/DHEG (review_log #52) -- os dois temas com cards a 70d sem rever. Não tocam o FSRS.
- **`/revisar` -- 29 cards vencidos drenados (fila vencida ZERADA).** Distribuição **11×4 · 8×3 · 4×2 · 6×1** (66% nota ≥3 num lote 100% atrasado). **Leeches históricos assentaram** (#435 vWF, #70 sulfonilureia -- eram nota-1, viraram 4). **Progresso no ponto reincidente** #78 (hiperventilação -> cravou a vasoconstrição).
- **T13 -- Pediatria, Revisão por Questões (4 clusters: Cuidados Neonatais, Cardiopatias, Emergências, Icterícia/Sepse):** refresh de revisão high-yield (Cardiopatias em pointer, já consolidada nos cards). Bloco **49q / 43 (88%)**. 6 erros -> **6 cards (#564-569)** + 2 resumos.
- **Curadoria de cards:** #104 (CIA -- agora com critério de repercussão/Qp:Qs), #116/#118 (ectópica -- discriminador "estágio da investigação"). Regenerados in-place (FSRS preservado).
- **Volume `sessoes_bulk` s091:** Psiquiatria 51/44 + Pediatria 49/43 = **100q / 87 (87%)**.

## Padrões de erro identificados
- **🔴 Eixo do dia (e do bloco inteiro) -- bug nº1 / execução de prova.** Conteúdo sólido (86-88%); o que vazou foi processo:
  - **Ancoragem no dado parcial:** T12 Q3 (etilista+TGO -> "hepatite", ignorou abstinência+CK4000 = **hipofosfatemia**); T13 Q1 (sopro -> "CIV", ignorou **desdobramento fixo de B2** = CIA).
  - **Bug 1c (parar antes de completar a verificação):** T13 Q2 (corpo estranho pontiagudo -> EDA sem reavaliar o RX antigo -- objeto pode ter migrado).
  - **Não-transferência card->caso:** T13 Q5 -- **cravou os cards de T4F na revisão** (estenose pulmonar->hipofluxo) mas na questão de cianose-aos-esforços marcou CIV. Sabe o fato isolado, não aplica ao caso.
  - **🆕 Inversão de direção de marcador (3× na revisão):** TSH/DTG (hipo×**hiper**), VDRL/sífilis (tratada×**reinfecção**), FSH/menopausa (baixo×**alto**) -> **nova memória `feedback_inversao_direcao_marcador`** (faceta do bug nº1; fixar a direção no mecanismo).
  - **Calibração de gravidade (dois sentidos):** T12 Q1 (AUDIT 10 superdimensionado) × Q5 (DT->CAPS subdimensionado); T13 Q4 (cefalohematoma->RM, superdimensionou).
- **Banca-dependente registrado:** T12 Q2 (paracetamol -- "medida inicial" = carvão × NAC); T13 Q5 (estenose pulmonar × "EP isolada acianogênica").

## Artefatos criados/modificados
- **16 cards novos** (#554-563 T12 · #564-569 T13) + **3 curados** (#104/#116/#118).
- **4 resumos turbinados** (Regra de Acúmulo): `Dependência Química.md` (AUDIT, hipofosfatemia, arsenal SAA, DT hospitalar), `Intoxicações Exógenas.md` (paracetamol banca-dependente), `Cardiopatias Congênitas.md` (nuance cianose-aos-esforços), `Cuidados Neonatais.md` (cefalohematoma × bossa × subgaleal).
- **Memória nova:** `feedback_inversao_direcao_marcador`.
- **2 review_log** (dormant_refresh #51 Hanseníase, #52 DHEG).
- Temas novos na taxonomia: "Dependência Química" e "Intoxicações Exógenas" (Psiquiatria).
- Contadores: **340 erros · ~370 cards ativos · 41 andaimes.**

## Decisões / pendências
- **Resumo de ectópica** -- gap recorrente; conteúdo no **PDF `Sangramentos da Primeira Metade`** (`resumos/GO/`, confirmado pelo usuário). Extrair + redigir -> **abertura da s092**.
- **`TCE.md` reescrita** (gold standard, escopo grande -> confirmar).
- 🐛 **`performance.py` metas desatualizadas** (junho 4.500 / dez 17.000 pós-s084).
- Curadoria concluída (#104/#116/#118); resta varrer safra mar/2026.

## Meta de junho
- Meta acumulada: **4.500**. Acumulado atual: **3.839**. Déficit: **661** em **5 dias** (26-30/06) -> **~132 q/dia**.

## Próximo (s092)
Abrir com **FSRS** (16 novos #554-569 + relearning de hoje) -> **resumo de ectópica** (PDF Sangramentos 1ª Metade) -> **Semana 10, Tarefa 1 (Preventiva, Teoria+Exercícios)** com aula-base escada descomprimida. Manter o **ritual anti-vazamento** (conjunto > dado parcial; completar a verificação; transferir o card para o caso; direção do marcador).
