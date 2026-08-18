# Session 147 -- Rescoping ENAMED (fonte oficial) + aula-base CA Mama D10 + Autópsia reestruturada
**Data:** 2026-08-18
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 146 (Simulado 5 + engenharia)

---

## O que foi feito

### Frente A -- Rescoping do cronograma pré-ENAMED

1. **Tensão de 3 fontes resolvida.** A sessão 146 tinha recalibrado o cronograma S15-S30 contra um "blueprint ENAMED medido" (Simulado 2 classificado + 120 erros dos Simulados 2-4), com uma correção de premissa registrada no HANDOFF sugerindo abandonar isso pelo guia ENARE antigo (tese "ENARE==ENAMED"). Ao retomar essa pendência, o usuário apontou corretamente que a amostra "medida" é enviesada: 120 dos 215 pontos são *erros do próprio usuário*, então qualquer área onde ele é mais fraco aparece artificialmente inflada -- não é medição da prova, é medição da fraqueza dele.
2. **Pesquisa via WebSearch** confirmou que o ENAMED substitui a prova objetiva própria do ENARE (Acesso Direto) -- o guia ENARE antigo (2019-2024) descreve uma prova já extinta. E revelou uma terceira fonte, melhor que as duas: o **Guia Estatístico ENAMED** da própria Estratégia MED (e-book público), construído sobre todas as provas do Revalida INEP (2011-2025) + a prova real do ENAMED/ENARE 2025/2026 -- banca certa, sem viés de performance do usuário.
3. PDF baixado (WebFetch + `extract_pdfs.py`) e estruturado em `core/simulados/guia_enamed.json`: 20 especialidades com pct/n, subáreas (top-5 com %) e assuntos (top-N ranqueados) por especialidade.
4. **Links de exercícios extraídos do `Cronograma.pdf`** por posição (pdfplumber: `page.extract_words()` + reconstrução da URL fragmentada por coluna) -- `core/cronograma/links_exercicios.json`. Validado semana a semana: soma das questões dos links bate exatamente com o total oficial do `grade.json` em 16/16 semanas (S15-S30), incluindo 2 casos de tarefa sem link próprio (continuação de teoria já linkada antes).
5. **`core/simulados/rescoping_final_com_links.json`**: 92 blocos únicos do cronograma pendente, peso = `%especialidade x %relevância-do-tema-dentro-dela` (blocos combo/revisão-por-questões usam a MÉDIA dos componentes decompostos, não o máximo -- corrigido um bug que inflava blocos com 1 tema forte e 3 fracos), ordenados por peso, com Nova Semana calculada por empacotamento a 500q/semana (ritmo real do usuário: 100q/dia x 5d).
6. Artifact **"Fila ENAMED"** publicado (`.../93162128-...`) com a lista completa, troca de blocos que sobem/descem, e notas de cautela (ex.: HAS sai da janela pré-ENAMED não por ser fraca, mas porque Cardiologia é 3,46% da prova -- mesmo o pico de uma especialidade pequena perde pra temas médios de especialidade grande).
7. Achado registrado, não resolvido: tarefas "Revisão por Questões" no `grade.json`/PDF vêm com `tema=""`, mas a planilha real do Drive (que o usuário reorganizou por cores Roxo>Rosa>Salmão) tem o tema preenchido -- confirmado comparando a S15/S16 real que o usuário relatou contra o parse do PDF.

### Frente B -- Aula-base Câncer de Mama (D10)

8. Aula-base extensiva pedida explicitamente em D10 (já errou o tema em simulado). Ancorada nos **6 erros já catalogados** no `ipub.db` (4 de Câncer de Mama: Ki-67 invertido, intervalo de rastreio alto-risco x habitual, mamografia x radioterapia na gestação, atipia=alto risco formal; 2 de Doenças Benignas adjacente: Phyllodes, fibroadenoma complexo) -- fio condutor = padrão de inverter/generalizar fronteiras finas de categoria.
9. 3 PDFs-fonte do EMED lidos (`11. Câncer de Mama.pdf`, `7. Rastreamento do Câncer de Mama.pdf`, `9. Doenças benignas da Mama.pdf`) para garantir fidelidade D10 (dever de Deep-Researchness).
10. **Resumo `resumos/GO/[GIN] CA de Mama.md` corrigido contra o PDF-fonte**: achada e corrigida uma divergência factual real (Ki-67 corte de Luminal A é 20%, o resumo tinha 14%) + lacunas preenchidas (tabela de rastreio por critério de alto risco com idade amarrada ao critério, não genérica; BI-RADS 4A/4B/4C; vocabulário de imagem BI-RADS 3 vs 4/5; tipos de biópsia; Oncotype DX; discriminador de dor carcinoma inflamatório x mastite; exceção PRIME-2; exceção artrite reumatoide na contraindicação de quadrantectomia; rastreio em população trans). `auto_check.py --changed` passou limpo.

### Frente C -- Autópsia dos Simulados reestruturada (feedback do usuário)

11. Usuário leu o artifact publicado na s146 e deu 4 pontos de feedback, todos aplicados:
    - **Fusão de blocos**: "o discriminador que faltou" + "por que é armadilha" + "o que faltou" viram uma seção única "Anatomia do erro" (`anatomiaErro()` em `tools/autopsia_template.py`), reordenada para depois da cadeia de habilidades e antes de "Racional correto".
    - **Destaque de dados-chave na vinheta**: função `marcaChave()` no JS, regex sobre números+unidade clínica e negações/exceções, aplicada só no bloco da vinheta via `<mark class="dk">`.
    - **3 legendas decorativas removidas**: nota de percentual em `respostas()`, legenda de cores em `ladder()`, nota de "card ainda não introduzido" em `cardsBlock()`.
    - **Acentuação**: dicionário `ACC` em `tools/autopsia_simulados.py` expandido de ~200 para ~950 entradas, via varredura de vocabulário dos 157 erros contra sufixos suspeitos (-ção/-ável/-ível/-ário/-ência/esdrúxulas -ico/-ica irregulares). Mesma regra dura documentada no arquivo: nenhuma entrada que colida com verbo conjugado comum (indica, aplica, seria, varia, deveria etc. ficaram de fora deliberadamente).
    - **Heurística do elo quebrado recalibrada**: viés posicional de 0.12 para 0.38 em `analisa_cadeia()`, para reduzir o falso-positivo de cobertura lexical em blocos curtos (1 palavra em comum já dava cobertura alta) que fazia o algoritmo "confundir a quebra com o último passo executado" -- palavras do próprio usuário.
12. `auto_check.py --changed` passou limpo (suíte central de testes + linter de resumos). Artifact republicado na mesma URL (`.../c414a4f3-...`, `force:true` após confirmar via WebFetch que não havia edição concorrente -- só a versão da s146 sem as mudanças de hoje).

## Volume do dia
Nenhum -- sessão 100% engenharia/conteúdo. Usuário está executando 103 questões (S15: SUS-Revisão + Asma-Revisão à frio, Câncer de Mama-Teoria com a aula) + 100 flashcards fora desta sessão; resultado e comentários de erro vêm numa sessão nova.

## Artefatos criados/modificados
- `core/simulados/guia_enamed.json` (novo) -- Guia Estatístico ENAMED estruturado
- `core/cronograma/links_exercicios.json` (novo) -- link do caderno de exercícios por (semana,tarefa)
- `core/simulados/rescoping_final_com_links.json` (novo) -- 92 blocos por peso + Nova Semana + links
- `resumos/GO/[GIN] CA de Mama.md` -- corrigido/enriquecido contra PDF-fonte
- `tools/autopsia_simulados.py` -- ACC expandido (~200->~950), viés posicional de `analisa_cadeia` (0.12->0.38)
- `tools/autopsia_template.py` -- `anatomiaErro()` (fusão), `marcaChave()`/`KEYRX` (highlight), 3 legendas removidas, `card()` reordenado
- `artifacts/autopsia-simulados.html` -- regenerado e republicado (link preservado)
- Artifact "Fila ENAMED" (`.../93162128-...`) -- publicado nesta sessão
- `HANDOFF.md` -- rotação completa; `history/INDEX.md` -- nova entrada

## Decisões tomadas
- Guia Estatístico ENAMED (Estratégia MED, Revalida INEP + ENAMED real) é a fonte única de prevalência (macro e micro) para o rescoping -- substitui tanto o guia ENARE antigo quanto o "medido" enviesado.
- Blocos combo/revisão-por-questões usam a média dos pesos dos componentes decompostos, nunca o máximo.
- Ritmo assumido para o rescoping: 500q/semana (100q/dia x 5d), à parte dos simulados.
- `tools/fila_enamed.py` ("A Fila Errada") fica superado por esta sessão, não deletado -- candidato a aposentadoria formal futura.

## Próximos passos
Ver `HANDOFF.md`. Em resumo: usuário traz numa sessão nova os comentários dos erros das 3 listas (~103q) + dados de performance + os 100 flashcards; processar erros (paralelizar em subagents se o volume justificar), registrar volume via `registrar_sessao_bulk.py` antes de processar erros, drenar a fila FSRS. Investigar depois por que o parser do PDF do cronograma perde o tema de tarefas "Revisão por Questões" que a planilha do Drive tem preenchido.
