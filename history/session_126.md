# Session 126 — VIRADA MULTI-BANCA (fim do foco ENAMED) + drenagem FSRS 61/61 + replanejamento de metas

**Data:** 2026-07-24 (bloco DII) e 2026-07-25 (virada + drenagem)
**Ferramenta:** Claude Code (Opus 5 [1M])
**Continuidade:** Sessão 125

---

## O que foi feito

### Reconcile de abertura -- drift de ponteiro
- O boot reportou "6 dias parados"; **era falso**. A sessão de 24/07 (DII) tinha registrado em `sessoes_bulk` (s126, Gastro, **26q/19a = 73,1%**, 7 erros #589-595) mas **nunca foi selada** em `history/` -- o HANDOFF seguia apontando s125. Este arquivo fecha o buraco.
- 36 revisões FSRS de 24/07 ficaram carimbadas em **25/07** (recorrência de `feedback_data_hora_registros`). Não corrigido de propósito: reescrever `review_time` reagenda o FSRS por 1 dia e não paga o custo.

### 🔄 VIRADA ESTRATÉGICA -- fim do foco total ENAMED (decisão do usuário)
- Motivo declarado: probabilidade de aprovação baixa em Psiquiatria (concorrência), e a meta apertada cansava com retorno incerto. Novo norte: **ENAMED (13/09) + UERJ + USP (nov-dez, sem edital)**, com **constância > pico**.
- **Achado que sustenta a virada:** a grade do EMED tem 30 semanas e a **S30 fecha ~25/10**, ~6 semanas DEPOIS do ENAMED. Perseguir 10.000q até 13/09 comprimia 13 semanas de grade em 50 dias -> ritmo-alvo fictício de ~96q/dia. **A meta estava errada, não o ritmo do usuário.**
- **Bug real corrigido:** `_cronograma_hoje` calculava `ritmo_cronograma = grade_inteira / dias_ate_ENAMED` -- duas escalas de tempo somadas. Era a origem do "116,5q/dia". Agora divide pelo fim da grade (`dias_grade`), derivado do último `fim` em `grade.json`. Mesmo bug estava em `recomendar_dia` (usava `dias_enamed`).

### Replanejamento (código)
- `performance.MARCOS`: marcos de ENAMED **por volume** removidos -> `Cronograma EMED (grade completa) 9454 @ 25/10` · `2o ciclo UERJ/USP 12500 @ 31/12` · `Stretch 15000`. `ENAMED_DATA` fica como referência de calendário.
- `METAS_MENSAIS` refeito jul-dez (5.500 -> 12.500); ramp de 17.000 **aposentado**. `META_CUSTO_Q` 0,26 -> **0,35** (4.410/12.500). `RITMOS_PROJECAO` (80,90,100) -> **(40,55,70)**.
- **Simulado volta a contar no volume** (reverte s099): `get_totais(conn, escopo=)` com `total|cronograma|simulado`, `get_questoes_do_mes(escopo=)`, `db.get_ritmo_real(incluir_simulado=True)`, `day_plan.q_hoje` sem filtro. `cronograma --gap` usa `escopo='cronograma'` (o gap mede a grade). Separação passa a ser de **apresentação**, não de contagem.
- `TETO_BASE` 30 -> **40 cards/dia** (usuário pediu "flashcards mais frequentes" ao trocar o regime).
- Rótulo "ENAMED" no render agora vem de `MARCOS[0]`, não hardcoded.
- `test_orquestrador.test_get_ritmo_real_janela` atualizado ao novo contrato (+ asserção do escopo grade-only). Suítes: `auto_check --changed` PASS · `test_orquestrador` PASS · `test_revisao_calibrada` PASS · `test_day_plan_telemetria` PASS · `test_aderencia` 11 passed.

### Drenagem FSRS -- 61/61 (DRENAR, lotes de 6 e 8)
- **37×4 · 14×3 · 6×2 · 4×1 -- 84% em 3-4.** Dívida de 44 atrasados **zerada**.
- **Imunizações 8/8 com nota 4** num cluster marcado com frieza 28.7. O agente **previu que desabaria e errou a previsão**; usuário recusou o PREPARAR ("no seco") e estava certo. -> `dificuldade` de Imunizações recalibrada **D10 -> 6** (`fonte='agente_inferida'`).
- **Erros catalogados revertidos:** #416 (K na rabdomiólise, tinha invertido) · #755/#756 (Febre Amarela com reforço aos 4a, 2× sem reincidir) · #498 (cisto de cordão, não hérnia encarcerada).
- **Uso ATIVO do discriminador negativo** (inverso do padrão-mestre) em #761 ("sem perda de peso" -> não escala) e #829 ("peso P30" -> não fecha RCF pela AU). É a habilidade-alvo funcionando.
- Interrupção de infra no meio (classificador de Bash/PowerShell indisponível ~1 turno); lote 2 avaliado offline e gravado no turno seguinte. Nenhum dado perdido.
- Agente errou a nota de #759 (deu 3, era 4) e **não regravou** -- Invariante C respeitada, registrado aqui.
- Agente **pulou o #358** no split de lotes; recuperado ao final.

### Re-drill dos 10 cards < 3 (a pedido do usuário)
- Consolidação **sem regravar** no FSRS (nota 10 min após ver a resposta mede eco, não retenção; e 2 linhas no revlog corrompem o cálculo). Os 4 de nota 1 voltam sozinhos amanhã.
- Resultado: 6/10 completos, incluindo os dois que estavam quebrados (#475 T4F e #422 renovascular).

### Revisão Direcionada (Camada 2) -- diagnóstico contra o resumo
- **`Lesão Renal Aguda.md`: NÃO editado.** Já cobria IECA/BRA em rim angiotensina-dependente E dipstick sem hemácias = pigmentúria. Gap de **recall puro** -> re-ensino no chat, sem inflar o resumo.
- **`Síndromes Hipertensivas da Gestação.md`:** +2 armadilhas (IECA/BRA proibidos + BRA não é saída de emergência; restrição de sal não se aplica à PE). O limiar 140/90 já existia.
- **`Icterícia e Sepse Neonatal.md`:** +1 armadilha -- os **3 galhos** da icterícia prolongada; **hipotireoidismo congênito não era mencionado no arquivo** e a linha 125 mandava "BI elevada -> considerar leite materno", galho incompleto que gerou o erro.
- **`Cardiopatias Congênitas.md`:** +seção "matriz fluxo x idade" + 5 armadilhas. **Hipoplasia de VE não existia no arquivo** e as Armadilhas eram boilerplate genérico.

### Aula-base D10 -- Pneumologia Intensiva II
- Escopo confirmado no `Cronograma.pdf` (a pedido do usuário): **Parte II = S13 Tarefa 9, págs 58-83, seção 4.0 Ventilação Mecânica, 22 questões**. Parte I = S10, págs 11-57 (IRpA + via aérea). **SDRA/Hemoptise = S16, fora do escopo.**
- Aula ancorada no PDF-fonte (`5. Pneumologia Intensiva.pdf`), não de memória.

---

## Padrões de erro vivos

- 🔴 **Bug nº 1c (fato no contexto errado) -- DOIS eventos com IECA no mesmo dia:** #422 (quis trocar IECA por BRA sem ver que é o mesmo eixo) e #358 (indicou IECA em gestante, onde é teratógeno). Assinatura comum: "IECA reduz proteinúria" é verdade na DRC e foi transportado para fora da condição.
- 🔴 **Conceito solto que gruda no caso errado:** "hipoplasia de VE" foi inventada na Tetralogia (#475) e não reconhecida onde era a resposta (#95).
- 🔴 **Discriminador que exclui, ignorado:** #213 (AESP + asmático + pressão positiva = pneumotórax, não intubação seletiva) e #490 (sinais neurológicos = hipotireoidismo, não leite materno).
- 🟡 **Pergunta composta** segue aparecendo (#282, #201, #821, #830), mas em intensidade menor.

---

## Estado ao fechar

- Volume **5232** / 9454 (grade) · perf. 79,1% · ritmo-alvo **45,9q/dia** (~54q em 6 dias/sem), 92d p/ fechar a grade.
- FSRS: **0 atrasados** + 4 p/ hoje (relearning) · pool 372 nunca introduzidos · teto 40/dia.
- Cronograma: conteúdo S13, calendário S17 (atraso 4 sem).

## Próximo passo

Bloco de **22 questões de Pneumologia Intensiva II (VM)** pós-aula. Depois, as 3 tasks restantes da S13: Transtornos de Humor + Psiquiatria Social/Reforma (Teoria) · Hepatologia + Ictericia não-obstrutiva + Hepatites Virais (Revisão) · Arboviroses + Meningites + Sepse (Revisão por Questões).
