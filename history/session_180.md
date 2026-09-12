# Session 180 -- Simulado 9 (86/100): o override do modal ganha nome, numero e regra; e o Raio-X dos 9 simulados

**Data:** 2026-09-11 (noite, ~23h20) -> 2026-09-12 (madrugada, ~01h30) - **Ferramenta:** Claude Code (Opus 5 1M -> Fable 5.1 no fechamento) - **Continuidade:** `session_179.md` (mesmo dia, tarde)
Sessao de **ESTUDO**. Zero engenharia. Abriu com o operador trazendo o Simulado 9 feito na noite de 11/09 e os 5 PDFs em `simulados/`.

---

## 0. O que o usuario trouxe

- *"fiz um simulado hoje, 86/100. foda."* -- Simulado 9 (ENARE 2024, 100q), PDFs `simulados/Simulado 9 - parte 1..5.pdf`.
- **Primeira aplicacao da regra nova da s179:** ele mandou as 14 erradas **com o racional de cada marcacao**, sem que eu pedisse. Foi isso que tornou o achado desta sessao possivel.
- Encerrou pedindo um **overview de todos os simulados** cruzado com padroes de erro e temas de cards, e o fechamento formal. Sabado 12/09 = descanso + 100-200 cards.

## 1. Registro e extracao -- ordem dura respeitada

`registrar_sessao_bulk --sessao 180 --area Simulado --feitas 100 --acertos 86` **antes** de qualquer analise. Acumulado **7.126 -> 7.226**.

**Metodo de extracao (reutilizavel, confirmado pela 2a vez -- s171 foi a 1a):** o PDF do Estrategia traz por questao `CERTA|ERRADA`, `ANULADA`, `GABARITO PROVISORIO` e "N% ACERTARAM", mais o percentual de marcacao por alternativa. **O gabarito e a alternativa cujo % bate com o do cabecalho**; quando uma letra some na extracao, ela e o complemento (100 - soma das outras 4). Parse em `scratchpad/parse2.py` + `final.py`: 98 cabecalhos lidos, 2 perdidos em quebra de pagina (#60 e #100, ambos CERTOS por aritmetica: 84 + 2 = 86). Um empate (A/B em 43%) resolvido lendo o texto -- era erro de leitura de um " 31%" com espaco. A numeracao derivada do id sequencial divergiu da tela em 1 (meu 75 = Q76 dele); usei a **dele** no banco.

**Estrutura da prova:** 5 anuladas (Q1, Q5, Q42, Q45, Q99 -- ele errou so a Q1) e Q82 com gabarito PROVISORIO (acertou). Leituras: bruto 86/100 · com anulada creditada 87/100 · so nas 95 validas 82/95 = 86,3%. **Tres provas seguidas acima do banco (79%)**: S7 82, S8 82,1, S9 86.

## 2. O achado -- o override do modal (medido, nao inferido)

Cruzando as 13 erradas reais com a distribuicao de respostas dos candidatos:

| metrica | valor |
|---|---|
| vezes que marcou a alternativa mais votada | **0 de 13** |
| media do % da alternativa marcada | **17,9%** |
| media do % do gabarito | **63,5%** |
| extremos | Q66: marcou 2%, gabarito 88% · Q33: 10% x 86% |

Em **4 questoes ele narrou o mecanismo**: Q26 *"achava que a B fazia mais sentido"* (B era o gabarito); Q28 sabia APC **e** sabia atividade fisica -- as duas metades da D -- e *"apostei na alternativa menos provavel"*; Q66 *"a mais provavel era a resposta obviamente"*; Q81 descartou a certa por *"excesso de assertividade"* (comentario oficial: *"correta, sem ressalvas"*). Mais a Q33 parcialmente. Nas palavras dele: *"resolver inventar moda e tentar pensar de forma diferente para nao ser pego em pegadinhas, mas acabar errando por justamente nao haver pegadinha na questao."*

**Custo aritmetico: 4-5 questoes. O 86 era 90-91.**

**Por que e familia nova:** todo padrao catalogado ate hoje (bug n1 e sub-tipos) e *analise clinica que para cedo*. Este e o oposto -- a analise termina certa e uma segunda decisao meta-cognitiva a descarta. **Nao se corrige com conteudo.** O S8 ja mostrava a assinatura (*"nunca marcou o distrator dominante"*: 7%, 6%, 18%, 14%) e a s171 leu como nota de extracao.

**Registrado em 3 portadores:** `docs/PLAYBOOK_EXECUCAO_PROVA.md` (sub-familia propria + **item 7 do reflexo: a regra dos dois finalistas**), memoria `feedback_bug_override_do_modal` (ponteiro + porque) e, nos cards, a alternativa marcada dentro do campo de armadilha.

> **Regra dos dois finalistas:** restaram duas, marca a que a analise apontou. So troca se conseguir **nomear o erro** da favorita. "Facil demais", "assertiva demais", "a banca nao faria isso" nao sao erros nomeaveis. Corolario: a pegadinha real mora no **enunciado** (Q26: VR de 10.000 plantado para gestante), nao na alternativa que parece certa.

## 3. Os erros que sao conteudo (7 de 13)

- **Q2** Ziehl-Neelsen -- chute assumido; coloracao segue a parede do agente (BAAR).
- **Q6** CURB-65 duplo: usou FR > 20 (e >= 30) e esqueceu ureia > 50; e a resposta era **contexto social interna com 1 ponto**. Escore mede risco, nao destino.
- **Q8** FA lida como TSV -- nao mediu RR no DII longo; e marcou *cardioversao quimica* com PA 80/50 (instavel nunca leva quimica -- a 2a metade ja denunciava a alternativa).
- **Q18** Jarisch-Herxheimer = lise treponemica, nao alergia; nao se suspende penicilina.
- **Q19** teriparatida e ANABOLICA; alendronato e antirreabsortivo. PTH continuo reabsorve, intermitente forma.
- **Q76** Gartner = mesonefrico/Wolff, terco superior anterolateral; ele escolheu entre B e D, **as duas de Muller**.
- **Q88** fio 5-0 (mais zeros = mais fino); vaso e **banca-divergente** (EMED discorda do gabarito), o calibre nao.

## 4. O que ficou no banco

- **14 erros** em `questoes_erros` (Q1 anulada **sem card**, F26). **13 cards** (#1615-#1627).
- 🔴 **Defeito meu, pego pelo linter:** 7 dos 13 cards nasceram com **pergunta composta** -- o mesmo defeito que pegou o operador no #583 na s179, no mesmo dia. **11 reforjados** via `recurate_cards.py --apply` antes de entrar na fila (7 frentes desdobradas; 4 armadilhas ganharam a alternativa marcada + %). O detector de atomicidade recusou uma reforja ("quais os dois genes") e ela foi refeita mirando o gap real (MSH2 -> Lynch). FSRS preservado.
- ⚠️ `[SEM-LASTRO]`: **Gastro / Polipos e Neoplasias Intestinais nao tem resumo nem PDF-fonte** -- 4a maior area de erro (19), 9/9 cards capotaram na memoria, e somou a Q28. Card existe, materia nao.

## 5. Raio-X dos Simulados -- artifact

Publicado: **https://claude.ai/code/artifact/b719eb1c-2d16-42ee-a25b-ec70df4b2ed1** (copia versionada em `artifacts/raio-x-simulados.html`). Fontes recuperadas: Autopsia da s143 (`artifacts/autopsia-simulados.html`, blob `D` com 157 erros S2-S5 por mecanismo), `core/simulados/_s{6,7,8}_erros_batch.json`, `habilidades.py --reincidentes`, `review_radar.py --all --json`, `fsrs_queue.py --list --new-limit 200`, `blueprint_enamed.json`.

**Numeros que a serie inteira entrega:**
- 9 provas, 28/06 -> 11/09, **239 erros**: **144 execucao (60%) x 95 lacuna (40%)**. A proporcao nao mudou com a nota; o **volume** de execucao caiu de 28 (S2) para 7 (S9).
- Mecanismo (120 de S2-S4): exclui 30 · comporta 26 · lacuna 23 · desatualizada 10 · contexto 9 · escore 6 · negativo 5 · inversao 4 · categoria 4 · degrau-anterior 2 · par 1. **81% processo.**
- Area (223, S2-S9): **Clinica Medica 33% dos erros** para 27% do ENAMED e **20% da UERJ**; Cirurgia 18% para 21,5%; **MFC = 0 questoes, 0 cards, 0 erros** para 20% da UERJ.
- Baralho: 1.419 ativos / 272 temas / pool **676** (os 13 do S9 entraram) / 272 na reforja. Os 8 temas de maior erro sao os de maior baralho -- a cunhagem seguiu o erro. Dormentes: Anemias Hemoliticas 71d (60%), Olho Vermelho 71d, Potassio/Acido-Base 64d, DM Cronicas 63d, Pneumo Intensiva 48d (19 novos).
- Tabela **padrao -> tema -> remedio** (9 linhas, a 9a e o override).

## 6. Pendencias abertas por esta sessao

1. **`registrar_sessao_bulk` da lista de Diarreia de 09/09** -- **3a sessao seguida** sem feitas/acertos. Os 5 cards de erro fresco de Diarreia (#1598-#1602) provam que o bloco foi analisado; o volume nunca entrou.
2. **Backfill do override no ledger de habilidades** -- as 13 questoes do S9 ainda nao carregam a habilidade "nao sobrescrever a alternativa modal"; `habilidades.py --add ... --veredito errou --questao-id N` por questao. Lote de operador/engenharia, nao desta janela.
3. **Polipos e Neoplasias Intestinais SEM RESUMO** (+ Farmacodermias) -- conteudo, nao card.
4. **Sabado 12/09:** 86 vencidos (14 atrasados + 8 erros frescos + 64 de hoje) + intake dirigido aos dormentes; teto do contrato = 90 em divida, 150 defensavel num dia sem questoes, 200 vira divida na terca. **Domingo: ENAMED.**
5. **Segunda 14/09:** rescope UERJ (CM 27 -> 20%, MFC 6,7 -> 20%) + quais ~460 dos 676 entram ate 01/11.
6. F98 (blackout nao cobre intervalo < 4d), F99 (sem CLI por id), F100 (re-ensino nao fecha fato arbitrario) seguem **abertos** no ledger; permit de engenharia consumido.
