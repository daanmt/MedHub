---
type: session
sessao: 089
data: 2026-06-23
area_foco: Infectologia (Meningites -- T8 da Semana 09)
---

# Sessão 089 -- Meningites (T8 da Semana 09)

## Contexto
Continuação do dia 23/06 (mesma diária da s088, contexto limpo). Atacada a **T8 (Meningites, Teoria, 24q)** do `Cronograma.pdf`. Tema novo, sem resumo `.md` -- substrato via PDF do EMED (`resumos/Clínica Médica/Infectologia/1. Meningites (Infecções do Sistema Nervoso Central).pdf`, 37 págs, extraído). **T9 (Pólipos/CCR) não entregue** -- decisão do usuário de encerrar o dia.

## O que foi feito
- **Aula-base "escada de degraus" COMPLETA** (lição da s088 aplicada): cobriu o escopo inteiro do EMED -- anatomia/barreira hematoliquórica -> LCR (régua dos 5 números) -> clínica/PL (TC antes da PL) -> etiologia por idade -> conduta empírica + 3 modificadores (Listeria/dexametasona/Harrison) -> personagens bacterianos -> virais/herpética -> TB/cripto/neurocisticercose/abscesso -> precaução/profilaxia/notificação. **Nenhum tema cortado.**
- **Bloco T8:** 24 questões, **18 acertos (75%)**. Volume em `sessoes_bulk` (s089, Infecto).
- **6 erros analisados:**
  - **2 eram raciocínio correto** (não penalizados): **Q4** (gabarito oficial ruim -- banca-dependente; o usuário marcou rifampicina/C, clinicamente correto, o próprio Estratégia defende C contra o oficial D) e **Q6** (acertou o esquema de neuroTB pediátrico, errou só a dose por peso: ≤20 kg = 2 comprimidos, não 3).
  - **5 erros reais -> 5 cards (#528-532):** TB×Hib no LCR (#528), hidrocefalia obstrutiva pós-meningite -> derivação (#529), profilaxia = rifampicina 1ª escolha (#530), LCR viral com glicose normal (#531), esquema neuroTB pediátrico (#532).
  - **1 card conceitual** do Q4 via `insert_card_base` (andaime, sem erro de origem): profilaxia do próprio paciente (quem não usou ceftriaxona precisa) + armadilha banca-dependente.

## Aprendizados
- **Padrão metacognitivo central: leitura do LCR.** 2 dos 5 erros reais (Q1 TB, Q5 viral) são o **mesmo bug** -- ler o LCR por um **dado parcial** (presença de neutrófilos / contexto clínico) em vez do **conjunto** (predomínio + glicose + proteína). É o bug nº1/ancoragem aplicado a exame complementar. Os cards drilam "ler o LCR como gestalt".
- **Bug nº1 (não fechar a conduta)** reapareceu em Q2 (sabia que não era PL, mas não chegou na derivação) e Q3 (validou "contatos próximos" sem conferir o fármaco embutido -- cipro errado vs rifampicina).
- **Aula-base completa funcionou:** 75% num tema novo de Teoria, sem erro de fisiopatologia grosseiro; os erros foram de discriminação fina e execução, não de base ausente. Contraste com a s088 (53%, aula incompleta) -- confirma [[feedback_aula_base_cobertura_escopo]].

## Achados de sistema
- 🐛 **`performance.py` com o ramp de metas DESATUALIZADO** (pré-reconcile s084): reporta meta de junho = **8.000** e final = **23.000**. Os valores corretos (ESTADO/Dashboard EMED pós-s084) são **junho 4.500, dez 17.000**. Corrigir a config do script.

## Meta de junho (pedido do usuário)
- Meta acumulada de fim de junho: **4.500**. Acumulado atual: **3.663**. Déficit: **837** em **7 dias** (24-30/06) -> **~120 questões/dia**. (No ritmo ENAMED de ~102/dia, fecharia em ~4.377 -- a 123 da meta.)

## Próximo (s090)
T9 Pólipos/CCR (Teoria, 23q) + seguir a Semana 09 (T10 TCE+Demências Rev, T11 HAS Pt1…). Drenar a fila FSRS (vencidos + os 6 novos de Meningites). Aula-base escada COMPLETA antes de cada bloco.
