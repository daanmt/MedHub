# Session 128 — Hepatologia S13 (41q) + dreno de 40 cards + atomicidade do baralho (F39)

**Data:** 2026-07-25 (estudo) -> 2026-07-26 (fechamento, virou a madrugada)
**Ferramenta:** Claude Code (Opus 5 [1M])
**Continuidade:** Sessão 127

---

## O que foi feito

### Bloco de Hepatologia — S13, questões-primeiro
- Aplicada a **regra híbrida nova** (s127): `--difficulty` deu **D5 (nota 6)** para Hepatites Virais -> foi direto às questões, **sem aula-base prévia**. Transtornos de Humor deu **D10/extensivo/deep-research** e foi adiado — teoria pesada na véspera de simulado é sequenciamento ruim.
- **Bloco: 41q / 28a = 68,3%.** Abaixo da média geral (79%), mas Hepato vinha de **57%** no dashboard. 6 das 13 erradas tinham acerto nacional < 50% (uma com 25%).
- **13 erros analisados e persistidos** via `insert_questao.py --errors-file` (lote transacional), gerando **32 cards**. Temas: `Hepatites Virais`, `Introdução à Hepatologia e Icterícia Não Obstrutiva` e **`Hepatopatias da Gestação`** (tema novo — a interface que o usuário sinalizou não dominar).

### 🔴 Achado do padrão-mestre: o discriminador é um exame NORMAL
6 dos 13 erros são o padrão-mestre (ancora no achado saliente, ignora o que exclui). Mas em **3 deles o discriminador era um valor NORMAL** — Q5 (transaminases normais excluíam hepatite), Q10 (hemograma e DHL normais excluíam hemólise), Q13 (transaminases normais excluíam indicação de tratar). **Faceta nova:** o usuário processa achado alterado com precisão e lê "normal" como ausência de informação. Ritual cunhado: *"o que está normal aqui, e o que esse normal proíbe?"* Registrado no ledger de habilidades em 2 temas.

### Cards de VM da s127 (pendência fechada) + correção de um erro meu
- **11 cards** cunhados dos 6 erros de VM (`insert_card_base`, tema_id=260) — curvas, assistido x controlado, VCV x PCV, obstrutivo, autoPEEP, Berlim.
- 🔴 **Descoberto:** os 6 erros de VM da s127 **nunca entraram em `questoes_erros`** — só o volume e as habilidades. Virou **F38** no ledger, com retroativo: 466 erros esperados x 335 gravados = **delta de 131 (~28%)**, com a ressalva de que parte vem de volume importado da planilha (teto, não piso).
- 🔴 **Errei ao afirmar que faltava a seção de VNI no resumo.** O grep buscou "VNI" e o resumo escreve "VMNI". A seção 7 existe e é completa — inclusive a linha *"IRpA pós-operatória (primeiros 7 dias)"*, que era exatamente o conteúdo da Q6. Reenquadramento: **não foi lacuna do resumo, foi lacuna da minha aula.** 4 cards de VNI cunhados com o lastro que já existia.

### Dreno FSRS — 40 cards em 5 blocos de 8
- **Média 2,83** — 15 notas 4 · 7 notas 3 · 14 notas 2 · 4 notas 1. Por bloco: 3,75 / 2,13 / 2,75 / 2,88 / 2,63.
- Bloco 1 era relearning de cards já vistos no mesmo dia (todos com nota 1 às 11h26); do bloco 2 em diante foi **estreia fria de pool**. Leitura honesta: ~2,6 em recall verdadeiramente frio.
- **Clusters de gap (Revisão Direcionada entregue):** Emergências do DM (5 cards, média 2,0), LRA (3 de 4 abaixo), Úlceras Genitais (4 abaixo).

### 🔴 F39 — 40% do baralho viola o princípio atômico (achado do USUÁRIO)
O usuário percebeu, no meio do dreno, que **a frente que ele via era comprimida enquanto o verso trazia exigências extras** pelas quais estava sendo descontado, e formulou a régua melhor do que o contrato tinha: *"que os cards não tenham diversos requisitos de acerto, e focassem no núcleo epistemológico do erro"*.
- **Custo já materializado:** eu havia contabilizado **6 ocorrências** de um padrão de erro dele ("para na primeira metade") usando cards duplos como evidência. **5 das 6 eram defeito do card** — estava importando ruído do baralho para o prontuário cognitivo dele. Retratado na hora.
- **Reincidi duas vezes na mesma sessão:** (a) pré-anunciei quais cards eram "capciosos", contaminando a sonda (é o F8 do meu próprio ledger); (b) depois de catalogar o defeito duplo, servi mais 3 cards duplos no bloco seguinte. Ambas apontadas pelo usuário, ambas corrigidas com regra nova ("em card duplo avalio o núcleo; a segunda metade é adendo, nunca desconto").
- **Entregue:** `tools/audit_card_atomicity.py` (detector read-only, WARN-first, com a classe de falso-positivo do **card discriminador** documentada); **check 9 do `auto_check`**; cláusula **"UM CRITÉRIO DE ACERTO por card"** em `estilo-flashcard.md` + espelho sincronizado; **8 cards atomizados** (reescrita in-place preservando FSRS + 12 desmembramentos).
- **Medida:** 358 de ~900 cards ativos — 227 duplo-ask, 259 resposta-multifato, 122 ambos.

### Conta de ritmo — a notícia boa
O `day_plan` reporta "20,9 q/dia real x 64 necessários", o que soa fatal. Refazendo por **dia trabalhado**: julho fechou **853 questões em 15 dias de estudo = 56,9 q/dia trabalhado**, já **acima** dos ~53/dia que a meta pede a 6 dias/semana. O gargalo é **frequência (15 de 26 dias = 58%)**, não capacidade. A 6 dias/semana o marco de 9.454 cai (~9.745 projetado). **Não fecha:** cobertura da grade EMED inteira exigiria ~75 q/dia trabalhado — a 6 dias/semana chega-se a ~76% da grade até 25/10. Fork registrado, não decidido.

---

## Padrões de erro vivos

- 🔴 **Padrão-mestre — faceta nova: o discriminador NORMAL.** 3 instâncias limpas hoje.
- 🔴 **Bug nº 1 (número contra a régua)** — card 421: "diálise depende do valor?" -> não, depende de AEIOU.
- 🟡 **Pergunta composta** — existe e está catalogado *de questões de prova*, mas as 6 ocorrências que contei hoje eram 1 real + 5 defeito de card. **Não inflar.**
- 🟢 **Sensor em desenvolvimento:** no card 462 ele *verbalizou* o discriminador ("essa função mínima aí é foda") e ainda assim respondeu furosemida. Detecta, não converte em mudança de resposta — é o alvo do próximo ciclo.

## Estado ao fechar

- Volume **5.295** / 9.454 · perf. ~79,0% · ritmo-alvo 45,7q/dia (91d).
- FSRS: dívida 0 · pool **395** nunca introduzidos · 40 revisados hoje.
- Cards: **908** no banco (+47 cunhados, +12 desmembrados, 9 reescritos).
- Erros: **606** (+13).
- ⚠️ Drive stale há 17 dias (F36, elevado a ALTA).

## Próximo passo

**SIMULADO ENAMED de 100 questões (26/07)** — fecha o débito aberto desde 28/06 e é a primeira medição de variância em condição de prova (desvio atual 11,9 pp, gargalo isolado nº 1). Registrar com `--area Simulado`. Depois: as 2 tasks restantes da S13 (Transtornos de Humor com aula-base D10; Arboviroses+Meningites+Sepse direto a questões) e o ataque em lotes à worklist de atomicidade (227 duplo-ask primeiro).
