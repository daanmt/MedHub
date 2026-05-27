# Session 021 — FSRS Optimizer e Algoritmos de Machine Learning
**Data:** 2026-03-14
**Ferramenta:** Antigravity
**Continuidade:** Sessão 020

---

## O que foi feito
- Consumo e interpretação da documentação core do repositório público `fsrs4anki` a pedido do Mestre, especificamente a sub-wiki `The mechanism of optimization`.
- Divisão arquitetural da solução no roadmap do IPUB em dois braços do FSRS: o **Scheduler** (sistema de regras curtas para a sessão de revisão diária atualizando estabilidade E e dificuldade D) e o **Optimizer** (pipeline em PyTorch rodando MLE - *Maximum Likelihood Estimation* e BPTT - *Backpropagation Through Time*).
- Validação da tabela `fsrs_revlog` existente no nosso `ipub.db`. Ela está estruturalmente compatível (temos history e delta_t previstos) para extrairmos nossos próprios datasets temporais quando chegarmos à marca necessária de revisões para treinar a regressão do modelo.

## Artefatos criados/modificados
- `roadmap.md` (Update do modelo Otimizador)
- `ESTADO.md`
- `HANDOFF.md`
- `history/session_021.md`

## Decisões tomadas
- O Otimizador não rodará em tempo real a cada click no Streamlit (esmagaria nosso processamento e geraria over-fitting). O Agendador cuidará do real-time guiado pelos parâmetros consolidados, enquanto o Otimizador será um job periódico lendo os arrays de `fsrs_revlog`.

## Próximos passos (se houver)
- Fazer a migração massiva do velho `caderno_erros.md` para o DB. Sem as 67 entradas pregressas corremos o risco de adiar violentamente a nossa massa crítica de "primeiras 1000 reviews" que otimizam o modelo nativamente.
