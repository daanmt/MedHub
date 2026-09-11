## Audit Report: alinhamento-frente-do-card (B1 / F81, item 0.2)

**Verdict: PASS**

Spec: `.vibeflow/specs/alinhamento-frente-do-card.md` · Suite: **485 passed** (baseline antes
deste trabalho: 465; +20 da suite nova) · `auto_check --changed`: PASSED ·
Data: 2026-09-10 (s176).

---

### Veredito POR PREDICADO (o formato que o orquestrador pediu)

Comando unico que produziu as tres linhas -- os predicados rodados sobre o baralho ativo:

```
SELECT id, frente_contexto, frente_pergunta FROM flashcards
WHERE COALESCE(frente_contexto,'') <> '' AND COALESCE(frente_pergunta,'') <> ''
  AND COALESCE(needs_qualitative,0) < 2          -- 951 cards
```

| predicado | positivos (todos DISPARAM) | negativos (todos SILENCIOSOS) | populacao |
|---|---|---|---|
| **P1** `checar_contexto_redundante` | #673 (100%) · #525 (90%) · #664 (88%) | #284 | **12** |
| **P2** `checar_pergunta_generica_com_contexto` | #1574 · #1572 · #390 · #1571 | #284 | **4** |
| **P3** `checar_contrafactual_mal_formado` | #1568 | #1184 · #279 · #1060 · #1108 · #1572 · #293 | **1** |

16 asserções de fixture, 16 verdes (`tools/test_card_alinhamento_frente.py`, 20 testes).

🔴 **Os negativos carregam o peso da auditoria, e sao os certos.** Populacoes de 12/4/1 sao
pequenas o bastante para um predicado DECORAR o positivo; o que separa medicao de memorizacao e o
negativo que um regex ingenuo pegaria:
- **#284 x #1574** -- shape `A x B` identico. A diferenca e a TAREFA: *"qual a hipotese mais
  provavel?"* obriga a ler a vinheta, *"que achado separa uma da outra?"* nao. P2 acerta os dois.
- **#1184** -- a palavra "ausencia" na pergunta e o **nome da epilepsia**. Um predicado sobre a
  palavra solta acusaria um card bom.
- **#792 x #1568** -- mesmo desenho contrafactual; **#792 traz o "se presente"** e por isso e
  bem-formado. O par e o que DEFINE o P3 (`test_p3_o_condicional_e_o_que_separa...`).

---

### DoD Checklist

- [x] **1. P1 com corte parametrizado.** `CORTE_CONTEXTO_REDUNDANTE = 0.8` no topo do modulo, com
      a distribuicao medida (951 cards: >=0.7->26, >=0.8->12, >=0.9->4, ==1.0->3) escrita como
      proveniencia. `test_p1_corte_e_parametro_nomeado_e_nao_constante_enterrada` prova que baixar
      o corte MUDA o veredito -- sem isso o parametro seria decorativo.
- [x] **2. P2 exige a conjuncao.** Nao dispara sem contexto (`test_p2_exige_a_conjuncao_e_nao_so_o_par`)
      nem quando a pergunta manda aplicar ao caso.
- [x] **3. P3 deliberadamente estreito.** Exige deixis + verbo de exclusao + ausencia de
      condicional. 1 disparo em 7 cards com a palavra "ausente".
- [x] **4. DoD por CADA um dos 7 writers de `flashcards`** -- verificado por grep, nao assumido:

  | writer | veredito | evidencia |
  |---|---|---|
  | `tools/insert_questao.py` | roda | `:179` `validar_card` |
  | `tools/insert_card_base.py` | roda | `:88` `validar_card` |
  | `tools/insert_card_extra.py` | roda | `:42` `validar_card` |
  | `tools/recurate_cards.py` | roda | gate 6 novo, 3 predicados sobre a visao mergeada |
  | `app/utils/db.py::update_flashcard_fields` | roda | 3 predicados sobre a visao mergeada |
  | `tools/dedup_taxonomia.py` | **declarado: nao toca a frente** | `:87` unico UPDATE = `SET tema_id=?` |
  | `tools/normalize_taxonomia.py` | **declarado: nao toca a frente** | `:151` unico UPDATE = `SET tema_id=?` |

  🔴 **Achado da auditoria, corrigido dentro do proprio item.** Os dois caminhos de REFORJA
  (`recurate_cards.aplicar` e `db.update_flashcard_fields`) **nao chamam `validar_card`** -- rodam
  um subconjunto escolhido a dedo (encoding, template, resposta_embutida). Sem intervencao, os
  predicados novos nunca alcancariam justamente quem reescreve a frente, que e o F81 se repetindo
  um nivel acima. Ambos passaram a rodar os tres **sobre a visao MERGEADA** (payload por cima do
  valor armazenado): edicao parcial e legitima ali, e rodar so sobre o payload faria o predicado
  ver contexto vazio e ficar mudo -- gate verde por nao olhar.

- [x] **5. Contador de gate-miss com JANELA DECLARADA.**
      `python tools/audit_flashcard_quality.py --gate-miss` ->
      ```
      cards marcados por algum predicado : 18  (no baralho ativo: 17)
      JANELA (reason_servido preenchido) : 76 revisoes
      FORA da janela (anterior ao F76)   : 2642 revisoes — nao entram em nenhuma classe, por contrato
      [DECLARADO] A janela tem 76 revisoes; o contador so passa a informar com >= 300.
      ```
      Denominadores separados: as 2642 NULL sao reportadas **como fora**, com contagem visivel, e
      **nunca** como classe. O contador **nasce dizendo que nao sabe** em vez de nascer verde.
      O 18 x 17 (baralho inteiro x ativo) e explicitado na saida para nao divergir em silencio da
      populacao da spec -- a pergunta do gate-miss e historica, e card aposentado hoje pode ter
      sido servido ontem.
- [x] **6. Craftsmanship gate.** `auto_check --changed` PASSED; suite 485; `sync_skills --check`
      exit 0 (espelho da skill regenerado no mesmo commit, §10.3).

---

### Pattern Compliance

- [x] **Nucleo PURO em `card_checks.py`** — os tres predicados recebem dict e devolvem string ou
      `None`; zero I/O, zero excecao, zero `sqlite3`. Evidencia: `tools/card_checks.py`, docstring
      do modulo ("Nucleo PURO (zero I/O de banco)").
- [x] **Severidade por contrato, nao por palpite** — os tres entram em `validar_card` como
      `avisos`. `test_os_tres_sao_aviso_e_nunca_erro` fixa isso. Warning-first (`AGENTE.md §6`).
- [x] **Assinatura canonica em UMA skill (§7.2)** — a regua de autoria dos 3 defeitos vive em
      `.claude/commands/estilo-flashcard.md`; a spec nao a duplica, referencia.
- [x] **Zero LaTeX / ASCII limpo (`AGENTE.md §4.5`)** nos arquivos novos.
- [x] **Numero sem comando nao entra (D72)** — a spec carrega a distribuicao com a formula, e
      `test_populacao_medida_e_a_que_a_spec_declara` RE-MEDE contra o banco em vez de confiar no
      numero escrito.

---

### Critical Gate

**Limpo — nenhuma operacao destrutiva detectada.** Varredura do `git diff HEAD` contra o Rules
Catalog: zero ocorrencias de DROP/TRUNCATE/DELETE-sem-WHERE, mass delete, exec dinamico, segredo
hardcoded, TLS desligado ou debug ligado. O diff e composto de predicados puros, um novo modo
read-only de CLI, dois writers ganhando AVISO (nunca bloqueio novo) e documentacao. Nenhuma
escrita nova no banco; nenhum DDL.

---

### Ponto cego DECLARADO (nao e gap — e fronteira, e esta correta)

O **eixo C pleno** do F81 (a vinheta trabalha CONTRA a pergunta por razao semantica) continua
**nao coberto e declarado como tal**, com **#792** de sentinela em
`test_ponto_cego_declarado_o_eixo_C_pleno_nao_e_pego_por_nenhum_predicado`. A docstring do teste
instrui: se ele um dia falhar, a leitura e *"atualize a declaracao"*, jamais *"regressao"*.
Isto e lapide, nao prescricao (`AGENTE.md §10.8`, verification-stack).

Igualmente declarada: a **faixa 0.55-0.79** do P1 contem redundancia real que o corte 0.8 nao pega
(ex.: #1277, 0.750). 14 cards conhecidos e deliberadamente fora, ate o passivo de 12 zerar.
Escrito na spec para que ninguem leia o verde do gate como "nao ha mais redundancia".

---

### Nota de proveniencia (decisao registrada)

A ordem selada mandava usar **#1568/#1574** como fixtures do **primeiro** predicado. A medicao
desmentiu (0.056 e 0.091, o chao da distribuicao) e o item PAROU para bifurcacao em vez de
afrouxar o corte ate os fixtures caberem -- o que teria sido inventar a metrica. Decisao do
`/ai-eng` em 10/09: GO aos tres predicados nomeados, corte 0.8, com as tres condicoes de forma
(fixture negativo por predicado · #792 como sentinela · contador com janela declarada), todas
implementadas e auditadas acima.

---

**Ready to ship.**

2 hotfix docs not yet consolidated (`.vibeflow/hotfixes/2026-09-10-*.md`) —
ver `audit --consolidate-hotfixes`.
