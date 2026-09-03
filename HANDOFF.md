# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-03 -- S162 (veredito da des-colagem + FSRS 45 cards, blocos 4-6)*

## > Proximo passo imediato

1. 🔴 **REDRILL em debito 2 sessoes seguidas** -- 10 cards nota 1-2 da s162 (540, 570, 1290, 313, 311, 245, 650, 155, 1416, 1415) + 8 nota 3 + **16 da s161**. E passo OBRIGATORIO do protocolo (`/revisar` §Relearning intra-sessao), nao opcional. Fechar antes de abrir bloco novo.
2. **Blocos 7-9 do FSRS** -- 43 vencidos restantes zeram a divida. O bloco 7 ja foi servido na s162 e NAO respondido (cards 422, 699, 709, 4, 244, 1354, 122, 485, 459, 1089, 1101, 1117, 706, 558, 297 -- seguem na fila, sem record).
3. 🎯 **Simulado ENAMED na integra** -- em debito ha 10 dias, prova em 10. Sob `PLAYBOOK_EXECUCAO_PROVA.md`. Retorno: autopsia dos erros.
4. **Inscricao UERJ 2027** -- aberta desde 02/09, fecha **01/10 (23h59)**, Cepuerj, R$ 380 (pgto ate 02/10, 16h). Acao do usuario.
5. **Grade EMED S17, so os temas ROXOS** ate 13/09: Diarreia (Teoria) -> SUA (Teoria) -> APS (Revisao) -> Diarreia (Revisao) -> Urologia I -> Pneumonias I. As outras 5 tasks da S17 (Cirurgia Vascular Revisao, Vitalidade Fetal, Neoplasias de Estomago e Esofago, Nefrolitiase) **nao entram na janela**.
6. **Frente MFC (Gusso + Duncan)** -- abre 14/09. Vale 20% da UERJ, lastro zero.
7. 🔬 **ENGENHARIA: F63/F64/F65 abertos** em `AUDITORIA_MEDHUB.md §4o` -- fila de trabalho do agente. F65 tem o caminho mais curto e o maior retorno.

## Estado por frente
- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (59d). ENAMED 13/09 (10d) termometro.
- **Volume & Metas:** 6631 / 10400 (perf. ~78.8%). Hoje: 0. Ritmo-alvo ~63.9q/dia (59d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 26 atrasados + 17 p/ hoje -- pool 684 nunca introduzidos (entram <=60/dia).
- **Conteudo:** 128 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 922 erros registrados · 1253 cards ativos · 2 needs_qualitative na fila · taxonomia 269 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S23, atraso 6 sem) [derivado: preparacao_estado]
- **Reforja:** **15 itens** na fila -- 821, 702, 283, 505, 411 (s161) + 570, 128, 705, 1360 (bl4) + **311/313 (colisao de clones)**, 470 (bl5) + 1415, 1086, 1126 (bl6).
- **Zona (variancia.py):** COBERTURA -- desvio 10.2pp entre blocos, simulado prescrito.
- **Datas:** ENAMED 13/09 (10d) · fim da grade 25/10 · **UERJ 01/11** (59d).

## Prova da UERJ -- o que o edital diz (Ed. 15/2026, PDF em `data/`)
- 100 questoes objetivas, **20 por conteudo**: Clinica Medica, Cirurgia Geral, GO, Pediatria, **MFC**.
- **Etapa unica.** Sem prova pratica. **5 horas** (3 min/q -- erro a combater: fechar cedo, nao pressa).
- Aprovacao: >=50 pontos e nao zerar nenhum conteudo.
- MFC: **20 vagas, 15 ampla concorrencia**. Bibliografia = **Gusso & Lopes + Duncan** (MFC clinica, nao saude coletiva).

## Ultima sessao -- s162 (VEREDITO DA DES-COLAGEM + 45 CARDS)
**A reforma foi APROVADA.** O teste decisivo (P7 -- regra load-bearing viaja com o repo) passou do jeito mais duro: a s161 rodou inteira em **Antigravity**, sem memoria do harness do Claude Code, bootando so do repo, e selou o rito correto. F58/F60 acusaram sem engolir; o painel de DIVIDA abriu o `posicao_ssot` no minuto do selo. **3 falhas:** (a) sensores funcionam, fechamento nao -- a s161 escreveu "S17" na prosa e nao no SSOT, e o plano do dia da s162 bootou com S16 (**corrigido**: `--set-semana 17`, ledger opened->resolved); (b) painel de DIVIDA conta LINHA, nao item aberto (`memory_errors.log` sao 7 linhas de um bug morto); (c) `scratch/` nao limpo, e o conteudo revela que o harness estrangeiro reimplementou o parser da fila FSRS.
**Placar da s161 corrigido:** era 22 nota-4, nao 25 -- **49% recall perfeito / 64% retencao**, nao 55%.
**FSRS 45 cards em 3 blocos:** 25 nota-4 · 10 nota-3 · 6 nota-2 · 4 nota-1 = **56% recall perfeito / 78% retencao** (contra 49%/64% da s161). Curva do dia: 64% -> 80% -> 67% -> 87%. 🔴 **Erro meu registrado:** diagnostiquei fadiga apos o bloco 5 e recomendei PARAR; o bloco 6 (melhor dos tres, zero nota-1) refutou -- a queda era a colisao de clones 311/313, com o instrumento contaminando a leitura de um bloco inteiro.
**Padrao critico:** 🔴 **TCE -- reflexo neuro antes do ABC, 3a ocorrencia** (card 540: respondeu "cabeceira + manitol", que e literalmente a armadilha impressa no card; a resposta e evitar HIPOXIA e HIPOTENSAO). A s151 ja tinha 2 instancias de hiperventilacao em TCE. Tambem: inversao de direcao no beta-hCG do MTX (card 1290), fato-no-contexto-errado (313 respondido com o 311), ancoragem no dado saliente (1416: leu trastuzumabe, ignorou o inibidor de aromatase), binaria com conteudo certo e sim/nao errado (155), AVB reincidente (245).
**Acertos:** card 1358 (integralidade Starfield x SUS) -- gap que a s161 flagrou NA MESMA MANHA, fechado em horas; card 325 (peritonite dispensa imagem) -- o padrao "instavel = via aberta" que o pegou 3x na s161; card 1096 (endometriose) veio mais completo que o proprio verso.

## Pendencias/observacoes ativas
- 🔴 **REDRILL de 34 cards** (10 nota 1-2 + 8 nota 3 da s162 + 16 da s161) -- 2 sessoes em debito.
- 🎯 **Simulado ENAMED** -- 10 dias em debito, prova em 10 dias.
- 🔴 **Inscricao UERJ** -- fecha 01/10.
- 🔴 **F66 (NOVO, descoberto no fechamento):** 45% da memoria de fraquezas (111/244 WeakAreas) e ORFA por ABREVIACAO -- vocabulario canonico usa `Infecto`/`Gastro`/`Hepato`, o Haiku escreve `Infectologia`/`Gastroenterologia`, e `_norm` nao faz substring. O **top 8 de fraquezas do boot** e disputado por so 55% do store, e o log cresce 111-139 linhas por consolidacao pra sempre. Fix = dicionario de alias. **Maior prioridade de engenharia.**
- 🔬 **F63** (prioridade roxa nao viaja com o repo) · **F64** (gatilho do teto: `atrasados` x `vencidos`; + a sessao cruzou a meia-noite sem nenhum aviso) · **F65** (72 cards em baldes `[bulk]` cegos ao radar de dormencia; `[bulk] Cirurgia` abriga demencia e esclerose multipla).
- 📚 **Frente MFC do zero** -- abre 14/09.
- 🗓️ **Rescope cronograma pro formato UERJ** -- 14/09, apos ENAMED.
- 💉 **Diretrizes versao nova**: Calendario Vacinal 2026, GINA 2026, Reanimacao SBP 2026.
- 🔍 **`card_id=120`** (Gravidez Ectopica) para `/pesquisar-evidencia`.
- 🗓️ **Auditoria ampla do banco** -- reforja dos 15 itens da fila; rodar `detect_clones.py` apos reclassificar os `[bulk]`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_162.md*
