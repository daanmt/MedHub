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
| **Enunciado negativo (EXCETO/ERRADA)** | Marca a afirmação **verdadeira** em vez de isolar a falsa (primo de *leitura*, não de verificação) | s079-080 (3×) |

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
5. **Enunciado negativo (EXCETO/ERRADA)** → rotule cada alternativa **V/F** e marque a **F** (processo separado, deliberado).

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

> Atualizar esta tabela conforme novos temas forem dissecados em revisão/análise de questões. A comporta de cada tema é o que o `/revisar` e a análise de erro devem extrair e nomear em tempo real.
