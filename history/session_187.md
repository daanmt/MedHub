# Session 187 -- Janela de engenharia 6: o selo da reforma

**Data:** 2026-09-18 (tarde -> noite)
**Ferramenta:** Claude Code / Opus 5 (1M context)
**Tipo:** ENGENHARIA
**Custo:** ZERO subagentes -- nenhum lote passou o limiar do F93; o principal fez tudo.

Delegacao do operador, verbatim: *"Continue o trabalho ate o selo de 'completa'. Decida a melhor estrategia no meu lugar, junto ao medhub."* -- os gates de ENGENHARIA passaram a ser decididos pelo `/ai-eng` (N=80); os de DADO/politica continuaram dele.

**11 commits, harness verde em cada um, suite 858 -> 912.** Zero questoes, zero cards revisados.

---

## Tabela da janela

| Item | Terminal |
|---|---|
| **F115** | ✅ FEITO -- comprimento TOTAL do card ganha gate (`140e284`) |
| **1.10** | ✅ FEITO (mecanismo) + 4 portadores centrais 100% (`9ea675a`, `29b4e61`) |
| **Invariante A** | ✅ FEITO -- o ensino nunca escreve FSRS, agora com gate (`966995a`) |
| **F99** | ✅ FEITO -- `fsrs_queue --card CARD_ID`, leitor read-only por id (`966995a`) |
| **G14b** | ✅ FEITO -- cabecalho x versao do portador (`011eb83`) |
| **F104** | ✅ FEITO na metade que e minha (`TCE.md` reescrito) + GATE do operador (`011eb83`) |
| **F116** | 🆕 ACHADO e RESOLVIDO -- o linter no `--staged` auditava o corpus inteiro (`ed61f16`) |
| **F117** | 🆕 ACHADO e RESOLVIDO -- o DRENAR do chat mandava re-drillar ate sair 4 (`4230cdd`) |
| **F36 · F72** | ⚰️ SUPERADOS -- o sujeito do achado foi removido na part-8 |
| **F109 · F110** | ⚰️ cabecalho corrigido -- os riders pousaram na s185 |
| **Selo** | 🔒 `tools/selo.py` -- 0 sem terminal, 0 discordancia (`ffc7bde`) |

---

## O fio da janela: *o sensor alcanca exatamente o que diz alcancar?*

Quatro achados, quatro faces da mesma pergunta. Nao foi tema escolhido -- apareceu.

- **F115 -- escopo MENOR que o necessario.** `LIMITE_CHARS = 220` media so o VERSO e so na reforja; um card nascia com 1.130 chars espalhados por contexto+pergunta+verso sem estourar nada.
- **Invariante A -- o sensor mira a coisa VIZINHA.** A allowlist do F49 cobre escrita SQL direta por arquivo e nunca veria `dormant_refresh` chamando `db.record_review`, porque a escrita aconteceria dentro de `db.py`, que esta legitimamente na allowlist.
- **G14b -- o sensor olha o REGISTRO vizinho.** O G14 compara o cabecalho do achado contra a lapide do §11; F109 e F110 nunca entraram la.
- **F116 -- escopo MAIOR que o declarado.** O linter no `--staged` auditava os 136 resumos rotulando-se "(1 arquivos)".

---

## 1. F115 -- a derivacao entrega uma BANDA, nao um numero

As 6 marcas do operador na previa do R2 bound-eiam o corte em **[736, 1059]**, e **dentro da banda todo corte tem precisao identica no lote** (2/2 positivos, 4/4 negativos): n=6 nao discrimina por dentro, por construcao. E a banda e cara -- 736 daria **334 cards** (22,2%), 1059 da **30** (2,0%): fator 11 sobre a mesma evidencia.

**1059** e o unico ponto com regra declarada: *nenhum card sinalizado e mais curto que o mais curto que ele mesmo chamou de longo*. `test_o_corte_esta_dentro_da_banda` derruba a suite se alguem mover o numero sem mover a evidencia.

🔴 **A suite pegou um defeito que leitura nenhuma pegaria.** Escrevi `>` e o **#92 tem exatamente 1059 chars** -- o gate perderia um dos DOIS cards que o originaram. *Gate reprovado na propria evidencia fundadora.* Forma nova: nao e escopo errado, e **fronteira fora por um**, e so aparece quando o caso-fonte vira fixture com o numero real.

Os 30 candidatos foram ingeridos na fila de reforja sob o rito §10.7 (backup, COUNT-ASSERT 291 -> 321, `flashcards` e `revlog` intactos), por decisao do `/ai-eng`: sensor sem terminal e a divida que a janela existe para fechar, e `--descartar` e a reversao.

## 2. Item 1.10 -- anotar clausulas e varredura que acha defeito vivo

O mecanismo: tres terminais anotados **no proprio portador**, com o registro de gates **DERIVADO** (slugs do `auto_check` + modulos e funcoes de teste por AST; 1.031 nomes). Anotacao que nomeia gate inexistente nasce **BLOCK** -- *cobertura aparente e pior que cobertura ausente*, o F90 um nivel acima.

O terceiro terminal (`NAO-NORMATIVA`) existe porque o detector e lexical e erra ~14%: linha narrativa que CITA uma regra nao e prescricao, e marca-la "nao-verificavel" seria mentira -- nao e regra sem gate, **nao e regra**. Fica em coluna propria, fora do denominador.

**Inventario:** 347 hits crus -> 64 removidos por medicao (doc de flag de CLI, que o argparse ja impoe, e heading) -> **287**; 40 marcadas nao-normativas -> **247 normativas**. Amostra de 14 lida a olho antes de reportar: 12 normativas (~86%).

🔴 **O 1.10 se pagou na primeira anotacao** -- foi anotando `revisar.md` que o F117 apareceu.

## 3. F117 -- a prescricao morta que o gate nao via, e o limite estava declarado

`revisar.md:187` prescrevia *"todo card avaliado **< 4** (1, 2 ou 3) ... **ate sair 4**"*. A linha 146 do mesmo arquivo e `player.html:397/:463` usam **`< 3`**.

Sob a regua v2 (s186) `3 = lembrou` e o caso normal e o alvo; `4 = sem esforco` e raro -- o F114 mediu **zero exemplo de Easy** no corpus. A regra morta manda re-drillar **todo acerto comum ate virar sem-esforco**: um loop que nao fecha. E governa o caminho **CONVERSACIONAL**, o que roda quando o operador drena pelo celular.

🔴 **O `CONTRATO_REVOGADO` casa substring LITERAL, e `AGENTE.md §10.10` ja declarava esse limite verbatim.** A s186 cadastrou a redacao do **player**; a do **chat** e outra string e passou. *O limite declarado do gate mordendo um dia depois de ser declarado.* Resolvido pelos 3 passos do §10.10 no mesmo commit, com 3 redacoes cadastradas.

**Impacto medido: ZERO.** So existem 3 linhas v2 no revlog (ids 3072-3074, todas 18/09 12:28, todas nota 4, todas do lote do player); zero card com 2a linha v2, zero nota 3 sob a v2. A regra morta nunca teve chance de disparar. ⚠️ Limite: o revlog nao distingue player de chat por coluna -- infiro pelo timestamp identico, assinatura de `--record-lote`.

## 4. F104 -- o achado subestimava o defeito, e o linter dava PASSED

O ledger dizia "linguagem coloquial". Eram **mecanismos clinicos INVERTIDOS**:

- `TCE.md:67` afirmava que o manitol "hiperglicemico **perfura a barreira encefalica**". E o oposto: ele age **porque nao atravessa** a BHE integra -- fica no intravascular e cria o gradiente osmotico. A frase ensinava exatamente a alternativa errada de uma pegadinha classica.
- Hiperventilacao agindo em "macro arterias subaracnoides" (e arteriolar); "35 incursoes" confundindo alvo de PaCO2 com FR; "Triade **Branca** de Cushing" (nao existe); LAD "que nao recupera a 9"; PECARN reduzido a prosa incoerente. Mais ~25 erros de digitacao.

🔴 **E o `audit_resumos` dava PASSED nesse arquivo** -- ele ve ESTRUTURA, nao semantica. **Um resumo pode estar clinicamente invertido e verde**, e e por ele que o operador estuda. O linter passou a **declarar o escopo na propria saida**, e o rotulo de sucesso deixou de ser "AUDITORIA PERFEITA": virou "ESTRUTURA OK".

## 5. F116 -- o achado saiu de dois numeros que nao batiam

No commit do F104 o harness imprimiu `Linter de Qualidade de Resumos (1 arquivos)  ⚠️ 35 WARN`, com o arquivo staged medindo `WARN_TOTAL=0`. Os 35 eram o passivo GLOBAL dos 136 resumos. Causa, uma linha: a lista de arquivos so era anexada no `--changed`, e **`--staged` e o modo do git pre-commit hook**.

Duas consequencias: o rotulo mente (**eu ia registrar os 35 no ledger como propriedade do `TCE.md`**) e o **escopo do gate** e outro -- BLOCK em resumo alheio derrubaria commit que nao o toca. Nao mordeu porque o `BLOCK_TOTAL` global esta em 0: **sorte, nao desenho**. E contradizia `AGENTE.md §6` verbatim.

## 6. O selo recusou fechar 4 vezes

`tools/selo.py` deriva a tabela item -> terminal. Ele **recusou fechar quatro vezes**, e nas quatro havia coisa real: **17 achados com cabecalho sem classe nenhuma** (F1-F9, F21, F63, F65, F67-F69 -- os mais antigos do ledger nunca carregaram status); **F36 e F72** dizendo ABERTO com o sujeito removido; **F78 e F2** sem terminal; e **3 sensores novos sem limite declarado na docstring** -- consertei os 3 sensores, nao o verificador.

🔴 **Terceira forma de cabecalho mentiroso, DECLARADA e nao construida:** o achado morreu porque o **codigo que ele descrevia deixou de existir**. Nem o G14 (quer lapide no §11) nem o G14b (quer portador reivindicando) a veem. Base = 2; nao paga um terceiro gate.

---

## Erros meus nesta sessao

1. 🔴 **Reproduzi um defeito que o proprio ledger ja registrava.** Escrevendo `selo.py` por heredoc, pus uma sequencia de escape numa string **nao-raw** e gravei **backspace (0x08)** dentro de dois regexes. Um deles fazia **todo achado RESOLVIDO aparecer como "SEM TERMINAL"**. O modulo importava, o regex compilava, a saida era *plausivel* e simplesmente nao era verdade -- e o ledger ja tinha isso escrito para o `audit_resumos`: *"regex corrompido por 0x08 ... linter verde, check morto"*. Virou `test_sem_caracter_de_controle` (BLOCK, com a prova do DANO e nao so da presenca), **e o gate me pegou repetindo o mesmo erro 10 minutos depois**. Convencao que fica: **regex sempre em string RAW**.
2. 🔴 **Escrevi `>` onde devia ser `>=` no F115** -- o gate perderia o #92, um dos dois cards que o originaram. Pego pela suite, nao por leitura.
3. 🔴 **Um teste meu tinha `or True`** (tautologia) em `test_status_portador`. Verde sem testar nada -- a licao da s186, cometida por mim. Reescrito com positivo sintetico.
4. 🔴 **Um fixture meu dropou o prefixo que tornava a corrupcao fatal.** Em `test_sem_caracter_de_controle`, simplifiquei o padrao e o teste falhou -- por sorte, porque a simplificacao apagava justamente o que fazia o byte importar.
5. Escrevi o `clausulas_check` **antes** do teste. Compensei plantando o defeito (desligando a validacao do registro) e confirmando que a suite cai -- nao aceitei verde de nascenca.

---

## Numeros da janela

- **Commits:** 11 (`a9dfb34` `140e284` `9ea675a` `966995a` `011eb83` `ed61f16` `4230cdd` `29b4e61` `ffc7bde` + 2 de fechamento)
- **Suite:** 858 -> **912** (+13 F115, +11 1.10, +5 Invariante A, +8 F99, +7 G14b, +6 F116, +4 controle)
- **Subagentes:** **0**
- **Operacao em lote sob o rito §10.7:** ingestao dos 30 candidatos do F115 (backup `ipub_backup_20260918_175908`, COUNT-ASSERT 291 -> 321)
- **FSRS preservado:** 1543 cards / 3070 revlog o tempo todo -- nenhuma escrita de revisao nesta janela
- **Item 1.10:** 0% -> **49,4%** (53 CHECK · 69 declaradas · 125 orfas em 247 normativas)
- **AGENTE.md §7.4 regenerado 5x** (tabela GERADA, por contrato)

---

## Fronteiras declaradas (nao ler verde de gate como limpeza)

- **DECLARADO e NAO construido, com a contagem:** 3a forma de cabecalho mentiroso (base 2) · familia de tokens no `CONTRATO_REVOGADO` (2 limiares reais em 23 termos, mesma regra) · coluna `origem` no revlog (player x chat, hoje inferida por timestamp).
- **O item 1.10 nao esta completo:** 125 clausulas orfas em 14 portadores, com contagem por portador no HANDOFF.
- **`audit_resumos` mede forma, nunca verdade clinica** -- declarado na propria saida desde esta sessao.
- **`CONTRATO_REVOGADO` casa substring literal** -- uma 4a parafrase passaria.
- **Invariante A:** o gate cobre o CODIGO do caminho de ensino, nao o comportamento do agente.
- **F113 PARCIAL** (#685/#689). **F110** sem gate por construcao. **F78** e **F2** declarados nao-verificaveis com data.
- **6 GATES do operador abertos** -- ver HANDOFF.
