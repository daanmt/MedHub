## Audit Report: trilha-autoridade-unica

> s189 (madrugada 18 -> 19/09/2026). Auditor: o proprio MedHub, loop do vibeflow (AGENTE.md §10.6:
> implement E audit sao do MedHub; o `/ai-eng` decide nas bifurcacoes). Spec:
> `.vibeflow/specs/trilha-autoridade-unica.md`. Diff auditado: `ec61a1b..521c885` (6 commits,
> 33 arquivos) + o status da spec na arvore.

**Verdict: PASS**

Suite: `python -X utf8 -m pytest -q` -> **954 passed** (baseline 933 no inicio da sessao; +21).
Harness: `python tools/auto_check.py --changed` -> PASSED (exit 0). Selo: `python tools/selo.py` ->
0 item sem terminal, 0 discordancia. Checks ao vivo no banco real (19/09, 01h): `tools/trilha.py`
-> `IDENTICO (+0 -0 ~0)`, propriedades OK; `plano.py --semear --dry-run` -> 0 nova, **0 mudaria**.

### DoD Checklist
- [x] 1 ritmo da Fase 1 -- `day_plan._cronograma_hoje` soma so as semanas 1-7; alvo vencido -> `None`.
  Evidencia: `test_ritmo_da_fase1_nao_conta_fase2_nem_reserva` (Fase 2 e reserva NO BANCO); real:
  273,3 -> 74,8 em 18/09 e 76,6 em 19/09 (3.293q / 43d).
- [x] 2 cota do dia -- `cota_do_dia` PURA, semana de calendario, atraso declarado, `None` fora do
  calendario. Evidencia: `test_cota_do_dia_divide_o_restante_da_semana_pelos_dias`; real ~81q/dia.
- [x] 3 reguas declaradas -- Volume = "marco de volume"; plano = "cota do dia" + "ritmo da Fase 1";
  `2o ciclo 12k` virou `Ciclo 2026 (12500 ate 31/12)`; recomendador le a Fase 1 ("necessario 76.6").
  Evidencia: `test_render_declara_o_que_cada_regua_mede`, `test_cota_cabe_no_corte_do_boot`.
- [x] 4 tres camadas de DADO -- `core/cronograma/trilha/parametros.json` + `custom.json` ->
  `tools/trilha.py` -> `plano_trilha.json` com `gerado_por` e `_doc` "NAO EDITAR A MAO".
- [x] 5 entrada fixada -- `core/cronograma/trilha/entrada/` (plano, cobertura, catalogo) + mapa UERJ
  versionado, identico ao do scratch (520 linhas, mesma ordem, 0 divergencia).
- [x] 6 GOLDEN -- delta ZERO. Golden de partida (scratch re-rodado em copia fora do repo) = 115
  overrides; gerador do repo = os mesmos 115, na mesma ordem; diff do git no arquivo: so
  `_doc`/`gerado_por`/`versao`. Evidencia: `test_golden_o_arquivo_gravado_e_a_saida_do_gerador`.
- [x] 7 PROPRIEDADE -- `verificar_propriedades` (a mesma do `--gravar`) sobre o gravado; cada
  invariante derruba a sua adulteracao. Evidencia: `test_propriedades_da_trilha_gravada`,
  `test_propriedade_pega_saida_adulterada`, `test_gravar_recusa_saida_que_viola_propriedade`.
- [x] 8 so o re-executado entra -- agrega/reconcilia/gera/custom portados; relatorio, selo,
  veredito, extracao de links e classificacao por edicao ficam no scratch (gitignored).
- [x] 9 reserva -- `plano.py --reserva` + `docs/RESERVA-FASE1.md`. Evidencia:
  `test_reserva_ordena_por_peso_uerj_avisa_faixa_alta_e_nomeia_o_nao_casado`, `test_cli_reserva_pelo_main`.
  Desvio JUSTIFICADO: o WARN dispara so para faixa alta SEM nenhuma linha na fila cobrindo o tema
  (13 de 22) -- a spec pedia "WARN para faixa alta"; as 22 seguem listadas em duas secoes.
- [x] 10 guard do `--mover` -- recusa (exit 2) linha que esta ou iria para a Fase 1, com a entrada
  da camada manual. Evidencia: `test_mover_recusa_linha_da_fase1_com_a_trilha_ativa`,
  `test_cli_mover_le_a_trilha_do_disco`; banco real: tarefa 38 recusada.
- [x] 11 `links_exercicios.json` removido -- 0 consumidores `.py`; lapides nas mencoes.
- [x] 12 estado explicito -- 577 url / 482 `sem_link_no_pdf` / 28 `varios_links_no_pdf`; faltando 0.
  Evidencia: `test_links_listas_da_estado_explicito_a_toda_tarefa`.
- [x] 13 clausulas + catraca -- 134 -> 127 (51,0%); `BASE_ORFAS` + `catraca` + WARN
  `CLAUSULA_ORFA_SUBIU`. Evidencia: `test_catraca_de_orfas_so_avisa_quando_a_contagem_sobe`.
- [x] 14 custo pelo harness -- clausula 10 do F93 (`analisar-questao.md`) + AGENTE §1.1.
- [x] Toda fatia -- commit proprio e verde: `7f311fd`+`f12c4ef` (1), `342a86e` (3), `83b3e50` (2),
  `390ee43` (4), `521c885` (5); pre-commit hook rodou a suite completa em cada um.

### Pattern Compliance
- [x] db-access-layer -- nenhum `import sqlite3` novo; `plano.py` escreve/le so por `app/utils/db.py`
  (`plano_listar`, `plano_obter`, `plano_mover`); `trilha.py` nao toca banco (so `db.bloco_de`, pura).
- [x] warn-first-check -- a catraca mora em modulo proprio (`clausulas_check.catraca`, pura, testada);
  o `auto_check` so orquestra; nasce WARN. DESVIO LEVE (confianca alta, severidade baixa): o bloco
  16c nao instrumenta o ledger-of-self (`_ledger_record`), nem antes nem agora -- a catraca herdou
  a convencao local do bloco, nao a do pattern.
- [x] Agent norms -- assinatura canonica dos flags novos (`trilha.py --gravar/--tabela`,
  `plano.py --reserva`) em `/engenharia-cli`; `sync_skills --check` exit 0 em todo commit; D5 PASSED.
- [x] Tests -- `tools/test_trilha.py` registrado em `pytest.ini` (contagem coletada 938 -> 948
  conferida; o pitfall da whitelist fixa nao se repetiu).

### Convention Violations (if any)
- `.vibeflow/conventions.md` (§Git) prescreve `sessao NNN:` / `chore:`; a pratica do repo ha dezenas
  de sessoes e `tipo(sNNN): ...`, que os commits desta sessao seguem. Doc de convencao desatualizado,
  nao violacao desta spec (confianca alta, severidade baixa).

### Critical Gate
Clean -- no destructive operations detected. Unica ocorrencia do scan: `sha256` removido/adicionado
em `core/cronograma/links_listas.json` -- metadado de checksum do PDF-fonte re-serializado com o
MESMO valor (o arquivo foi regravado com `indent=1`); arquivo de dado, fora do alvo de DAT103.

### Achados registrados (todos, com confianca e severidade)
1. **F125** (confianca alta, severidade ALTA, CORRIGIDO): loop infinito herdado da s188 no
   agendamento do gerador -- travaria a recalibracao pos-prova. Regressao com prazo.
2. Divisor da Fase 1 com DUAS fontes de data (confianca alta, severidade baixa, DECLARADO): o ritmo
   divide por `FIM_CONTEUDO_ALVO` (01/11, travado por teste desde a s159) e a cota le o calendario
   da trilha (fim 31/10). Diferenca de 1 dia no fim da fase; mesma fase, fontes diferentes.
3. `plano_custom.json` carrega `semana_plano`/`ordem` das tarefas custom, mas 28 de 29 tem override
   na trilha (confianca alta, severidade media, DECLARADO): editar a semana la nao tem efeito -- mais
   uma instancia de "duas autoridades", fora do DoD desta spec.
4. Diff ruidoso do `links_listas.json` (+6615/-3496) por re-serializacao (confianca alta, severidade
   baixa): conteudo preservado (381 links aplicados; re-seed 0 mudanca).
5. O golden prova "arquivo == saida do gerador"; a prova de que a MUDANCA DE CASA nao alterou a
   trilha e a medicao unica de partida (registrada no ledger F124 e na spec) -- apos uma
   recalibracao legitima, os dois mudam juntos (confianca alta, severidade baixa, por desenho).
6. Fatia 6 (regra de recalibracao como dado + gold set de MFC) NAO feita -- opcional por decisao do
   `/ai-eng`; a regra estatistica vai como texto no HANDOFF (confianca alta, severidade media).

### Next steps
Ready to ship. Pendente fora do DoD: fechamento da sessao (HANDOFF, session_189, INDEX, memoria),
destilado ao `/ai-eng`, e a fatia 6 no backlog.

12 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
