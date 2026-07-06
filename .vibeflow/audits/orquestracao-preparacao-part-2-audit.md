# Audit Report: Orquestracao da Preparacao -- Part 2 (Recomendador do dia)

> Auditado em 2026-07-06. Spec: `.vibeflow/specs/orquestracao-preparacao-part-2.md`.
> Dependencia part-1: audit PASS confirmado. Testes rodados de forma independente.

**Verdict: PASS**

### DoD Checklist

- [x] 1. Secao "Recomendacao do dia" com mix + quantidades + justificativa >=3 sinais -- `recomendar_dia()` + render; `test_mix_normal` (fixtures deterministicas); smoke real: 3 blocos com quantidades e motivos.
- [x] 2. Projecao (ritmo real 14d, dias p/ fechar, folga, necessario) -- `test_mix_normal` (folga -10) e `test_folga_positiva_limita_pelo_necessario` (folga +52); smoke real: "ritmo real 65.6q/dia -> grade fecha em ~96d (folga -27d) - necessario 91.0q/dia".
- [x] 3. `--tempo`/`--energia` mudam a saida conforme contrato; defaults declarados; condicao registrada -- `test_tempo_curto_reduz_capacidade`, `test_energia_baixa_sem_folga_nao_descansa`; render mostra `[defaults: 4h/media]` vs `[dia: 1.5h/baixa]`; `registrar_condicao_dia` grava em preparacao_estado (upsert testado na part-1).
- [x] 4. Descanso e simulado como saidas reais -- `test_descanso_energia_baixa_com_folga` (R2: sem tema novo, FSRS leve capado) e `test_simulado_semana_multipla` (R3); negativo coberto (energia baixa SEM folga nao descansa).
- [x] 5. Cards frescos do tema-alvo -> mini-drill primeiro -- `test_frescos_viram_primeiro_bloco`; `db.get_fresh_error_cards` testada com db temp (filtro tema + janela; frescor via due de state-0, contrato fixado por teste).
- [x] 6. Norma no contrato com parametros nomeados == constantes do CLI + AGENTE aponta -- `core/contracts/orquestracao-contract.md` (R1-R5 + tabela); `test_paridade_contrato_cli` verifica cada parametro da tabela contra o modulo; AGENTE 2 passo 4 estendido.
- [x] 7. Craftsmanship -- `recomendar_dia` e funcao PURA (zero db/arquivo; testavel por fixtures); a secao ADICIONA ao render (chaves antigas intactas, `test_render_inclui_recomendacao`); pytest 24 passed; standalone verde; ASCII no contrato/teste.

### Pattern Compliance

- [x] `db-access-layer.md` -- get_ritmo_real/get_fresh_error_cards/registrar_condicao_dia em db.py (DataFrame/dicts, close disciplinado).
- [x] Precedente F4 (norma no contrato + mecanica no CLI com constantes nomeadas) -- replicado; paridade agora TESTADA (endurecimento vs F4, que nao tinha teste de paridade).
- [x] Precedente infer_nota (funcao pura + fixtures) -- replicado em recomendar_dia.

### Critical Gate

Clean -- diff aditivo; sem operacoes destrutivas, secrets ou remocao de protecoes.

### Notas

- Comportamento observado com dados reais no smoke: recomendador expos deficit projetado de 27 dias (ritmo real 65.6 vs necessario 91.0) -- o tipo de sinal que motivou o PRD (s109: "nao consegui fazer as 120q planejadas").
- Energia baixa + grade atrasada NAO gera descanso (R2 exige folga >= limiar) -- correto por norma; o caminho de descanso fica reservado a quem tem folga projetada.
- Gate anti-decorativo declarado no contrato (3 sessoes sem alterar decisao real -> revisar/remover).

**Ready to ship.** Proximo: part-3 (pre-bloco + detector de reincidencia).
