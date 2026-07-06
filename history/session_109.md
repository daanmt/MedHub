# Session 109 — Apendicite (aula-base D10/D7 + 60q em 2 blocos) + Papel Coordenador-Observador (ledger F16-F26)

**Data:** 2026-07-05
**Ferramenta:** Claude Code (Fable 5)
**Continuidade:** Sessão 108 (drenagem FSRS + abertura do ledger de engenharia F1-F9)

---

## O que foi feito

**Trilha A — Estudo de apendicite (prova de R+ em gastroenterologia, alvo paralelo ao cronograma ENAMED):**
- Cunhada a **aula-base de apendicite** em dois registros: primeiro **D10** (extensivo, escopo EMED inteiro + camada R+ gastro), depois re-renderizada em **D7** a pedido do operador ("baixando a agressividade"). Substrato: extração do PDF-fonte EMED (`resumos/Cirurgia/8. Abdome Agudo Inflamatorio - Apendicite Aguda.pdf`), mapeado como checklist de cobertura.
- **60 questões de apendicite em 2 blocos:** bloco 1 = 18q/13a (72,2%); bloco 2 = 42q/31a (73,8%). Combinado **60q/44a (~73%)**. Volume em `sessoes_bulk` (s109 = bloco 1; s110 = bloco 2, ver F22).
- **10 flashcards de erro cunhados** (727-731 no bloco 1; 732-736 no bloco 2), todos ancorados no elo metacognitivo, via `insert_questao.py`.

**Trilha B — Papel Coordenador-Observador (contrato do operador, s109):** o operador formalizou o agente-coordenador como **observador-auditor contínuo** — enquanto conduz o estudo, alimenta o ledger `AUDITORIA_MEDHUB.md` (F16+) com fricções de uso, para o Fable (ciclo 2) + ai-eng implementarem. Memória `project_papel_auditor_ledger`. **11 achados novos: F16-F26** (seções 3c/3e/3f do ledger).

## Padrões de erro — DELE (conteúdo, trilha A)

Diagnóstico sólido: nos 60q, quase nenhum erro foi de RECONHECER a doença. Os erros se agruparam em 3 assinaturas + factuais:

- 🔴🔴 **REINCIDÊNCIA — "reflexo de confirmação" (bug nº1 vestido de conduta):** o link "jovem típico < 48h = operar, não pedir imagem" foi carded no **bloco 1** (card 730). No **bloco 2**, mesma sessão, horas depois, reincidiu **3x** — Q4 (pediu US), Q8 (pediu TC), Q11 (pediu US). "Não tolere errar 2x pelo mesmo motivo" = alarme. Mesma família do bug nº1 (parar antes de completar a conduta) + isca do ruído urinário (piúria não afasta, card 729). **Prioridade nº1.**
- 🔴 **Cluster NOVO — discriminação de DDx (ancoragem em "FID = apendicite"):** Q1 bloco 2 (1 semana + febre 40 + leucopenia/linfocitose = adenite, ignorou os dados CONTRA), Q2 (cronicidade + emagrecimento = Crohn/ileíte terminal), Q3 (enunciado negativo: Crohn é o MENOS provável no agudo). Fecha apendicite pela dor de FID sem rodar o checklist do "contra" (duração, febre, hemograma, cronicidade). Carded 732/733.
- 🔴 **Massa/líquido = intervir (mesmo eixo do trauma):** Q5 (plastrão bloqueado estável -> marcou "operar já"; é conservador) e Q7 (dreno -> marcou "líquido livre"; é autólise de base/abscesso localizado). Espelha o ponto fraco do trauma ("líquido livre -> superestima intervenção"). Carded 734/735.
- **Factuais:** ATB profilaxia dose única/<= 24h (Q6, chamou apêndice flegmonoso de "normal"); artéria apendicular = mesentérica SUPERIOR não inferior (bloco 1 Q5); adenite = mimetizador pediátrico não gastroenterite (bloco 1 Q1). Carded 736/731/727.
- **Não contam:** bloco 2 Q9 (acertou); Q10 (anulada: gabarito oficial A x EMED C, marcou o do EMED). Ver F26.

## Padrões de erro — MEUS (processo, trilha B — "aprimorar a si mesmo")

O operador pediu explicitamente para eu registrar os MEUS erros de processo, não só os dele. Honestamente:

- 🔴 **Sobre-compressão da aula D7 (F21):** ao comprimir D10 -> D7, ELIMINEI um ponto de decisão de alto rendimento ("isquemia de base -> ileotiflectomia") em vez de só encurtar profundidade. A Q2 do bloco 1 caiu exatamente ali. Violação da regra de cobertura (a nota calibra profundidade, nunca corta tema). Erro meu, não do operador.
- **Falha de quoting no insert em lote (F24):** encadear `insert_questao.py` via shell quebrou (`bash -c`, aspas desbalanceadas, exit 2, ZERO inseridos). Recuperei com driver Python (args por lista). Aconteceu nos 2 blocos -> falta modo batch.
- **Workaround da idempotência do bulk (F22):** tive de gravar o bloco 2 como "sessão 110" porque `registrar_sessao_bulk` bloqueia 2o registro na mesma (sessão, área). Volume preservado, mas o rótulo 110 não tem `session_110`.
- **Colisão de numeração no ledger:** tentei F20 para o achado do D7, mas a rodada de engenharia paralela (Fable/ai-eng) já o havia tomado (venv); renumerei para F21 e segui a convenção de corrida da seção 3d.

## Observações sobre a preparação (contexto para o Fable / próximo coordenador)

- **O gargalo confirmado NÃO é conteúdo, é execução/conduta.** Em 60q, o diagnóstico esteve certo quase sempre; os erros foram de CONDUTA (operar x esperar x imagem) e de DISCRIMINAÇÃO de DDx. Consistente com o "gargalo nº1 = execução de prova" do ESTADO.
- **A reincidência intra-sessão é o dado mais valioso da sessão:** o mesmo elo carded no bloco 1 caiu 3x no bloco 2, horas depois. Prova de que o card fresco precisa ser drilado ANTES do próximo bloco do mesmo tema (F23).
- **Calibração da aula importa e é medível:** o D7 comprimido custou uma questão (Q2) que o D10 teria coberto. A cobertura de pontos de decisão não pode ser sacrificada pela compressão — só a profundidade (F21).
- **Prova paralela (R+ gastro) fora do cronograma ENAMED:** boot/day_plan assumem ENAMED; esta sessão foi de alvo paralelo, atendido ad-hoc pelo eixo tema (F19).

## Otimização da gestão da curva de esquecimento

- **10 cards novos de apendicite (727-736) entram como state 0** (novos, sem due). Pela política atual só entram pela fila de novos (`--new-limit`), sem prioridade por serem do tema quente-recém-errado.
- **Oportunidade (F23):** um **PREPARAR direcionado por tema-alvo** — antes do próximo bloco de apendicite, drilar os cards de erro frescos do tema (em especial 729 piúria + 730 caso-clássico, os do reflexo de confirmação). Estende o PREPARAR (hoje só do dormente) para o tema-quente.
- **Recomendação operacional imediata:** na próxima abertura de apendicite, mini-drill de 729+730 ANTES do bloco. Matar o reflexo de confirmação sobe a taxa sozinho.

## Consolidação de informação (pendência de alto valor)

- 🔴 **Apendicite ainda NÃO tem resumo `.md` (F16)** — só o PDF-fonte + a aula efêmera no chat + 10 cards; o RAG é cego ao tema. A aula-base D10 desta sessão + as armadilhas dos 10 cards são insumo PRONTO para cunhar `resumos/Cirurgia/Apendicite Aguda.md` no padrão gold (cumulativo). **Alta alavanca de consolidação** — fecha cobertura E realimenta o RAG.
- A aula-base é efêmera (F18): re-forjada do zero a cada vez, sem registro da nota de dificuldade. O `.md` seria a forma durável.

## Achados de engenharia (ledger — detalhe em AUDITORIA_MEDHUB.md, seções 3c/3e/3f)

- **F16** — tema de alto rendimento sem SSOT `.md` (RAG cego a apendicite).
- **F17** — PDFs EMED retidos "p/ o RAG" nunca indexados (index só lê `.md`).
- **F18** — aula-base efêmera, sem persistência nem registro de calibração.
- **F19** — ambiente ENAMED-cêntrico; prova paralela (R+) sem suporte.
- **F21** — compressão por dificuldade eliminou ponto de decisão (D7 cortou isquemia-de-base; Q2 caiu ali).
- **F22** — `registrar_sessao_bulk` idempotente bloqueia 2o bloco da mesma área/sessão.
- **F23** — cards de erro frescos não são surfaced antes do próximo bloco do mesmo tema -> reincidência.
- **F24** — `insert_questao.py` sem modo batch; N erros = driver ad-hoc (falha de quoting).
- **F25** — sem detector automático de reincidência ("errar 2x pelo mesmo motivo").
- **F26** — questões anuladas/banca-dependentes contam como erro limpo; sem tag.
- (F20 = venv dessincronizado, da rodada de engenharia paralela; seção 3d.)

## Decisões tomadas

- **Papel Coordenador-Observador é contrato ativo** (memória `project_papel_auditor_ledger`): duas trilhas — conteúdo -> session log + HANDOFF padrões vivos; engenharia -> ledger F16+. Eu observo/organizo; o Fable (ciclo 2) + ai-eng implementam.
- **Aula-base por nota (D7) validada como falível:** a nota calibra profundidade, NUNCA corta cobertura de ponto de decisão de alto rendimento (F21).
- **Git deixado para o Fable** ("o Fable cuidará do resto"): há sessão de engenharia paralela com trabalho não commitado; encerramento documental feito, commit/push fora do escopo deste coordenador.

## Próximos passos

1. **[Fable / ciclo 2]** consumir o ledger **F16-F26** (11 achados novos além de F1-F15). Alto retorno: **F23** (surfacing anti-reincidência — resolve o padrão vivo nº1) + **F16** (resumo de apendicite fecha cobertura + RAG) + **F22/F24** (bulk + batch, DX barato).
2. **[próximo coordenador]** antes do próximo bloco de apendicite: mini-drill de 729+730. Consolidar `resumos/Cirurgia/Apendicite Aguda.md` a partir da aula D10 + armadilhas dos cards.
3. **[FSRS]** os 10 cards novos (727-736) devem reaparecer; validar que o reflexo de confirmação consolidou.
4. **[git]** Fable commita os artefatos de estado da s109 (HANDOFF, session_109, ledger F16-F26, ESTADO) ao tocar o ciclo 2.
