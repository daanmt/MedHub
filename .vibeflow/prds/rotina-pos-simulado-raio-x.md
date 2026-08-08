# PRD: Rotina Pós-Simulado (Raio-X + Cards + Performance)

> Gerado via /vibeflow:discover em 2026-08-07/08 (sessão 139)

## Problem

Hoje, a análise pós-simulado -- cruzar cada erro contra o cronograma (`grade.json`) e o histórico do banco pra saber se é buraco real de conteúdo, esquecimento (retenção), ou tema genuinamente fora do escopo nomeado -- é montada do zero pelo agente a cada vez: queries SQL ad-hoc, classificação manual em status de cobertura, design de um artifact HTML novo. Funcionou muito bem nas sessões 138/139 (o usuário conferiu os 86 erros do artifact da s138 e "aprendeu bastante"), mas o processo não é repetível sem reconstrução -- e a cadência de simulados (~2x/semana) vai gerar essa mesma análise, do zero, toda vez, se não virar rotina.

## Target Audience

O usuário (residency-prep self-study, foco Psiquiatria UFRJ/IPUB + piso ENAMED), operando via o agente MedHub.

## Proposed Solution

Uma **skill nova** que orquestra, a cada simulado feito:
1. Cruzamento estrutural erro x tema x posição no `grade.json` x histórico de erros/resumos no `ipub.db` -> classificação em status de cobertura (retenção confirmada, sem registro, resumo sem erro prévio, fora do grade, blind spot estrutural, futuro).
2. Cunhagem de cards atômicos pareados por erro (reaproveita `analisar-questao`/`insert_questao.py` -- Siamese Twins, não duplica).
3. Registro/documentação de performance (reaproveita `registrar_sessao_bulk.py`/`importar-planilha`).
4. Publicação de um artifact HTML com **design fixo** (dashboard + breakdown por área + blind spots estruturais + superfície de revisão card-a-card expansível) -- reaproveitando a estrutura visual já validada na s138, não redesenhada a cada rodada.

## Success Criteria

A cada simulado feito, o usuário consegue disparar a rotina e obter o artifact + cards + registro sem o agente reprojetar o processo do zero. O artifact mantém o padrão de qualidade pedagógica já validado nas s138/139 (critério subjetivo, mas ancorado no feedback real: "ficou excelente e pedagógico").

## Scope v0

- Skill nova (nome a definir no gen-spec, ex. `/analisar-simulado` ou `/raio-x`).
- Design do artifact **fixo/específico** (não redesenhado a cada vez) -- reaproveita a estrutura da s138.
- Reaproveita `analisar-questao` pra cunhagem de cards (não recria o pipeline de erro->card).
- Cruzamento estrutural: o *como* (CLI determinístico vs. agente montando via SQL a cada vez) fica em aberto -- ver Open Questions.

## Anti-scope

- **Integração com Streamlit/dashboard de BI da preparação.** O usuário tem a intenção explícita de eventualmente subir esses dados como dashboard (retomando o padrão que a UI já tinha antes da pivotagem agent-first), mas decidiu explicitamente **não aprofundar isso agora** -- fica como direção futura, não trabalho deste ciclo.
- Gatilho automático (o agente detectar sozinho "simulado novo registrado" e disparar sem pedido) -- v0 é disparo deliberado, a menos que o gen-spec decida diferente.
- Reformular o pipeline de cunhagem de cards ou o schema do `ipub.db` -- a rotina consome o que já existe.

## Technical Context

- `tools/cronograma.py` já tem `--radar` (cobertura x performance) -- candidato natural a estender se o cruzamento estrutural virar CLI determinístico.
- `tools/insert_questao.py` já cunha erro + card pareado (padrão Siamese Twins, `AGENTE.md §6`).
- O padrão visual do artifact (dashboard + área + blind spots + cards expansíveis) já existe como referência concreta: artifact da s138 ("Raio-X · Simulados 2+3 × Cronograma").
- A s139 rodou esse cruzamento uma vez em escala maior (86 erros, 2 simulados) via workflow multi-agente (`aula-base-raiox-restante`) -- útil como referência de quais campos por erro importam (status_cronograma, macro_status, grade_semana, grade_tema_match, nota_bundling) mas **não é o desenho final da rotina** (foi uma correção pontual de dívida acumulada, não o fluxo recorrente).

## Open Questions

1. **CLI vs. agente para o cruzamento estrutural.** O usuário respondeu "provavelmente uma skill" sem fechar se a classificação de status (retenção confirmada / fora do grade / blind spot / etc.) vira uma flag nova e testável em `cronograma.py`, ou se continua o agente montando a query a cada vez. Decidir no gen-spec -- pesar contra o quanto de correspondência difusa (bundling manual de temas) o processo da s138 exigiu, que é heurístico demais pra determinismo puro.
2. **Gatilho exato.** Disparo manual pelo usuário ("analisa o simulado X") é o padrão v0 assumido; considerar no gen-spec se o boot proativo (`day_plan.py`) deveria sinalizar "há simulado sem raio-x" como parte do Plano do Dia.
3. **Formato de dados pensando na integração futura com Streamlit.** Mesmo sem construir a UI agora, vale decidir no gen-spec se os dados dessa rotina (classificação de status por erro, por exemplo) deveriam persistir em alguma forma estruturada no `ipub.db` (nova coluna/tabela) em vez de viverem só no HTML do artifact -- para não exigir retrabalho quando a integração Streamlit acontecer.
