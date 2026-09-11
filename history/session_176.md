# Session 176 -- Janela de reforma remota: 6 itens do Tier 0, e o dia em que os gates pararam de mentir

**Data:** 2026-09-10 (noite) - **Ferramenta:** Claude Code (Opus 5, 1M) - **Continuidade:** `session_175.md`
Sessao de **ENGENHARIA**, orquestrada pelo `/ai-eng` N=78 (regime D71). O operador deu `/clear` na
sessao de estudo e a entregou para a reforma, com foco declarado em **eficiencia no uso de subagents**.
**Permit do operador, verbatim: "Fila inteira, sem parar"** -- dado CONTRA a recomendacao do `/ai-eng`
e a minha (as duas propunham so os 2 hotfixes antes do ENAMED). Decisao dele; a ressalva fica no registro.

---

## O que foi entregue (6 itens, 8 commits, 0 spawns de subagente)

| item | achado | commit |
|---|---|---|
| **0.0** | **F93** (novo) regua de subagents vira portador versionado + **F90** gate de revogacao cego | `dbaa23b` |
| **Tier 3** | os 8 achados sem status ganham marcador MEDIDO (5 fechados + 3 parciais) | `3ae2124` |
| **0.1** | **F80b** relogio unico `db.agora()` passa a valer do lado do LEITOR | `3f55f47` |
| **0.1b** | **F91** o leitor de evidencia para de devolver `[]` quando a busca nao aconteceu | `b9058c9` |
| **0.2** | **F81/B1** alinhamento interno da FRENTE vira 3 predicados nomeados | `84e75ad` |
| **0.3** | **B2** a fila de reforja vira ESTADO, com fechamento VERIFICADO | `315ae01` |
| **0.4** | **B4/F77+F77b** o derivador para de jogar fora o que ja calcula | `1948457` |

Suite **452 -> 503** (+51 em 5 suites novas). `auto_check --changed` PASSED em todas as rodadas.
Dois hotfix docs `verified` e tres audits `PASS` em `.vibeflow/`.

---

## O fio que costura o dia

Todos os seis itens sao a mesma doenca em superficies diferentes: **o mecanismo existe, esta certo,
e nao alcanca**. O `/ai-eng` batizou a serie de *Reachability-Debt* e ela ganhou hoje **duas formas
novas**, medidas na propria sessao:

- **Sem perimetro** (nova, 2 instancias no mesmo dia). O F80 estabeleceu o relogio unico para
  WRITERS e a suite que o protege varre `INSERT` -- ninguem olhava o lado da LEITURA, e os SELECTs
  novos escolhiam sozinhos (F80b). E os dois caminhos de REFORJA nao chamavam `validar_card`, entao
  os predicados novos do 0.2 nunca alcancariam justamente quem reescreve a frente do card.
- **Sem consulta / sem ponteiro / sem escopo** (Tier 3): `cobertura_conhecimento.py` mede **327
  orfaos** e nada no boot o consulta; a aula-base persiste como Artifact e nada liga tema -> URL;
  a regua de subagents vivia so na memoria do harness.

🔴 **O caso-sintese e o F90.** O gate `CONTRATO_REVOGADO` existe, mira `.claude/commands/revisar.md`
**nominalmente**, e imprimiu `PASSED` com tres prescricoes revogadas em vigor -- porque o registro
dele tinha 3 termos enumerados a mao sob um comentario que prometia *"ninguem enumera a mao"*. O
defeito nao era o gate; era a ausencia do passo "cadastrar" no rito de revogacao. Virou regra
versionada: `AGENTE.md §10 item 10` -- **revogar tem TRES passos, e os tres vao no mesmo commit.**

---

## O que cada item ensinou alem do fix

**0.0 -- falsificar > rodar.** Nao aceitei o `PASSED` do gate consertado: montei fixture sintetica e
medi que com o termo em linha ativa ele acusa **4/4**, com lapide **0**, e o arquivo real **0**.
Antes do commit ele era verde por nao olhar.

**Tier 3 -- a triagem inverteu um achado.** O F17 supunha wiring atrasado em relacao a intencao.
Era o contrario: **a intencao morreu** (RAG gold-only), e a premissa morta ainda vivia no
`AGENTE.md §6`, contradizendo a decisao duas linhas acima. Lapidada.

**0.1 -- o teste mede a propriedade, nao o sintoma.** A suite verifica **obediencia ao relogio
unico**, nao um offset de 3h: um teste ancorado em "3 horas" passaria por acidente num CI em UTC,
que e exatamente onde o defeito seria invisivel.

**0.1b -- o teste-antes corrigiu o ESCOPO do fix.** Escrevendo o caso do consumidor descobri um
**segundo silenciador** em `get_topic_context` (`except Exception: pass`). Consertar so o `rag.py`
teria produzido um fix que parece certo, passa em revisao e nao muda nada no caminho real.

**0.2 -- medir antes de escrever derrubou o DoD da ordem.** Os fixtures que a ordem selada mandava
usar (#1568, #1574) pontuam **0.056 e 0.091** na metrica -- o chao da distribuicao. Force-los ali
exigiria afrouxar o corte ate varrer metade do baralho. **Parei e virou bifurcacao**, e o `/ai-eng`
decidiu tres predicados nomeados. Os fixtures NEGATIVOS viraram o melhor produto do item: **#792 x
#1568** tem o mesmo desenho contrafactual e so um e defeituoso (o outro traz o *"se presente"*).

**0.3 -- "alguem editou" nunca foi evidencia.** Medi a segunda instancia do F82: **#1568** tem
evento `reforja` de 09/09 (`v1 -> v2`) e **continua disparando** o predicado criado horas antes.
Dai o invariante: fechar uma marca **re-roda o predicado** e recusa se ele ainda acusar.

**0.4 -- uma desconfianca que nunca foi medida custou 3 sessoes.** O dado por tarefa era calculado
e descartado por medo de que o PDF nao amarrasse link a tarefa. Medido: **27 das 30 semanas
reconciliam**. O bom viaja com marca de confianca; as 3 degradam em voz alta.

---

## Fronteiras DECLARADAS (o que NAO ficou coberto, escrito para ninguem ler verde como limpeza)

- **Eixo C do F81** (vinheta que trabalha CONTRA a pergunta, semantico) -- nao alcancavel por regex.
  **#792 e sentinela**: se um predicado passar a pega-lo, a leitura e *"atualize a declaracao"*,
  jamais "regressao".
- **Faixa 0.55-0.79** do predicado de contexto redundante: 14 cards com redundancia real que o corte
  0.8 nao pega. Aperta quando o passivo de 12 zerar.
- **"Passivo ~37" de reforja** NAO migrado: existe o numero, nao existe a lista. Fabricar 37 linhas
  a partir de um numero sem nomes seria inventar estado.
- **Contador de gate-miss** so passa a informar com **>= 300** revisoes na janela (hoje 76).
- **Sitios gemeos do F80b em `tools/`** (`audit_fsrs.py`, `variancia.py`) deferidos por teto de
  hotfix; a varredura declara o proprio escopo (`app/`) na docstring.

---

## Colaterais corrigidos no caminho

- `AGENTE.md §6` afirmava que os PDFs alimentam o RAG, contra a decisao **gold-only** da linha 152
  do mesmo paragrafo. Lapidado (F17).
- O extrator da tabela `§7.4` nao tolerava **shebang**: todo CLI executavel aparecia como "sem
  docstring". Os `—` da tabela caem de **14 para 6** -- e os 6 restantes sao ausencias reais.
- `HANDOFF_LONGO` barrou um commit de 61 linhas (teto 60). Registro porque e o **oposto** do F90:
  gate que pegou.

---

## Custo, medido

**0 spawns de subagente na sessao inteira** -- a regua versionada no 0.0 (ate ~8 itens o principal
faz sozinho) aplicada a si mesma. Contraste com a s175: 3 spawns, ~673k tokens e ~66 min para 15
erros de questao, com 2 afirmacoes rejeitadas por re-medicao.
