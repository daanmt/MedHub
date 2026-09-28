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
hub-backend (pos-selo): 2026-09-27b gravado (9 validas · 0 quarentena · 1 marca de reforja, #659) -> 2026-09-27c no ar (1 card, saldo final) -- Version 37
hub-backend (pos-selo, 28/09): republicado com o mesmo lote 2026-09-27c (painel e quadro mudaram com a virada do dia: semana 3, ~74 q/dia) -- Version 38
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

## Adendo pós-selo (28/09/2026, manhã)
- **Pergunta dele:** *"por que quando finalizo os cards ou uma lista o painel não é atualizado automaticamente"*. Resposta: o painel é uma FOTO gerada no PC (`painel.py` lê o `ipub.db`); a página só anota no `db` do hub; quem leva ao `ipub.db`, regenera e republica é o tique (latência = 1h, só com o PC acordado e a sessão aberta); e o tique só via cards -- lista comum terminada no hub ficava sem volume até alguém registrar no chat (a `t49_1` de 27/09). O botão "atualizar agora" foi barrado pelo classificador na s194.
- **Decisão dele: A agora, B na próxima sessão de engenharia.** (A) `/hub-backend` ganhou o **passo 2b**: registra TODA lista com `status` = `resolvida` e tarefa pendente (passo 3 do tique do `/banco-emed`; a análise dos erros NÃO roda no tique). Skill + espelho sincronizados; job do loop trocado de `d56e5a2b` para `3f6af4b9` com o prompt `/hub-backend` puro. (B) "Hoje" ao vivo no painel (a página soma o feito-e-não-gravado) -> fila de engenharia no HANDOFF. (C) tique mais frequente: descartado por custo.
- hub-backend (pos-selo, 28/09): lote `2026-09-27c` (1 card) em 0/1; a UERJ 2021 segue `capturada` -- ele vai resolvê-la hoje.
- hub-backend (pos-selo, 28/09): 2026-09-27c gravado (1 válida · 0 quarentena) -> 2026-09-28a no ar (50 cards, teto 99) -- Version 39. Operador deixou um `/loop 20m /hub-backend` ligado nesta sessão (CronCreate, session-only) e saiu para o hospital.
- Operador (28/09): "esse loop pode ser de 1/1h. sem problemas" -- cancelado o job de 20 min (`3ac2c1d6`); segue só o job de hora em hora já existente (`3f6af4b9`, herdado da sessão anterior).
- hub-backend (pos-selo, 28/09): 2026-09-28a gravado (46 válidas · 5 quarentena, todas "Card longo": #367 #677 #678 #679 #1481) -> 2026-09-28b no ar (13 cards, teto do dia caiu para 53 pelo rebalanceamento FSRS) -- Version 40.
- **F140 (28/09, ABERTO) -- fila pos-bloco intercala cards rebaixados no mesmo dia à frente de cards novos.** Relato dele: drenou os 50 do `2026-09-28a` sozinho, algumas notas < 4 foram pra reforja no fim da lista (correto); pediu mais cards e o `2026-09-28b` (13) trouxe de volta 3 dos mesmos cards que ele tinha acabado de errar (`1444`, `638`, `1589`, todas nota 1/Again, todos cards `agendado` com histórico prévio) ao lado de 10 `novos`. Pedido dele: **não corrigir agora**, só documentar o mecanismo (fila, notas, agendamento) pro `/hub-backend` e pra próxima sessão decidirem. Rastreei sem alterar nada: `app/utils/fsrs.py` usa `learning_steps=()` (fiel ao FSRS, sem piso de dias — um Again sobre estabilidade baixa pode cair dentro do dia); `db.get_cards_by_bucket` classifica `hoje` sem distinguir "vencia hoje mesmo" de "rebaixado há 10 min"; `fsrs_queue.py` fixa a ordem `atrasados -> erros_frescos -> hoje -> novos` sempre, e `--new-limit` (default 10) capa os novos por export independente da folga do teto. Assimetria observada e NÃO fechada: só os Again sobre cards com histórico prévio voltaram no mesmo dia — os 2 Hard (`640`,`644`) e os 6 Again "novo" (1ª exposição, `662`-`670`) não. 3 perguntas em aberto no ledger (F140), nenhuma decidida. Entrada em `AUDITORIA_MEDHUB.md` + ponteiro no HANDOFF ("ABRIR A s204" item 5 e fila de engenharia item 2c).
