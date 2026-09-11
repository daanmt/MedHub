# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-11 -- **S178 (ENGENHARIA, janela 3)**: **Tier 1 FECHADO** (1.5 a 1.9), suite **578 -> 621**, **0 spawns**. HEAD `270ac57`, main == origin/main.*

> 🔴 **A reforma acabou por FIM DE FILA, nao por teto de contexto.** Tier 0 e Tier 1 zerados em tres janelas. **Semana de ENAMED (dom 13/09): questoes, simulados e cards.** A janela 4 so abre por decisao do operador, e ja tem abertura definida (abaixo).

## > Proximo passo imediato

1. 🃏 **VOLTAR AO ESTUDO.** Re-drill dos **12 cards nota 1-2 da s175** (so as frentes; **nao gravar FSRS** -- e consolidacao) + fila FSRS do dia + intake novo.
2. ❓ **DUAS PERGUNTAS ABERTAS da s175**, curtas, na abertura: (a) **fork da PAC Q3** -- *"quando voce marcou A, estava afirmando que o pneumococo NAO e o agente mais provavel naquele etilista diabetico, ou marcando a que achou verdadeira?"*; (b) **valores laboratoriais da Uro II Q2** (eram imagem) -- se havia relacao PSA livre/total, o gabarito fecha sem depender do corte NAO-VERIFICAVEL.
3. 🎯 **Simulado 9 (qui) e 10 (sab):** `--area Simulado` direto no CLI; erros analisados no mesmo dia. Domingo: **ENAMED** = termometro.
4. 🔴 **O numero do passivo de cards MUDOU: `reforja --fila` diz 272 abertas, nao 2.** Nao e defeito: os 270 nao-atomicos que o WARN ja reportava viraram **estado triavel** (F39). Triar e do operador -- `--fechar` re-verifica o predicado, `--descartar` e *"olhei e nao era defeito"*, e **card discriminador legitimo sai por `--descartar`**, nunca por `--fechar`.
5. 📚 **Backlog de conteudo:** 6 temas do Simulado 8 sem resumo (Doenca Hemorroidaria, Lesoes Hepaticas Focais, Abdome Agudo Obstrutivo, Farmacodermias, Esquistossomose, Liquido Amniotico) + s172 (Disturbios Resp. Neonatais, Infeccoes Congenitas, cerclagem). **395 PDFs / 136 `.md` / 327 orfaos** (`cobertura_conhecimento.py`).

## Fila de engenharia -- **TIER 0 e TIER 1 ZERADOS**. Inventario: `docs/MEMORIA-AUDITORIA.md §11`

- ⚰️ **s176 (janela 1):** 0.0 (F93+F90) · Tier 3 · 0.1 (F80b) · 0.1b (F91) · 0.2 (B1/F81) · 0.3 (B2) · 0.4 (B4/F77+F77b).
- ⚰️ **s177 (janela 2):** 0.5 (B3/F35) · 0.6 (F89+F94) · 0.7 (promotes x3) · 1.1 (F79b) · 1.2 (F64+F95) · 1.3 (F66) · 1.4 (F42).
- ⚰️ **s178 (janela 3):** **1.5** (F7 morto por medicao) · **1.6** (F39, fila mecanica) · **1.7** (D5 + **F97**) · **1.8** (varredura unica: G5/G10/G14 CHECK, portadores e termos DERIVADOS, G11/G3/D11 fechados, G6 ja coberto) · **1.9c** (convencao de trace). Riders: **F96**, **F97**.
- 🔜 **ABERTURA DA JANELA 4 (decidida pelo `/ai-eng`):** o smell **`db.py -> tools/card_checks` por `__file__`** (camada invertida, **toca 7 writers**). Vai **por spec** -- `gen-spec -> implement -> audit` -- com a analise do §11 linha 1.15 como **insumo**, nunca como spec. O raio **cresceu** neste ciclo: `card_checks` agora tambem delega a `audit_card_atomicity` (F39).
- 🧑‍⚖️ **1.10 segue CANDIDATO, sem GO do operador** (toda clausula de skill/`AGENTE.md` = CHECK nomeado ou marca literal "nao-verificavel").
- 🧑‍⚖️ **Decisoes empilhadas do OPERADOR:** (a) `reforja.py --backfill --apply` (9 linhas em dry-run, **nao colidem** com as 272 de agora); (b) **RODADA 3** do `normalize_taxonomia` (18 linhas fantasma: 39 cards + 33 erros); (c) 19 cards em overflow no 13-14/09; (d) backfill UTC->local; (e) `--new-limit` x pool 671; (f) **`Oncologia`/`Urologia`/`Radiologia`/`Medicina de Emergencia` sao areas?**; (g) **F64** mudou politica de estudo (teto 60 -> 90 em dia de divida); (h) 🆕 **G1/G8 -- rotacao do ledger (251 KB)**: e **F62**, decisao dele. Engenharia **nao** apaga registro de auditoria por conta propria; (i) 🆕 **F57** (72 memorias com ponteiro) e **lote de sessao de ESTUDO**, nao de engenharia; (j) os de sempre: apagao do `/graphify`, planilha ainda e fonte? (F35), regua de "card bom" (F87), F62/F55/F37.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (51d). ENAMED 13/09 (**2d**) termometro.
- **Volume & Metas:** 7126 / 10400 (perf. ~79.0%). Hoje: 0. Ritmo-alvo ~64.2q/dia.
- **FSRS:** divida 4 atrasados + 78 p/ hoje -- pool 671 nunca introduzidos (entram <=90/dia).
- **Conteudo:** 136 resumos. **Cobertura medida: 327 temas com PDF e sem `.md`.**
- **Erros & Cards:** 1002 erros · 1419 cards ativos · taxonomia 288 temas. 🆕 **Fila de reforja: 272 abertas** (270 `nao_atomico` + 2 do F7).
- **Engenharia:** suite **621** · `auto_check --all` PASSED · **3 checks novos** (D5 **BLOCK**, consistencia, termo-sem-marcador) · ledger **99 ids**.
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem).
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s178 (2026-09-11, manha) -- ENGENHARIA

Detalhe integral em `history/session_178.md`.
🔴 **O fio da janela: quatro registros que ninguem conseguia manter a mao** -- o lexico do F7 (68 dias com 2 termos, 0,5% do baralho), a worklist de 270 nao-atomicos (47 dias, 202 repeticoes, porque **olhar nao tinha onde ser gravado**), a regra §7.2 em prosa (65 flags orfas) e as duas listas do gate de revogacao (digitadas, com o comentario do codigo prometendo que nao eram). **O remedio foi o mesmo nos quatro: parar de manter -- matar, mecanizar ou derivar.**
**Tres achados de graca:** **F96** (a suite escrevia no log de PRODUCAO a cada rodada, inflando o numero que o painel mostra) · **F97** (o passo do dia prescrevia `PREPARAR`, revogado ha 6 dias, porque o gate so varria markdown) · **o sensor que se acusou** (regex casando o `add_argument` da propria docstring).
🔬 **Os tres sensores da janela nasceram errados** e foram consertados **medindo antes de aceitar o numero**: G14 deu 2 achados e os 2 eram falsos; G10 deu 3 falsos de 5. Regra que sobrou nos dois: **lapide nao e mentira**, e **`PARCIAL` nao e contradicao** -- e o meio-termo declarado.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- **F7:** a CLASSE segue real e agora e **declarada nao-verificavel por gate** -- o instrumento morreu, o defeito nao.
- **F39:** o item entrega **onde registrar**, nao o conserto. O passivo so cai quando alguem triar -- e a precisao do detector **nao** foi re-medida (herda a calibracao da s128 + o FP declarado do card discriminador).
- **D5** mede **presenca, nao semantica** (flag generica infla a cobertura; *"flag em duas skills"* nao e reportada -- co-ocorrencia nao e prova) · **G10** isenta por **LINHA** · **G5** e sensivel a arquivo novo (tabela §7.4 se re-gera **por ultimo**) · **G14** ve **rotulo**, nao verdade · o **gate de revogacao** casa substring literal, e a isencao por SECAO nao existe em `.py`.
- Herdadas e vivas: **F35** (fidelidade ao Drive nao verificavel sem o F36) · **F89** (vocabulario, nao verdade) · **F79b** (ausencia de vinheta, nao suficiencia) · **F66** (34% de orfandade permanece) · **F64** (sessao que cruza a meia-noite: sintoma legivel, nao sensor) · **eixo C do F81** · **sitios gemeos do F80b** em `audit_fsrs.py`/`variancia.py`.

## Pendencias/observacoes ativas

- 🃏 **Reforja:** `python tools/reforja.py --fila` e a **unica cifra citavel** do passivo -- agora **272**, com resumo por motivo e `--limit`.
- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 46d sem sync (F72); Dashboard EMED x db medido pelo boot (F35).
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl`. Portador dele: `C:/Users/daanm/ai-eng/brain/interactions/2026-09-10-handoff-medhub-reforma-subagents.md`.
- 🧹 `tmp/s5_bloco1_patch.py` continua no repo -- scratch antigo, candidato a auto-higiene (§3.4) numa proxima passagem.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_178.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
