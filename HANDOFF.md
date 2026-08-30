# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-30 -- S160 (auditoria de engenharia do motor: F45-F60 + handoff p/ /ai-eng)*

## > Proximo passo imediato

1. **Inscricao UERJ 2027** -- abre **02/09 (14h)**, fecha 01/10 (23h59), site do Cepuerj, R$ 380 (pgto ate 02/10, 16h). Acao do usuario. Conferir no PDF oficial se a divisao 20/20/20/20/20 se mantem.
2. **Ritmo novo: 60q/dia + 60 flashcards/dia** -- media sustentavel declarada pelo usuario (s159). Constancia acima de pico: nada de 500q em 5 dias e 3 dias parados.
3. **Grade EMED na ordem atual ate 13/09** -- o rescope pro formato UERJ so acontece DEPOIS do ENAMED (decisao explicita do usuario).
4. 🔴 **ABERTURA DA S160 = AUTOPSIA DO SIMULADO ENAMED.** O usuario se comprometeu a fazer o simulado na integra em **30/08, mais tarde no dia**, e entregar o resultado. Rodar sob `PLAYBOOK_EXECUCAO_PROVA.md`. Era o simulado em debito ha 7d.
5. 🔬 **ENGENHARIA: auditoria s160 EXECUTADA (30/08) -> proximo ato e do /ai-eng.** Achados
   F45-F60 + matriz de portadores + swap test selados em `AUDITORIA_MEDHUB.md §3o`. O dossie de
   consumo para o /ai-eng (PRD da "cola": determinismo + consumo do harness + portabilidade;
   perguntas P1-P7) esta no workspace DELE: `~/ai-eng/HANDOFF-MEDHUB-COLA.md` (precedente do
   perito) -- autossuficiente, evidencia inline, nao re-derivar. Consertos NAO aplicados de proposito
   (salvaguarda read-only). 🔑 Quem dispara o /ai-eng e o usuario.
6. **Frente MFC (Gusso + Duncan)** -- abre em 14/09 junto do rescope. Vale 20% da prova e o lastro hoje e zero.

## Estado por frente
- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (63d). ENAMED 13/09 (14d) e **termometro**, nao piso -- o CRM e automatico. Horizonte real: UERJ -> R1/R2 MFC (mar/27-fev/29) -> RQE -> ENAMED com +10% p/ Psiquiatria.
- **Volume & Metas:** 6631 / **10.400 @ 01/11** (perf. ~78.8%). Faltam 3769 em 63d -> ritmo-alvo **~59.8q/dia**. Marco antigo (grade 9454 @ 25/10) aposentado.
- **FSRS:** divida 24 atrasados + 21 p/ hoje · pool 684 nunca introduzidos. **Teto 60/dia** (era 40). Projecao: pool zera **~29/09**; depois ~25/dia de manutencao.
- **Conteudo:** 128 resumos em `resumos/`. Faltam 2823q p/ fechar a grade EMED -- **a 60q/dia com MFC aberto ela NAO fecha inteira**; a cauda de baixo rendimento UERJ sai no rescope.
- **Posicao:** conteudo S16 (nominal S22, atraso ~6 sem) [derivado: preparacao_estado].
- **Zona (variancia.py):** COBERTURA -- desvio 10.2pp entre blocos, simulado prescrito.
- **Datas:** ENAMED 13/09 (14d) · fim do internato + fim do conteudo da grade **09/10** (40d) · fim formal da grade 25/10 · **UERJ 01/11** (63d).

## Prova da UERJ -- o que o edital diz (Ed. 15/2026, PDF em `data/`)
- 100 questoes objetivas, **20 por conteudo**: Clinica Medica, Cirurgia Geral, GO, Pediatria, **Medicina de Familia e Comunidade**.
- **Etapa unica.** Sem prova pratica, sem analise curricular. **5 horas** de prova (3 min/questao -- tempo nao e a restricao).
- Aprovacao: >=50 pontos **e nao zerar nenhum conteudo**. Desempate: CM -> Cirurgia -> Pediatria -> MFC -> idade -> sorteio.
- MFC: **20 vagas, sendo 15 de ampla concorrencia**. Duracao 2 anos. Bonus de 10% do PRMFC vale na propria UERJ (uso unico).
- Bibliografia do bloco MFC = **Gusso & Lopes (Tratado de MFC)** + **Duncan (Medicina Ambulatorial)**. E MFC clinica, **nao** saude coletiva.
- Item 1.11: a partir de 15/03/2027 da p/ concorrer a vagas ociosas de outros programas AD sem nova taxa (a UERJ tem 5 vagas de Psiquiatria).

## Ultima sessao -- s160 (AUDITORIA DE ENGENHARIA DO MOTOR)
Sessao de engenharia pura (Fable), zero estudo, zero patch (salvaguarda read-only). **(1)** Executado `docs/HANDOFF-AUDITORIA-MEDHUB.md` na integra: 4 varreduras por dominio + verificacao ao vivo (suite 317 PASSED; 342 WARNs; queries read-only nos 3 bancos). **(2)** **16 achados F45-F60** selados em `AUDITORIA_MEDHUB.md §3o` + matriz de portadores (3 vinculantes, 9 decorativos) + swap test s156-s158 (5 divergencias, todas classe 2/3 -- tese confirmada; caso-sintese F57: s156 deletou o alvo de uma memoria-CONTRATO invisivel). **(3)** Bugs vivos achados: F47 (precedencia da nota de dificuldade ignora a fonte, 12/21 temas), F46 (consolidacao de memoria falhando no proprio dia), F45 (ranking de fraquezas do boot ordena por recencia), F50 (`autopsia_simulados.py` quebrado desde 25/08). **(4)** **Handoff autossuficiente entregue ao /ai-eng** em `~/ai-eng/HANDOFF-MEDHUB-COLA.md`, com perguntas de politica P1-P7 e as propostas marcadas como hipoteses a desafiar. Relatorio executivo em Artifact.

## Pendencias/observacoes ativas
- 🔴 **Inscricao UERJ abre em 3 dias** (02/09, 14h) -- unica pendencia com data dura. Fecha 01/10; R$ 380 ate 02/10 (16h).
- 📥 **Simulado ENAMED de 30/08** -- feito pelo usuario apos o encerramento da s159; resultado entra na s160.
- 🗓️ **Rescope do cronograma pro formato UERJ** -- executar em 14/09, apos o ENAMED.
- 📚 **Frente MFC do zero** (Gusso + Duncan): MCCP, abordagem familiar, SOAP, prevencao quaternaria, rastreamento, manejo ambulatorial.
- 🎯 **Recalibrar o `PLAYBOOK_EXECUCAO_PROVA.md`**: 5h/100q inverte a instrucao de ritmo. O gap de execucao (banco 78.8% x simulado 60.8%) e fechamento precoce, nao pressa.
- 💉 **Diretrizes em versao nova na bibliografia**: Calendario Vacinal 2026, GINA 2026, Reanimacao SBP 2026. Imunizacoes e fraqueza persistente nº 8.
- 🔬 **Retorno do /ai-eng (PRD/implementacao da des-colagem)** -- dossie entregue (`~/ai-eng/HANDOFF-MEDHUB-COLA.md`); ao receber, reler HANDOFF/ESTADO antes de escrever (co-edicao) e revalidar ancoras F45-F60 via git log. Depois disso, volta o estudo.
- 🗓️ **Auditoria ampla do banco** -- reforja cards 321, 273, 293 (+F37).
- 🔍 **`card_id=120`** (Gravidez Ectopica) para `/pesquisar-evidencia`.
- 📌 **2 padroes reincidentes sem Revisao Direcionada dedicada** ("remedio certo, sequencia errada"; "exame normal exclui").

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_159.md*
