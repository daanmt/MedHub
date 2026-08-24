# Session 153 -- 2 aulas-base D7 (Pediatria+Ginecologia) + corrige card GINA STEP1 via auditoria de evidência
**Data:** 2026-08-24
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 152

---

## O que foi feito

### Arco 1 -- Projeção de fila + 2 aulas-base em paralelo
Antes de qualquer aula, conferida a projeção de carga FSRS até 13/09 (ENAMED): dívida zerada pela drenagem da s152 ainda segurando, carga já agendada rodando em média ~11 cards/dia (teto normal de 40/dia, pool de 690 nunca-introduzidos como reserva sem pressão imediata).

As tarefas "Revisão por Questões Pediatria" (51q) e "Revisão por Questões Ginecologia" (57q) do cronograma vêm com tema vazio (bug de parsing conhecido, `tools/cronograma.py`). Perguntado ao usuário como escopar a aula-base pedida (D7 de descompressão) -- escolheu explicitamente "Panorama das lacunas reais" em vez de cobertura enciclopédica da área inteira.

2 forks paralelos construíram as aulas: cada um levantou os temas com mais volume de erro histórico em `questoes_erros` por área (dados já agregados nesta sessão via SQL antes de disparar), puxou os erros reais (elo/armadilha/explicação) por tema prioritário, verificou resumo-fonte existente em `resumos/` (ancorando nele) e publicou como Artifact HTML seguindo o contrato `artifact-design` + paleta/tokens herdados do motor da Autópsia (com liberdade de tipografia própria).

- **Pediatria** -- "Caderneta de Falhas" (https://claude.ai/code/artifact/27dd0c0e-9a21-414b-b7ea-3099af286ffc): tronco Imunizações (20 erros -- falsas contraindicações, família DTP, calendário de gestante/prematuro, PEP) + branches Doenças Exantemáticas (13, bloqueio vacinal x PPE), Aleitamento Materno (9, incluindo os 4 de hoje), Asma (8, gravidade/via/STEP/mecanismo do AINE), Emergências Pediátricas (4). Imunizações, Aleitamento Materno e Asma eram tema-zero -- ancoradas direto nos PDFs-fonte do EMED.
- **Ginecologia** -- "Chave Diferencial de Ginecologia" (https://claude.ai/code/artifact/1a0ac2da-160c-42c7-8e27-19daea67b740): 2 troncos (Vulvovaginites 15 erros -- 7 entidades por pH/inflamação; Planejamento Familiar 13 erros -- categorias OMS + combinado x isolado + LARC no puerpério) + branches Câncer de Mama (18 erros incluindo os 7 de hoje), Úlceras Genitais, Rastreamento do Colo. Todos os 5 resumos-fonte já existiam em `resumos/GO/`, nenhum tema-zero.
- `review_log` carimbado (`directed_review`) em 12 tema_ids (5 Pediatria + 7 Ginecologia).

### Arco 2 -- Auditoria de evidência e correção do card GINA STEP1
O fork de Pediatria, ao ler o PDF-fonte de Asma (`resumos/Pediatria/21. Asma.pdf`) pra construir a aula, notou uma divergência entre o card `id=650` e a fonte: o card afirmava "GINA aboliu o SABA isolado -- STEP1 usa CI-formoterol por demanda", mas o PDF descrevia SABA como resgate no STEP1 pediátrico.

Disparado `evidence-researcher` (governado por `core/contracts/evidence-governance.md`), que triangulou 3 fontes independentes (PDF-fonte EMED verbatim + 2 sínteses do GINA 2024 oficial via WebSearch) e confirmou: o card descrevia o esquema do **Track 1 adulto/adolescente (>=12 anos)** -- CI-formoterol PRN desde o STEP1 -- catalogado sob "Asma na Infância", que no material do curso é especificamente **6-11 anos**. Para essa faixa, o STEP1 real mantém SABA de resgate + CI dose baixa concomitante; CI-formoterol só entra no STEP3-4. Veredito: divergência de conduta por faixa etária trocada, não desatualização nem simplificação de banca -- inclusive o próprio material-fonte do curso já ensina a versão correta.

Card 650 corrigido (agora específico de 6-11 anos, com a armadilha explicando a troca de faixa etária). Verificação rápida nos outros 2 cards de asma pediátrica já cunhados (262, 263) confirmou que estavam corretos -- caso isolado. Card novo cunhado (`tools/insert_card_base.py`, tipo `nuance`, tema Asma id=345) cobrindo o esquema real de >=12 anos, a pedido do usuário.

**Nota de transparência:** o feedback dado ao usuário no redrill da s152 (bloco 1, card 650) estava incorreto por causa desse card -- ele havia respondido "STEP 1, SABA por demanda" (correto) e foi corrigido às avessas na hora, como se tivesse errado o fármaco. Esclarecido diretamente com o usuário nesta sessão.

## Padrões de erro identificados
- Nenhum erro de questão do usuário nesta sessão (sessão de engenharia/aula-base, sem volume de questões).
- **Modo de falha de autoria de card, novo candidato para a auditoria ampla:** card ensina o mecanismo correto, mas para a FAIXA ETÁRIA/GRUPO errado sob um rótulo de tema que implica outro grupo -- distinto dos 4 padrões de F40 (que eram sobre formulação, não conteúdo). Registrado como observação em `HANDOFF.md`, não elevado a achado F-numerado formal (caso pontual até agora, não padrão confirmado em mais de uma ocorrência).

## Artefatos criados/modificados
- `ipub.db`: card 650 reforjado (v1->v2, conteúdo clínico corrigido), 1 card novo (`insert_card_base.py`, tema Asma), 12 carimbos de `review_log` (`directed_review`)
- `HANDOFF.md` (fechamento)
- 2 Artifacts publicados (URLs acima)

## Decisões tomadas
- Aula-base para tarefa de cronograma sem tema definido ("Revisão por Questões" bundlada) escopa como panorama de lacunas reais (volume de erro histórico), não cobertura enciclopédica da área -- decisão explícita do usuário, vale de precedente para casos futuros do mesmo bug de parsing.
- Card com conteúdo correto mas para o grupo/faixa etária errada é corrigido no lugar (mesmo card_id, FSRS preservado) quando o card errado e o conteúdo correto ocupam o mesmo "slot" conceitual; um card novo separado só quando o conteúdo do grupo que ficou descoberto pela correção for genuinamente distinto o suficiente para merecer seu próprio recall.

## Próximos passos
Ver `HANDOFF.md` -- Revisão por Questões Pediatria (51q) e Ginecologia (57q) com aula de apoio pronta; auditoria ampla do banco com escopo maior (considerar variar de "conduta estratificada por grupo errado" como novo eixo de varredura); habilidade reincidente "exame normal exclui" ainda sem Revisão Direcionada dedicada.
