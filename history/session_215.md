# Session 215 -- Fila de 05/10 no hub, medição do hub em 3 blocos (P13), backend de 2 em 2 h e 5 revisões direcionadas do lote

**Data:** 2026-10-05 (segunda, 06h -> 18h30) - **Ferramenta:** Claude Code (Opus 5.5 como orquestrador; 2 subagentes Opus) - **Continuidade:** `session_214.md`

---

## Pedido

Abertura: *"pode atualizar o bloco de cards com a fila de segunda 05.10. ademais, como ficou o tamanho da tarefa de engenharia? painel segue 'desconexo' dos blocos de cards / listas. [...] pensei em algo como: painel = performance + cronograma + ritmo, bloco teoria = revisões + aulas do cronograma/tarefas pré-lista e bloco cards/questões de mão-na-massa."* Depois: *"faremos em sessão dedicada. essa permanece apenas como backend do medhub, de 2/2h."* Às 12h45: *"pode remover o tique. resolvi os cards. já salve de uma vez, atualizando o painel."* E: *"após concluir, pode publicar nas aulas"* (as RDs).

## Feito

1. **Fila de 05/10 no hub (Version 69):** lote `2026-10-05a` = 150 cards (36 atrasados + 42 hoje + 8 erros frescos + 64 novos; 35 retidos por marca de reforja), `--limit 150` pela decisão dele de 05/10 (o lote 04a conta como 04/10). Publish exigiu leitura integral do `index.html` (344 KB) -- o E01 de novo.
2. **P13 medido** (subagente Opus read-only, 291 mil tokens, 61 chamadas, 11,5 min pelo `usage`): `docs/MEDICAO-HUB-3-BLOCOS-2026-10-05.md`. O cronograma sai inteiro 2x (92 tarefas S4-S7 no Painel e na aba Aulas; só 12 de aula), cada lista tem 3 portas (43 + 43 + aba Listas), documentos 2x, saldo de cards diverge. v0 = 4 fatias (~145 linhas, ~25 testes, 1 sessão, sem dado novo). Contagens conferidas por `grep` no build. Linha P13 no `docs/BACKLOG-PRODUTO.md` + adendo no handoff do /ai-eng. 3 decisões dele pendentes (4 x 3 abas; Documentação; Biblioteca retroativa).
3. **Backend `/loop 2h /hub-backend`** (cron `7 */2 * * *`): tiques das 08h (`mesmo_lote`, retenção 74,6 -> 74,5%, Version 70) e das 10h/12h (nada). Removido às 12h45 a pedido dele.
4. **Lote `2026-10-05a` gravado:** 150/150 (104x4, 5x3, 12x2, 29x1; 41 redrill ok; 0 marca de reforja); revlog 4014 -> 4164. Saldo do dia zerado pelo relógio (consumo 212 = 62 do lote 04a depois de 00h + 150): sem fila nova; Version 71 = painel.
5. **5 Revisões Direcionadas** (subagente Opus, 244 mil tokens, 53 chamadas, 12,1 min) sobre os 41 cards de nota 1-2, publicadas na Version 72: `rd-neoplasias-tgi` (9), `rd-meningites` (7), `rd-dm-cronicas` (6), `rd-hemostasia-2` (3), `rd-pilulas-0510` (16). Cada bloco declara o resumo-fonte (decisão do P03); "Teste agora" com 56 perguntas de recuperação. Lidas inteiras pelo principal antes do publish. 22 temas carimbados `directed_review` (review_log 201-222).
6. **Siamese Twins:** +5 armadilhas (só acréscimo): Meningites (dexametasona antes/junto do antibiótico; neurocisticercose subaracnóidea), Hemostasia (HIT: sair da classe; varfarina com plaquetas > 150.000), Polipose e CCR (as 3 condições da polipectomia curativa), HAS Parte 1 (média das 2 últimas aferições). `auto_check --changed` PASSED.

## Correções clínicas (fora da aula; decididas por ele)

Aprovadas por ele às ~18h (*"sim, aplica as duas"*) e aplicadas em `Meningites.md`; a `rd-meningites` foi atualizada com a posologia e republicada (Version 73).
- **Rifampicina** (§8.5): era "2 dias para Hib, 4 dias para meningocócica" -> meningococo 10 mg/kg/dose (máx. 600 mg) 12/12 h por 2 dias (4 doses), < 1 mês 5 mg/kg/dose; Hib 20 mg/kg/dose (máx. 600 mg) 1x/dia por 4 dias, < 1 mês 10 mg/kg/dose. Fonte: Guia de Vigilância em Saúde (MS, 6ª ed., 2023). O card #966 já estava certo.
- **Ceftriaxona** (armadilha da quimioprofilaxia): dizia que "não é droga de escolha" e chamava de desalinhados os gabaritos que a marcam -> rifampicina preferencial, ceftriaxona 250 mg IM dose única alternativa válida e preferida na gestante; quem decide é o perfil do contato. Alinhada à linha das alternativas e ao MS.
- **Card #639** (LES): marca de reforja aberta ("Pergunta composta": pergunta "o MAIS específico" e responde dois; o mais específico é o anti-Sm).
- Menores, só registrados: TB meníngea "subaguda" (card) x "crônica > 4 sem" (resumo); carcinoide "a partir de 2 cm" (card) x "> 2 cm" (resumo); margem da polipectomia > 2 mm x >= 1 mm (diretrizes americanas); dexametasona 2-4 dias (card) x 4 dias (resumo); card #639 (LES) pergunta "o MAIS específico" e responde dois -> candidato a reforja (anti-Sm).

## Fricções

- O publish do hub exige ler o `index.html` inteiro sempre que o lote ou o quadro mudam (~100 mil tokens por vez; 3 vezes nesta sessão). Mitigação usada: comparar por script contra a cópia já lida e ler só as linhas que mudaram. É o E01; o v0 do P13 reduz (lista concluída deixa de mudar o `index.html`).
- O Painel mostrou "212 de 100" depois da gravação: conta pelo relógio (P09).
- O WARN `CLAUSULA_ORFA_SUBIU` (128 > 127) apareceu no 1o commit da sessão sem portador tocado por ela; não investigado.

## Fechamento

Selada a pedido dele (*"após, pode encerrar formalmente"*). Ele já adiantou parte das RDs (a `rd-dm-cronicas` está assinada) e vai terminá-las antes das listas atrasadas. Simulado UERJ 2022 ainda não feito (sábado, S4): sem autópsia nova até lá. Próxima sessão: export de 06/10, registrar as listas que ele resolver e analisar erros/chutes no chat; P13 em sessão de engenharia dedicada (3 decisões dele antes do spec).

## Custo

Principal (Opus 5.5) + 2 filhos Opus: 535 mil tokens nos filhos (291k + 244k), pelo `usage` do harness.
