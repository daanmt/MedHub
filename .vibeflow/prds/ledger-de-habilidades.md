# PRD: Ledger de Habilidades -- da narrativa do erro à entidade consultável

> Gerado via /vibeflow:discover em 2026-07-25
> Fonte: 2 transcrições de Pedro Martins (UFJF; 9/9 aprovações SP, 5 primeiros lugares, 1o geral Einstein; residente Radiologia USP)

## Problema

O MedHub registra **593 erros** e todos têm `habilidades_sequenciais` preenchido. Mas o campo é uma **string de prosa** ("Classificar como colite grave -> internar -> afastar C.difficile -> corticoide EV"). Isso torna o MedHub capaz de narrar a cadeia de raciocínio de **uma** questão e **incapaz de responder a pergunta que decide a aprovação**: *quais habilidades eu falho repetidamente, através de temas diferentes?*

As transcrições nomeiam o problema com precisão. Na faixa dos 75-80%, o gargalo **deixa de ser conteúdo e passa a ser direcionamento**: "o perfil do seu erro tende a variar mais... deixa de ser 'vou estudar cirurgia pediátrica' e passa a ser 'eu não sabia que a gastrosquise era mais à direita'". O usuário está em **79,1%** -- exatamente essa faixa. As áreas fracas que o sistema reporta hoje são **temas** ("Cirurgia Abdominal / Colecistite"), que é a granularidade errada para esta fase.

Três buracos concretos, todos visíveis no vídeo 2 e ausentes no MedHub:

1. **Habilidade não é entidade.** Não há como agregar, contar reincidência, nem ordenar por dor. O `weak_areas` da memória lista temas, não habilidades.
2. **Só o erro entra.** `questoes_erros` é alimentado exclusivamente por questão errada. No vídeo, a questão de mioma é **acertada na habilidade-alvo** e mesmo assim rende 3 aprendizados ("essas três outras coisas eu absolutamente não tinha prestado atenção e agora eu sei"). Hoje esse sinal é descartado inteiro.
3. **Acerto é binário.** Não existe estado de **incerteza**. "Vou marcar aqui como incerteza, que o algoritmo sabe que eu fiquei em dúvida." Acertar por eliminação e acertar sabendo produzem o mesmo registro -- e o primeiro é uma bomba-relógio que a prova vai detonar.

Consequência prática: os flashcards nascem ancorados no erro (o que já é correto e é a filosofia da casa), mas **não nascem ancorados na habilidade específica que quebrou**, e não nascem de questões acertadas com dúvida. O card certo é "o score de Glasgow-Blatchford < 1 permite manejo ambulatorial", não "hemorragia digestiva alta".

## Público-alvo

Usuário único (o dono do MedHub), em preparação para ENAMED (13/09) + UERJ + USP (nov-dez). Performance atual 79,1% acumulado -- **dentro do platô descrito**. Secundariamente, o próprio agente, que consome o ledger para priorizar cunhagem, revisão direcionada e abertura de bloco.

## Solução proposta

Promover **habilidade** a entidade de primeira classe do `ipub.db`, alimentada pelo pipeline de análise que já existe, com três estados por habilidade (`acertou` / `incerteza` / `errou`) e desacoplada do acerto global da questão.

1. **Tabela `habilidades`** (catálogo normalizado, dedup por texto normalizado) + **`questao_habilidades`** (o veredito por questão). A `habilidades_sequenciais` em prosa é **preservada** (não migrar destrutivamente) e passa a ser a fonte do backfill.
2. **Ingestão de questão ACERTADA.** Novo caminho para registrar aprendizados de questão que o usuário acertou -- sem poluir a contagem de erros nem o volume.
3. **Estado `incerteza`** como cidadão de primeira classe, distinto de acerto e de erro.
4. **Relatório de reincidência:** quais habilidades falharam mais vezes, em quantos temas distintos, há quanto tempo. Habilidade que falha em **temas diferentes** é sinal de padrão de raciocínio, não de lacuna de conteúdo -- e essa distinção é o produto central.
5. **Cunhagem ancorada na habilidade:** o card passa a citar qual habilidade quebrou, fechando o elo `erro -> habilidade -> card`.

## Critérios de sucesso

- É possível responder, por comando, "quais são minhas 10 habilidades mais reincidentes" com contagem e nº de temas distintos.
- Habilidade reincidente **em 3+ temas distintos** é sinalizada como padrão de raciocínio (candidata à família bug nº 1), separada de lacuna de conteúdo.
- Uma questão **acertada** consegue gerar aprendizado registrado sem incrementar erro nem volume.
- Uma habilidade marcada `incerteza` aparece na fila de atenção com peso próprio -- nem ignorada como acerto, nem tratada como erro.
- O backfill converte os 593 erros existentes sem perda: nenhuma linha de `questoes_erros` é alterada ou apagada.

## Escopo v0

- Migração de schema: `habilidades` + `questao_habilidades` (idempotente, padrão `init_db.py`).
- Parser determinístico do formato `A -> B -> C` para backfill dos 593 registros.
- CLI `tools/habilidades.py`: `--backfill`, `--report`, `--reincidentes`, `--add` (registrar habilidade avulsa de questão acertada).
- Estado `veredito` em (`acertou`, `incerteza`, `errou`).
- Integração de leitura no `day_plan.py` (bloco de habilidades reincidentes no plano do dia).
- Atualização da skill `/analisar-questao` para emitir habilidades estruturadas.

## Anti-escopo

- 🔴 **NÃO clonar o Prisma.** O MedHub **não possui banco de questões** -- ele só enxerga a questão que o usuário traz. Toda a mecânica de "revisão espaçada por questões" e "algoritmo sugere a próxima questão" é **inaplicável** e fica de fora. O que é portável é o *ledger de habilidades*, não a plataforma.
- Nenhuma alteração no FSRS, no agendamento ou no cálculo de estabilidade.
- Nenhuma migração destrutiva de `habilidades_sequenciais` -- o campo em prosa permanece.
- Nenhuma taxonomia hierárquica de habilidades (sem árvore, sem parent/child). Texto normalizado + dedup basta em v0.
- Nenhuma UI Streamlit.
- Nenhuma inferência automática de habilidade por LLM em lote sobre o histórico -- o backfill é **parser determinístico**; o que ele não conseguir separar fica marcado para curadoria manual.
- Métrica de **variância entre provas** e **diagnóstico de zona** (vídeo 1) ficam para um segundo spec -- é analítica sobre `sessoes_bulk`, sem sobreposição de schema com este.

## Contexto técnico

- `import sqlite3` só em `app/utils/db.py` e CLIs standalone de `tools/` (`.vibeflow/patterns/db-access-layer.md`).
- Pipeline existente: `.vibeflow/patterns/error-insertion-pipeline.md` -- `insert_questao.py` já escreve `questoes_erros` + `flashcards` + `fsrs_cards` + `taxonomia_cronograma`. O ledger pendura-se nele, não o substitui.
- `questoes_erros.habilidades_sequenciais`: TEXT, 593/593 preenchidos, formato dominante `A -> B -> C` (separador ` -> `, ASCII, garantido pela convenção Zero-LaTeX de `AGENTE.md §4.5`).
- Filosofia de card ancorado no elo metacognitivo já é contrato (`.claude/commands/estilo-flashcard.md`); este PRD **não a substitui**, dá a ela um índice consultável.
- Harness obrigatório: `python -X utf8 tools/auto_check.py --changed` deve sair verde (`AGENTE.md §1.3`).
- `ipub.db` é local-only, não versionado -- migração precisa ser idempotente e reexecutável.

## Questões em aberto

- **Tensão real entre o vídeo 1 e a situação do usuário:** Pedro recomenda "jogue o cronograma no lixo e só faça simulado" na faixa dos 75%. O usuário está em 79,1% **mas ainda tem 4.263 questões de grade e 4 semanas de atraso** -- ou seja, tem a nota do platô **sem ter fechado o conteúdo**. A recomendação de Pedro pressupõe conteúdo coberto. Registrar a tensão; **não** implementar "abandone o cronograma" como regra automática. Decisão do usuário, não do sistema.
- Formato exato do `veredito` para habilidades vindas do backfill: os 593 registros históricos são todos de questão **errada**, mas nem toda habilidade da cadeia falhou. Proposta v0: marcar as habilidades do backfill como `errou` apenas quando o texto do `o_que_faltou`/`tipo_erro` casar; caso contrário `indefinido`, e deixar para curadoria incremental. Não inventar veredito.
