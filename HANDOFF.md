# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-24 -- 2 aulas-base D7 panorama (Pediatria+Ginecologia) + corrige card GINA STEP1 via auditoria de evidencia (sessao 153)*

## > Próximo passo imediato

1. **Revisão por Questões Pediatria (51q) e Ginecologia (57q)** -- últimas tarefas confirmadas do S16, agora com aula-base de apoio publicada para as duas (ver Estado por frente). Usuário decide quando fazer; ao retomar, registrar volume + `/analisar-questao` nos erros, mesmo padrão de sempre.
2. **🗓️ Auditoria ampla do banco (pendente desde s148, 4ª convocação)** -- escopo em `AUDITORIA_MEDHUB.md`: F35-F39 (reconcile de volume, Drive/MCP, atomicidade) + **F40 novo** (defeito de formulação de card -- pacote-de-fatos, frente ambígua, pergunta circular, pergunta composta). Considerar somar a esse escopo o padrão descoberto hoje: card ensinando o mecanismo da FAIXA ETÁRIA ERRADA sob um rótulo de tema que implica outra faixa (achado pontual no card 650, corrigido, mas pode haver outros em condutas estratificadas por idade/estágio).
3. **Habilidade reincidente "ler exame NORMAL como dado que EXCLUI"** (>=3 temas) segue sem sessão dedicada de Revisão Direcionada.

## Estado por frente
- **Volume & Metas:** 6523 / 9454 (perf. ~78.5%). Hoje: 0 (sessão de aula-base + engenharia, sem volume novo). Ritmo-alvo ~47.3q/dia (62d p/ Cronograma EMED).
- **FSRS:** dívida 57 atrasados + 21 p/ hoje (a virada de dia moveu os 45 "hoje" de ontem para atrasados) -- pool 690 nunca introduzidos (+1 card novo cunhado hoje). Teto sobe pra regime de dívida (<=80/dia).
- **2 aulas-base D7 publicadas** (panorama de lacunas reais, não cobertura enciclopédica -- construídas via 2 forks paralelos que puxaram os erros reais de `questoes_erros` por tema antes de escrever, ancoradas nos resumos/PDFs-fonte existentes):
  - **Pediatria** -- "Caderneta de Falhas": https://claude.ai/code/artifact/27dd0c0e-9a21-414b-b7ea-3099af286ffc -- tronco Imunizações (20 erros, maior lacuna) + branches Doenças Exantemáticas, Aleitamento Materno, Asma, Emergências Pediátricas. Imunizações/Aleitamento/Asma eram tema-zero (sem `.md`) -- ancoradas direto nos PDFs-fonte do EMED.
  - **Ginecologia** -- "Chave Diferencial de Ginecologia": https://claude.ai/code/artifact/1a0ac2da-160c-42c7-8e27-19daea67b740 -- 2 troncos (Vulvovaginites 15 erros, Planejamento Familiar 13 erros) + branches Câncer de Mama, Úlceras Genitais, Rastreamento do Colo. Todos os 5 resumos-fonte já existiam em `resumos/GO/`, nenhum tema-zero.
  - `review_log` carimbado (`directed_review`) em 12 tema_ids ao todo (5 Pediatria: 265, 252, 373, 345, 117; 7 Ginecologia: 264, 258, 441, 337, 156, 320, 236).
- **🔴 Achado de auditoria de evidência (card 650 corrigido):** o fork de Pediatria sinalizou que o card "GINA STEP1" (id=650, tema Asma) descrevia o esquema do adolescente/adulto (>=12a, CI-formoterol PRN desde o STEP1) sob o rótulo "Asma na Infância" (6-11a no material do EMED) -- erro real, não simplificação de banca. `evidence-researcher` triangulou PDF-fonte EMED (`resumos/Pediatria/21. Asma.pdf`, verbatim) + GINA 2024 oficial (WebSearch): para 6-11a, o STEP1 mantém SABA de resgate + CI concomitante; CI-formoterol só do STEP3-4. Card 650 corrigido (agora específico de 6-11a) + card novo cunhado (nuance, tema Asma id=345) cobrindo o esquema correto de >=12a. **Nota honesta:** o feedback dado ao usuário durante o redrill da s152 (bloco 1) estava incorreto por causa desse card -- ele tinha acertado "SABA por demanda", foi corrigido às avessas na hora. Já esclarecido com o usuário.
- **Datas:** ENAMED 13/09/2026 (20d) -- grade fecha 25/10/2026 (62d).

## Última sessão -- s153 (AULAS-BASE PEDIATRIA+GINECOLOGIA + CORRIGE CARD GINA VIA AUDITORIA)
Sessão curta, 2 arcos. **(1) Verificação de fila + 2 aulas-base em paralelo:** conferida a projeção de carga FSRS até 13/09 (tranquila, dívida zerada da s152 ainda segurando, ~11 cards/dia de carga já agendada) antes de partir pras aulas. Como as tarefas "Revisão por Questões Pediatria/Ginecologia" do cronograma vêm com tema vazio (bug de parsing conhecido), o usuário escolheu explicitamente (AskUserQuestion) escopar as aulas como "panorama das lacunas reais" em vez de cobertura enciclopédica da área -- 2 forks paralelos levantaram os temas com mais erro histórico em `questoes_erros` por área, puxaram os erros reais (elo/armadilha/explicação) antes de escrever, verificaram resumo-fonte existente (ancorando nele) e publicaram os Artifacts. **(2) Auditoria de evidência e correção de card:** o fork de Pediatria, ao ler o PDF-fonte de Asma, notou uma divergência entre o card 650 e a fonte -- disparado `evidence-researcher` (governado por `core/contracts/evidence-governance.md`), que triangulou 3 fontes e confirmou: o card misturava o esquema do Track 1 adulto (>=12a) com o rótulo pediátrico (6-11a no material do curso). Card corrigido; card novo cunhado pra cobrir a faixa etária que ficou sem card depois da correção; usuário pediu a criação do card complementar e o fechamento da sessão.

## Pendências/observações ativas
- 🗓️ **Auditoria ampla do banco** -- ver Próximo passo #2.
- 📌 **Habilidade reincidente "exame normal exclui"** -- ver Próximo passo #3.
- ⚠️ **Revisão por Questões Pediatria (51q) e Ginecologia (57q)** -- únicas tarefas do S16 ainda não iniciadas, agora com aula de apoio pronta.
- 📝 **2 aulas-base candidatas antigas ainda abertas** (DRGE cirúrgica+necrose pancreática; neoplasias intestinais raras).
- Vale considerar, na próxima auditoria ampla, uma varredura por "conduta estratificada por idade/estágio/critério numérico" -- o card 650 sugere que esse é um modo de falha de autoria distinto dos 4 já catalogados em F40 (não é formulação, é conteúdo correto mas para o grupo errado).
- `tools/fila_enamed.py` -- superado, considerar aposentar formalmente.
- Achado técnico não resolvido: `tools/cronograma.py` perde tema em tarefa "Revisão por Questões" e desalinha URL em "Teoria" pura.
- Guias estatísticos de UERJ/USP (fase 2, pós-ENAMED) ainda não existem no repo.

---
*Histórico: history/INDEX.md * Macro: ESTADO.md * Sessão: history/session_153.md*
