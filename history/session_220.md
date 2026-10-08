---
type: session
layer: history
status: canonical
---

# Session 220 -- listas resolvidas registradas, P21 (Listas = questões, Teoria = aula) e a cadeia de elos nas 19 listas da S4

**Data:** 2026-10-07 (noite; mesma conversa da s219, depois do selo)
**Ferramenta:** Claude Code (Opus 5.5, principal) + 10 subagentes Opus. Operador presente, resolvendo listas no hub.
**Continuidade:** s219.

## Pedidos dele

1. *"estou matando as listas. atualize. ademais, o bloco 'listas' está bugado, alternando entre tarefas com e sem hiperlinks abaixo. em suma, se estou em listas e clico na tarefa, naturalmente devo ir especificamente para as questões e, por outro lado, se estou na teoria, abro automaticamente a aula."* -> **P21**.
2. *"as listas novas não contém os elos do raciocínio prontas, enquanto as antigas [...] tem. [...] despache um subagent para cuidar desse processamento de todas as listas atrasadas, inicialmente. Amanhã, fazemos as restantes, e também já acrescentamos no método de confecção das listas esse pré-processamento das habilidades sequenciais e nos elos do raciocínio metacognitivo."*

## Feito

- **Listas resolvidas registradas:** t530 (REMIT e cicatrização) 11/20 = 55% e t875 (Prevenção Quaternária) 14/15 = 93%. `emed_banco --registrar --apply --expect 35`; `sessoes_bulk` 136 e 137 (sessão 220, data 07/10); tarefas #530 e #875 concluídas por `--sessao`.
- **Hub Version 80** (publicador Opus: 296.335 tokens, 29 chamadas, 2,5 min): painel + quadro (530/875 concluídas), mesmo lote.
- **P21** (subagente Opus: 299.805 tokens, 118 chamadas, 32,0 min; 17 testes vermelhos antes, conferido no Edge a 390 px claro/escuro com o plano real): aba Listas = só o botão da lista, o toque abre o player (Estudo/Prova é o 1º passo; não havia página intermediária -- o "alterna" eram os links de aula/resumo debaixo das listas com aula); saíram `qzAulasHtml`, `HUB_LIGACOES`, `.qz-aula`, `@hub:ligacoes`, `dados_ligacoes`/`html_ligacoes` e o hash `ligacoes` da projeção. Teoria: 1 aula = o cartão inteiro é o link; 2+ (#811) = um alvo de 44 px por aula; sem aula = cartão apagado ("aula a preparar" volta só aí, para dizer por quê). Painel intocado. **Hub Version 81** (publicador Opus: 286.066 tokens, 27 chamadas, 2,5 min).
- **Cadeia de elos (Solução MedHub v3) nas 19 listas da S4 sem cadeia -- 541 questões.** Não havia lista atrasada de S1-S3 (pendente com questões = 0); o atraso é a S4 (26 listas, 6 já com cadeia). Um subagente só levaria > 3 h e estouraria o contexto (referência s211: ~220 mil tokens por lista de 20-33 q): 5 subagentes em paralelo, 1 lote cada, ordem do plano (adendo `brief_v3_lote.md` sobre `docs/SOLUCAO-MEDHUB-BRIEF.md`). Antes: **19 temas novos em `core/objetivos.json`** (6-8 objetivos cada, dos assuntos de cada lista) e a entrada `tmp/solucoes_v3_<lista>/in/` sem spoiler. Ingestão progressiva por marcador `PRONTO.json` (Monitor) -> `emed_banco --solucoes --apply --expect N` -> `--exportar` -> `ArtifactData batch set` pinado (v1 -> v2). 0 inválidas em 541. Custo pelo `usage`: lote 1 311.065 tokens/49 chamadas/21,9 min; lote 2 384.825/58/22,4; lote 3 289.995/45/21,6; lote 4 391.157/58/24,1; lote 5 408.871/63/24,4. Amostra lida pelo principal: t882 Q5 (identificar -> recordar -> descartar C, chave e habilidade corretas).
- **Análise dos 10 erros de 07/10** (subagente Opus: 269.329 tokens, 60 chamadas, 15,7 min; `insert_questao.py --errors-file`): `questoes_erros` 1129-1138, cards 1916-1924. Padrão dominante: **fato no contexto/fase errada (família 1c)** em 5/10 -- EBB x FLOW (t530 Q5, Q6, Q10), hemostasia x inflamação (Q11, Q13); 2º grupo: pressão negativa e manejo de ferida (Q12, Q14, Q18); **riscou a certa em 5** (Q2, Q6, Q11, Q13, Q18). t875 Q8 = `banca-divergente` sem card (apostila: controle glicêmico = prevenção secundária; banca: terciária; o card #1747 diz "terciária" -> fila do `/pesquisar-evidencia`). #1921 (Q12, desatenção) só existe porque o writer recusa erro sem card -- aposentar se a régua prevalecer. Destrava o F38 (`test_db_real_nao_ganha_orfao_novo`), que barrava o commit.
- Suíte **1505** (`python -X utf8 -m pytest tools/ -q`); commit `04c7339`.

## Divergências das cadeias novas (a cadeia mostra; não força o gabarito)

t112 Q19 (monoamniótica 32-33 x 34 sem); t833 Q14 (tela com/sem profilaxia), Q25 (ferida de 12 h: aproximar x deixar aberta); t393 Q51 (Dunphy é sinal -- EXCETO sem resposta); t19 Q16 (média das 2 últimas medidas), Q35 (IECA pós-IAM também verdadeiro); t380 Q30 e t376 Q28 (quimioprofilaxia: rifampicina MS x ceftriaxona gabarito); t683 Q28 (colecistectomia profilática no DM assintomático), Q32 (CPRE x colangiorressonância); t367 Q13 (esvaziamento radical bilateral em cN0 x ATA 2015). Ressalvas no `porque`: t881 Q14 (NT 626/2025, 40-74), Q15 (BRCA pelo NCCN); t380 Q7/Q14/Q21/Q44/Q52 (diretriz mudou desde 2020-2022); t577 Q12/Q32 (USG após ITU depende da banca); t768 Q6 (TEVAR no Marfan).

## Achados para o método (amanhã)

- **A captura do EMED perde imagem sem marcar `figura`**: dezenas de `sem_figura` com `figura` ausente no `in` (t22 7, t683 7, t393 7, t768 4, t5424 4, t832 4, t380 4, t63 3...). Cadeia feita pelo texto; nos de tabela (t832 Q30/Q35) o `porque` das erradas ficou genérico.
- **Catálogo de objetivos estreito**: "outro:" em 15/39 da t833 (história da cirurgia, acesso venoso central, cirurgia oncológica, ambulatorial, incisões, pilonidal, abscesso esplênico, Pringle, paramentação), 6/32 da t832, 5/20 da t882 (insônia no adulto), 5/37 da t683.
- Mesma `habilidade` em 2 elos da mesma cadeia em t882/t590 (o validador aceita).

## Pendências

- Perguntas da análise para ele: t530 Q6 (por que riscou a D, se usou o hipometabolismo da EBB para descartar a B?); Q18 (fechou a ferida por ler como ressutura, ou por não saber que ferida infectada não se fecha?); Q2 e Q11 (por que riscou a certa com confiança sólida?).
- Amanhã (pedido dele): cadeia nas listas restantes (S5-S7) e o pré-processamento (objetivos do tema + cadeia v3) no método de montar listas, antes do hub; refinar o catálogo com os "outro:".
- Simulado UERJ 2022 (t1794) sem cadeia de propósito (modo prova no sábado).
