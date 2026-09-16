# Notas de implementacao -- plano-ssot-e-cards-v2-part-1

Coding Agent, 2026-09-16. Ver relatorio completo no handback ao orquestrador.

## Divergencias da spec (declaradas, nao corrigidas por conta propria)

1. **DoD 4 diz "total_questoes: 10218.5"**. O `--rebuild` real (e toda a
   documentacao historica -- `.vibeflow/decisions.md`, `history/session_106.md`,
   `history/session_107.md`, `.vibeflow/prds/extensivo-cronograma-deep-research.md`)
   diz **10218** (inteiro), sempre. Tratado como typo da spec; nao alterei
   `parse_grade`/`rebuild` (fora do anti-scope) e o `--rebuild` real bate 352/10218
   como sempre bateu.

2. **"Radiologia" nao esta em `core/areas.json`.** Decisao tomada (autorizada pela
   spec: "use Multi ou proponha"): `Multi`, documentada em
   `normaliza_area_extensivo()` e em `cronograma.md`. 6/735 tarefas (0,8%).

3. **`--expect-tasks N` destrava a checagem INTEIRA** (tarefas E semanas, contra o
   que o parser efetivamente encontrou), nao so a contagem de tarefas. A spec
   define um unico flag para "o PDF do EMED mudou de verdade"; duas valvulas
   separadas exigiria uma 2a flag que a spec nao previu (violaria a doc-e-so-uma
   skill do D5).

## Achados durante o parse do PDF real (nao previstos no prototipo)

- **Marca d'agua** ("Medicina livre, venda proibida, twitter @Livremedicina",
  2100x no doc) cola na ultima tarefa do Resumo de CADA semana (ela nao tem
  "Tarefa N+1" pra bounda-la) e quebra o `_TIPO_EXT_RE` (ancorado em fim-de-linha).
  Sem o filtro, 51/735 tarefas caiam em `tipo_norm='outro'`. Filtro global em
  `parse_extensivo_text` (constante `_WATERMARK_EXT`) resolveu -- 0 tarefas em
  'outro' no rebuild real.
- **Disciplina abreviada** ("Preventiva", "Hepato", "Gastro", "Hemato", "Reumato",
  "Endocrino", "Cardio", "Neuro", "Pneumo", "Infecto", "Dermato", "Otorrino",
  "Oftalmo") aparece a partir de certas semanas (S20+ p/ Preventiva, S29+ p/ as
  demais) -- o prototipo ja prevcirca isso (`CANON` dict) mas eu tinha simplificado
  na 1a passada. Portado como `_EXTENSIVO_DISC_ALIASES`.
- **Semana 52 ("Revisao Final") lista disciplinas encadeadas** por tarefa (ex.
  "Cardio, Psiquiatria e Nefro") -- nao e uma disciplina de nome comprido, e uma
  task genuinamente multi-area. Sem tratamento, virava a 1a disciplina da lista
  sozinha (errado). `_eh_tarefa_multi_disciplina` detecta o conector (","/"e")
  seguido de outra disciplina conhecida e reclassifica p/ `Todas as
  Disciplinas`/`Multi`. Mesmo padrao pegou a Semana 50 ("Otorrinolaringologia e
  Oftalmologia" etc, 6 tarefas).

## Limitacao cosmetica conhecida (nao bloqueante)

- `assunto` da S52 T7 mostra "Reumato, Ortopedia, Otorrino, Der - | mato e
  Oftalmo" -- o PDF hifeniza "Dermato" na quebra de linha ("Der-\nmato") e o
  heuristico de wrap (trailing-space = continuacao) nao reconhece hifenizacao
  tipografica, so espaco. Afeta 1/735 tarefas (a ultima da Semana 52, ja um
  catch-all multi-disciplina); `area_norm`/`tipo_norm`/`n_links_questoes` dessa
  task estao corretos, so o texto do `assunto` tem o artefato. Nao corrigido por
  ser overfit de 1 palavra especifica com risco de regressao em texto legitimo
  que termina em hifen.
