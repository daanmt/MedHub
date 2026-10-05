# Session 215 -- Fila de 05/10 no hub, medição do hub em 3 blocos (P13), backend de 2 em 2 h e 5 revisões direcionadas do lote

**Data:** 2026-10-05 (segunda, 06h -> 13h) - **Ferramenta:** Claude Code (Opus 5.5 como orquestrador; 2 subagentes Opus) - **Continuidade:** `session_214.md`

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

## Para ele decidir (correções clínicas fora da aula)

- **Rifampicina** (`Meningites.md:133`): hoje "2 dias para Hib, 4 dias para meningocócica" -> proposto: meningococo 10 mg/kg/dose (máx. 600 mg) 12/12 h por 2 dias (4 doses); Hib 20 mg/kg/dose 1x/dia por 4 dias. Fonte: Guia de Vigilância em Saúde (MS, 6ª ed., 2023). O card #966 está certo.
- **Ceftriaxona** (`Meningites.md:230`): diz que "não é droga de escolha" e chama de desalinhados os gabaritos que a marcam; a linha 134 e o MS a tratam como alternativa válida e preferencial na gestante. Proposto: alinhar a 230 à 134.
- Menores, só registrados: TB meníngea "subaguda" (card) x "crônica > 4 sem" (resumo); carcinoide "a partir de 2 cm" (card) x "> 2 cm" (resumo); margem da polipectomia > 2 mm x >= 1 mm (diretrizes americanas); dexametasona 2-4 dias (card) x 4 dias (resumo); card #639 (LES) pergunta "o MAIS específico" e responde dois -> candidato a reforja (anti-Sm).

## Fricções

- O publish do hub exige ler o `index.html` inteiro sempre que o lote ou o quadro mudam (~100 mil tokens por vez; 3 vezes nesta sessão). Mitigação usada: comparar por script contra a cópia já lida e ler só as linhas que mudaram. É o E01; o v0 do P13 reduz (lista concluída deixa de mudar o `index.html`).
- O Painel mostrou "212 de 100" depois da gravação: conta pelo relógio (P09).
- O WARN `CLAUSULA_ORFA_SUBIU` (128 > 127) apareceu no 1o commit da sessão sem portador tocado por ela; não investigado.

## Custo

Principal (Opus 5.5) + 2 filhos Opus: 535 mil tokens nos filhos (291k + 244k), pelo `usage` do harness.
