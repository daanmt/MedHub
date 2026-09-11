# Spec: Alinhamento interno da FRENTE do card (B1 / F81)

> Escrita em 2026-09-10 (s176), item **0.2** do Tier 0. Ordem: `/ai-eng` N=78, regime D71.
> Ledger: `AUDITORIA_MEDHUB.md` F81 · inventário `docs/MEMORIA-AUDITORIA.md §11`.
> **Toda medição abaixo foi feita nesta sessão, com o comando registrado.** Número sem
> comando não entra em spec (D72).

## Objetivo

Fechar o eixo de defeito que `card_checks.py` **não** mede: o alinhamento entre
`frente_contexto` e `frente_pergunta`. Todo predicado existente compara **frente x verso**
(`checar_resposta_embutida`) ou olha a pergunta isolada. A relação interna da FRENTE está
inteiramente fora de cobertura -- e foi de lá que saíram os três últimos defeitos achados por
leitura humana, não por gate (família F79 / F79b / F81).

## Contexto

Origem (s170): o usuário sinalizou "reforja" em três cards do mesmo bloco e nomeou o padrão --
*"parece que contexto e pergunta 'falam de coisas diferentes'"*. A intuição estava certa e era
**agregada**: os cards que ele juntou sob um sintoma percebido são, medidos, defeitos de três
naturezas distintas. Tratá-los como um só levaria a corrigir o passivo errado.

🔴 **Por que esta spec tem três predicados e não um.** A ordem original mandava usar **#1568** e
**#1574** como fixtures do primeiro predicado (containment contexto->pergunta). A medição
desmente:

```
containment = |tokens(ctx) ∩ tokens(perg)| / |tokens(ctx)|   (_norm_tokens de card_checks.py)
sobre 951 cards ativos com contexto E pergunta preenchidos
  >= 0.5 -> 91 | >= 0.6 -> 48 | >= 0.7 -> 26 | >= 0.8 -> 12 | >= 0.9 -> 4 | == 1.0 -> 3
  #673 1.000 · #525 0.900 · #664 0.875 · #321 0.467 · #1574 0.091 · #243 0.095 · #1568 0.056 · #792 0.000
```

**#1568 (0.056) e #1574 (0.091) estão no chão da distribuição.** Forçá-los no predicado de
containment exigiria afrouxar o corte até ~0.05, varrendo metade do baralho -- inventar a
métrica para o painel ficar verde, exatamente o que `AGENTE.md §10.8` proíbe. Cada fixture passa
a viver sob a métrica que de fato o descreve (bifurcação levada ao `/ai-eng` e decidida em
10/09: GO aos três predicados, corte 0.8, com três condições de forma incorporadas abaixo).

## Definition of Done

1. **P1 `checar_contexto_redundante` (eixo A) -- WARN.** Dispara quando
   `containment >= CORTE_CONTEXTO_REDUNDANTE` (**0.8**, parâmetro nomeado no módulo, nunca
   constante enterrada no corpo da função). Fixtures **positivos**: #673 (1.000), #525 (0.900),
   #664 (0.875). Fixture **negativo**: **#284** (0.000) -- vinheta com dado concreto (RN de 16 h,
   vômitos biliosos, dupla bolha) que a pergunta precisa. População hoje: **12 cards**.
2. **P2 `checar_pergunta_generica_com_contexto` (conjunção) -- WARN.** Dispara **só na
   conjunção**: a pergunta nomeia um par `A x B` **E** pede um **discriminador geral** (*"qual das
   duas"*, *"que achado separa/distingue/diferencia"*, *"presente em X e ausente em Y"*) **E**
   existe `frente_contexto` não-vazio. Não dispara quando a pergunta manda **aplicar ao caso**
   (*"qual a hipótese mais provável"*, *"qual o diagnóstico"*, *"qual a conduta"*) -- aí a vinheta
   é load-bearing. Fixtures **positivos**: **#1574**, #1572, #390, #1571. Fixture **negativo**:
   **#284** -- mesmo padrão `A x B`, mas pergunta de aplicação. População do shape `A x B` com
   contexto: **5 cards**; 4 disparam, 1 não.
3. **P3 `checar_contrafactual_mal_formado` (sub-forma estreita do eixo C) -- WARN.** Dispara
   quando a pergunta afirma que um achado está **ausente NESTE quadro** (`ausente`/`ausência` +
   dêixis: *"nesse quadro"*, *"neste caso"*, *"no quadro"*) **E** usa verbo de exclusão
   (`afastaria|descartaria|excluiria|fecharia`) **E não** traz o condicional que tornaria a
   pergunta bem-formada (*"se estivesse presente"*, *"caso estivesse"*). Fixture **positivo**:
   **#1568**. Fixtures **negativos**: **#1184** (*"perda de consciência (ausência)"* -- aqui
   "ausência" é o **nome da doença**, e um regex ingênuo sobre a palavra dispararia) e **#279**
   (*"a ausência de bolha gástrica aponta para..."* -- a ausência é o achado real e o verbo não é
   de exclusão). População com `ausente|ausência` + contexto: **7 cards**; 1 dispara, 6 não.
4. **DoD por CADA um dos 7 writers de `flashcards`.** Para cada writer da allowlist F49, o
   veredito é binário e escrito: *roda os três predicados* ou *declaradamente não toca
   `frente_contexto`/`frente_pergunta`*. Nenhum fica sem linha.
   | writer | veredito exigido |
   |---|---|
   | `tools/insert_questao.py` | roda (cunha card novo com os 5 campos) |
   | `tools/insert_card_base.py` | roda (cunha card de andaime) |
   | `tools/insert_card_extra.py` | roda (cunha card vinculado a erro) |
   | `tools/recurate_cards.py` | roda (reescritor in-place canônico) |
   | `app/utils/db.py::update_flashcard_fields` | roda (caminho da reforja) |
   | `tools/dedup_taxonomia.py` | declarado: só reaponta `tema_id`, não toca a frente |
   | `tools/normalize_taxonomia.py` | declarado: só reaponta `tema_id`, não toca a frente |
5. **Contador de gate-miss com JANELA DECLARADA.** Reporta, por classe lida de
   `fsrs_revlog.reason_servido`, quantas revisões de cards que os predicados pegariam foram
   servidas. 🔴 **Denominadores separados:** a janela é `reason_servido NOT NULL` (revisões
   posteriores ao F76, s174) -- hoje **76 linhas** (`agendado` 55 · `novo` 10 · `vencido` 9 ·
   `fresh_error` 2) contra **2642 NULL**, que são reportadas como **"fora da janela"** com
   contagem visível, **nunca** como uma classe. Com 76 linhas o contador **ainda não informa**:
   a saída declara isso literalmente e só passa a emitir leitura a partir de **>= 300 revisões
   dentro da janela**. Nasce dizendo que não sabe, em vez de nascer verde.
6. **Craftsmanship gate:** `python -X utf8 tools/auto_check.py --changed` verde; suíte completa
   verde (baseline **465**); ASCII limpo, sem seta Unicode nem LaTeX (`AGENTE.md §4.5`).

## Promote: `fsrs_revlog.reason_servido` é CAMPO, não instrumentação (item 0.7, s176 -- F76)

> Promovido em 10/09/2026 porque é comportamento **permanente** e estava sem portador: vivia como
> detalhe de um hotfix. Este spec é o portador certo -- o contador do DoD 5 acima **existe por causa
> dele**, e quem for reimplementar a leitura precisa achar a regra antes, não depois.

`reason_servido` é o bucket **recomputado no ato da gravação** (`db.bucket_de`, função pura, sobre
`state`/`due`/`questao_id` do card **antes** da revisão), gravado em toda linha de `fsrs_revlog` por
`record_review`. Ele não é telemetria opcional: é a **única** resposta confiável a *"por que este
card apareceu?"*, porque `selection_reason` é o que o **chamador alegou** e pode divergir do estado
real da fila. A divergência `selection_reason != reason_servido` é **WARN em stderr, nunca bloqueio**
-- a revisão do usuário jamais é derrubada por discordância de rótulo -- e fica consultável por SQL.

🔴 **A consequência que governa quem usar o campo:** `NULL` significa **"revisão anterior ao F76"**,
e isso é **fora da janela**, nunca uma classe. Qualquer leitura que trate `NULL` como um bucket
inventa uma população que não existe. Toda métrica construída sobre ele declara **os dois
denominadores** (dentro e fora da janela) e declara também quando a amostra ainda é pequena demais
para informar -- é o que o DoD 5 faz ao se calar abaixo de 300 revisões. Norma de fundo:
`AGENTE.md §10.8` (*verification-stack*) -- eixo conhecido e não verificável se declara, não se
maquia.

## Escopo

- `tools/card_checks.py`: +3 predicados puros + o parâmetro de corte nomeado; os três entram em
  `validar_card` como **avisos** (WARN), nunca como `erros`.
- `tools/test_card_alinhamento_frente.py` (novo): fixtures positivos E negativos por predicado,
  mais o teste de população que re-mede a distribuição com o comando.
- `tools/audit_flashcard_quality.py` ou CLI equivalente: o contador de gate-miss com janela.
- `.claude/commands/estilo-flashcard.md`: a régua de autoria ganha os três defeitos nomeados.

## Anti-escopo

- 🔴 **Não promover a BLOCK.** Warning-first (`AGENTE.md §6`): vira BLOCK quando o passivo zerar,
  não antes. Os três nascem WARN.
- 🔴 **Não medir o eixo C pleno com regex.** P3 é uma **sub-forma estreita** dele. O eixo
  contrafactual semântico -- **#792**, vinheta de crise inequivocamente epiléptica pedindo o
  achado de crise NÃO epiléptica -- continua **declarado não-verificável**. Ver §Ponto cego.
- Não reforjar os cards do passivo: os 12 do P1 são fila de reforja de FRENTE (remédio M do F81,
  `cards_regen_queue.py`), e a reforja é do operador.
- Não tocar FSRS, agendamento, estabilidade ou o texto clínico de card algum.
- Não mexer no corte 0.7 citado no F81: ele foi estimado sobre 904 cards e esta spec o substitui
  por 0.8 com a medição de hoje (951 cards) escrita como proveniência.

## Ponto cego DECLARADO (não é bug, é fronteira)

**#792 é sentinela, não teste.** Vinheta de crise inequivocamente epiléptica; pergunta cobra
*"qual achado apontaria para crise NÃO epiléptica"*. `containment 0.000`, `maior_run 0`: nenhuma
das três métricas o alcança, e nenhuma alcançará -- o defeito é a **relação semântica** entre
vinheta e pergunta. A suíte registra #792 como **ponto cego declarado**: se algum dia um
predicado passar a pegá-lo, isso significa **atualize a declaração**, jamais "regressão".
É lápide, não prescrição (`AGENTE.md §10.8`, corolário *verification-stack*).

**Faixa 0.55-0.79 do P1, também declarada:** contém redundância real que o corte 0.8 não pega
(ex.: **#1277**, 0.750, cujo contexto a pergunta reengole quase inteiro). São **14 cards**
conhecidos e deliberadamente fora -- o corte aperta quando o passivo de 12 zerar, não agora.
Declarado aqui para que ninguém leia o verde do gate como "não há mais redundância".
