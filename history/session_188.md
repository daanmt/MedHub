# Session 188 -- Raio-X UERJ 2021-2026: as 6 provas mapeadas por tema, reconciliadas com o que ele estudou, e a trilha ate 01/11 virando DADO no banco

**Data:** 2026-09-18 (21:25 -> ~23:05) - **Ferramenta:** Claude Code (Fable 5.1) - **Continuidade:** `session_187.md`
Sessao de **ESTUDO/orquestracao** (pauta do operador), com um corte de engenharia exigido pelo proprio pedido.

## 0. O que ele pediu

*"Sinto que voce deu uma enfase muito grande em MFC."* Conferir o painel, comparar o cronograma de 52 semanas com o de 30, ler no Drive os temas marcados de roxo, levantar as ultimas provas da UERJ num relatorio como o do ENAMED, cruzar com o que ja estudou e entregar *"o cronograma com tarefas e listas de exercicios, tarefas para bater a meta do dia"*. Subagentes Sonnet/Haiku para o simples, Opus para o pesado; achados para o `/ai-eng` auditar depois.

## 1. O que foi medido

- **Provas:** 520 questoes (2021-2022 com 60q, 2023-2026 com 100q), texto dos cadernos oficiais via `pdfplumber`, bloco do cabecalho. Gabarito local 2022/23/24/26; 2025 pos-recurso (anuladas 36, 66, 96) e 2021 por subagente web isolado, conferidos a olho 5/5. 2017-2020 nao estao publicas.
- **Classificacao:** 5 subagentes Sonnet, catalogo fechado de 258 temas (Dashboard EMED + 12 temas MFC-clinica). Lentes: amostra a olho 15/15; vs mapa manual de MFC da s183 81/104 (78%) estrito, ~90% lidas as divergencias; 1 correcao do principal (2025 Q88).
- **Achados de conteudo:** 53% das questoes em tema sem registro de estudo (CIR 65%, MFC 63%, CM 53%, PED 43%, GO 42%). Concentracao: 8 temas = metade do bloco de MFC; 20 na CM. **Tuberculose = tema nº1 (14q, 4 blocos).** 36 temas cobrados >= 2x (113q) nao existem na Reta Final de 30 semanas (REMIT/cicatrizacao 6, vias biliares 5, temas gerais 7, infertilidade, Ca endometrio, RPMO, Kawasaki, infeccoes congenitas, celiaca/FR, aorta/pericardio...). 11 deles nem lista tem no EMED.
- **Drive (F63):** a cor esta na FONTE da celula do xlsx (roxo `9900FF`, rosa `FF00FF`, salmao `FF8080`): 51/52/45 pendentes. O Dashboard nao tem marcacao. Bytes recuperados do transcript / do arquivo persistido pelo harness -- nada passou pelo contexto do principal alem do xlsx de 23KB.
- **52 x 30:** 87 dos 246 temas do extensivo nao aparecem em nenhuma das 352 tarefas da Reta Final.

## 2. O que foi entregue

- 🩻 **Artifact** https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc (`artifacts/uerj-raio-x.html`): veredito, cobertura por bloco, temas por bloco com situacao, 52x30, roxo x UERJ, **trilha dia a dia com 76 links de lista**, estilo da banca, metodo e limites. Painel regenerado na mesma URL (v5).
- **Trilha no banco:** 115 overrides, 46 linhas tiradas da Fase 1, 16 reabertas, 7 custom novas (provas UERJ INTEIRAS no lugar dos recortes do bloco MFC; TB 360; abordagem familiar; condicoes cronicas; 2 cadernos UERJ 2017-2020). Por bloco de prova: CIR 19% · GO 19% · PED 18% · CM 17% · simulados 19% · listas de MFC 8% + 10 sessoes de aula. ~3.300q em 43 dias.
- **Dados novos:** `prevalencia_uerj.json`, `uerj_mapa_questoes_2021-2026.json` (spoiler), `gabaritos_2021-2026.json`, `prioridade_cor_rf.json`, `links_listas.json`, `plano_trilha.json`.
- **Engenharia (spec `trilha-uerj-plano-como-dado`, teste antes do codigo):** `plano.aplicar_trilha` + `indexar_links`; 9 testes; suite 924 -> 933; `auto_check --changed` PASSED; selo verde. Backup `ipub_backup_20260918_224430.db`; `--semear --apply --expect 7`; 16 `--reabrir` declarados e conferidos.

## 3. Ledger (para o `/ai-eng`)

F119 (link nunca conectado, RESOLVIDO) · F120 (estrategia cravada em codigo + `--mover` desfeito pelo re-seed, RESOLVIDO com residuo declarado) · F121 (instrumento media outra prova, RESOLVIDO; fecha o dado do F63) · F122 (extensivo sem 6 blocos da S48, DECLARADO) · F123 (ritmo do boot divide a Fase 2 pelos dias da Fase 1 + sem cota diaria, DECLARADO).

## 4. Custo de subagentes (usage do harness)

| filho | modelo | tokens | min |
|---|---|---|---|
| export do Dashboard | Haiku | 36.248 | 0,5 |
| destilado da reforma | Sonnet | 277.557 | 8,5 |
| UERJ 2021+2022 / 2023 / 2024 / 2025 / 2026 | Sonnet x5 | 1.012.978 | 18-47 |
| web isolado (gabaritos, edital) | Sonnet | 164.373 | 17,6 |
| links das listas | Opus | 249.211 | 49,0 |

**Total 1.740.367 tokens, ~49 min de relogio.** Licoes de brief: (1) caminho `C:/` para Python nativo -- o filho de 2025 perdeu ~30 min com `/c/...`; (2) minuto auto-relatado por filho nao vale (35-40 declarados x 8,5 medidos); (3) export binario do Drive por filho Haiku cai em arquivo do harness e nunca entra no contexto do principal.

## 5. Pendencias

1. Diagnostico UERJ 2023 no sabado 19/09 e recalibragem dos blocos da S2.
2. Ele cria os 2 cadernos UERJ 2017-2020 no banco do EMED (S7).
3. `links_exercicios.json` superado (deslocamento na S15): auto-higiene com grep, nao feita.
4. +7 clausulas orfas (skill/spec novas) no burn-down do 1.10.
5. F122/F123 aguardam triagem do `/ai-eng`; F87, F111/R8 e `TCE.md` seguem gates dele.

## 6. Selo formal (23h20) -- o que fica para RECONCILIAR na s189

O operador encerrou aqui (janela de contexto esgotada) e volta na proxima sessao com o resultado do simulado UERJ 2023.

- **Comunicado ao `/ai-eng`:** destilado <= 3k enviado a sessao `ai-eng-5a` (F119-F123 com remedio por achado + 5 pontos para ele atacar). Sem resposta ate o selo; silencio = GO para seguir, resposta so se ALTERA/NO-GO.
- **Geradores preservados:** `scratch/s188_trilha/` (gitignored, local): `agrega_uerj.py` -> `reconcilia.py` -> `gera_trilha.py [--gravar]` -> `build_relatorio.py`, mais `consolida_uerj.py`, `monta_links.py`, `extrair_links.py` e os insumos (`class_*.jsonl`, `q_*.json`, `links_*.json`). Rodam do proprio diretorio. 🔴 A DERIVACAO da trilha nao esta versionada -- so o JSON resultante; declarado ao `/ai-eng` como divida a julgar.
- **A reconciliar na s189, nesta ordem:** (1) bulk do simulado + `--concluir 893`, com acerto POR BLOCO e racional declarado dos erros; (2) recalibrar a S2 e re-semear; (3) volume e cards feitos fora de sessao (#38, #26, #96; divida FSRS de 103 em 18/09); (4) resposta do `/ai-eng`; (5) cadernos UERJ 2017-2020 que ele cria no EMED.
- **Nao feito, declarado:** `links_exercicios.json` superado continua no repo; +7 clausulas orfas no 1.10; F122 nao re-medido pelo principal; o artifact do relatorio nao foi conferido em navegador (uma passada de leitura do texto renderizado, sem screenshot).
