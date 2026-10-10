# Sessão 222 -- 09-10/10/2026 (sexta, tarde -> sábado, manhã)

**Executor:** Claude Code / Opus 5.5 + subagentes (5 Opus de cadeia v3, 2 Opus de análise t40/t100, 1 Sonnet de reforja, 1 Sonnet evidence-researcher). Custo pelo `usage` do harness: cadeias 106-133 mil tokens cada; análise t40 202+209 mil; t100 192+200 mil; reforja 95 mil; pesquisa 34 mil.
**Suíte:** 1509 passando (`python -m pytest tools/ -q`, medida no pre-commit de 10/10).

## O que ele pediu
1. *"fiz cards hoje e irei fazer questões"* -> gravar o lote e abrir a fila.
2. *"a de tópicos de pediatria apresentam o padrão prévio da análise dos elos [...] confira o de todas as tarefas atrasadas"* -> cadeia v3.
3. *"como funcionará a absorção do feedback [...] os elos estão virando cards? como tudo se conecta?"* -> explicado no chat (mapa elo -> destino).
4. *"como poderíamos fazer com que essa rotina acontecesse de maneira periódica?"* -> decidiu: **registrar + analisar no tique, a cada 30 min**.
5. (10/10) processar as listas, cards do dia, painel; reforja com subagente Sonnet; pendências; pesquisar a SBP 2026.
6. *"junte todas as pendências [...] some ao escopo a revisão de todas as referências utilizadas na nossa solução das questões [...] processos internos bem amarrados e previsíveis"* -> esta lista + recrutamento do /ai-eng.

## Feito
- **Cards:** lote `2026-10-08b` gravado (149 válidas + defeito #370, P09 = conta em 08/10); `2026-10-09a` no ar (0 notas, saiu); **`2026-10-10a` no ar (100, Version 88)**.
- **Cadeia v3 nas 5 listas atrasadas em v1** (t1 47q, t3 30q, t68 21q, t141 24q, t651 30q) **+ t100 (36q)** = 188 questões; 5 temas novos em `core/objetivos.json` (+ "Cuidados paliativos" em Saúde do Idoso, 10 relabels). 0 inválidas.
- **Tique passa a analisar** (`hub-backend.md` passo 2b; memória `feedback_tique_registra_e_analisa`); `/loop 30m /hub-backend` ligado (cron `7,37 * * * *`, desligado no fecho).
- **t40 (Diabetes na Gestação):** resolvida em 08/10 e esquecida um dia (a prova do furo) -> registrada (sb 138, 33q / 24 = 72,7%), concluída, analisada: erros 1139-1145, cards 1943-1954; 6 pendências respondidas por ele no chat; Q18 descartada, Q22 erro de instrumento.
- **t100 (Tópicos em Pediatria):** registrada (sb 139, 36q / 31 = 86,1%), concluída, analisada: erros 1146-1150 (Q8 banca-divergente sem card), cards 1957-1969, desatenções #3925 #3926; Q27 respondida (card 1969, sal).
- **Reforja (Sonnet):** #370 (marca dele) + 8 não auto-suficientes + 3 não atômicos -> 12 cards, 2 divididos; detectores limpos.
- **SBP 2026 do ferro EXISTE** (Diretriz SBP nº 32, 17/03/2026): a troca "SBP 2026 -> MS/PNSF" feita sem pesquisa na Q18/Q25 foi revertida -- erro meu, corrigido.
- `tools/test_hub_resumos.py`: o teste da S4 media "31 resumos" do plano real; concluir a t40 levou a 30 -> mede a forma, não a contagem.
- Hub: Versions 85-88.

## PENDÊNCIAS -- para a s223 (contexto limpo)

### Dele (decisões e respostas)
1. **Autópsia UERJ 2021:** 22 perguntas abertas no hub (obrigatórias Q30, Q44, Q47).
2. **5 correções clínicas de cards** (s221): #522 intussuscepção (faixa contraditória; típica 3 m-3 a); #639 LES (anti-Sm x anti-DNA -- banca x evidência?); #640 vesícula em porcelana (sem colecistectomia universal); #714 NASCIS III (AANS/CNS 2013: não usar); #844 meta de SvcO2 (EGDT superada).
3. **2 correções de conteúdo** (s217): resumo SHG §2 (rastreio combinado 1º tri) e profilaxia HBV com rituximabe (#879 "até 12 m" x resumo "6 a 12").
4. **Perguntas da análise de 07/10** (s220): t530 Q6, Q18, Q2/Q11.
5. **#1921** (t530 Q12, desatenção): aposentar se a régua de desatenção prevalecer.
6. **Divergências das 10 aulas (s219) e das cadeias (s220)**: pergunta fechada por bloco.
7. **t557 cirrose:** API achou 24, plano previa 43 -- conferir no EMED.
8. **Simulado UERJ 2022** (t1794, 60q) -- da vez, sábado 10/10.

### Minhas (engenharia e conteúdo)
9. **🆕 Revisão de TODAS as referências das Soluções MedHub** (pedido dele, escopo novo): 872 soluções em 31 listas, **631 rótulos de fonte distintos, texto livre**, 23 vazios; 22 divergentes. Casos desta sessão: "SBP 2026" dada como inexistente por um subagente (existe) e "SBP 2018 = 6 meses" afirmado pelo pesquisador contra o que as Soluções dizem (3 meses) -- não resolvido. Precisa: fonte estruturada (sigla, ano, documento, URL/PMID), verificação por amostra, regra de quem pode citar diretriz de memória.
10. **Pré-processamento no método de montar listas** (pedido de 07/10): objetivos + cadeia v3 ANTES do hub, com teste -- o furo da t100 nasceu daí. Restam em v1: t61, t65 (Hérnias, sem semana); demais S5-S7 sem cadeia.
11. **Figuras perdidas:** t40 Q5, Q6, Q18, Q21, Q22 (tabela do perfil glicêmico) sem `figuras` no banco; recapturar; declarar a perda na captura (`sem_figura` sem `figura`).
12. **Pendência de lista não tem lugar no hub:** as perguntas fechadas da análise (t40, t100) foram feitas no chat porque `analises/pendencias/itens` só renderiza dentro de documento (`form.pend`). Com o tique analisando, a pergunta precisa aparecer na própria lista.
13. **Ancoragem de card de consolidação:** `insert_card_extra.py` exige `questao_id`; cards de questão CERTA (incerteza) foram ancorados em erros vizinhos "por proximidade" (1947-1951, 1965 com tema herdado Ética Médica).
14. **Catraca de cláusulas:** CLAUSULA_ORFA 128 > base 127 (1 nova sem terminal, origem não localizada na s222).
15. t875 Q8 -> `/pesquisar-evidencia` (secundária x terciária; card #1747).
16. Aulas que faltam: #882 #887 #880 #483 #740 #1795 #889 #467 #5426.
17. Pró-MFC 2017-2020 em t1798/t1799.
18. Podar coleções velhas de `sessoes/` (08b, 09a e as herdadas da linha 3 do HANDOFF).

## Lições
- **Correção de fonte sem pesquisa é erro:** troquei "SBP 2026" por MS/PNSF só porque o subagente não achou; a diretriz existia. Regra: fonte só sai com 2ª lente (pesquisa), nunca por ausência de evidência.
- **"Tem cadeia" não é "tem cadeia v3":** a s220 contou como prontas listas em v1. O sensor certo é a `versao` da solução, não a existência dela.
