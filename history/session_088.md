---
type: session
sessao: 088
data: 2026-06-23
area_foco: Cirurgia (Cirurgia Infantil Pt 2)
---

# Sessão 088 -- Cirurgia Infantil Pt 2 (T7 da Semana 09)

## Contexto
Primeira sessão guiada pelo **`Cronograma.pdf`** (Estratégia MED, "Reta Final: 30 semanas", na raiz). Identificado que o estudo está na **Semana 09** (13 tarefas; T1-T6 já feitas). O plano "Cardio/IC" do HANDOFF anterior era inferência da sessão prévia, **não** o cronograma -- corrigido. Atacada a **T7 (Cirurgia Infantil Pt 2, Revisão, 43q)**.

## O que foi feito
- **Bloco T7:** 43 questões, 23 acertos (**53%**). Volume em `sessoes_bulk` (s088, Cirurgia).
- **Aula-base de hérnia/abdome neonatal** entregue antes do bloco -- mas **incompleta** (algoritmo do abdome obstrutivo neonatal; cortou apendicite, rasou Meckel/hérnias). O caderno expôs a falha.
- **Análise dos 20 erros em 3 lotes**, cada um com revisão completa do tema antes dos cards:
  - **Lote 1 -- Hérnias (10q):** andaime CPV (`mecanismo`) + #518 régua de conduta + #519 encarcerada×estrangulada + #520 ovário/transiluminação.
  - **Lote 2 -- Intussuscepção (4q):** #522 enema×cirurgia + #523 lactente×neonato.
  - **Lote 3 -- ECN/Meckel/Apendicite (6q):** #524 fatores de risco ECN + #525 pneumatose×pneumoperitônio + #526 Meckel ulceração + #527 apendicite dx clínico.
- **10 itens FSRS** cunhados (1 andaime + 9 cards). Erros 297->306; cards 318->328 (andaimes 35->36).

## Aprendizados
- **Lição de processo:** a aula-base deve cobrir o **escopo inteiro** da tarefa (tópicos do cronograma + índice do resumo); calibrar profundidade, **nunca cortar tema**. Memória `feedback_aula_base_cobertura_escopo`.
- **Padrão dos 20 erros:** ~metade foi **base** (hérnia -- régua de conduta e discriminador encarcerada×estrangulada, errou pros dois lados); ~metade foi **execução** (intussuscepção/ECN/apendicite -- acertou o diagnóstico, não fechou a conduta / não checou o modificador) = **bug nº1** vivo.

## Próximo (s089 -- contexto limpo)
T8 Meningites (Teoria, 24q) + T9 Pólipos/CCR (Teoria, 23q) da Semana 09. Aula-base **escada COMPLETA** do zero (PDFs já em `resumos/`). Commit + push na entrega de T9.
