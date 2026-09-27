# Session 203 -- golden t3 pela API, cards 99/99, player que volta ao banco, meta única de 10.000 em 01/11

**Data:** 2026-09-27 (domingo) - **Ferramenta:** Claude Code (Opus 5.5 1M) - **Continuidade:** `session_202.md` - **/ai-eng:** não estava aberto (checkpoint pendente, abaixo)

---

## O que foi feito
1. **Boot com o panorama** (5 seções) + resumo da sessão com o /ai-eng de 26-27/09 (s201/s202) para o operador.
2. **Item 0 -- golden t3 VERDE** (`3af3ef3`). O operador colou o `authorization` no chat; gravei `.emed_token` (gitignored, não rastreado, conferido; expira 26/10 16h27). A 1a corrida real recusou 2x pelo mapa do cic-0003 (limite que o /ai-eng tinha declarado): banca = catálogo `CATALOGO_INSTITUICAO` + ano (o `exams[].institution` não existe) e discursiva SEM a chave `alternatives` com `answer_type` DISCURSIVE; o golden pegou a 3a (alternativa multi-linha na Q9 -> `uma_linha`). Sondas no scratchpad imprimiram só caminho/posição/tipo. Resultado: 31 achadas = 30 + [24]; `--conferir` 30/30 iguais em emed_id e gabarito; banca 24/30 exata e 26/30 sem caixa; alternativas 27/30 idênticas -- as 3 restantes estão assim NA FONTE (`sanitized_body == body`: "a.buso", "Indice", "gravi- dade"); a captura por LLM no Chrome as tinha limpado.
3. **Cards:** lote `2026-09-26b` trocado a pedido dele com 12/51 (1 nova gravada) -> `2026-09-27a` com 99 cards (`--new-limit 37`, a pedido: "~100") -> drenado 99/99 = **89 gravadas + 10 marcas de reforja, todas "pergunta composta"** -> `2026-09-27b` (10, saldo do dia) no ar.
4. **F138 (`3b392b4`):** o aviso "SEM CONEXAO COM O BANCO (unavailable)" no celular -> o player desligava o banco pelo resto do lote após 1 falha passageira; agora a nota seguinte tenta e reenvia as pendentes. A tela de fim deixou de dizer "nada salvo" com o espelho local ok. Legenda de atalhos sob o card removida (pedido dele).
5. **F139 (`69c7a4a`) -- uma meta, um ritmo:** decisão do operador (*"a única meta por hora é 01/11 e o alvo é 10k"*). Mapa das 5 réguas por subagente; `MARCOS` com 1 entrada (10.000); linha Meta = único "por dia" (~71,8); Fase 1 = cobertura (10.668 fechando o plano, 540 de simulados); cota da semana, Ciclo 2026, ritmo da Fase 1 e meta mensal revogados nos 3 passos do F90; docs mortos do `/performance` e do `/cronograma` corrigidos.
6. `/loop 1h` do backend ligado (job de sessão, aos `:07`): 4 tiques rodados, todos "nada a fazer" (2 com o lote `27a` em curso, 2 com o `27b` em 0/10); o simulado UERJ 2021 segue sem respostas.

hub-backend: 2026-09-26b gravado (1 válida · 0 quarentena; 12/51, trocado a pedido) -> 2026-09-27a no ar (99 cards)
hub-backend: republicado com o mesmo lote 2026-09-27a (player: banco volta a tentar; legenda fora) -- Version 35
hub-backend: 2026-09-27a gravado (89 válidas · 0 quarentena · 10 marcas de reforja) -> 2026-09-27b no ar (10 cards) -- Version 36 (meta única)
banco-emed: t3 pela API (dry-run + `--apply` em `tmp/emed_api/t3`, 30 docs + Q24 declarada) · não reingerida (já no banco e no hub) · t1793 sem respostas

## Decisões tomadas
- Operador (27/09): **meta única = 10.000 questões em 01/11**; a cota de 27/09 sai do painel; "o alvo anda junto com as listas" -> Fase 1 como cobertura. Em aberto com ele: meta FIXA (implementado) ou DERIVADA do plano (10.668 hoje).
- Operador (27/09): token do EMED colado no chat (escolheu a opção DevTools); o agente o gravou no arquivo gitignored.
- Operador (27/09): ~100 cards no dia (`--new-limit 37` pontual; o default do contrato segue 10); troca do lote em curso a pedido dele.
- Operador (27/09): legenda do player fora.

## Achados de engenharia (ledger)
- **F138** RESOLVIDO (player x falha passageira do `db`) e **F139** RESOLVIDO (5 réguas de ritmo -> meta única). Selo derivado: 0 discordâncias.
- Item 0 do HANDOFF fechado sem F novo (era limite DECLARADO do mapa de campos).

## Erros meus
- 1a recusa do F136 no dia: commitei o player com o HANDOFF dizendo 1219 e a suíte em 1221 -- o pre-commit barrou, corrigi o número.
- Escrevi uma linha nova do HANDOFF citando "Ciclo 2026" sem lápide logo depois de cadastrar o termo; o `CONTRATO_REVOGADO` pegou.
- Heredoc longo com Python partiu no shell de novo (padrão da s202); refeito por script no scratchpad.
- Um `\n` dentro de string num heredoc virou quebra real no teste (SyntaxError), corrigido.

## Custo dos subagentes
1 filho (Explore, Sonnet, read-only): mapa das réguas de meta/ritmo -- **136.492 tokens, 53 tool uses, 539 s (~9 min)**, lidos do `usage` do harness. Não gravou o arquivo pedido (perfil read-only estrito); o relatório veio inline e foi usado inteiro.

## Pendências
- **UERJ 2021 no hub:** o `/loop` desta sessão registra quando `listas/t1793` fechar (`--registrar` + bulk `--area Simulado` com acerto por bloco + `plano.py --concluir 1793`); a **Autópsia/discussão dos erros abre a s204**. Sem o PC acordado, o registro é o 1o ato da s204.
- 10 cards com marca de reforja ("pergunta composta") + #616 "card longo" -> curadoria.
- Releitura da coleção `sessoes/2026-09-26b` no fechamento de cards (trocada com 12/51) e poda das coleções drenadas.
- Checkpoint ao /ai-eng (item 0, F138, F139) -- ele não estava aberto.
- Pergunta ao operador: meta fixa x derivada do plano; divergência "semana 1" (boot) x "semana 2" (painel).
