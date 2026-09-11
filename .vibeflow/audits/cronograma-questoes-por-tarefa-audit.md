## Audit Report: cronograma-questoes-por-tarefa (B4 / F77 + F77b, item 0.4)

**Verdict: PASS**

Classe **quick** (<=1h): a spec vive no proprio ledger (`AUDITORIA_MEDHUB.md` F77 e F77b, que ja
traziam evidencia, remedio S e remedio M escritos). Nao gerei spec redundante -- citacao >
reconstrucao. Suite: **503 passed** (baseline 496; +7) · `auto_check --changed` PASSED ·
2026-09-10 (s176).

---

### DoD (do remedio escrito no ledger)

- [x] **F77 -- `questoes` por tarefa persistidas com marca de confianca.** `grade.json` ganha
      `questoes` em toda task e `questoes_fonte` (na task e na semana), valores
      `link_no_bloco` | `rateio_igual`.
- [x] **F77 -- invariante no rebuild.** Se `sum(task.questoes) != total_questoes` da semana:
      **WARN nomeando a divergencia** + degradacao para o rateio igual **naquela semana**.
      Medido no PDF real: **27 semanas reconciliam, 3 degradam**. O dado bom viaja em 90% das
      semanas em vez de ser descartado em 100%.
- [x] **F77 (remedio M) -- o consumidor usa o dado.** `radar()` soma a cobertura por area com a
      contagem por tarefa quando `questoes_fonte` existe, e cai no rateio quando nao existe --
      `grade.json` anterior a esta sessao **nao quebra** (teste dedicado).
- [x] **F77b -- `Assunto:` reconhecido.** Regex passa a `(?:Livro Digital|Assunto):`. O literal
      antigo foi **ampliado, nao trocado** (teste dedicado para cada um).

### Evidencia medida (com o comando)

`python tools/cronograma.py --rebuild`, e o `grade.json` antes (git HEAD) x depois:

| medida | antes | depois |
|---|---|---|
| campo `questoes` na task | **ausente** | presente em 352 tasks |
| tarefas sem `tema` | **35** | **15** |
| ... das quais `revisao_questoes` | **32** | **12** |
| semanas com contagem por tarefa | 0 | **27 de 30** (3 degradam com WARN) |

S17, a semana que o achado usou de exemplo -- rateio igual daria **26,6q para toda tarefa**:

```
50q  Atencao Primaria a Saude no Brasil   (revisao)
43q  Cirurgia Vascular                    (revisao)
41q  Diarreia                             (revisao)
...
16q  Pneumonias Bacterianas               (teoria)
 0q  Atencao Primaria a Saude no Brasil   (teoria)
```

Bate exatamente com o intervalo que o ledger previu (**16q a 50q**) -- erro de ate 3x no rateio,
confirmado. O item de **0q** e a anomalia que o F77 ja havia resolvido por evidencia externa: no
xlsx do operador essa linha esta **riscada**. Dois sinais independentes concordando, de novo.

Os invariantes historicos do derivador seguem verdes no rebuild: `S10 = 273q`,
`S11-28 = 6689q`, `S11-28 = 222 tasks`, todas `area_norm` em `AREAS_VALIDAS`.

---

### Pattern Compliance

- [x] **Read-only sobre o `ipub.db`** — o derivador continua sem escrever no banco
      (`cronograma-contract.md`, fronteira dura). O diff so toca `grade.json` e o parser.
- [x] **Degradacao DECLARADA, nunca silenciosa** — a semana que nao reconcilia diz o porque em
      `stderr` **e** carrega `questoes_fonte: "rateio_igual"` no proprio dado. Quem consome nao
      precisa adivinhar se o numero foi medido ou rateado (D67: numero sem proveniencia envelhece
      mentindo).
- [x] **Lapide na regra revogada** — o comentario que instruia o rateio preventivo ganhou `⚰️`
      com o motivo e a medicao que o derrubou, no lugar onde ele vivia.
- [x] **Compatibilidade para tras** — leitor testado contra `grade.json` sem os campos novos.

### Critical Gate

**Limpo.** Zero escrita em banco, zero DDL, zero operacao destrutiva. O unico artefato regravado e
`core/cronograma/grade.json`, que e derivado e reconstruivel do PDF por `--rebuild`.

---

### Declarado, nao mascarado

As **15 tarefas que seguem sem tema** nao sao miss do parser: sao S29 ("Todas as Disciplinas",
7 tarefas) e S30 (5 tarefas multi-area, tipo "Pediatria e Cirurgia") -- semanas de revisao final
em que o PDF **nao tem** um assunto unico a extrair, mais 3 casos em S1/S4. O parser passou a
pegar tudo o que esta escrito; o que sobra nao esta escrito.

As **3 semanas que degradam para rateio** ficam com o motivo em `stderr` no rebuild. Nao investiguei
a causa da divergencia nelas -- e trabalho de conteudo sobre o PDF, nao do derivador, e o
mecanismo ja as trata corretamente.

---

**Ready to ship.**

2 hotfix docs not yet consolidated (`.vibeflow/hotfixes/2026-09-10-*.md`) —
ver `audit --consolidate-hotfixes`.
