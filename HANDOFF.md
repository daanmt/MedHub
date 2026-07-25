# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-25 -- **s127: Pneumo Intensiva II (VM, 72,7%) + 2 loops vibeflow (Ledger de Habilidades · Variancia e Zona, 2 audits PASS) + aula-base vira HIBRIDA por dificuldade. ESTADO.md sincronizado com a virada da s126.***

## > Proximo passo imediato

1. 🎯 **SIMULADO ENAMED de 100 questoes -- 26/07** (decidido pelo usuario). Fecha o debito de simulado (aberto desde 28/06) e e a **primeira medicao de variancia em condicao de prova**. Registrar com `--area Simulado` (conta no volume, bloco dedicado).
2. **Ainda em 25/07:** o usuario volta para mais questoes + **~30 flashcards** (drenar o pool de 372).
3. Depois, as 3 tasks restantes da S13: **Transtornos de Humor + Psiq Social/Reforma** (Teoria -- pela regra nova, provavelmente tema-zero, leva aula-base completa) · **Hepatologia + Ictericia nao-obstrutiva + Hepatites Virais** (Revisao -- vai direto a questao) · **Arboviroses + Meningites + Sepse** (Revisao por Questoes).

## 🔬 Diagnostico vigente (rodar `python tools/variancia.py --zona`)

**Zona COBERTURA** -- desempenho alto (media de blocos 77,6%) sobre **43,0% da grade percorrida**. Prescricao: **AVANCAR a grade**, nao trocar cobertura por refinamento.
🔴 **Variancia entre blocos = 11,9 pp (alta).** Corre POR FORA da zona: prescreve **simulado** em qualquer quadrante -- bloco tematico nao corrige sensibilidade a perfil de prova. **E o gargalo isolado nº1 hoje, acima da media.**

## Capacidades novas (s127) -- usar

- **`tools/habilidades.py`** -- ledger de habilidades. `--reincidentes` responde "qual habilidade eu falho em temas DIFERENTES"; `>= 3 temas` = padrao de raciocinio, nao lacuna de conteudo. **`--add` registra aprendizado de questao ACERTADA** (nao vira erro nem volume) e o estado **`incerteza`** ("acertei na duvida"). Assinatura em `/analisar-questao §10`.
- **`tools/variancia.py`** -- variancia + zona de 2 eixos + debito de simulado. Assinatura em `/performance`.
- **`/analisar-questao §11` -- ORCAMENTO de correcao por tipo:** direta = 1 aprendizado, **nao reler a resolucao**; fluxograma = achar o NO que quebrou; raciocinio = analise cheia. Tempo de correcao e finito.
- 🔴 **`AGENTE.md §1.2` -- aula-base agora e HIBRIDA POR DIFICULDADE.** Tema-zero ou D8+ -> aula completa ANTES. D5 ou menor -> **questoes primeiro**, aula depois mirando o buraco. Muda o gatilho, nao a profundidade (Clausula 10 intacta).

## Padroes de erro vivos -- atencao do scrum master

- 🔴 **Padrao-mestre (discriminador ignorado)** -- caso limpo na s127 (Q6): item dizia "TEP **no 1o pos-operatorio de artroplastia**"; leu "TEP", concluiu certo que TEP nao e indicacao de VNI, e **parou antes da segunda metade da frase**. Ritual: ler o item ATE O FIM antes de julgar.
- 🔴 **Bug nº1 (numero contra a regua)** -- Q3: tinha PaO2 e FiO2 e nao fez 60/0,4 = 150 nem situou em Berlim (moderada, nao grave).
- 🟡 **SINAL NOVO -- retencao de conteudo fresco sob prova:** 2 dos 6 erros foram material ensinado **2h antes** (correcao de autoPEEP; VNI no pos-op). Nao e lacuna de conteudo. **Observar se repete** nos proximos blocos pos-aula.
- 🔴 **Familia bug nº1c (fato no contexto errado)** -- 2 eventos com IECA na s126 (trocar por BRA; IECA em gestante).

## Estado por frente
- **Volume & Metas:** 5254 / 9454 (perf. ~79.1%). Hoje: 22. Ritmo-alvo ~45.7q/dia (92d p/ Cronograma EMED (grade completa)). [derivado: day_plan --handoff-block]
- **FSRS:** divida 0 atrasados + 4 p/ hoje -- pool 372 nunca introduzidos (entram <=40/dia). [derivado]
- **Conteudo:** 71 resumos. `Pneumologia Intensiva.md` expandido na s127 (leitura de curvas + ventilacao do obstrutivo) -- as duas secoes **faltavam na aula-base do agente**, nao no aluno.
- **Erros & Cards:** 6 erros de VM analisados; **7 habilidades registradas no ledger** (veredito=errou). Nenhum card novo cunhado ainda -- **pendente**.
- **Posicao cronograma:** db=S13 (nominal S17, atraso 4 sem). Drive stale (F36 aberto).

## Pendencias ativas
Cunhar os cards dos 6 erros de VM. Reforja de `TCE.md` + `Sistemas de Informacao em Saude.md`. Ledger: vereditos majoritariamente `indefinido` ate a curadoria avancar. Ledger `AUDITORIA_MEDHUB.md`: **F37 novo** (`taxonomia_cronograma.questoes_realizadas` inflado ~3,7x -- 19.597 contra 5.232 reais; nao afeta metas, que leem `sessoes_bulk`, mas contamina qualquer feature que confie nele), **F36** (Drive `--sync-drive` pulado 3 sessoes), **F35** (seletor de suite do auto_check), F8. Regra 90-50 / ponderacao por incidencia (video 3): proxy existe (repeticao de tema na grade), spec nao escrito.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_127.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
