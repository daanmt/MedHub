---
type: session
sessao: 165
data: 2026-09-05
harness: Claude Code (Fable 5.1)
---

# Sessao 165 -- Aulas EMED -> prevalencia ENAMED; regra "prevalencia = prioridade" (2026-09-05)

## O que aconteceu
1. **Boot** achou drift: s164 commitada e nao selada. Reconstruida em `session_164.md`.
2. Decisao do usuario: **2 blocos de 60 cards/dia (120) como sprint ate 13/09**. Minha leitura: bloco 1 consolida (54 redrill ja vencidos + 8 fresh do S6), bloco 2 expande (novos por prevalencia). Blocos 1.1 e 1.2 montados com tronco (PREPARAR sem versos; `review_log` 111 Epilepsias, 112 Vulvovaginites). **Nao foram respondidos** -- o usuario redirecionou para as aulas.
3. **5 transcricoes das Horas da Verdade do Estrategia MED** (Ped I, Gineco, CM I, Cirurgia I [Revalida, proxy], Preventiva I) digeridas: cada tema recebeu prevalencia alta/media/baixa com evidencia e timestamp, cruzado com pool/ativos/erros/resumo; padroes de banca gravados. Persistencia: `core/cronograma/prevalencia_enamed.json` (89 temas, 59 alta, 35 padroes, 5 fontes; 15 temas sem linha na taxonomia). 5 commits.
4. **Regra do usuario:** prevalencia = prioridade na fila dos nunca introduzidos -> `tools/fsrs_queue.py --prevalencia` (opt-in; reordena `novos` alta->media->baixa->sem sinal, desempate FIFO, corte em `--new-limit`; FSRS intocado). Suite `test_fsrs_queue_prevalencia` (5), registro em `pytest.ini`, skill `/revisar` + espelho. auto_check PASSED (363). Smoke: bucket novo abre com Cirurgia Infantil 22.

## Achados (para o estudo)
- **SCA**: zero linha, zero card, zero resumo; "esta na moda". Maior buraco do banco.
- **Cirurgia Infantil**: fraqueza nº 1 (30 erros) com **43 cards no pool nunca vistos**; a aula de cirurgia cobre 6 dos 10 subtemas dos erros (nao cobre ECN/Hirschsprung/atresia/volvo).
- **SUA** (3o tema de Gineco): zero card, sem linha; resumo existe; e roxo da S17.
- **Q66 do Simulado 6** e a questao que o professor de endocrino resolve ao vivo (volume -> potassio -> insulina).
- Card 540 / familia "reflexo neuro antes do ABC": 3 portadores agora (neuro CM-1, trauma ATLS 11, resumo) -- PPC = PAM - PIC, sem hipotensao permissiva em TCE/TRM.
- Resumos: HAS Pt2 ja com 130/80 + MAPA; Epilepsias ja com levetiracetam; Trauma.md com ATLS 11 parcial (faltam sangue total, Sellick, conferir classificacao do choque); Dislipidemia nova rasa.

## Achados (engenharia -> AUDITORIA §4o)
- F65 agravado: `[bulk] Cirurgia` 148 erros, `[bulk] Pneumo` 17 -- historia enterrada sem tema.
- F67 taxonomia duplicada (colo x2, TH x2, Asma x5, PF/Contracepcao, Ulceras x2, TCE x3) divide FSRS e dormencia.
- F68 15 temas prevalentes sem linha na taxonomia.
- F69 lacunas de diretriz nova em resumos (banca-dependente): Trauma (ATLS 11), Dislipidemia 2025, SINAN 2026.

## Numeros
- Cards gravados: **0**. Questoes: **0**. Redrill em debito: 5a sessao (64 nota 1-2).
- Commits: 575e42c, a6f80c5, c1b1c18, 9711cc3, f4128bc (prevalencia), 07fe441 (fsrs_queue), + selo.
