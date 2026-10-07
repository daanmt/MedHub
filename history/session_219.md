---
type: session
layer: history
status: canonical
---

# Session 219 -- spoiler da UERJ 2022 tirado do hub, 26 cadernos do Chrome (511 q), 10 aulas e a UI da Teoria (P20)

**Data:** 2026-10-07 (tarde)
**Ferramenta:** Claude Code (Opus 5.5, principal) + 5 subagentes Opus (3 de aulas, 1 de UI, 1 publicador). Operador presente.
**Continuidade:** s218.

## Pedido dele

Colou o relatório do Chrome (máquina danielm): 26 cadernos criados no EMED, um por tarefa sem lista (anos 2019-2026, objetivo Residência, só múltipla escolha; t1798/t1799 = UERJ HUPE 2017-2018/2019-2020). Depois: *"Após, pode trabalhar nas outras pendências: criação de aulas para as tarefas sem aula e corrigir as inconsistência de UI. Por fim, pode encerrar formalmente."*

## Achado crítico: o simulado de sábado estava nas listas do hub

- Antes de importar, medi as listas JÁ no hub. Lente 1 (rótulo): 37 questões UERJ 2022-2026 em 22 listas da Fase 1 (36 de 2022, 1 de 2023). Lente 2 (texto do enunciado contra os cadernos dos simulados pendentes t1794/t892/t891/t890, sem imprimir conteúdo): **36 eram questões da própria prova UERJ 2022** (26 distintas das 59 válidas -- quase metade do simulado de sábado), 0 de 2024-2026; 4 falsos-positivos UNESP (enunciado curto parecido, alternativas 0,12) descartados. Nenhuma respondida no hub.
- O classificador do auto mode barrou o `batch delete` ("Cloud Storage Mass Delete") e depois até leituras do banco; parei e relatei. Ele autorizou por `/permissions`; 37 docs `questoes/*` saíram do hub e as 22 `listas/*` ganharam `q` corrigido + `spoiler_uerj_fora`. Ficam no `ipub.db`.

## Feito

- **Filtro de spoiler (regressão escrita antes, 4 testes):** `emed_api.spoiler_uerj` -- UERJ (qualquer programa) com ano 2022-2026, olhando TODOS os exames da questão, antes das regras de forma; declarado (`spoiler_uerj` no JSON), contagem fecha em 5. `emed_banco --exportar` aplica a mesma regra a lista do EMED (`fora_do_hub`; a prova `prova_pdf` sai inteira). Conferido no banco real: a regra pega exatamente as 37.
- **26 cadernos importados:** dry-run dos 26 = contagem do Chrome nos 26 (duas fontes independentes); 5 spoilers declarados (t876 Q7, t879 Q3/Q9, t483 Q6, t740 Q5) + 1 alternativa-imagem (t5424 Q4); backup `ipub_backup_20261007_123245.db` -> 511 novas, 0 sobrescritas; lente 2 de texto contra os simulados pendentes = 0; `--exportar` -> 12 lotes `ArtifactData` (511 questões + 26 `listas/*`, com o link do caderno); hub 4.358/25.000 docs; `as_level: interact` não lê questão. Erro meu de transcrição pego pelo cheque de UUID duplicado (t882 com o UUID da t881) e corrigido antes da rede.
- **P20 (subagente Opus, 461.656 tokens, 170 chamadas, 50,5 min):** sai o quadrado "feito" da Teoria (assinar já conclui; o estado `quadro/<slug>` segue lido); 16 títulos custom acentuados em `core/cronograma/plano_custom.json` (re-semeado por mim: backup `ipub_backup_20261007_133940.db`, 0 novas, 16 `tema`); meta da tarefa numa regra só (Teoria = Painel); "aula a preparar" apagado; `plano.tema_exibido` (' | ' -> ' · ', 'Endócrino- |' junta); `plano.q_da_tarefa` conta o banco do hub pelo critério do `--exportar`: S4 768 -> **818**, S5 861, S6 729, S7 425 (Teoria = Painel = boot). 12 testes novos; conferido no Edge a 390 px claro/escuro (eu olhei Teoria claro e Painel escuro).
- **`plano --concluir --leitura` recusa tarefa com questões no banco do hub** (#875 e #1797 ganharam caderno: assinar a aula não conclui com a lista aberta). Teste antes do fix; `/hub-backend` atualizado.
- **11 `listas/*` do hub com o título acentuado** (`ArtifactData update`, pinado).
- **10 aulas** (ancoradas nos PDFs do EMED; registradas em `core/hub_quadro.json`): lote A MFC (435.601 tokens, 100 chamadas, 24,0 min) `rastreamento-programas-br` #881, `mccp-decisao-compartilhada` #878, `cronicas-aps-metas` #1796; lote B (664.743 tokens, 164 chamadas, 42,6 min) `idoso-amg-polifarmacia` #876+#879, `rodapes-retorno-alto` #5425, `imagem-obstetrica` #5424 (9 SVG); lote C CM (387.190 tokens, 77 chamadas, 23,3 min) `anemias-macrociticas` e `oncohemato-cronicas` #811, `insuficiencia-adrenal` #310, `iamcsst` #777.
- **Pendências do hub:** `rd-hernias_q4` e `_q20` respondidas por ele às 10h32 -> absorvidas (update pinado, `retorno_agente`). Q4: negou I (mulher opera assintomática; card 1906) e IV (tela e dor crônica: igual ou menor; SEM card). Q20: redução = "resolvida por ora" (card 1909) + cardiopatia/AAS/idade como freio (isca; SEM card). Os 2 cards novos ficam para a próxima sessão de cards.
- **Lote de cards `2026-10-07a`: 0/100 notas no `db`** (`sessoes/2026-10-07a/notas` vazia; `--precisa-publicar` = "lote em curso 0/100"). O HANDOFF da s218 dizia "drenado"; nada a gravar. Pergunta a ele.
- Suíte **1503** (`python -X utf8 -m pytest tools/ -q`); `auto_check --changed` PASSED. Commits `120599d` e `4122645`.

## Divergências clínicas das aulas novas -- DECISÃO DELE (nenhuma aplicada a resumo)

A aula segue o PDF do EMED e marca o ponto como "banca-dependente" ou "fora da apostila"; os relatórios completos dos subagentes (com páginas e fontes) ficaram no scratch da sessão (`aulas/relatorio_{A,B,C}.md`).
- **MFC (A):** colo -- PDF 2016 sem DNA-HPV, MS 2025 com (o `.md` já tem); mama 50-69 (PDF) x 50-74 (NT MS 626/2025, no `.md`); colorretal 50 (PDF) x 45 (`.md`); DM2 rastreio 45 (`.md` SBD) x 35 (PDF 2026, ADA/SBD) -- revisar o `.md`; meta de HbA1c no idoso contraditória entre os `.md` de DM2 (aula: "até 8-8,5%"); DRC: encaminhar com proteinúria > 1 g ou > 500 mg (`.md` ambíguo); ICFEp: fonte diz nenhum remédio reduz mortalidade (iSGLT2 hoje indicado, reduz hospitalização); próstata "até 70 anos" (SBU, PDF) possivelmente antigo; DPOC vacinas pelo CDC, não pelo PNI; `Melanoma.md` diz linfonodo sentinela "opcional" com Breslow < 0,8 mm (em geral não se indica). Fora das fontes locais, não conferido em fonte primária: Wilson-Jungner, vieses, Leis 11.664/12.732/13.896, os acordos de Stewart e os passos de Elwyn.
- **Idoso/rodapés/obstetrícia (B):** zóster -- vacina viva no PDF x recombinante 2 doses >= 50 (SBIm); dTpa e VPP23 para todo idoso (material) x PNI (dT; VPP23 só acamado/institucionalizado); vitamina D 800 UI contra queda (USPSTF 2024 não recomenda); isoniazida como indutora do P450 no PDF (é inibidora); MEEM com corte fixo (BR: por escolaridade); Estatuto do Idoso "2013" no PDF -> 2003 (corrigido com aviso); Fried "quinto quintil" -> forma padrão (sem nota); SHU atípica: plasmaférese no resumo x eculizumabe; Down: recorrência na translocação 43%/28% (PDF) x 10-15%/até 5%, celíaca e RX cervical de rotina (PDF) x AAP 2022 só com sintoma, GATA1 ligado à LLA no PDF (aula segue o resumo: mieloide), TN 2,5 mm (sem nota); CTG: "DIP 2" para variável no GO/15 (aula: DIP III, clássica); partograma: PDF 2026 diz que as linhas de alerta/ação não se traçam mais x resumo/MS 2017; inconsistências internas (corte do TUG 10/12,4/13,5/20 s; telefone como AVD básica e instrumental; typo do expulsivo com analgesia em GO/5). Citados de memória, sem busca: calendário vacinal, USPSTF, AAP, eculizumabe, "reavaliar em 4 h" do grupo B da dengue.
- **CM (C):** aplásica -- ATG de coelho (PDF) x cavalo + eltrombopague; Hodgkin IA com RT isolada (hoje só no predomínio linfocitário nodular); SMD 20% de blastos (OMS/ICC 2022 redesenharam 10-19%); adrenal: paracoco antes da TB como causa infecciosa; corte de cortisol 18 x 14-15 mcg/dL nos ensaios atuais; mecanismo da hipercalcemia trocado por "reabsorção óssea + contração de volume"; IAM: BRE "novo" (ESC dispensa), tempos 30/90/120 x 10/60 da ESC, prasugrel sem pré-tratamento, estatina após 12-24 h x o mais cedo possível; anemia perniciosa: mulher > 60 (PDF) x > 40 (`.md`). **Killip não existe em nenhuma fonte local** -- degrau escrito de fonte externa (Killip 1967) e complicações mecânicas por ESC/AHA, marcados "fora da apostila"; idem imagem em espelho V1-V3 e CK-MB no reinfarto; cortrosina normal na insuficiência central recente e "sem fludrocortisona na crise". Grafias do PDF corrigidas ("Ann Arbor", "fosfatase leucocitária", linfonodo supraclavicular).

## Publish

**Version 79** (subagente publicador Opus: 564.110 tokens, 59 chamadas, 7,4 min pelo `usage`): mesmo lote `2026-10-07a`; 11 arquivos enviados (as 10 aulas + `painel.html`) + a página; 61 mantidos, 0 removidos; `--check` OK, sem item 'Sem área'; capabilities mantidas (7 regras). O publicador leu os 12 inteiros: sem questão UERJ 2022-2026, sem comentário de professor, sem credencial; questões não vão na página. 2 recusas da ferramenta (versão no ar não lida; conteúdo igual até abrir o arquivo salvo) resolvidas sem forçar. Build com o `--out` default `tmp/hub` (onde mora o `registro_publicado.json`); `hub.py --confirmar` exit 0 (72 arquivos registrados).

## Pendências

- Ele: (1) o lote 07a foi drenado? (0 notas no banco); (2) decidir as divergências acima (aula + resumo, como na TB da s217); (3) Pró-MFC (UERJ) 2017-2020 em t1798/t1799 -- recomendei incluir (bloco MFC = 20%, sem spoiler), volta ao Chrome se ele aceitar.
- Cards novos: tela e dor crônica (igual ou menor que o reparo tecidual) e "cardiopatia/AAS não adiam a urgência da encarcerada; AAS de prevenção secundária se mantém".
- `q_previstas` das 26 tarefas no plano segue 0/20/60 (a tela já conta o banco; a trilha não).
- Aulas que faltam na Fase 1: S4 #882 (saúde mental APS); S5 #887 (onco pediátrica); S6 #880 #483 #740 #1795 #889 #467; S7 #5426 (leitura).
