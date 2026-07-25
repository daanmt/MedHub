# Session 127 — Pneumo Intensiva II (VM) + 2 loops vibeflow (ledger de habilidades · variância e zona)

**Data:** 2026-07-25
**Ferramenta:** Claude Code (Opus 5 [1M])
**Continuidade:** Sessão 126

---

## O que foi feito

### Aula-base D10 + bloco de Pneumologia Intensiva II
- Escopo confirmado no `Cronograma.pdf` **a pedido do usuário** (não no `grade.json`): Parte II = **S13 Tarefa 9, págs 58-83, seção 4.0 Ventilação Mecânica, 22 questões**. Parte I = S10 (págs 11-57). **SDRA/Hemoptise = S16, fora do escopo.** Esse recorte só existe no PDF -- o `grade.json` tem o tema, não a subdivisão.
- Aula em 13 degraus ancorada no PDF-fonte, com refresh da Parte I. Dificuldade registrada **pós-análise**: 9 (`fonte=aula`).
- **Bloco: 22q / 16a = 72,7%.**

### Análise dos 6 erros -- com o orçamento de correção novo
🔴 **Achado que é falha do AGENTE, não do usuário:** 3 dos 6 erros bateram em conteúdo que **a aula não cobriu**.
- **Leitura de curvas** (Q2, Q5): ensinei o sinal de autoPEEP e parei; faltou o sistema de identificação (não toca = pressão · cruza = fluxo · toca = volume), a regra **FR aferida > FR programada = assistida**, e **fluxo quadrado = volume / livre = pressão**.
- **Parâmetros iniciais do obstrutivo** (Q1): dei os ajustes gerais e a *correção* da autoPEEP, mas não que asma/DPOC **começa** com FR e VC baixos.
- `Pneumologia Intensiva.md` expandido com as duas seções (auto_check PASS).

**2 erros foram conteúdo ensinado 2h antes** (Q4 correção de autoPEEP -- marcou aumentar PEEP; Q6 VNI no pós-operatório). Não é lacuna de conteúdo, é retenção sob condição de prova.

**Q6 = padrão-mestre limpo:** o item dizia "TEP **no 1º pós-operatório de artroplastia de quadril**". Leu "TEP", concluiu certo que TEP não é indicação, e **parou antes da segunda metade da frase** -- que era o que tornava o item verdadeiro.

**Q3 fora de escopo** (SDRA = S16). PaO2/FiO2 = 60/0,4 = 150 -> moderada, não grave.

📊 **Reenquadramento honesto:** as 6 erradas tinham acerto nacional de 41/59/36/53/30/44% (média ~44%). O bloco era objetivamente difícil.

### 🔁 Loop vibeflow 1 -- Ledger de Habilidades (commit 3710cc7, audit PASS)
Fonte: 2 transcrições de Pedro Martins. `questoes_erros.habilidades_sequenciais` estava em 593/593 registros mas como **prosa** -- o sistema narrava a cadeia de uma questão e não sabia responder *"qual habilidade eu falho através de temas diferentes"*.
- Tabelas `habilidades` + `questao_habilidades`; CLI `--backfill`/`--report`/`--reincidentes`/`--add`.
- Veredito com enum fechado; **`incerteza` e `desatencao` como estados próprios** (acertar na dúvida não é acertar; desatenção pede ritual, erro pede conteúdo).
- **`--add` registra aprendizado de questão ACERTADA** sem virar erro nem volume -- sinal que o pipeline descartava inteiro.
- **Descobertos ao rodar contra dados reais:** sentinela `N/A` era a "habilidade" nº 1 (125 ocorrências em 31 temas); existia um **segundo formato** (lista numerada) em ~22% dos registros.
- **Validação externa:** o ledger reconstruiu sozinho o padrão *enunciado negativo* ("marcar a falsa" / "rotular cada alternativa V/F", 4 temas cada) que estava catalogado à mão.
- Limitação documentada: 1.324 habilidades para 1.336 ocorrências -- prosa sob medida por questão nunca reincide. Valor vem do forward-flow.

### 🔁 Loop vibeflow 2 -- Variância e Zona (commit 1d49acb, audit PASS)
- **Troca de métrica:** de média (77,6%, já boa) para **variância entre blocos (11,9 pp, alta)**.
- **Zona de 2 eixos** (desempenho × cobertura). O modelo de 1 eixo do vídeo misclassifica quem tem nota de platô sem ter fechado a grade. Estado real: **COBERTURA** (77,6% sobre 43% da grade) -> prescrição é **avançar**, não refinar.
- Variância corre **por fora** da zona: desvio >= 10 pp prescreve simulado em qualquer quadrante.
- 🔴 **Defeito de dado encontrado:** `taxonomia_cronograma.questoes_realizadas` está **inflado ~3,7x** (19.597 contra 5.232 reais). A 1ª versão da cobertura usava esse campo e dava "89,5% coberto / DIRECIONAMENTO" -- falso. Fonte trocada para a grade versionada; teste estrutural impede a regressão. **O campo segue inflado: pendência aberta.**

### Ajustes de contrato (o "agente gerenciador com mais recursos")
- **`AGENTE.md §1.2` -- aula-base vira HÍBRIDA POR DIFICULDADE** (decisão do usuário via AskUser): tema-zero ou D8+ mantém aula completa antes; D5 ou menor vai direto às questões e a aula entra depois, mirando o buraco. Muda o **gatilho**, não a **profundidade**.
- **`/analisar-questao §11` -- taxonomia + ORÇAMENTO de correção:** direta (1 aprendizado, sem reler resolução) · fluxograma (achar o NÓ) · raciocínio (análise cheia). Tempo de correção é finito.
- **Cadência de simulado 1/semana** (decisão do usuário), com detecção de débito.

### ESTADO.md sincronizado
Estava macro-desatualizado desde a s126: ainda trazia meta-prova 10.000, ramp 17.000 e ~87q/dia. Marcos, ramp, indicador e o bloco de Volume & Metas refeitos.

---

## Padrões de erro vivos

- 🔴 **Padrão-mestre (discriminador ignorado)** -- Q6 desta sessão é caso limpo: parou na primeira metade do item.
- 🔴 **Bug nº 1 (número contra a régua)** -- Q3: tinha PaO2 e FiO2, não fez 60/0,4 nem situou em Berlim.
- 🟡 **Retenção de conteúdo fresco sob condição de prova** -- 2 erros em material ensinado 2h antes. Sinal novo, vale observar se repete.

## Estado ao fechar

- Volume **5.254** / 9.454 (grade) · perf. 79,1% · ritmo-alvo **45,7q/dia** (92d).
- **Zona COBERTURA** · média de blocos 77,6% · **desvio 11,9 pp** · grade 43,0%.
- FSRS: **0 atrasados** + 4 p/ hoje · pool 372 · teto 40/dia.
- ⚠️ **Simulado em débito** desde 28/06.

## Próximo passo

**Simulado ENAMED de 100 questões amanhã (26/07)** -- decidido pelo usuário; fecha o débito e é a primeira medição de variância em condição de prova. Registrar em `area='Simulado'` (conta no volume, bloco dedicado). **Ainda hoje:** retorno para mais questões + ~30 flashcards (drenar pool). Depois, as 3 tasks restantes da S13.
