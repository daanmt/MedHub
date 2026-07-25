# Spec: Diagnóstico de Variância e Zona

> Gerado via /vibeflow:gen-spec em 2026-07-25
> Fonte: transcrições Pedro Martins (vídeos 1, 3, 4, 5). Sequência de `ledger-de-habilidades` (PASS).

## Objetivo

Trocar a métrica que dirige o diagnóstico do estudo: de **média** (77,6%, que já está boa e não diz o que fazer) para **variância entre blocos** (12,0 pp, que é o sinal de alarme) + uma **zona** de duas dimensões que prescreve o próximo movimento.

## Contexto

Hoje o MedHub reporta média acumulada e áreas fracas por tema. A tese do vídeo 1 é que, no platô, **a média não é o sinal — a variância é**: "tirar nota alta numa prova e não ir nem para a segunda fase de outra mostra que o desempenho depende do perfil da prova, não do conhecimento".

Medido no `ipub.db` (80 blocos com >= 15q): **média 77,6% · desvio-padrão 12,0 pp · amplitude 73,7 pp** (26,3% a 100%). Últimos 10 blocos: 45,8 a 96,4. A variância é alta e nada no sistema a reporta.

Pedro classifica em zonas de 1 eixo (60-65% = conteúdo; 70-80% = direcionamento). Isso **misclassifica o usuário**: ele tem 77,6% de média (zona "direcionamento") **sem ter fechado o conteúdo** (4.263q de grade restantes, 4 semanas de atraso). Zona de 1 eixo assume cobertura completa. Precisamos de 2 eixos.

## Definition of Done

1. **Métrica de variância:** `tools/variancia.py --metricas` devolve n de blocos, média, desvio-padrão, amplitude e coeficiente de variação sobre `sessoes_bulk` (blocos >= piso de questões configurável, default 15), com janela opcional `--ultimos N`.
2. **Zona de 2 eixos:** `--zona` classifica em `CONTEUDO | COBERTURA | RETENCAO | DIRECIONAMENTO` cruzando **desempenho** x **cobertura da grade**, e devolve a prescrição correspondente. Cobertura é derivada de `taxonomia_cronograma` (temas com volume > 0 sobre o total da grade), nunca assumida.
3. **Variância é sinal independente da zona:** `desvio >= 10 pp` emite recomendação de **simulado** qualquer que seja a zona — a sensibilidade ao perfil de prova não se corrige com mais bloco temático.
4. **Cadência de simulado:** `--simulado-check` responde se há simulado registrado na janela de 7 dias e, quando não há, sinaliza o débito (política decidida na s126: 1 simulado/semana, contando no bloco dedicado).
5. **Integração no plano do dia:** `day_plan.py` exibe bloco de variância + zona + habilidades reincidentes (fechando a integração adiada do spec 1). Falha de qualquer sinal degrada graciosamente — nunca derruba o plano.
6. **Craftsmanship gate:** `auto_check --changed` verde (0 BLOCK); `import sqlite3` só em `db.py` + CLI standalone; suíte própria cobrindo os cortes de zona e o cálculo estatístico com fixtures determinísticas.

## Escopo

- `tools/variancia.py` (novo): `--metricas`, `--zona`, `--simulado-check`, `--json`.
- `app/utils/db.py`: `get_serie_blocos` (série de % por bloco) + `get_cobertura_grade`.
- `tools/day_plan.py`: bloco de diagnóstico (variância + zona + reincidentes + débito de simulado).
- `.claude/commands/performance.md`: assinatura canônica do novo CLI.
- `tools/test_variancia.py` (novo).

## Anti-escopo

- Nenhuma predição de nota (arquivada na s099, decisão do usuário — não ressuscitar).
- Nenhuma alteração no FSRS, no ledger de habilidades ou no cálculo de metas.
- Nenhuma automação de "abandone o cronograma" — a decisão de trocar grade por simulado é do usuário; o sistema **sinaliza**, não executa.
- Nenhuma UI Streamlit.
- Nenhuma ponderação por incidência/regra 90-50 (vídeo 3) — spec separado; o proxy de incidência (repetição de tema na grade) existe mas não entra aqui.
- Nenhum ajuste de contrato (`AGENTE.md`, `/analisar-questao`) — governança, vai em passada própria.

## Decisões técnicas

- **Desvio-padrão populacional (`pstdev`), não amostral.** Os blocos não são amostra de população maior; são a série inteira. Evita inflar o número em janelas curtas.
- **Piso de 15 questões por bloco.** Bloco de 5 questões produz % com granularidade de 20 pp e envenena a variância com ruído de amostragem. Configurável, mas o default protege a métrica.
- **Zona de 2 eixos, cortes explícitos.** Desempenho: `< 70%` baixo, `>= 70%` alto. Cobertura: `< 70%` baixa, `>= 70%` alta. Trade-off: cortes fixos são grosseiros, mas auditáveis e testáveis — preferíveis a um score contínuo que ninguém consegue verificar.
  - baixo desempenho + baixa cobertura -> **CONTEUDO**
  - alto desempenho + baixa cobertura -> **COBERTURA** (a zona real do usuário hoje)
  - baixo desempenho + alta cobertura -> **RETENCAO**
  - alto desempenho + alta cobertura -> **DIRECIONAMENTO**
- **Variância corre por fora da zona.** É um eixo ortogonal: prescreve simulado independentemente do quadrante. Modelar como flag, não como quinta zona.
- **Simulado conta como volume mas não como cobertura de grade** — coerente com a s126 (`escopo='cronograma'` exclui simulado do avanço da grade).

## Padrões aplicáveis

- `.vibeflow/patterns/db-access-layer.md`
- `.vibeflow/patterns/agent-workflow-protocol.md`
- Degradação graciosa do `day_plan` (padrão já estabelecido em `_cronograma_hoje`: sinal ausente não derruba o plano).

## Riscos

- **Zona virar rótulo fatalista.** "Você está em COBERTURA" não ajuda se não vier com prescrição. Mitigação: a zona sempre retorna acoplada à ação, nunca sozinha.
- **Variância confundida com inconsistência de esforço.** Um bloco de 45% pode ser tema novo, não sensibilidade a banca. Mitigação: reportar a série junto da métrica, para o agente ler o contexto antes de prescrever.
- **Cortes fixos mal calibrados.** Mitigação: cortes ficam em constantes nomeadas no topo do módulo, e a suíte fixa o comportamento nos limites.
