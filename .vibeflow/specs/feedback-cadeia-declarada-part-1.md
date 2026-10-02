# Spec: Feedback por elo declarado -- part 1: contrato da cadeia v3 + conferência pela API

> Escrita em 2026-10-02 (s211). PRD: `.vibeflow/prds/feedback-cadeia-declarada.md` (Scope v0, item 1).
> Ordem de execução do PRD: part-1 -> part-2 -> part-3 -> part-4 -> part-5 -> part-6.
>
> 🔴 **Emenda de 02/10/2026 (mesma sessão, decisão do autor da spec):** a conferência do comentário pela API SAIU desta part e virou a `part-1b` (BLOQUEADA). O classificador de permissões do harness negou a edição que acrescentava `--comentario` em `tools/emed_api.py` (motivos declarados: `[PII Data Handling]` e `[Instruction Poisoning]`). Ninguém contornou: o subagente reverteu o que tinha entrado no arquivo e parou. O que segue abaixo marcado com ⚰️ foi movido; o resto do contrato v3 não depende da API. A REGRA DURA "sem ler o comentário do professor" do brief **continua em vigor** até a part-1b ser destravada pelo operador.

## Objetivo

A cadeia de cada questão passa a ser uma sequência de raciocínio que o aluno consegue autoavaliar (identificar -> recordar -> descartar), validada por um contrato novo (`versao: 3`), e o agente ganha um caminho para CONFERIR o comentário do EMED em caso de dúvida, sem gravá-lo.

## Contexto

Hoje (`versao: 2`, `docs/SOLUCAO-MEDHUB-BRIEF.md`, `db.solucao_v2_problemas`):

- o elo é uma habilidade abstrata no infinitivo, "sem detalhe desta questão" (ex.: "Situar o corte do açúcar");
- cada alternativa errada carrega `elo: k`, "o elo cuja falha leva a ela" -- é isso que a página usa para pintar a "provável quebra". Medido em 02/10/2026 no db do hub: 5 das 7 análises (t26, t96) foram refeitas com o racional declarado; na t96 Q17 a letra marcada cai no elo 1, que ele tinha firme, e a lacuna era o elo 2, para o qual nenhuma alternativa aponta;
- há cadeias que não são sequência: t96 Q8 = 4 julgamentos paralelos, um por alternativa; t96 Q14 = um elo que engole 3 alternativas.

O operador nomeou os defeitos (02/10): "cadeia mal construída" e "alternativa no elo errado". E decidiu, no mesmo dia: *"Em caso de dúvidas sobre as habilidades, você pode CONFERIR o comentário/resolução do EMED via api, bem como checar nas apostilas/resumos, e criar a nossa própria sequência - desta forma nos mantemos autorais."* Isso reverte EM PARTE a decisão de 26/09 (brief: "REGRA DURA: sem ler o comentário do professor"; `emed_api.py`: o comentário "morre em memória -- nunca em disco, log, `tmp/`, stdout").

**Fricção que esta spec remove:** o agente refazer a análise depois do racional porque a cadeia não permitia localizar a quebra -- viciosa. A fricção virtuosa (racional e declaração do aluno) é protegida: a part-2 a torna o dado primário.

## Definition of Done

1. **Validador v3.** `db.solucao_v3_problemas(doc, catalogo=None)` devolve `[]` para o exemplo do brief e nomeia cada defeito abaixo, um teste por defeito em `tools/test_emed_banco.py` (`test_solucao_v3_*`):
   cadeia com menos de 2 ou mais de 4 elos; elo sem `elo`, `chave`, `habilidade` ou `tipo`; `tipo` fora de `identificar | recordar | descartar`; 1o elo que não é `identificar`; nenhuma `recordar`; ordem violada (identificar antes de recordar antes de descartar); `descartar` sem `letra`, com letra inexistente ou com a letra certa; alternativa sem `porque`; número de certas diferente de 1; `pede` vazio; `objetivo` fora da lista fechada.
2. **Convivência v2/v3.** `db.solucao_problemas(doc)` despacha por `versao` (3 -> v3; senão v2); `solucao_estruturada` devolve o dict para `versao` 2 e 3; `emed_upsert_solucoes` grava doc v3 válido e continua gravando doc v2 (os testes v2 existentes passam SEM alteração).
3. ⚰️ *Conferência pela API (`emed_api.py --comentario NUM`): movida para a `part-1b` em 02/10/2026 -- edição barrada pelo classificador.* Nesta part: `tools/emed_api.py` e `tools/test_emed_api.py` ficam INTOCADOS e `test_propriedade_nada_alem_da_whitelist_chega_a_disco_ou_saida` segue verde.
4. **Brief reescrito para a v3**, com o exemplo JSON validado por teste (`test_exemplo_do_brief_passa_no_validador`: extrai o bloco do brief e roda o validador), e a cláusula "cada errada aponta o elo cuja falha leva a ela" revogada com o rito de 3 passos do `AGENTE.md §10.10` no mesmo commit: lápide (`⚰️` + data + motivo) no brief e em `.claude/commands/banco-emed.md` §Solução MedHub, e o termo no registro do gate (`docs/MEMORIA-AUDITORIA.md` §12). Gate `CONTRATO_REVOGADO` verde. ⚰️ *A revogação de "sem ler o comentário do professor" foi para a part-1b.*
5. **Harness:** `python tools/sync_skills.py --check` exit 0; `python -X utf8 tools/auto_check.py --changed` PASSED; `python -m pytest tools/ -q` verde.
6. **Craftsmanship:** nenhum `import sqlite3` fora de `app/utils/db.py`; nenhum valor do comentário em mensagem de recusa, log ou arquivo; português com acentos e pontuação ASCII (`->`, `--`) em brief, skill e docstrings.

## Scope

**Contrato v3** (o doc que o subagente de cunhagem grava em `<BASE>/solucoes/<lista>_<n>.json`):

```json
{
  "lista": "t26", "num": 15, "versao": 3,
  "objetivo": "DM prévio x DMG",
  "pede": "Hipótese e conduta em gestante de 7 semanas com GJ 116 e 108 e HbA1c 6,8%.",
  "cadeia": [
    {"tipo": "identificar", "elo": "Identificou que as duas GJ (116 e 108) estão na faixa de DMG, não de DM prévio.",
     "chave": "GJ 92-125 = DMG; GJ >= 126 = DM prévio.", "habilidade": "Classificar a glicemia de jejum do 1º trimestre"},
    {"tipo": "recordar", "elo": "Recordou que HbA1c >= 6,5% na 1ª consulta fecha DM prévio e prevalece sobre a GJ.",
     "chave": "HbA1c >= 6,5% no 1º trimestre = DM diagnosticado na gestação.", "habilidade": "Aplicar o critério de DM prévio pela HbA1c"},
    {"tipo": "descartar", "letra": "B", "elo": "Descartou o DMG (B) porque a HbA1c de 6,8% o exclui.",
     "chave": "As GJ sozinhas dariam DMG; a HbA1c decide.", "habilidade": "Usar o achado que exclui o diagnóstico concorrente"}
  ],
  "alternativas": {
    "A": {"certa": true, "porque": "HbA1c 6,8% fecha DM prévio; o tratamento começa já."},
    "B": {"porque": "As duas GJ sozinhas dariam DMG, mas ignora a HbA1c >= 6,5%."},
    "C": {"porque": "TOTG não se faz com GJ já alterada: o diagnóstico já está feito."},
    "D": {"porque": "GJ >= 92 tira a gestante do rastreio de rotina de 24-28 semanas."}
  },
  "divergente": false, "conferir": "", "fontes": "Consenso OPAS/MS/FEBRASGO/SBD 2017"
}
```

Regras que o brief passa a carregar:

- **2 a 4 elos, em sequência:** `identificar` (o dado do enunciado que classifica o cenário) -> `recordar` (o critério/regra que decide) -> `descartar` (0 a 2: só os distratores FORTES, com o dado que os exclui; `letra` obrigatória). Nunca um elo por alternativa; nunca elo que só repete o gabarito.
- **`elo` = frase sobre ESTA questão**, verbo no pretérito ("Identificou ...", "Recordou ...", "Descartou ..."), que o aluno responde com Sim / Incerteza / Desatenção / Não. 1 linha.
- **`habilidade` = rótulo reutilizável** entre questões (infinitivo, sem detalhe do caso) -- é a entrada do ledger de habilidades.
- **`alternativas`:** toda letra com `porque` (1 frase); exatamente uma `certa`. Alternativa errada NÃO carrega mais `elo` (presente = ignorado).
- Enunciado negativo (EXCETO/INCORRETA): o 1o elo `identificar` é a leitura do comando.
- **Fontes, nesta ordem:** resumos (`get_topic_context`) -> apostila do EMED em PDF dentro de `resumos/` -> `/pesquisar-evidencia` para afirmação decisiva. ⚰️ *A conferência do comentário pela API (subagente devolve "dúvidas de habilidade", o principal confere com `emed_api.py --comentario`) foi para a part-1b.* Enquanto isso, dúvida que resumos e apostilas não fecham vira `divergente` + `conferir`, como já era.

**Arquivos (5):** `docs/SOLUCAO-MEDHUB-BRIEF.md` · `app/utils/db.py` · `tools/test_emed_banco.py` · `.claude/commands/banco-emed.md` (+ espelho gerado por `sync_skills`) · `docs/MEMORIA-AUDITORIA.md` (o registro do termo revogado).

## Anti-scope

- A seção "Estado por elo" do brief e qualquer coisa da página (`core/templates/hub.html`, `tools/test_hub_render.py`): é a part-2.
- Recunhar t40/t49 (operação de conteúdo do principal, depois desta part, pelo rito do `/banco-emed`).
- Migrar docs v2 existentes; apagar o validador v2.
- Conferência em lote, cache do comentário, ou comentário gravado em `tmp/`.
- `emed_banco.py` (`--erros`, leitura metacognitiva): part-5.

## Technical Decisions

- **Versão nova em vez de mexer na v2:** t26/t96 têm respostas e análises ligadas à cadeia v2 (índices `quebrou`/`estados`); reescrever a v2 quebraria o histórico. Custo: dois validadores até a v2 sair de uso.
- **`descartar` carrega `letra`:** é o único vínculo alternativa-elo que sobrevive, e serve só para apontar CONFLITO determinístico na part-2 (declarou "Sim" em "Descartou B" e marcou B). Não pinta nada.
- **Comentário só em stdout, uma questão por corrida:** é o mínimo que deixa o agente ler para conferir e preserva o resto da fronteira (nada em disco, nada no hub). Trade-off declarado: stdout entra no transcript da sessão local.
- **Token só no principal:** o subagente de cunhagem não faz chamada credenciada; devolve dúvidas.

## Applicable Patterns

- `patterns/db-access-layer.md` (validador e upsert moram em `db.py`).
- `patterns/warn-first-check.md` (gate `CONTRATO_REVOGADO`, D5).
- Convenções: skill canônica + `sync_skills`; CLI com assinatura em UMA skill (`/banco-emed`).

## Risks

- **A API mudar o campo do comentário** (interna, sem contrato): recusa nomeada + `--esquema`; o teste usa fixture sintética, o campo real foi visto no `--esquema` de 27/09.
- **Cadeia v3 virar fórmula** (sempre 1-1-1): a régua de defeito do PRD (até 10% das questões sinalizadas nas listas de aceitação) é o sensor; acima disso o brief volta para revisão.
- **Paráfrase do comentário escapar para a cadeia:** sem gate possível (semântico); declarado como não-verificável no brief.

## Dependencies

Nenhuma.
