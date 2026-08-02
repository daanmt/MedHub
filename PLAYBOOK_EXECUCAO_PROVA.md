---
type: reference
layer: root
status: active
---

# Playbook de Execução de Prova — Decompose do Bug nº 1

*Criado na sessão 085 (2026-06-19). Capstone do achado recorrente: os erros do estudante são, em maioria, de **processo de resolução**, não de conteúdo. Frente registrada em `project_decompose_bug_execucao_prova` (memória). Atualizar cumulativamente conforme novos sub-padrões aparecerem.*

---

## O bug, em uma frase

> **Você tem o conhecimento, mas interrompe a verificação antes de completá-la** — aplica um fato/conduta verdadeiro **sem checar a CONDIÇÃO (comporta) que o libera.** O erro raramente é falta de conteúdo; é o processo de resolução parando cedo demais.

Um **gatilho saliente** no enunciado (um número fora da faixa, um fármaco, uma incompatibilidade aparente, um diagnóstico óbvio) dispara a resposta **antes** de você passar pela comporta de verificação. A resposta marcada é a **primeira coisa que "casa"** — e você para ali.

---

## A família de sub-padrões (cumulativa)

| Sub-padrão | O que é | Onde apareceu |
|---|---|---|
| **1 — Ancoragem no número/lab** | Lê o exame contra a tabela de valores, não contra o **contexto clínico** | s077 (transferível: PTI, asma, trauma) |
| **1b — Ancoragem no fármaco** | Atribui o quadro ao medicamento citado, pula a evidência discriminante | s079 (rabdomiólise→AINE; pré-renal→nimesulida) |
| **1c — Fato no contexto errado** | Aplica um fato verdadeiro **fora da condição** em que ele vale | s081 (Pringle, beta-2, GLP-1, meta-idade) |
| **"Para antes do porquê"** | Sabe o **diagnóstico** (o fato), não o **elo causal** que o defende / exclui o vizinho | s085 (HCE canal-dependência; resistência decide o shunt; idade exclui atresia pulmonar) |
| **Ancoragem na linha de dados** | Vê "mãe O, bebê A" e dispara "incompatibilidade" sem checar as regras | s085 icterícia (Q1, Q2, Q4, Q8, Q10, Q15) |
| **Super-aplicação (não-checar-a-comporta)** | Transfere uma conduta correta para um caso onde a **comporta mudou** | s085 trauma (TTA→laparoscopia no instável; estável→TC com TC já feita) |
| **Enunciado negativo (EXCETO/ERRADA)** | Marca a afirmação **verdadeira** em vez de isolar a falsa (primo de *leitura*, não de verificação); não usa o **nº de F como checksum** (deve ser 1) | s079-080 (3×), s086 (Q4 hipertensivas), s112-118, **s120 (mini-drill: checksum nº de F=1; REINCIDIU em prova real no dia seguinte -- Q2 SUS "NÃO traduz descentralização", marcou ação verdadeira)** |
| **Viés de posição (default-to-C)** | Sob incerteza, a mão gravita para a **opção do meio (C)** em vez de forçar a verificação até o fim | **s086 hipertensivas: 6 de 7 erradas = letra C** (gabaritos espalhados D,B,D,A,B,A) |
| **Reflexo de over-tratamento** | Ao ler "grave"/dado assustador, dispara a conduta mais agressiva (interromper já / hidralazina / cesárea) sem checar o **limiar** (PA ≥160/110?) ou a **IG** | s086 hipertensivas (Q5 PA 150x100→hidralazina; Q6 grave→interromper já) |
| **Fechamento precoce em discriminador parcial** | Um achado parcial (tosse/coriza) dispara o diagnóstico vizinho **antes** de ler a marca patognomônica; **pior sob pressão de tempo** (marca sem terminar de ler) | s086 exantemáticas (Q3/Q4/Q7: tosse+coriza→sarampo, ignorou face esbofeteada/rendilhado = parvovírus). **Autorrelatado pelo estudante.** |
| **Paciente especial → resposta exótica** | A palavra "imunossuprimido/neoplasia/gestante" puxa para a complicação rara/grave em vez da **mais comum** | s086 exantemáticas (Q2: imunossuprimido→marcou PEES; a mais comum é pneumonia) |
| **Achado normal/ausente = exclusão, não lacuna de dado** | Um exame ou achado **dentro da normalidade / ausente** é lido como "faltou informação", quando na verdade ele **exclui ativamente** o diagnóstico/conduta mais saliente | s131 simulado — **5 temas, 100% erro quando aparece**: bridas sem peritonite (não é cirurgia), demência vascular sem ventriculomegalia (não é HPN), pré-eclâmpsia sem sinais de gravidade (não interna), cancroide com dor presente (exclui sífilis). Síntese em [[feedback_bug_discriminador_exclui]] |
| **Pula a hierarquia do exame/conduta inicial** | Gravidade aparente do quadro empurra direto pro exame/conduta **mais avançado**, pulando o degrau **inicial** (barato/simples) que a condição pede primeiro | s131 simulado — 3 temas: lombalgia com sinal de alarme→RM direto (devia ser radiografia); anemia perniciosa→biópsia de medula direto (devia ser anti-FI); TCE leve com intoxicação→neurocirurgia direto (devia ser TC). Irmã diagnóstica do "reflexo de over-tratamento" acima (mesma lógica, eixo diagnóstico em vez de terapêutico) |

---

## Sub-família à parte: conhecimento desatualizado (não é bug de processo)

*Adicionado na s131 (simulado ENARE/ENAMED, 100q, 54%). Mecanismo diferente do resto da tabela: aqui a verificação **foi** completada, mas contra uma versão **desatualizada** do fato/protocolo. Não é "parou cedo", é "a régua na cabeça está velha".*

**Confirmado em 4 especialidades no ledger de habilidades** (`tools/habilidades.py --reincidentes`): SBC-HAS 2025 (nova faixa "pré-hipertensão" 120-139/80-89), Reanimação Neonatal 2026 (sem aspiração traqueal de rotina mesmo com mecônio espesso), Diretriz de Dislipidemia 2025 (meta de LDL <40 em risco extremo/eventos recorrentes), ATLS 11ª edição (xABCDE — controle de hemorragia exsanguinante antes da reposição volêmica).

**Reflexo a treinar (distinto do tripé de comporta):** antes de aplicar uma diretriz/protocolo numérico ou classificatório que você aprendeu há tempo, perguntar **"essa regra teve atualização recente que eu não incorporei?"** — especialmente em temas com sociedade/diretriz nomeada explicitamente no enunciado (SBC, GINA, ATLS, MS). Não dá pra "decorar de novo" preventivamente; o achado serve de alerta para checar quando a questão *cheirar* a atualização (ano citado, "segundo as diretrizes mais atuais", termo que parece novo).

---

## Evidência da s085 — 6 temas em 1 dia

Na revisão e no bloco de neonatologia, a **mesma assinatura** disparou em:
- **Cardiopatias:** dx certo, porquê ausente (441/442/98).
- **Trauma:** conduta sem checar **estabilidade** (37, 84).
- **Hemostasia:** levou "anticorpos" para o **contexto errado** (426).
- **DM2:** acertou o destino, **inverteu a seta** do mecanismo (54 — natriurese).
- **Ectópica:** **tratou antes de confirmar** (114 MTX, 116 laparotomia).
- **Icterícia neonatal:** **ancorou nos tipos sanguíneos** (6 das 15 erradas).

Não é coincidência nem azar de tema. É **um** gargalo, transversal. Por isso o decompose rende mais que estudar mais um assunto: ataca a raiz comum.

---

## Evidência da s131 — simulado ENARE/ENAMED (100q, 54%), 3 padrões cruzam o limiar

Primeiro simulado completo desde a virada multi-banca (s126). Resultado bem abaixo do patamar de blocos por tema (54% vs 78,2% de média) — mas o gap virou 3 mecanismos nomeados via `tools/habilidades.py --reincidentes`, não um "esqueci tudo":

- **Achado normal/ausente = exclusão** (ver tabela acima): confirmado em **5 especialidades**, 100% erro quando aparece. Já vinha de s128 (Hepato); este simulado somou Cirurgia, Neurologia e Obstetrícia.
- **Pula hierarquia do exame inicial** (ver tabela acima): **3 especialidades**, 100% erro quando aparece. Padrão novo, nascido nesta sessão.
- **Conhecimento desatualizado** (ver seção própria acima): **4 especialidades**, mecanismo diferente (não é processo, é régua velha).
- Confirmação direta de área fraca preexistente: **drenagem biliar (colangite/coledocolitíase) foi atingida 2x** na mesma sessão (Q31 colangite aguda, Q98 CPRE-vs-colecistectomia) — mesmo tema do radar de 884 erros. E **tamponamento cardíaco antes de laparotomia** bateu direto na área "sequência ATLS desorganizada" já catalogada.
- **Achado metodológico:** o bloco de 20q com pior desempenho (35%, Bloco 4) não tinha questões mais difíceis que os outros blocos pela dificuldade populacional média (~51% ali vs 49-60% no resto) — o usuário relatou atenção dividida durante a prova. Reforça que **variância intra-prova também é sinal de execução**, não só de conteúdo.

---

## Os gatilhos (quando o bug dispara)

1. Quando há um **dado muito saliente** (número fora da faixa, fármaco, incompatibilidade aparente, diagnóstico clássico).
2. Quando a pergunta é **"por quê"** ou **"o que exclui"** — você para no "o quê".
3. Quando você **já domina a conduta de um tema vizinho** — transfere sem rechecar a comporta.
4. **Pior sob fadiga** (motivo nº 1 para não estudar exausto).
5. **Temas densos em comporta** (hemato/hepato/imuno/neonato) **amplificam** o custo — não é falta de aptidão, é o bug encontrando mais comportas para pular.

---

## O reflexo a treinar (rodar em TODA questão, ~2 segundos antes de marcar)

1. **"Qual é a COMPORTA deste tema?"** — a variável que muda tudo.
2. **"Passei por ela, ou pulei pro dado saliente?"**
3. Se a pergunta é **"por quê" / "o que exclui"** → dê **MAIS UM passo** depois do fato. *("É T4F" → "e por que não atresia? — a idade.")*
4. Antes de aplicar uma **conduta conhecida** → *"a comporta deste caso é a mesma do caso onde aprendi essa conduta?"*
5. **Enunciado negativo (EXCETO/ERRADA)** -> rotule cada alternativa **V/F** e **conte os F: deve dar exatamente 1**. Deu **0** (não achei a falsa) ou **2** (rotulei alguma errado)? Você **NÃO terminou** -- volte nas duvidosas, não chute. O nº de F é o *checksum* da questão. (s120: Q1 terminou com 2 F -> chutou e errou; Q3 terminou com 0 F -> não achou a falsa e perdeu.)
6. **(s131) O tripé, antes de marcar QUALQUER resposta:**
   - **"Qual dado aqui EXCLUI a opção óbvia?"** (achado normal/ausente conta como exclusão, não como silêncio)
   - **"Isso é protocolo/diretriz que mudou recentemente — minha régua pode estar velha?"**
   - **"Estou pulando o exame/conduta inicial pro avançado só porque o quadro parece grave?"**

---

## As comportas por tema (o que checar ANTES de responder)

| Tema | Comporta(s) — a ordem importa |
|---|---|
| **Trauma** | **Estável ou instável?** (instável→sala/laparotomia; estável→imagem/seletivo/laparoscopia) |
| **Icterícia neonatal** | **Tempo** (<24h=hemólise / 3-5d=fisiológica / >1sem=prolongada) → **Direta ou indireta** (direta=colestase/AVB) → **Regras de incompatibilidade** (ABO=mãe O; Rh=mãe Rh-/bebê Rh+/sensibilizada) |
| **Ectópica** | **Confirmou?** (zona discriminatória + curva 48h) → **Estável?** → MTX (baixo/pequeno/parado) vs cirurgia vs expectante |
| **Hemostasia** | Que **braço** (mucocutâneo×profundo)? → **TP/TTPa**? → mistura **corrige**? → defeito **funcional oculto** (uremia/hipotermia)? |
| **Cardiopatias congênitas** | **Cianose = shunt D→E?** → a **idade**? → **canal-dependente**? |
| **Mecanismo de fármaco** | A **seta** está na direção certa? (não inverter causa/efeito) |
| **Sepse neonatal** | **Tempo** (precoce<72h vs tardia) define agente e antibiótico |
| **Doenças exantemáticas** | **(1) Febre↔exantema** (roséola: febre some ANTES) → **(2) a MARCA** (Koplik=sarampo / face esbofeteada=parvovírus / polimórfico=varicela / língua framboesa+lixa=escarlatina) → **(3) viral×bacteriana** (só escarlatina = ATB). Ler até o fim: coriza/tosse NÃO fecham sarampo |

> Atualizar esta tabela conforme novos temas forem dissecados em revisão/análise de questões. A comporta de cada tema é o que o `/revisar` e a análise de erro devem extrair e nomear em tempo real.
