---
type: report
layer: root
status: working-draft
relates_to: [AGENTE, ESTADO, HANDOFF]
---

# AUDITORIA_MEDHUB -- o que esta EM ABERTO

> **Este arquivo so tem achado em aberto.** O que foi resolvido mora em
> `history/auditoria/resolvidos.md`, com o texto inteiro e as secoes narrativas de cada sessao.
> Decisao do operador em 28/09/2026 (s204): *"o que resolvermos, sai da frente"*.
>
> **Encoding:** ASCII limpo, Zero LaTeX, sem setas Unicode (AGENTE.md secao 4.5). Usar `->`, `<=`, `--`.

## Como usar

1. **Ver o estado:** `python tools/selo.py` -- aberto x resolvido, e quem decide cada item. **Achar um achado:** `python tools/selo.py --onde F38`.
2. **Antes de escrever achado novo:** buscar o mecanismo AQUI e no historico (`grep` pelos termos). Se ja existe, a entrada nova cita a antiga. Gate-miss da s204: o F140 re-derivou errado o que o F32 ja tinha certo.  <!-- NAO-VERIFICAVEL: nada le a intencao de escrever um achado; conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->
3. **Cabecalho do achado:** id, titulo, severidade e status, nesta ordem, separados por ` -- `. Severidade: ALTA (fere integridade de estado/SSOT), MEDIA (custo recorrente), BAIXA (polimento). Status que FICA na frente: ABERTO, GATE (pergunta ao operador), DECLARADO (remedio proposto ou nao-verificavel datado), PARCIAL, MITIGADO. Status que SAI: RESOLVIDO, SUPERADO, RETRATADO.
4. **No selo da sessao:** `python tools/selo.py --rotacionar` (dry-run) e depois `--apply --expect N`. O bloco viaja inteiro; nada e reescrito, resumido nem apagado.  <!-- CHECK: test_repo_real_consistente -->
5. **Regime de saldo minimo (s207; aprovado pelo operador em 29/09/2026):** tres destinos -- FRENTE (alguem vai fazer ou decidir, com dono), HISTORICO (`history/auditoria/resolvidos.md`, fechou com prova) e LIMITES CONHECIDOS (`history/auditoria/limites_conhecidos.md`: decisao de NAO fazer, cabecalho `**LIMITE CONHECIDO (revisar: AAAA-MM-DD; ...)**`; o selo acusa a data vencida). Achado NOVO (id > F142) traz a linha `- vizinhos: F.., F..` com o que a busca do item 2 achou -- sem ela o check `frente` recusa. Instancia nova de mecanismo ja registrado vira evidencia do achado antigo, nao id novo.  <!-- CHECK: test_achado_novo_sem_vizinhos_e_recusado_na_frente -->

## Indice

<!-- selo:indice:inicio -->
**Em aberto: 7** · Resolvidos: 115 (em `history/auditoria/resolvidos.md`) · Limites conhecidos: 4 (em `history/auditoria/limites_conhecidos.md`) · indice gerado por `python tools/selo.py --rotacionar`, nunca editado a mao

| Id | Sev. | Status | Quem decide | Achado |
|---|---|---|---|---|
| F111 | MEDIA | GATE | operador | Fase 2 do plano (extensivo, leitura-first: 465 tarefas de teoria em 735; 39q/dia nativo) nao garante recall... |
| F78 | MEDIA | DECLARADO | engenharia | Extracao de PDF descarta em silencio todo conteudo que vive em FIGURA, e nada no harness mede essa perda |
| F69 | MEDIA | GATE | operador | resumos com lacuna de diretriz nova = risco banca-dependente (s165) |
| F63 | MEDIA | PARCIAL | engenharia | a prioridade que governa o estudo nao viaja com o repo (o usuario e a camada de transporte) |
| F39 | ALTA | PARCIAL | operador | 40% do baralho viola o principio atomico; a nota FSRS vira ininterpretavel |
| F16 | MEDIA | PARCIAL | engenharia | Tema cirurgico de alto rendimento sem SSOT clinico (.md); so o PDF-fonte existe |
| F2 | MEDIA | DECLARADO | engenharia | Latencia de shell no ambiente Windows |
<!-- selo:indice:fim -->

## Achados em aberto

### F111 -- Fase 2 do plano (extensivo, leitura-first: 465 tarefas de teoria em 735; 39q/dia nativo) nao garante recall no dia da primeira exposicao: tarefa T sem bloco de questoes gera ZERO sonda -- **MEDIA** -- **ABERTO (decisao do operador; prazo 02/11/2026)**
- **Como apareceu:** o video 1 resolve a primeira exposicao com "3 exposicoes em 24h" (video -> cards do tema na mesma noite -> revisao na manha). No MedHub o card nasce de ERRO (`insert_questao`) ou de andaime (`insert_card_base`); o R1 mini-drill (`orquestracao-contract`) so ve erros frescos de 48h. Na Fase 1 (question-first) isso nao aparece; na Fase 2 aparece por construcao.
- **Evidencia a favor de agir:** Rawson 2013 (relearning ate criterio: >60% x <20% em 24 dias); Murre & Dros (primeiro intervalo apos uma noite). **Evidencia que limita o remedio:** Deng 2015 (deck pronto nao prediz; cards proprios predizem) e Step 2 CK sem beneficio de Anki -- intake **filtrado e pequeno**, nunca bulk.
- 📬 **DECISION BRIEF (R8, entregue na s187; devido ao operador ate 02/11) -- 10 linhas:**
  1. **O problema so existe na Fase 2.** Na Fase 1 (question-first) todo tema chega com bloco de questoes, e o erro gera card. No extensivo, **465 das 735 tarefas sao teoria pura**: o tema e lido e nao deixa sonda nenhuma.
  2. **O que muda no seu dia:** ao rodar `plano.py --concluir` numa tarefa de TEORIA, eu te mostro 5-8 cards candidatos do corpus EMED daquele tema; voce aprova ou corta um a um (30-60 s); os aprovados entram hoje, dentro do teto de 60.
  3. **O que NAO muda:** teto diario, regua de nota, fila FSRS, e o fato de que card de ERRO continua nascendo do erro. Isto so cobre a tarefa que hoje nao gera sonda alguma.
  4. **Custo:** ~1 minuto por tarefa de teoria concluida.
  5. **Evidencia a favor:** Rawson 2013 (relearning ate criterio: 60% x 20% de retencao em 24 dias) e a queda do primeiro intervalo apos uma noite (Murre & Dros).
  6. **Evidencia que LIMITA:** Deng 2015 -- deck pronto **nao** prediz desempenho, card proprio prediz; e Step 2 CK sem beneficio de Anki. Por isso o intake e **filtrado e pequeno**, com triagem sua, nunca bulk.
  7. 🔴 **O risco real nao e tecnico, e de volume:** 465 tarefas x 5 cards = 2.300 cards se a triagem afrouxar. A divida atual ja e 103 vencidos. **A triagem humana e o unico freio**, e ela e sua.
  8. **Reversivel:** sim, e barato. O intake e opt-in por tarefa; cards entrados ficam marcados pela origem e saem por `cards_prune.py` com criterio nomeado. Nada toca revlog nem cards existentes.
  9. **Nao-reversivel:** nada.
  10. ⏰ **Quando decidir: na proxima sessao**, junto com a adocao do cronograma extensivo -- e exatamente ai que o defeito passa a morder. Decidir antes seria decidir no escuro; depois, seria tarde.

- **Remedio proposto (spec, apos GO do operador):** intake por tarefa concluida -- `plano.py --concluir` -> `emed_flashcards.py --query` do tema -> triagem pelo teste de regenerabilidade (humana) -> `insert_card_base` dos sobreviventes no mesmo dia, dentro do teto 60. Muda politica de estudo: precedente F64 (politica e posicao do operador).

### F78 -- Extracao de PDF descarta em silencio todo conteudo que vive em FIGURA, e nada no harness mede essa perda -- **MEDIA** -- **DECLARADO nao-verificavel (s187)** -- medir a perda exigiria comparar o PDF-fonte com o `.txt` extraido por conteudo SEMANTICO (a figura nao deixa marca no texto: a extracao retorna sucesso e o buraco e invisivel). Sensor nenhum existe hoje e o custo nao se paga sem mais dado. A mitigacao demonstrada segue sendo a leitura humana do resumo contra a fonte -- revisar: 2027-03-31
- **Evidencia (s169):** 10 resumos do sprint S17-S20 foram cunhados em paralelo a partir dos PDFs do EMED. Dois agentes independentes reportaram a mesma lacuna com origem unica: `tools/extract_pdfs.py` so captura camada de texto; infografico e tabela renderizados como imagem saem VAZIOS do `.txt`.
  - Caso 1 (Tumores Anexiais): o `.txt` traz literalmente *"a seguir esta o estadiamento da FIGO"* e a pagina seguinte vem so com cabecalho/rodape. O estadiamento inteiro (IA a IVB) evaporou.
  - Caso 2 (Pneumonias Bacterianas): CURB-65, CRB-65 e os tres algoritmos de antibioticoterapia por nivel de cuidado estavam todos em figura.
- **Nao e incidente isolado, e a mesma familia ja declarada:** as "lacunas honestas" do artifact da s168 -- estadios FIGO do CA de ovario, 10 grupos de Robson, minimo de servicos do Decreto 7.508 e a tabela SBC 2025 -- tem exatamente esta causa. Quatro ocorrencias registradas antes desta sessao, tratadas cada vez como limitacao pontual, nunca como classe.
- **O defeito real e o SILENCIO, nao a perda.** A extracao retorna sucesso, o `.txt` existe, o resumo e escrito e passa no `audit_resumos.py` com "AUDITORIA PERFEITA". Nenhum gate compara o que o PDF tem com o que o `.txt` entregou. So um leitor que ja conhece o tema percebe o buraco -- ou seja, exatamente quem nao precisa do resumo. Um resumo com o estadiamento faltando e indistinguivel, para o harness, de um resumo completo.
- **Mitigacao DEMONSTRADA na propria sessao:** o agente de Pneumonias Bacterianas, ao perceber a lacuna, renderizou as paginas relevantes com **PyMuPDF (fitz)** e leu os infograficos visualmente antes de redigir. Todos os itens e cortes do CURB-65/CRB-65 e os esquemas de antibiotico do resumo vieram dessas imagens do PDF-fonte, nao de memoria. Mesmo problema, resolvido -- por iniciativa ad-hoc de um agente, sem estar em lugar nenhum do contrato.
- **Remedio (S):** `extract_pdfs.py` emitir WARN por pagina cujo texto extraido seja despropocionalmente curto para a area da pagina (heuristica: pagina com imagem e < N caracteres). Transforma o silencio em sinal, sem prometer resolver a leitura.
- **Remedio (M):** dar ao `extract_pdfs.py` um modo `--render <paginas>` que gera PNG das paginas indicadas, promovendo a mitigacao acima a passo de primeira classe do workflow `criar-resumo` -- hoje ela depende de um agente ter a ideia sozinho.
- **Remedio (L):** gate de cobertura que cruze os titulos do sumario do PDF com os headers do `.md` gerado.
- **Acao tomada na s169:** subagente `evidence-researcher` acionado para preencher o estadiamento FIGO no resumo de Tumores Anexiais a partir de fonte externa auditavel (hierarquia de `evidence-governance.md`), com citacao de fonte e ano -- em vez de deixar a lacuna declarada em blockquote.
- **Desdobramento (s169, mesma sessao):** o preenchimento do FIGO fechou com fonte canonica (documento oficial FIGO 2014, reconfirmado no update FIGO 2021; espelhado em portugues pela SBP 2019) -- e revelou um agravante que o F78 nao previa: **a figura do EMED nao estava so ausente, estava DESATUALIZADA**. A enumeracao preservada no PDF-fonte lista o estadio **IIC**, extinto na revisao de 2014, e nao tem IC1/IC2/IC3 nem IIIA1/IIIA2. Ou seja: onde a figura extrai, o conteudo pode estar velho; onde nao extrai, ninguem confere. Os dois modos de falha convergem no mesmo ponto cego -- nada no pipeline compara o material do cursinho com a diretriz vigente. Isso aproxima o F78 da lista de "diretrizes novas a conferir" do HANDOFF, que hoje e mantida a mao.
- **Nota de processo:** o subagente `evidence-researcher` foi acionado com um brief que mandava EDITAR o arquivo -- ele e read-only por contrato e nao tem `Edit`/`Write`. Recusou corretamente e devolveu o bloco pronto; a aplicacao foi feita pelo orquestrador. Brief mal-formado, nao falha do agente: pedir escrita a um agente de leitura desperdica um ciclo inteiro.
- **Padrao de fundo:** primo direto do achado de alcancabilidade e do F77 -- um dado que **existe na fonte e e perdido no caminho**, sem que nenhum instrumento acuse a perda. A diferenca para o F77 e que la o descarte era deliberado e documentado; aqui e invisivel ate para quem escreveu o pipeline.

### F69 -- resumos com lacuna de diretriz nova = risco banca-dependente (s165) -- **MEDIA** -- **GATE do operador** (quais diretrizes 2026 entram e decisao clinica dele; lista viva no HANDOFF)
**Evidencia (grep):** `[CIR] Trauma.md` ja tem X-ABCDE, torniquete, hipotensao permissiva, ABC score, pneumotorax oculto/3,5 cm, Beck, tranexamico; **falta** "sangue total > 1:1:1" e "Sellick contraindicada", e a classificacao do choque ainda cita "classe I" (11a ed = leve/moderado/grave). `Prevenção Secundária Pós-IAM (Dislipidemia).md`: 1 mencao a PREVENT/Lp(a)/bempedoico (diretriz 2025 rasa). `Sistemas de Informação em Saúde.md`: conferir SINAN 2026 (esporotricose, anomalias, Oropouche, parotidite). HAS Pt2 (130/80, MAPA) e Epilepsias (levetiracetam EV) ja atualizados. **Fix:** Revisao Direcionada com Regra de Acumulo; os `padroes_banca` do JSON sao a fonte.

### F63 -- a prioridade que governa o estudo nao viaja com o repo (o usuario e a camada de transporte) -- **MEDIA** -- **PARCIAL** (o DADO viajou na s165: `core/cronograma/prevalencia_enamed.json`, 89 temas, + `fsrs_queue --prevalencia`; falta ligar ao `infer_nota` -- residuo nomeado)

**Classe:** input do boot nao e verdadeiro (mesma familia de F45/F47) + regra load-bearing fora
do portador (P7, mas na camada de ESTUDO, nao na de engenharia).

**Observado.** O usuario reordenou o xlsx do Drive a mao por um codigo de cores
**Roxo > Rosa > Salmao** (prioridade por prevalencia no ENAMED, derivada do guia estatistico do
EMED). Essa ordem e o que de fato decide o que ele estuda ate 13/09: das 11 tasks da S17, so
**6 sao roxas** (Diarreia Teoria, SUA Teoria, APS Revisao, Diarreia Revisao, Urologia I,
Pneumonias Bacterianas I). As outras 5 (Cirurgia Vascular Revisao, Vitalidade Fetal, Neoplasias
de Estomago e Esofago, Nefrolitiase, APS Teoria III) nao entram na janela.

**O defeito.** `core/cronograma/grade.json` e um parse **fiel** do `Cronograma.pdf` -- verificado
task a task contra a planilha do usuario nesta sessao: 11/11 batem, mesma ordem. O que ele **nao**
carrega e a cor. Logo:
- nenhum consumidor (`day_plan.py`, `cronograma.py --radar`, `preparacao.py`) sabe distinguir
  roxo de salmao; as 11 tasks pesam igual;
- `infer_nota()` tem o **eixo 4 desenhado para consumir `prevalencia_enamed`** e roda em peso
  neutro por falta do campo -- soquete cabeado, sinal existente, ninguem ligou os dois
  (`core/contracts/revisao-calibrada-contract.md:119`, `docs/plans/s094-revisao-calibrada-PRD.md:265`);
- o snapshot `--sync-drive` (unica ponte para o xlsx real) esta **38 dias velho**.

**Consequencia medida.** A regra so existe em prosa (`HANDOFF.md:9`, `session_161.md:14`) e na
cabeca do usuario. Resultado: ele **reenuncia a prioridade a cada sessao e a cada harness** --
para o Antigravity em 02/09 e para o Claude Code no mesmo dia. O humano virou o transporte de um
dado que o repo deveria carregar. Registrado como "achado registrado, nao resolvido" desde a
**s147** (`history/session_147.md:18`) -- 15 dias em aberto.

**Por que importa agora.** E a propria tese do ciclo DESCOLAR (P7: "regra load-bearing vai para o
portador do repo, nao para a memoria do harness") violada na camada que o projeto existe para
servir. A des-colagem consertou o motor; a prioridade do estudo continua colada no operador.

**Direcao (nao implementada).** `grade.json` ganha `prioridade` por task (roxo|rosa|salmao) via
`cronograma.py --sync-drive` lendo o fill/font color da celula do xlsx; `prevalencia_enamed`
passa a ser derivada dela e o eixo 4 do `infer_nota()` liga sozinho -- **zero mudanca** em
`infer_nota()` (o contrato ja previu essa porta). Sensor de staleness do snapshot do Drive vira
WARN no painel de DIVIDA.

**Severidade:** ALTA (governa a alocacao de tempo a 11 dias do ENAMED e 60 da UERJ).

### F63 -- atualizacao (s165)
O insumo `prevalencia_enamed` agora EXISTE (89 temas, 5 aulas EMED) e ja governa o bucket `novos` via `fsrs_queue --prevalencia`. Falta: `cronograma.py`/`day_plan.py` consumirem o mesmo arquivo para o eixo 4 do `infer_nota()` (contrato §7.7 previa "basta fornecer o campo") e para a prioridade roxa da grade.

### F39 -- 40% do baralho viola o principio atomico; a nota FSRS vira ininterpretavel -- **ALTA** -- **PARCIAL: mecanismo COMPLETO (s177, item 1.6); 270 cards agora RASTREAVEIS, a reforja em si e do operador**
- **Origem:** achado do USUARIO durante o dreno da s128, formulado melhor do que o contrato tinha:
  *"e importante que a informacao solicitada no card seja clara, que os cards nao tenham diversos
  requisitos de acerto, e focassem no nucleo epistemologico do erro"*. Ele percebeu ao vivo que a
  frente que ele via era comprimida enquanto o verso (que so o agente lia) trazia exigencias extras,
  pelas quais estava sendo descontado.
- **Evidencia (medida, nao estimada):** `tools/audit_card_atomicity.py` (criado nesta sessao) acusou
  **364 cards**: 220 com **duplo-ask** (a frente cobra duas respostas) e 259 com
  **resposta-multifato** (verso em paragrafo, viola a regra 3 do formato atomico); 122 com ambos.
  Temas mais afetados: Cirurgia Infantil (40), Hemostasia I (29), Cardiopatias Congenitas (21).
- 🔴 **DUAS CORRECOES DE MEDIDA feitas na propria sessao (registrar, para nao repetir):**
  1. **Denominador errado no 1o relato.** Reportei "~40% de ~900 cards ativos". Os ~900 eram o TOTAL
     da tabela; **230 cards estao aposentados** (`needs_qualitative >= 2`) e o detector nunca os le.
     A base ativa era ~678 -> a taxa real era **~54%**, nao 40%. O problema era pior do que o relato.
  2. **Dois bugs de precisao no proprio detector.** O corpus grava sem acento (secao 4.5), o que
     colapsa a copula "e" e a conjuncao "e" na mesma letra: `"Qual e a unica vacina ...?"` casava
     como duplo-ask. Idem a construcao `"entre X e Y"`. Dois guardas + teste de regressao derrubaram
     **220 -> 203** cards de duplo-ask (~8% era falso-positivo). Ambos os bugs so apareceram ao
     **auditar a propria worklist item a item** -- nao ao escrever o detector.
- **Leitura de sistema -- por que e ALTA e nao cosmetica:** um card com 2 criterios de acerto admite
  "acertei metade", e **a nota FSRS deixa de significar alguma coisa**. Nota 2 num card duplo nao
  distingue "sabe metade" de "nao sabe nada", e o agendamento passa a mentir sobre a curva. O defeito
  nao degrada so a experiencia -- **corrompe a medida** que governa toda a repeticao espacada.
- **Dano colateral confirmado:** o agente contabilizou 6 ocorrencias de um padrao de erro do usuario
  (*"para na primeira metade da pergunta"*) usando cards duplos como evidencia. **5 das 6 eram
  defeito do card.** O ruido do baralho estava sendo importado para o prontuario cognitivo do aluno --
  a pior consequencia possivel, porque muda o que ele treina.
- **Entregue nesta sessao:** detector `tools/audit_card_atomicity.py` (read-only, WARN-first, com a
  classe de falso-positivo do **card discriminador** documentada); check 9 do `auto_check`; clausula
  "UM CRITERIO DE ACERTO por card" em `estilo-flashcard.md` + espelho sincronizado; **8 cards
  atomizados** (370, 372, 406, 407, 408, 447, 456, 457 reescritos in-place com FSRS preservado +
  12 desmembramentos via `insert_card_extra`).
- **Onda 2 (mesma sessao, 4 subagentes em paralelo -- pedido do usuario):** 91 cards dos temas mais
  contaminados (Hemostasia I, Cardiopatias, Cirurgia Infantil, Quadril Pediatrico, Polipos,
  Vulvovaginites, Arboviroses, Meningites, Imunizacoes) reescritos in-place + **109 splits**.
  **Arquitetura que tornou isso seguro: os agentes AUTORAM (db em `mode=ro`), o orquestrador
  PERSISTE.** Uma unica mao escrevendo -> zero contencao de lock no SQLite e um so ponto de gate.
  - Gate de aplicacao novo: `tools/apply_reforja.py` -- valida schema + encoding + **atomicidade do
    conteudo PROPOSTO** (o remedio auditado pelo criterio que diagnosticou a doenca), all-or-nothing,
    dry-run por default. Pegou 1 card que os agentes deixaram passar ("Coombs positivo ou negativo
    **e por que**") e 4 falso-positivos que exigiram olho humano.
  - Os agentes fizeram **triagem honesta**: o grupo B classificou 8 dos seus 23 como falso-positivo
    e os manteve quase intactos, em vez de inventar defeito para cumprir tarefa.
- **Estado:** de **364 -> 264 cards afetados**; duplo-ask **220 -> 125**. Base ativa 787 (34%).
  A queda tem tres componentes distintos, nao confundir: **91 consertos reais**, **~17 falso-positivos
  eliminados** pelos guardas do detector, e **diluicao** (109 cards novos, atomicos por construcao,
  engordam o denominador).
- **Aberto:** **264 cards**. Ordem: (1) os **125 de duplo-ask** -- sao os que corrompem a nota;
  (2) os ~139 so-multifato depois -- degradam retencao, nao a medida. Lotes por tema, priorizando
  os que caem na fila FSRS dos proximos dias. Nunca big-bang.
- 🔴 **Custo colateral a monitorar:** a onda cunhou 109 cards novos, todos entrando no pool
  (`state=0`), que foi de 383 para ~684. Com teto de 40/dia isso e divida de consolidacao, nao
  ativo -- **escalonar o intake priorizando os temas fracos**, sob pena de trocar um problema de
  qualidade por um de volume.

---

### F16 -- Tema cirurgico de alto rendimento sem SSOT clinico (.md); so o PDF-fonte existe -- **MEDIA** -- **PARCIAL (mecanismo feito, conteudo aberto)**
- 🔬 **TRIAGEM Tier 3 (s176, 10/09/2026) -- re-medido contra o codigo, nao lembrado:** a hipotese (a) FOI construida -- `tools/cobertura_conhecimento.py` e o relatorio `pdf-sem-md` que o achado pedia. O conteudo segue aberto e agora tem numero: `python tools/cobertura_conhecimento.py` -> **395 PDFs-fonte, 135 `.md`, 68 cobertos (61 exato + 7 fuzzy), 327 orfaos**. A evidencia original continua literalmente valida: **apendicite segue sem `.md`** (glob por `*apendic*` em `resumos/**/*.md` = vazio). 🔴 **Residuo de ALCANCE, nao de mecanismo:** `reachability_check --tabela` mostra o CLI alcancado so por `/extrair-pdf` -- nem o boot nem o `auto_check` o consultam, entao os 327 orfaos so aparecem para quem ja foi olhar. Mesma familia da frente de alcancabilidade (s144).
- **Evidencia:** apendicite ("um dos temas mais cobrados na prova de Cirurgia Geral", segundo a propria fonte EMED) tem em `resumos/Cirurgia/` apenas o PDF-fonte gitignored (`8. Abdome Agudo Inflamatorio - Apendicite Aguda.pdf`) e **nenhum `.md`**. Glob por `*Apendic*` retorna so o PDF; grep de termos (Alvarado/apendice/carcinoide) nos `.md` acha so mencoes tangenciais (Cirurgia Infantil, Polipose/CCR), nao resumo dedicado. Para cunhar a aula foi preciso extrair o PDF a mao na sessao.
- **Leitura de sistema:** `resumos/**/*.md` e o SSOT de conhecimento clinico E o unico corpus que o RAG indexa (`index_resumos.py`; AGENTE secao 6). Tema sem `.md` fica (a) invisivel ao RAG semantico (`obsidian-notes-rag search_notes` volta vazio p/ apendicite), (b) sem fonte consultavel nem armadilhas cumulativas, (c) re-extraido a mao a cada aula. O HANDOFF lista gaps pontuais (TCE.md, Sistemas de Informacao) mas nao ha check sistematico de cobertura.
- **Verificacao sugerida:** cruzar `resumos/**/*.pdf` (fontes EMED presentes) contra `resumos/**/*.md` (SSOTs existentes); listar temas com PDF sem `.md` par e quantos sao de alto rendimento.
- **Hipotese de melhoria:** (a) relatorio de cobertura `pdf-sem-md` (CLI ou check WARN no `auto_check`) que torna o gap visivel e priorizavel; (b) rodar o workflow `criar-resumo` p/ apendicite -- fecha o gap de conteudo E realimenta o RAG. A aula-base desta sessao ja e insumo pronto p/ o `.md`.

### F2 -- Latencia de shell no ambiente Windows -- **MEDIA** -- **DECLARADO nao-verificavel** (propriedade do ambiente, nao do repo; nenhum codigo nosso a controla -- revisar: 2027-03-31)
- **Evidencia:** comandos via Bash (`git log`, `ls resumos/**`) estouraram o timeout de 120s nesta sessao. CLIs Python (`fsrs_queue.py`, etc.) rodam normalmente e rapido.
- **Leitura de sistema:** qualquer hook ou rotina que faca *shell-out* pesado -- em especial o pre-commit `auto_check --staged` e o `day_plan.py` se dependerem de globbing amplo ou de `git` custoso -- herda essa latencia. Risco: hook lento demais ser abortado ou o operador aprender a fazer bypass.
- **Verificacao sugerida:** cronometrar `auto_check --staged` e `day_plan.py` isoladamente; identificar se o custo esta no `git`, no profile do shell, ou no glob de `resumos/**`. Testar se o gargalo e o carregamento do profile PowerShell/Bash vs. o comando em si.
- **Hipotese de melhoria:** (a) garantir que hooks usem caminhos diretos e evitem `ls`/`find` recursivo (preferir Python `pathlib` com escopo staged); (b) cache de indice quando aplicavel; (c) documentar em AGENTE.md que a superficie de tooling e Python-CLI-first, shell-glob-last.
