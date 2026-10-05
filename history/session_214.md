# Session 214 -- Absorver os feedbacks do hub: assinar conclui, listas S4/S5 pela API, 4 aulas da S4, 6 correções clínicas, seções recolhíveis e grifo no leitor

**Data:** 2026-10-04 (domingo, ~18h -> madrugada de 05/10) - **Ferramenta:** Claude Code (Opus 5.5 como orquestrador; 12 subagentes Opus) - **Continuidade:** `session_213.md`

---

## Pedido

Ele estava matando as Revisões Direcionadas no hub e trouxe os feedbacks (tema já marcado para a s214 no HANDOFF): *"os blocos das aulas também poderiam ter o mecanismo de selecionar e destacar, bem como poderia permitir ao aluno que editasse o texto/formatação, como no Notion [...] ampliarmos ele para um bloco 'Teoria', que tivesse tanto essas aulas/resumos dos temas, quanto as revisões direcionadas apontassem para esses resumos, mais ou menos como o obsidian faz [...] mesmo assinando as listas, elas não são 'resolvidas', tendo que clicar no concluir do lado de fora [...] Desconfio se o dashboard está de fato syncado"*. Depois: *"buscar as listas que ainda não foram cunhadas, avaliar os resumos existentes [...] subí-los nesse novo bloco de teoria (qual o limite de um artifact?) [...] utilizar a api do EMED para buscar as listas que ainda não existem, bem como analisar as apostilas sobre os temas do cronograma [...] que não possuem aulas/listas"*. No fim: *"Seria bacana poder recolher as semanas, deixando apenas a que eu quisesse (até os próprios blocos, como revisões direcionadas) [...] após, pode encerrar formalmente, sintetizando tudo o que você fez e já definindo insights e o plano da semana 4."*

## Feito

1. **Diagnóstico do "sync":** o Painel é uma foto tirada no publish; o backend estava MANUAL desde 24/09 (decisão dele na s195). Medido: `--precisa-publicar` = sim (painel e quadro mudados) e o lote vivo `2026-10-02a` era de dois dias antes, com 0 notas. Tique `/loop` religado a pedido dele (30 min, `7,37 * * * *`, job `1f6493a3`) e removido no fim, também a pedido dele.
2. **Assinar = concluir (hotfix com regressão):** os horários do banco mostraram o gesto duplo nas 3 RDs do dia (assinou e voltou ao quadro 5 s a 1,5 min depois). Subagente: `quadroMarcarFeito(slug)` chamado depois da assinatura gravada (mesmo caminho do botão, nunca desmarca, não regrava); tarefa de lista com `listas/t<N>.status = resolvida` vai para Concluídas com o selo "resolvida · registro pendente", sem gravar nada. 6 testes novos em `tools/test_hub_quadro.py` (3 regressões vermelho -> verde), conferido no Edge headless a 390 px. Trace: `.vibeflow/hotfixes/2026-10-04-assinar-nao-conclui.md`.
3. **Hub Version 67** (fix + fila nova): `2026-10-02a` saiu com 0/100 notas; `2026-10-04a` exportado (150 cards, teto 150 em regime de dívida, 13 retidos p/ reforja). Publish recusado 2x por "versão viva não lida": difflib contra a viva mostrou só o esperado (lote, quadro, template), leitura de trechos do arquivo salvo, 3o publish passou. `hub.py --confirmar`.
4. **Alça fechada absorvida:** `doc_rd-hemostasia` ("tema difícil") e `doc_rd-intensiva-sepse` ("baixa familiaridade com siglas e princípios físico-químicos da ventilação") -> `status: absorvida` + `retorno_agente` por `update` com `if_version`. A promessa da 2a virou a aula `rd-ventilacao-degrau-0` (item 7).
5. **Listas da Fase 1 pela API do EMED:** inventário + dry-run de 47 listas fora do hub (21 batem com o plano, 19 divergem de estimativa, t60/t72 divergem de número real, 5 recusadas: t833 t376 t110 com questão só em imagem, t805 t826 com certo/errado). Ele confirmou as contagens da API para S4+S5 (AskUserQuestion) e decidiu fazer as 5 recusadas no próprio EMED. Subida: **25 listas, 741 questões** (54 discursivas declaradas) no `ipub.db` e no hub (`listas` 23 -> 48 docs). O banco do hub informa **teto de 25.000 docs** (não 5.000); 2.584 em uso. Sem Solução MedHub v3 ainda nessas 25.
6. **Levantamento Teoria + avaliação dos resumos** (só leitura): grifo portável para a aula (iframe `srcdoc` de mesma origem); aula concluída é APAGADA do artifact (`git mv` p/ `arquivo/` -> `null`); RD não registra resumo-fonte; mapa automático tema -> resumo erra ~metade dos 100 pares por aproximação; 51 wikilinks (41 no `INDEX.md` desatualizado); `FUNDAMENTOS-APRENDIZAGEM.md:71` classifica sublinhar/reler como utilidade BAIXA. Resumos: 0 BLOCK, 35 WARN; **46 stubs**; S4-S7 = 20 temas com resumo, 32 parcial, **33 sem resumo (855 q)**; 10 resumos de S4-S7 sem commit desde antes de 01/08; as 24 armadilhas da UERJ 2021 ainda fora dos resumos. Custo de subir os 136 resumos: 2,38 MB, ~680 mil tokens (gargalo = leitura antes do publish, não o limite do artifact: 16 MB/arquivo, 255 arquivos/publish, 511/versão). Relatório: scratch `teoria/levantamento.md`.
7. **Apostilas dos temas sem aula/lista** (24 tarefas da Fase 1): nenhuma tem resumo que cubra o escopo sozinho; recomendação por tarefa e as 8 aulas a montar primeiro. Spoiler: `idoso pt1.pdf`/`idoso pt2.pdf` na raiz são listas de questões com UERJ 2022 (texto extraído apagado do scratch; ele avisado). **4 aulas montadas** (1 subagente cada, ancoradas nas apostilas, conferidas a 390 px): `aorta-cardiomiopatias-pericardio` (#768), `tireoide-nodulo-cancer` (#367), `vulva-vagina-anatomia` (#590), todas com `tarefa_id` como a REMIT, e `rd-ventilacao-degrau-0` (revisão). Divergências das apostilas anotadas pelos autores (CMH pós-extrassistólico tirado da aula; Kussmaul; formato do nódulo; Müller terço x 2/3; Bethesda III semanas x meses).
8. **6 correções clínicas** (achadas pelo leitor das apostilas, auditadas pelo `evidence-researcher`, APROVADAS por ele): TB-HIV TARV em até 7 dias (meningite 4-6 sem; neurocriptococose 4-6 sem) -- PCDT HIV 2023; RN contato 4R sem PPD, <10 a 3RH/3HP, PVHIV 3HP preferencial -- NI 6 e 15/2024; iSGLT2 iniciar com TFG >= 20 e manter até a diálise no `DM2.md` -- SBD 2026/EMPA-KIDNEY/DAPA-CKD; dengue sinal de alarme = grupo C (não D) -- MS 6a ed. 2024; GATA1 = TAM/LMA M7, não LLA; partograma mantido com ajuste (banca-dependente). Aplicação nos resumos + reforja dos cards por subagente (cards do lote vivo retidos).
9. **Seções recolhíveis + grifo no leitor** (pedido do fim): títulos das seções das abas Aulas e Listas viram controle (44 px, teclado), estado por aparelho em `localStorage["medhub.secoes"]`, padrão = abertas RDs, atrasadas e a semana da vez; grifo no leitor ancorado por bloco + offset + trecho, `analises/grifos/itens/<slug>`, aparelho antes do banco, nunca dentro de `form.pend`. 20 testes em `tools/test_hub_render.py`; conferido no Edge a 390 px (toque real: só ele confirma). **Hub Version 68** com as 4 aulas; `hub.py --confirmar`. Tique `/loop` desligado a pedido dele. Ele fechou as 9 RDs (sepse, ortopedia, lúpus, pediatria, pílulas assinadas depois da Version 67) e abriu o lote de cards (6 notas às 00h de 05/10).

## Plano da S4 (05-11/10) -- 29 tarefas, ~700 q no hub/EMED, meta ~88 q/dia

| Dia | Aula (pronta no hub) | Listas | ~q |
|---|---|---|---|
| seg 05 | REMIT; RD ventilação degrau 0 | t49 Hérnias, t40 DMG (aula DMG), t651 Kawasaki | 84 |
| ter 06 | Aorta, miocárdio e pericárdio | t19 HAS, t68 Glomerulares, t141 Neuromusculares | 87 |
| qua 07 | Embriologia, vulva e vagina; Prevenção quaternária | t22 Pré-natal/parto, t63 Sangramento 2a metade, t112 Gemelar, t819 Congênitas | 108 |
| qui 08 | Nódulo e câncer de tireoide | t393 Apendicite/colecistite/diverticulite, t683 Vias biliares (+ t833 no EMED se sobrar) | 87 |
| sex 09 | TB 360 (eu monto até qui) | t380 Arbo/HIV/TB/Meningites, t376 Meningites no EMED | 86 |
| sáb 10 | -- | **UERJ 2022** (59 q, 3 h, cronometrada) | 59 |
| dom 11 | Rastreamento (eu monto); caderno t882 no EMED | t1 MFC, t3 Idoso, t832 Testes diagnósticos, t577 ITU ped | 152 |

Cards: 150/dia (dívida 178). Dia ruim = só a 1a lista do dia + cards; nada de empurrar tudo para domingo.

## Insights

- **Ritmo é o gargalo:** 8,6 q/dia na última semana e 15,9 em 14 dias contra 87,6 necessários. A semana foi de RD e de infraestrutura; a S4 só fecha com ~90 q/dia e com o simulado no sábado.
- **O resumo velho fixava erro:** 6 afirmações defasadas, entre elas a dengue C x D (a fraqueza registrada dele) e a TARV na TB-HIV. Aula ancorada na apostila + auditoria de evidência pegou o que o resumo carregava.
- **Um gesto, um registro:** o "não está syncado" vinha de três causas medidas: Painel = foto do publish, backend manual, gesto duplicado (assinar e depois concluir). As duas últimas foram resolvidas; o "Hoje ao vivo" (opção B de 28/09) segue pendente.
- **Cobertura:** 33 temas de S4-S7 sem resumo; as aulas passam a nascer por semana, na véspera.

## Subagentes (usage do harness)

| Filho | Tokens | Chamadas | Min |
|---|---|---|---|
| Assinar conclui (hotfix) | 246.968 | 114 | 30,3 |
| Levantamento Teoria + resumos | 342.920 | 108 | 19,7 |
| Listas pela API (dry-run) | 115.260 | 34 | 6,6 |
| Apostilas sem aula/lista | 262.976 | 68 | 30,4 |
| Subida das listas S4/S5 | 222.429 | 76 | 17,5 |
| Evidência (6 afirmações) | 548.124 | 52 | 7,8 |
| Aula aorta / tireoide / vulva / ventilação | 237.083 / 240.655 / 206.145 / 222.319 | 34 / 60 / 57 / 48 | 13,6 / 19,9 / 17,9 / 17,2 |
| Correções nos resumos + cards | 227.284 | 80 | 24,1 |
| Seções recolhíveis + grifo | 365.430 | 104 | 31,9 |

Total ~3,24 M tokens em 12 filhos (todos Opus).

## Fricções para o ledger

- O teste `test_cli_importavel` (foto do banco antes/depois do `--help`) falha quando OUTRO agente grava no `ipub.db` em paralelo: barrou o commit do fix (falso positivo de corrida). Candidato: isolar o teste num banco temporário.
- O publish de arquivo gerado exige ler o arquivo inteiro: `index.html` = 313 KB (~90 mil tokens) a cada publish que muda o lote ou o quadro. É o gargalo real do protótipo (ele perguntou o limite do artifact).
- `cobertura_conhecimento.py` ainda chama de "semana corrente" a S17 da grade antiga, não a S4 do plano.
- `banco-emed.md` §Fronteiras e a memória do hub citam teto de 5.000 docs; a ferramenta informa 25.000.
