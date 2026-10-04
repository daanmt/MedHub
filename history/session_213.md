# Session 213 -- Gabarito pós-recurso da UERJ 2021, Autópsia no hub, dossiê v2, rota no Painel, aula REMIT

**Data:** 2026-10-03 (sábado, 23h40) -> 2026-10-04 (domingo, madrugada) - **Ferramenta:** Claude Code (Fable 5.1 como orquestrador; 25 subagentes Opus + 1 Sonnet) - **Continuidade:** `session_212.md`

---

## Pedido

Ele terminou o simulado UERJ 2021 no hub: *"desconfio que o gabarito está incorreto. A pauta envolve essa e outras frentes. Portanto, utilize subagents opus 5.5 (medium effort) para lhe ajudar."* No meio do turno: *"Mantenha essa sessão principal como orquestradora, enquanto você terceiriza o gasto de contexto para os subagents opus/sonnet. utilize os seus loops conhecidos para lhe auxiliar."* A pauta era a do fecho da s212: Painel (rota), dossiê (ampliar + padrões de erro dele), Autópsia da UERJ 2021 dentro do hub.

## Feito

1. **Gabarito da UERJ 2021: era o PRELIMINAR.** O JSON trazia desde 18/09 "preliminar x definitivo NAO VERIFICADO". Três lentes: (a) subagente isolado achou o pós-recurso oficial do Cepuerj (PDF de 21/01/2021; o espelho do Estratégia é byte a byte o preliminar de 06/12/2020); (b) releitura minha do PDF por coordenada e cor (R18 = "ANULADA" e R55/R56 = "D para C"/"C para B" em vermelho); (c) resolução cega das 60 por subagente sem gabarito (54/60 de concordância com o gravado; divergências de confiança alta em Q8, Q55, Q56). Resultado: **Q18 ANULADA, Q55 D -> C, Q56 C -> B**; as outras 57 iguais. `gabaritos_2021-2026.json` corrigido (fonte + observação), golden de `test_prova_pdf.py` (59 questões, [18]), `emed_banco.py --ingerir --apply --expect 2`, 4 docs do hub (`questoes` e `respostas` de 55 e 56). Com isto os 6 anos estão conferidos contra pós-recurso (fecha o resto do achado da s209).
2. **Registro do simulado:** `--registrar --apply --expect 60` -> **36/60** (CM 7 · CIR 7 · GO 6 · PED 4 · MFC 12; sólidas 16/24, dúvidas 18/23, chutes 2/13); `sessoes_bulk.id=134` (sessão 213, área Simulado, data 03/10); `plano.py --concluir 1793`.
3. **Autópsia UERJ 2021 no hub** (`artifacts/aula-autopsia-uerj-2021.html`, `tipo: analise`): 5 subagentes Opus, um por bloco, analisaram 44 questões (24 erradas + 20 certas não-sólidas, incluída a anulada) com fonte aberta, veredito e cards candidatos; um sexto escreveu o montador (`tmp/uerj2021/build_autopsia.py`, página recolhida por questão, filtros, busca, conferida a 390 px). Contestáveis: **Q37** (banca chamou de "obesidade grau I" um Z entre +2 e +3 aos 4 anos; SBP 2019/OMS = sobrepeso; o racional dele estava certo) e **Q8** (ceftriaxone da banca x rifampicina do Guia de Vigilância do MS). Gabarito mantido onde ele contestou: Q30, Q39, Q44, Q47. Datadas: Q33 (colo), Q42 (ROP). O `/analisar-questao` §3.3 passou a dizer que a Autópsia é arquivo do hub (lápide do "Artifact HTML avulso").
4. **Persistência:** subagente montou o lote e rodou o `--dry-run`; eu li os 30 cards (frente e resposta) e gravei: **21 erros + 30 cards** (`--errors-file`, cada erro com `sessao: 134` e `emed: t1793_<n>`; Q37 `banca-divergente`, sem card) e **19 incertezas** no ledger (`habilidades.py --add ... --veredito incerteza`). Fora, esperando a resposta dele: **Q30, Q44, Q47** (`tmp/uerj2021/lote_pendente.json`). Temas novos: Cirurgia | Câncer Gástrico, Ginecologia | Fisiologia do Ciclo Menstrual, Obstetrícia | Gemelaridade, Pediatria | Retinopatia da Prematuridade.
5. **Dossiê UERJ v2** (`artifacts/aula-dossie-uerj.html`, 22 KB -> 111 KB, 12 seções): 5 blocos reescritos em camadas (1 Opus por bloco), 8 seções transversais (obsessões, armadilhas, âncoras, atualizações, custo, geografia, o que não cai), a seção **"Onde você perde ponto nesta prova"** (2021 + 2023, 155 válidas, 64 erros: 42 sem base, 26 deles em CIR e GO; 22 erradas sólidas; corte numérico sólido 6/11; hipótese "diretriz antiga" não sustentada) e montagem final. **110 afirmações clínicas auditadas** por 4 subagentes: 89 confirmadas, 14 corrigidas, 4 banca-dependentes, 1 datada, 2 não verificáveis (1 retirada: revisão do choque no ATLS 11, sem fonte primária). Contagens recalculadas com a Q18 anulada: **502 válidas** (CIR 99). Corpus e jsonl da dissecação corrigidos para o gabarito oficial.
6. **Painel: rota S4-S7** (pedido dele no fecho da s212): varredura read-only (plano com `arquivo:linha`) -> implementação por subagente -> auditoria no padrão vibeflow: **PASS** (10/10 do DoD, Critical Gate limpo; `.vibeflow/audits/painel-rota-s213-audit.md`). `plano.panorama()["rota"]`; `painel.py` com `_tarefa`/`_html_tarefa`/`_html_rota` (semana futura em `<details>` fechado, mesmo `<li>` da semana corrente); lista que está no hub abre a aba Listas e o link do EMED some (painel e quadro da aba Aulas); aula que prepara a tarefa aparece; listener de `toggle` re-mede o iframe. Achados do revisor aplicados por mim: R1 (teste das duas réguas também trava a semana corrente) e R2 (semana corrente vazia não desenha "0 tarefa(s)" nem lista vazia). Contagem da rota = panorama: S4 29/789, S5 31/836, S6 23/707, S7 9/439.
7. **Aula-base #530 REMIT e Cicatrização** (`artifacts/aula-remit-cicatrizacao.html`, 42 KB, `tarefa_id: 530`): 2 atos em degraus, 18 gatilhos, ancorada nos dois PDFs do curso. Divergências do PDF anotadas pelo autor (insulina na fase flow, dose de vitamina C, prostaglandinas, área doadora, queloide, duração da fase ebb): o duvidoso ficou fora ou rotulado "segundo o curso" (`tmp/aulas_s213/remit_afirmacoes.md`, 37 afirmações; 4 complementos de livro-texto sem conferência na web).
8. **Hub Version 65:** tique rodado por subagente Sonnet até a véspera (decisão `mesmo_lote`, build `--check: OK`, 4 arquivos novos/alterados, 12 mantidos, diferença contra a v64 só no esperado, leitura integral dos 4 arquivos com atestado). Eu conferi o diff por script contra a página viva, li os trechos e publiquei; `hub.py --confirmar` rodado. `core/hub_quadro.json` ganhou `autopsia-uerj-2021` e `remit-cicatrizacao`.

## Subagentes (custo do `usage` do harness; em quem foi retomado, o último número)

| Filho | Modelo | Tokens | Chamadas | Min |
|---|---|---|---|---|
| Gabarito oficial (web isolada) | Opus | 116.763 | 28 | 4,0 |
| Resolução cega das 60 | Opus | 93.062 | 5 | 2,5 |
| Varredura do Painel | Opus | 167.616 | 42 | 7,1 |
| Dossiê bloco CM / CIR / GO / PED / MFC | Opus | 109.699 / 117.664 / 111.122 / 116.623 / 133.910 | 14 / 18 / 17 / 19 / 20 | 3,2 / 3,5 / 3,2 / 3,8 / 4,8 |
| Autópsia CM / CIR / GO / PED / MFC | Opus | 147.331 / 133.784 / 171.547 / 202.475 / 119.969 | 34 / 41 / 52 / 53 / 31 | 8,3 / 5,9 / 8,8 / 10,9 / 5,1 |
| Implementação do Painel | Opus | 226.924 | 112 | 24,7 |
| Dossiê transversais | Opus | 248.319 | 35 | 10,4 |
| Evidência A / B / T1 / T2 | Opus | 82.091 / 82.066 / 112.360 / 161.204 | 35 / 31 / 21 / 65 | 5,4 / 5,2 / 2,3 / 9,6 |
| Montador da página da Autópsia | Opus | 126.845 | 39 | 6,1 |
| Lote de erros (dry-run) | Opus | 114.337 | 27 | 2,4 |
| Padrões de erro dele | Opus | 120.053 | 21 | 4,8 |
| Aula REMIT | Opus | 239.344 | 32 | 8,2 |
| Montagem do dossiê | Opus | 246.153 | 48 | 9,0 |
| Auditoria do Painel (vibeflow) | Opus | 93.562 | 22 | 8,9 |
| Tique do hub | Sonnet | 240.097 | 24 | 7,4 |

Total aproximado: 3,8 milhões de tokens em 26 subagentes. Re-medido por mim antes de usar: o PDF do pós-recurso (coordenada e cor), o diff cega x gabarito, a contagem `contagens.py`, o `--dry-run` do lote, a suíte e o diff da página viva.

## Selos

- `banco-emed: t1793 ingerida 2 (correção de gabarito) · registrada 60 · erros analisados 44 (21 gravados, 3 pendentes de racional)`
- Suíte: **1361** (`python -X utf8 -m pytest tools/ -q`; era 1349).
- Hub: Version 65 (id 1791085334-5a25).

## Fricções (candidatas a achado; triagem pelo rito do ledger na próxima sessão de engenharia)

- O tique em segundo plano teve o 1o comando negado pelo classificador (encadeava `rm -rf` de pasta de rascunho com cópia e leitura). Não contornei: o "antes" do diff passou a ser a página viva salva pela ferramenta de artifact.
- `habilidades.py --add` com par (área, tema) inexistente grava `tema_id NULL` sem avisar (visto pelo subagente do lote; a Q32 foi para `Obstetrícia | Líquido Amniótico`).
- O auditor `evidence-researcher` não grava arquivo (contrato read-only): devolveu 8 mil caracteres no canal; para lote, usar `general-purpose` com o contrato de evidência.
- O gabarito de 2021 ficou 16 dias rotulado "não verificado" e só foi conferido porque ele desconfiou: a s209 conferiu 4 anos e deixou este.
- O racional dele da Q33 trazia um palavrão; tirei a interjeição da citação exibida na página (o banco guarda o original). Repo público.

## Pendências

- **Dele:** responder em 1 linha Q30, Q44 e Q47 (fecham os 3 erros restantes) e, se quiser, as 19 perguntas das certas não-sólidas (bloco "Perguntas para você" da Autópsia).
- **Resumos:** as armadilhas das 24 erradas ainda NÃO foram somadas aos resumos (Siamese Twins); `[SEM-LASTRO]` em Glomerulopatias e nos temas novos.
- **Painel:** D4-4 (placar das listas e das provas UERJ no bloco de performance, esforço M) e os achados baixos R3-R5 do audit.
- **Aulas da S4 que faltam:** #1797 Tuberculose 360, #5424 imagem obstétrica, #881 rastreamento, #882 saúde mental na APS, #5425 rodapés; sessões sem lista #768, #590, #367.
- Recalibrar peso por bloco depois da UERJ 2022 (3a prova), na S4.
- Herdadas da s212 e anteriores: ver HANDOFF.
