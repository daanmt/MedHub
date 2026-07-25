# Audit Report: Diagnóstico de Variância e Zona

> Auditado em 2026-07-25 · Spec: `.vibeflow/specs/variancia-e-zona.md`
> Dependência: `ledger-de-habilidades` (audit PASS) ✅

**Verdict: PASS**

## DoD Checklist

- [x] **1. Métrica de variância** — `--metricas` devolve n, média, desvio (`pstdev`), mín/máx, amplitude e coeficiente de variação; `--ultimos N` e `--piso Q` funcionam. Testes: `test_dod1_metricas_estatistica` (compara contra `statistics.pstdev` de série conhecida), `test_dod1_piso_filtra_ruido`, `test_dod1_janela_ultimos`, `test_dod1_serie_curta`.
- [x] **2. Zona de 2 eixos** — `classificar()` é função **pura** (sem db) cobrindo os 4 quadrantes + comportamento nos cortes. Cobertura derivada da grade versionada + semana de conteúdo. Testes: `test_dod2_quatro_quadrantes`, `test_dod2_cortes_nos_limites`, `test_dod2_cobertura_degrada`, e um **teste estrutural** (`test_dod2_cobertura_nao_usa_campo_inflado`) que falha se alguém reintroduzir `questoes_realizadas` como fonte de cobertura.
- [x] **3. Variância independente da zona** — `variancia_alta` é flag separada; `acao_variancia` prescreve simulado em qualquer quadrante. Teste: `test_dod3_variancia_e_sinal_independente` (série dispersa liga, série estável desliga).
- [x] **4. Cadência de simulado** — `--simulado-check` responde janela de 7d e sinaliza débito. Simulado **não entra** na série de blocos (série própria). Testes: `test_dod4_simulado_check`, `test_dod4_simulado_nao_entra_na_serie`.
- [x] **5. Integração no plano do dia** — `day_plan.py::_diagnostico()` com try/except por sinal; bloco 🔬 renderizado com zona, prescrição, ação de variância, débito de simulado e até 3 habilidades reincidentes. Verificado no `day_plan` real.
- [x] **6. Craftsmanship gate** — `auto_check --changed` verde. `import sqlite3` só em `db.py` + CLI standalone. Paridade command↔skill OK. `variancia.py` é **read-only** (zero `INSERT`/`UPDATE`/`DELETE`).

## Testes

| Suíte | Resultado |
|---|---|
| `test_variancia.py` (nova) | PASS |
| `test_habilidades.py` | PASS |
| `test_orquestrador.py` | PASS |
| `test_revisao_calibrada.py` | PASS |
| `test_day_plan_telemetria.py` | PASS |
| `test_aderencia.py` | 11 passed |

## Critical Gate

**Clean.** Único `UPDATE` no diff está em `tools/test_variancia.py:190`, contra `sessoes_bulk` de um **banco temporário de fixture** (`tempfile.mkstemp`, removido no `finally`). Não é operação de produção — informativo, não bloqueante. `variancia.py` não emite nenhuma escrita.

## Defeito de dado encontrado (importante)

🔴 **`taxonomia_cronograma.questoes_realizadas` está inflado ~3,7x.** Soma **19.597** contra **5.232** reais em `sessoes_bulk`. A primeira versão da cobertura usava esse campo e classificava o usuário como **DIRECIONAMENTO com 89,5% de cobertura** — falso, com 4.263 questões de grade pela frente e 4 semanas de atraso.

Trocada a fonte para a grade versionada + semana de conteúdo: cobertura real **43,0%** (5.826q restantes de 10.218), zona **COBERTURA**. Um teste estrutural agora impede a regressão. **O campo inflado segue no banco e não foi corrigido** — está fora do escopo deste spec; registrado como pendência.

## Diagnóstico produzido (estado real em 25/07)

- Série: **80 blocos** (>= 15q) · média **77,6%** · **desvio 12,0 pp** · amplitude 73,7 pp (26,3 a 100,0)
- **Zona COBERTURA** — desempenho alto, cobertura baixa (43,0% da grade). Prescrição: **avançar a grade**, não trocar cobertura por refinamento.
- 🔴 **Variância alta** — prescreve simulado independentemente da zona.
- ⚠️ Simulado em débito (último em 28/06; política s126 = 1/semana).

## Pattern Compliance

- [x] **db-access-layer** — `sqlite3` só em `db.py` + CLI standalone; leitura nova (`get_serie_blocos`) retorna DataFrame.
- [x] **Degradação graciosa** — `_diagnostico()` isola cada sinal em try/except, espelhando `_cronograma_hoje`. Sinal ausente vira zona "indefinida" declarada, nunca número inventado.
- [x] **Assinatura canônica em UMA skill** — `variancia.py` documentado só em `/performance`.

## Ajustes de contrato aplicados na mesma passada

Fora do DoD deste spec, mas parte do pedido do usuário ("o agente gerenciador ter mais recursos"):

1. **`AGENTE.md §1.2` — gatilho da aula-base vira HÍBRIDO POR DIFICULDADE** (decisão do usuário): tema-zero ou D8+ mantém aula-base completa; D5 ou menor vai direto às questões e a aula entra depois, mirando o buraco. Muda o *gatilho*, não a *profundidade* — a Cláusula 10 (cobertura = piso fixo) segue intacta.
2. **`/analisar-questao §11` — taxonomia de questão + orçamento de correção**: direta (1 aprendizado, não reler resolução) · fluxograma (identificar o NÓ que quebrou) · raciocínio (análise cheia). O tempo de correção é finito e gastá-lo uniformemente derruba o volume.
3. **Enum de veredito ganha `desatencao`** (5 estados). Separar desatenção de erro importa porque o tratamento é oposto: desatenção pede ritual de execução, erro pede conteúdo.

## Pendências

- `taxonomia_cronograma.questoes_realizadas` inflado — investigar origem (provável dupla contagem em import legado). Não afeta metas (que leem `sessoes_bulk`), mas afeta qualquer feature que confie nele.
- Ponderação por incidência / regra 90-50 (vídeo 3): o proxy existe (repetição de tema na grade: Asma 5x, Imunizações 4x) e não foi implementado — spec próprio.
- Vereditos do ledger seguem majoritariamente `indefinido` até a curadoria incremental avançar.
