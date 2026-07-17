# PRD: Cunhagem de flashcards alimentada pelo corpus EMED 2024

> Generated via /vibeflow:discover on 2026-07-17

## Problem

O fluxo atual de autoria de flashcards do MedHub (erro -> `insert_questao.py` -> card) produz **"paragraph cards"**: cada card empacota `frente_contexto` + `frente_pergunta` + `verso_resposta` + `verso_regra_mestre` + `verso_armadilha` num item unico. Isso viola o **minimum information principle** (Wozniak): o card testa varios fatos de uma vez, o aluno acerta parte, marca "Bom", e os pedacos esquecidos somem (illusion of competence). Auditoria do usuario (sessao 17.07) reprovou a safra recente: cards double-barreled (833: progesterona E aromatase), sim/nao com payload no verso (350, 398), sets/enumeracoes (835: ranking de sitios).

O usuario possui uma **referencia de ouro**: o curso EMED 2024 Extensivo completo, cujos flashcards (`Flashc.pdf`, 1 por tema) sao o oposto — **atomicos**: frente gerativa curta, resposta de uma frase, zero armadilha embutida; a consciencia da pegadinha emerge da **cobertura do deck + discriminacao por adjacencia**, nao de um aviso empacotado. Hoje esse corpus vive isolado num HD externo, sem alimentar a cunhagem.

## Target Audience

Usuario unico (o estudante-dono do MedHub) e o **agente cunhador** (Claude, operando o fluxo analisar-questao -> insert_questao). O agente e o consumidor direto do corpus e do padrao de autoria.

## Proposed Solution

Duas frentes:

**D1 — Colheita do corpus.** Copiar os 275 `Flashc.pdf` de `D:\Med\Estrategia 2024 Extensivo\Extensivo\<Especialidade>_-_Extensivo\<Tema>\<Tema>\Flashc.pdf` para `resumos/<area>/Flashcards - <Tema>.pdf` (espelhando o exemplo manual `resumos/GO/Flashcards - Endometriose.pdf`), com mapeamento correto de area (EMED -> taxonomia resumos). PDFs gitignored (IP do EMED, politica s086). Extrair o texto de cada deck (frente=pagina impar, verso=par, limpar watermark "Estrategia MED") para um store leve buscavel, para que a cunhagem localize os cards relevantes por tema/conceito.

**D2 — Religar a cunhagem (modelo: SELECAO POR CONTEXTO).** Quando um card e cunhado (gatilho = erro OU tema fraco OU lacuna declarada), o agente **consulta o deck EMED do tema** e puxa **so os cards que casam com o gap especifico** (o elo metacognitivo quebrado), reformulando-os no padrao atomico. **Nunca importa o deck inteiro por padrao.** O corpus EMED e biblioteca de referencia + fonte de cobertura + molde de estilo — nao um despejo no FSRS. Preserva a filosofia error-driven (personalizacao que o EMED nao tem) e o teto de 30 cards/dia.

O novo **padrao de autoria atomico** (a codificar em `/estilo-flashcard`): 1 fato por card; frente gerativa curta (nunca sim/nao com payload no verso); resposta de uma frase; o "porque"/mecanismo vai entre parenteses (lido-depois, nao recuperado) ou vira um card discriminador proprio (estilo interference-busting); evitar sets/enumeracoes (cloze ou cards ordenados); fonte+data em fato banca-dependente. Mantem o TARGETING metacognitivo (o card mira o elo que quebrou), troca a FORMULACAO (adota o formato EMED).

## Success Criteria

1. Os 275 `Flashc.pdf` estao em `resumos/<area>/Flashcards - <Tema>.pdf` com area correta — 0 arquivos perdidos, 0 misfiled (verificavel por contagem + spot-check por especialidade).
2. O texto de cada deck EMED esta extraido e **buscavel por tema/conceito** pelo agente na cunhagem.
3. `/estilo-flashcard` reescrito com o padrao atomico (as regras + antes/depois EMED) e vira o contrato de autoria vigente.
4. O fluxo `analisar-questao` (skill + workflow + `insert_questao.py`) **consulta o deck EMED do tema** e, quando ha match, cunha card(s) atomico(s) no formato novo ancorados no elo do erro. Demonstravel end-to-end num tema com deck disponivel (ex.: Endometriose).
5. Regressao: cunhagem de um erro num tema SEM deck EMED continua funcionando (fallback gracioso).

## Scope v0

- Colheita dos **275** decks agora (HD montado), com mapeamento de area e rename.
- Extracao de texto + indice leve buscavel dos decks.
- Reescrita de `/estilo-flashcard` (padrao atomico + referencia EMED).
- Passo de "consulta ao deck EMED + selecao por contexto" no fluxo de cunhagem (`analisar-questao.md` skill, `analisar-questoes.md` workflow, e o que `insert_questao.py`/engine exigirem para receber cards ja-atomicos).
- Reforja-piloto do cluster ja auditado (Endometriose 831-835 + os flagados 350/398/757/759) no padrao novo, como prova.
- Uso de **/workflows** no /implement para paralelizar colheita + extracao/indexacao dos 275 PDFs.

## Anti-scope

- **Import em massa de deck** como cards FSRS (rejeitado: ~6.000 cards detonariam a fila e a estrategia "matar os cards"). Selecao e sempre a-dedo, dirigida por contexto.
- Cards de imagem / OCR (extracao e text-only; decks image-heavy ficam como referencia visual, sem virar card automatico).
- Mudanca no algoritmo FSRS (`app/utils/fsrs.py`) ou no agendamento.
- UI Streamlit.
- Reescrita do RAG canonico (`app/engine/rag.py`); reusar/estender so se a busca nos decks exigir, sem trocar o motor.
- Gate de evidencia do card 760 (segue em trilha propria).

## Technical Context

- **Pipeline canonico** (`.vibeflow/patterns/error-insertion-pipeline.md`): `insert_questao.py` faz a transacao atomica (questoes_erros + flashcards + fsrs_cards + taxonomia). Cards nascem `qualitative` quando `--frente_pergunta` + `--verso_resposta` vem juntos. Os campos `--verso_regra_mestre`/`--verso_armadilha` sao o "paragraph card" a enxugar (mover para parentese/lido-depois ou card discriminador).
- **Contrato de autoria** = `.claude/commands/estilo-flashcard.md` (assinatura canonica; espelho gerado em `.agents/skills` via `sync_skills.py` — regenerar).
- **Corpus EMED**: estrutura regular `<Esp>_-_Extensivo\<Tema>\<Tema>\Flashc.pdf`; tema = nome da pasta (underscore->espaco, acentos preservados). Extraivel por PyPDF2 (frente impar / verso par; watermark "Estrategia MED"). Deck de Endometriose = 25 cards, validado.
- **Mapeamento de area EMED -> resumos** (derivar do layout real de `resumos/`): Ginecologia/Obstetricia -> GO; Cardiologia/Dermatologia/Endocrinologia/Gastroenterologia/Hematologia/Hepatologia/Nefrologia/Neurologia/Pneumologia/Reumatologia -> Clinica Medica/<esp>; Pediatria -> Pediatria; Medicina Preventiva -> Preventiva; Cirurgia -> Cirurgia. Bordas a confirmar: Infectologia, Psiquiatria, Ortopedia (ver Open Questions).
- **Politica de PDF** (s086): PDFs do EMED sao mantidos gitignored dentro de `resumos/` (IP; RAG local). `*.pdf` ja no `.gitignore`. Consistente com a colheita.
- **Selecao por contexto**: o sinal de gap ja existe (elo quebrado do erro, `taxonomia_cronograma.dificuldade`/area-fraca, `day_plan`/weak_areas). A busca no deck EMED casa o conceito do gap com os cards do tema.
- **Harness**: `auto_check.py` (WARN-first) valida mudancas estruturais; rodar `--changed` antes de reportar (Reflexo Autonomo §1.3). `sync_skills --check` acusa drift command<->skill.

## Open Questions

1. **Mapeamento de area em bordas:** onde vivem os resumos de Infectologia, Psiquiatria e Ortopedia no `resumos/` atual? (Resolver conferindo o layout real no gen-spec; nao inventar pasta nova sem confirmar.)
2. **Reconciliacao de nome de tema:** o nome da pasta EMED (`Sindrome_dos_Ovarios_Policisticos`) nem sempre bate com o `tema` do `taxonomia_cronograma`/nome do resumo. A cunhagem precisa achar o deck certo dado um tema — definir a estrategia de match (exato + fuzzy/alias) no gen-spec.
3. **Store do indice buscavel:** ChromaDB (reusar `app/engine/rag.py`) vs SQLite FTS dedicado vs leitura on-demand do PDF no momento da cunhagem. Decidir no gen-spec pelo custo/beneficio (a selecao precisa de busca semantica ou match de tema basta?).
4. **Granularidade do card EMED extraido:** guardar par frente/verso estruturado por card (para o agente escolher card a card) vs texto corrido do deck. Recomendacao: estruturado (par a par), ja que a selecao e card a card.
