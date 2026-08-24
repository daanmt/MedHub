# Session 152 -- Fecha S16 (Aleitamento+CA Mama, 11 erros) + drena FSRS 90 cards + Revisão Direcionada em Artifact
**Data:** 2026-08-23
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 151

---

## O que foi feito

### Arco 1 -- Aleitamento Materno + Câncer de Mama (S16 real)
- **Aleitamento Materno Revisão** (Pediatria): 46q, 42 acertos (91.3%). 4 erros analisados num lote atômico (`insert_questao.py --errors-file`, pré-validado): manejo do ingurgitamento mamário (manter mamada direta em livre demanda + crioterapia, não substituir por copinho), mecanismo do ácido graxo poli-insaturado do leite de vaca (neuro/retina, não digestivo -- isso é a caseína), discriminação Hepatite C (situação "questionável"/compartilhada) x HIV (contraindicação categórica, sem discussão possível), e inversão de direção na circulação êntero-hepática de bilirrubina (aleitamento precoce diminui, não aumenta).
- **Câncer de Mama Revisão** (Ginecologia): 45q, corrigido de 6 para 7 erros pelo usuário em cima da hora (38 acertos, 84.4%). 7 erros processados num 2º lote: pareamento BRCA1/2 x obesidade pós-menopausa entre 4 neoplasias que compartilham fator de risco (2 cards atômicos pro mesmo erro), atrofia cística x câncer de endométrio em usuária de tamoxifeno (prevalência real, não só risco elevado), "biópsia com atipia" x "cirurgia anterior" (troca de termo que invalida alternativa), indicação de linfonodo sentinela (axila já confirmada positiva vai direto pra dissecção), inibidor de aromatase é pós-menopausa (não pré), Ki-67 20% classifica Luminal B + subtipo molecular nunca indica radioterapia (2 cards), e dedução reversa fármaco->receptor (inibidor de aromatase + trastuzumabe = Luminal HER2-positivo, não triplo-negativo).
- 13 cards gerados no total, todos pré-validados contra `card_checks.validar_card` (1 ajuste de atomicidade antes do insert -- pergunta multi-parte simplificada). Ledger de habilidades atualizado via `--backfill` (403 habilidades novas, 407 ocorrências).
- **Padrão emergente nos 11 erros:** "ancoragem na gravidade" -- 3 casos (HIV x Hepatite C, câncer de endométrio x atrofia cística, triplo-negativo x Luminal HER2+) em que a opção mais grave/lembrada atraiu a resposta por cima do que os dados literalmente apontavam. Distinto do padrão-mestre "discriminador que exclui" (que é sobre ignorar o dado que exclui), este é sobre a alternativa mais dramática vencer por associação, não por evidência.

### Arco 2 -- Drenagem FSRS (90 cards, protocolo de pipeline novo)
6 blocos de 15 (98 atrasados + 8 erros frescos + 25 hoje, parando a pedido do usuário nos 90 antes de entrar nos novos). Usuário propôs e validado ao vivo um **protocolo de pipeline de 2 blocos em voo**: o agente entrega o feedback do bloco N junto com as perguntas do bloco N+2 (nunca sozinho), eliminando o tempo ocioso de esperar o processamento -- virou memória de feedback (`feedback_revisar_pipeline_blocos`). Redrill de notas 1-2 explicitamente adiado pro fechamento, absorvido pela Revisão Direcionada em vez de intercalado bloco a bloco.

Distribuição final: 20 nota 1, 9 nota 2, 14 nota 3, ~46 nota 4 (query real em `fsrs_revlog`). 4 cards reforjados por defeito de **formulação** (não de conteúdo) -- usuário pediu explicitamente que cada reforja vire "data flywheel" pra uma auditoria ampla do banco que vem em breve, não só o card individual corrigido:
- `id=44` (Damage Control): pedia lista de N passos como resposta única ("demanda tempo e cansa") -- reforjado pro eixo único (o princípio de abreviar a cirurgia).
- `id=1063` (corticoide em crise de asma): frente ambígua sobre se o corticoide sistêmico "era" indicado, quando só a via estava em jogo.
- `id=484` (TTA/laparoscopia): pergunta circular -- a frente já continha a palavra-chave da resposta.
- `id=1039` (HPN): pergunta composta pedindo 2 informações na mesma frase ("dá uma volta absurda").

1 card aposentado (`id=1349`, Lei 8080 Art 6º, pedido explícito do usuário). Os 4 padrões de defeito viraram achado **F40** em `AUDITORIA_MEDHUB.md`, mesma família do F7 (defeito de autoria de card).

### Arco 3 -- Fechamento: Revisão Direcionada em Artifact único
Clusterização dos gaps por tema, não por card, revelou **3 clusters que capotaram quase inteiros** (não foi recall pontual disperso):
- **Pólipos e Neoplasias Intestinais** (Gastro): 9 de 9 cards errados -- rastreamento por risco familiar, discriminação por profundidade de invasão (Haggitt), síndromes de polipose por fenótipo extraintestinal (Lynch/Cowden/Peutz-Jeghers), lesão cística pancreática por trio amilase/CEA/mucina.
- **Endometriose** (GO): 3 de 5 errados -- resistência a progesterona + aromatase local, classificação ACOSTA (sem grau "Mínima", isso é ASRM), malignização rara (endometrioide/células claras).
- **Arboviroses** (Infecto): 3 de 3 errados -- assinatura temporal/clínica de Zika x dengue x febre amarela.

Mais **8 erros pontuais** que não formaram cluster mas replicam armadilha catalogada: Integralidade (princípio SUS x atributo Starfield, reincidência confirmada 2x), DRGE cirúrgica, obstrução neonatal alta (dupla bolha), LRA renovascular pós-IECA, contracepção não-hormonal, sangramento pós-menopausa, delirium/EHH, step-up de asma pós-crise grave.

Publicado como Artifact único (design com paleta/tokens herdados do motor da Autópsia dos Simulados -- `paper/card/ink/teal/rose/ochre` -- mas tipografia própria Fraunces+Source Serif 4 e estrutura de leitura vertical, sem os filtros JS complexos que não fazem sentido pra 11 temas). `review_log` carimbado (`directed_review`) nos 3 temas centrais (ids 167, 301, 149).

**Nota (2026-08-24):** a URL original deste Artifact foi deletada da conta por motivo desconhecido (detectado pelo lifecycle de watch da sessão seguinte) e republicada a partir do arquivo local salvo: https://claude.ai/code/artifact/a27d3a31-6da8-40f1-b388-c035799316d2.

## Padrões de erro identificados
- **Ancoragem na gravidade** (novo, 3 instâncias no lote de erros): a opção mais grave/lembrada atrai a resposta por cima do que os dados apontam -- distinto do "discriminador que exclui" (que é sobre ignorar o dado que exclui, não sobre gravidade).
- **Fato verdadeiro, mecanismo errado** (2 instâncias): ácido graxo poli-insaturado (leite de vaca causa cólica de verdade, mas por outro mecanismo); pareamento BRCA/obesidade entre neoplasias que compartilham o fator.
- **3 clusters de lacuna sistêmica**: Pólipos e Neoplasias Intestinais (crítico, 9/9), Endometriose (3/5), Arboviroses (3/3) -- ver Revisão Direcionada.
- **Reincidência confirmada, não nova**: Integralidade Starfield x princípio SUS (2ª vez, sinalizada pelo próprio card).

## Artefatos criados/modificados
- `ipub.db`: 2 lotes de erros (4+7=11 questões, 13 cards), volume de 2 blocos (91q), 85 ratings FSRS + 4 reforjas + 1 card aposentado, ledger de habilidades (`--backfill`), 3 carimbos de `review_log` (`directed_review`)
- `AUDITORIA_MEDHUB.md` (nova seção 3j, achado F40)
- `HANDOFF.md` (fechamento)
- Memória: `feedback_revisar_pipeline_blocos.md` (novo), `feedback_reforja_flywheel_auditoria.md` (novo), `MEMORY.md` (2 pointers novos)
- 1 Artifact publicado (URL no HANDOFF.md e acima)

## Decisões tomadas
- Protocolo de pipeline de 2 blocos no `/revisar` DRENAR vira padrão para sessões de regime de dívida (múltiplos blocos grandes) -- não é preferência pontual, é como conduzir daqui pra frente.
- Toda reforja por defeito de formulação (não de conteúdo) vira achado F-numerado em `AUDITORIA_MEDHUB.md`, mesmo que a correção individual já tenha sido aplicada -- o padrão é o dado de valor, não só o card.
- Meta de drenagem ajustada de 120 para 90 cards nesta sessão, por decisão do usuário (parar antes de entrar nos cards novos).

## Próximos passos
Ver `HANDOFF.md` -- Revisão por Questões Pediatria (51q) e Ginecologia (57q) são as últimas tarefas confirmadas do S16; auditoria ampla do banco com escopo maior (F40 novo); habilidade reincidente "exame normal exclui" ainda sem Revisão Direcionada dedicada.
