# Session 159 — Virada de Norte: UERJ/MFC + Reset de Metas
**Data:** 2026-08-30
**Ferramenta:** Claude Code (Opus 5)
**Continuidade:** Sessão 158

---

## O que foi feito

Sessão de replanejamento estratégico. Nenhuma questão resolvida, nenhum card drenado — a sessão inteira foi recalcular a rota e reescrever os SSOTs que dependiam do norte antigo.

### 1. A virada
O usuário abandonou a aposta em **Psiquiatria via ENAMED 2026**. Razão declarada: sem o bônus de 10% do RQE em MFC seriam necessários ~90-95% para uma vaga, e **há mais inscritos com o bônus de MFC do que vagas de Psiquiatria no Brasil inteiro**. Nova rota em 3 tempos: **UERJ/MFC (01/11/2026) → R1/R2 de MFC (mar/2027-fev/2029) → RQE → ENAMED com +10% para Psiquiatria (2028/29)**. O MedHub deixa de ser um projeto de 4 meses e passa a ser de 2+ anos.

Dois enquadramentos morreram na mesma sessão:
- **"ENAMED é piso de CRM"** — o usuário leu a legislação: o registro no CRM é **automático**, não depende de proficiência no ENAMED. A prova de 13/09 vira **termômetro/ensaio geral** (com Psiquiatria escolhida na inscrição), não portão.
- **USP** saiu do radar. O multi-banca da s126 virou banca única.

### 2. Auditoria do edital (fatos, não portais)
Localizado e persistido o **Edital 15/2026 do Cepuerj** em `data/Edital_UERJ_2027_Acesso_Direto.pdf`. Achados que mudam o plano:
- **100 questões, 20 por conteúdo**: CM · Cirurgia Geral · GO · Pediatria · **MFC**.
- **Etapa única** (sem prova prática nem análise curricular) e **5 horas** de prova = 3 min/questão.
- Aprovação ≥50 pontos **e não zerar nenhum conteúdo**; desempate CM → Cirurgia → Pediatria → MFC.
- **MFC: 20 vagas, 15 de ampla concorrência**, duração 2 anos. Bônus de 10% do PRMFC vale na própria UERJ.
- Item 1.11: vagas ociosas de outros programas AD a partir de 15/03/2027, sem nova taxa (a UERJ tem 5 vagas de Psiquiatria).

### 3. Correção de leitura (hipótese refutada)
O usuário levantou a hipótese de que o bloco de MFC seria "Preventiva ampla, que inscreve MFC + SUS". **Refutada pela bibliografia do Anexo II**: o bloco tem **Gusso & Lopes (Tratado de MFC)** + **Duncan (Medicina Ambulatorial)** — zero saúde coletiva. O histórico do `Guia_Estatístico_-_UERJ.pdf` confirma a direção (bloco = 58% MFC · 26% Epi · 11% SUS). Consequência prática: **as 834q de Preventiva do banco cobrem ~40% do bloco, não o bloco** — o miolo clínico da MFC tem lastro zero.

### 4. Reponderação de conteúdo
Cruzamento do Guia Estatístico (histórico 2017-2023) com o formato novo: **CM cai de ~42% para 20%** (e concentra as áreas mais rasas do usuário — Cardio 99q/68,7%, Hemato 82q/70,7%, Hepato 80q/72,5% — mas é o 1º desempate); **MFC sobe de ~6,7% para 20%**; Cirurgia (13,9%) e Pediatria (13,2%) sobem para 20%; GO estável. A cauda longa (Ortopedia 0,36% · Oftalmo 0,48% · Dermato 1,20% · Otorrino 1,32% · Psiquiatria 1,44% · Pneumo 1,56% · Hepato 1,68%) hoje vive **dentro** das 20 questões de CM e vale ~2 questões somada — é de onde sai o corte no rescope.

### 5. Reset de metas (código + docs)
- `tools/performance.py`: `MARCOS[0]` deixa de ser "Cronograma EMED 9.454 @ 25/10" e passa a ser **"UERJ/MFC 10.400 @ 01/11"** (= 6.631 + 60q/dia × 63d). `RITMOS_PROJECAO` recentrado em (45, 60, 75). `UERJ_DATA` adicionada.
- `tools/day_plan.py`: **`TETO_BASE` 40 → 60** e **`CAP_MULTIPLICADOR` 2 → 1,5** (dobrar 60 daria 120/dia e reinstalaria o pico-e-queda que o usuário rejeitou explicitamente). `_teto_do_dia` passa a devolver `int`.
- `core/provas.json`: **UERJ/MFC 01/11** adicionada.
- `core/contracts/fsrs-management-contract.md`: números do teto sincronizados (o contrato ainda dizia 30, drift desde a s126).
- `ESTADO.md`: bloco Metas reescrito; banner do sprint de ≥100q/dia sepultado; regime de 3 fases documentado.
- `HANDOFF.md`: reescrito (43 linhas, dentro do teto B1).

### 6. Ritmo redefinido
**60 questões/dia + 60 flashcards/dia**, em média sustentável. Palavras do usuário: *"as metas devem ser realistas, pois de nada adianta fazer 500 questões em 5 dias, e depois passar 2~3 dias sem estudar, por excesso de cansaço."* O `day_plan` agora reporta ritmo-alvo de ~59,8q/dia — o número que o usuário escolheu, derivado do marco, não imposto sobre ele.

### 7. Correção de bug (fora de escopo, achado no caminho)
`tools/test_handoff_teto.py` estava com a coleta quebrada desde a s156: importava `LIMITE_HANDOFF` de `tools.auto_check`, mas a constante migrou para `tools/utils/state_utils.py` no desmembramento do God Module. Import corrigido — o gate do teto do HANDOFF voltou a ser testável.

## Projeções feitas
- **Questões:** 63 dias até a prova × 60q/dia = **~10.400 acumuladas** na véspera. Faltam 2.823q para fechar a grade EMED e, **com a frente MFC aberta, ela não fecha inteira** (~1.850 entregues) — o corte é decisão consciente, não fracasso.
- **FSRS (simulação com o filtro real de cards ativos):** sob teto de 60/dia o pool de 684 nunca-introduzidos **zera ~29/09**, e a carga cai para ~25/dia de manutenção antes da reta final. 60/dia é suficiente; não precisa de pico.
- **Calendário:** a grade tem 30 semanas, mas **S29-S30 (12/10-25/10) têm zero questões novas**. O último conteúdo é a **S28 (05-11/10)**, cuja sexta é **09/10 = fim do internato + colação**. A grade de conteúdo e o internato terminam juntos, e 12/10→01/11 já é reta final por construção.

## Decisões tomadas
- **Ordem do cronograma congelada até 13/09.** Rescope pró-UERJ só depois do ENAMED, pedido explícito do usuário.
- **Frente MFC (Gusso + Duncan) abre em 14/09**, junto do rescope.
- Ritmo 60+60; teto FSRS 60/dia com CAP 1,5x.

## Artefatos criados/modificados
- `data/Edital_UERJ_2027_Acesso_Direto.pdf` (novo)
- `core/provas.json` · `core/contracts/fsrs-management-contract.md`
- `tools/performance.py` · `tools/day_plan.py` · `tools/test_handoff_teto.py`
- `ESTADO.md` · `HANDOFF.md` · `history/session_159.md` · `history/INDEX.md`
- Memória: `project_norte_uerj_mfc.md` (novo) · `reference_edital_uerj_2027.md` (novo) · `project_objetivo_provas.md` · `project_novo_norte_multi_banca.md` (supersedida) · `feedback_politica_cards_diaria.md` · `MEMORY.md`

## Próximos passos
- **Inscrição UERJ: abre 02/09 (14h), fecha 01/10.** Conferir no PDF oficial se a divisão 20/20/20/20/20 se mantém. Única pendência com data dura.
- **Simulado ENAMED na íntegra:** o usuário se comprometeu a fazê-lo em 30/08, após o encerramento desta sessão, e entregar o resultado. **A autópsia abre a s160.**
- Recalibrar o `PLAYBOOK_EXECUCAO_PROVA.md` para 5h/100q: o erro a combater é fechamento precoce, não pressa.
- A partir de 14/09: rescope do cronograma pró-UERJ + abertura da frente MFC (Gusso + Duncan).

## Encerramento
Sessão de zero questões e zero cards por desenho — foi uma sessão de replanejamento, não de execução. O volume do dia (0q) fica registrado como tal. Ritmo vigente a partir de 31/08: **60q/dia + 60 flashcards/dia**.

**Projeção até a UERJ (01/11, 63 dias):**
- **Questões:** ~3.780 no período → **~10.400 acumuladas** na véspera. Marco batido no ritmo declarado, sem pico.
- **Cronograma:** S16 → S28 é o conteúdo restante (2.823q). Com a frente MFC aberta a partir de 14/09, entrega-se ~1.850 — **a grade não fecha inteira**, e o corte sai da cauda de baixo rendimento UERJ (Ortopedia, Oftalmo, Dermato, Otorrino, Pneumo, Hepato ≈ 2 questões da prova somadas).
- **Flashcards:** pool de 684 nunca-introduzidos **zera ~29/09** sob teto de 60/dia; depois ~25/dia de manutenção. Chega-se em 12/10 com o baralho inteiro introduzido.
- **Marcos de calendário:** ENAMED 13/09 (termômetro) · fim do internato + fim do conteúdo da grade **09/10** · reta final 12/10→31/10 com dedicação integral · **prova 01/11**.
