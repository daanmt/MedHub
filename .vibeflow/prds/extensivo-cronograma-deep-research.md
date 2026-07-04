# PRD: Detecção e Suprimento de Conhecimento para o Modo Extensivo (D10 / Deep-Research)

> Gerado via /vibeflow:discover em 2026-07-02
> Alinhamento Estrutural com `revisao-calibrada-contract.md` e `tools/cronograma.py`

## Problem

O cronograma oficial de estudos do MedHub (`Cronograma.pdf`) indica, para cada tarefa, se o foco de estudo deve ser o **Livro Digital Completo (Extensivo)** ou o **Resumo Estratégico (LDI/Resumos em `resumos/`)**. No entanto, o parser oficial do cronograma (`tools/cronograma.py`) extrai apenas metadados básicos (`tarefa`, `area`, `tema`, `tipo` e `questoes`), descartando as instruções textuais de material de estudo e gerando um `grade.json` cego para essa exigência.

Por consequência, o agente operacional, ao consultar a grade na abertura do dia via `day_plan.py`, não tem como saber de forma autônoma e determinística quando a tarefa exige o nível de profundidade de uma apostila do extensivo (calibração D10 com *Deep-Researchness*). Além disso, havia uma indefinição arquitetural sobre como o agente acessaria o conhecimento do extensivo: se o usuário precisaria anexar manualmente os PDFs das apostilas a cada sessão ou se o agente operaria de forma autônoma.

## Target Audience

Usuário único — médico candidato a residência (meta ENARE 17.000 questões), interagindo com o MedHub via CLI/chat no desktop ou mobile (remote-control), exigindo alto rigor técnico e antecipação de nuances de edital sem overhead de gestão de arquivos.

## Proposed Solution

A solução combina uma **evolução no pipeline de dados (Solução 1)** com uma **regra canônica de inferência no contrato de governança (Solução 2)**, estabelecendo também o **protocolo de suprimento de conhecimento**:

1. **Enriquecimento do Parser (`tools/cronograma.py` — Solução 1):**
   - Modificar `_parse_detail()` para capturar via regex as menções ao material no texto do PDF (ex: `Extensivo`, `Livro Digital Completo`, `Resumo Estratégico`, `LDI`).
   - Adicionar o campo `material_indicado` (`"extensivo"` | `"resumo"`) ao schema do `core/cronograma/grade.json`.
   - Modificar `tools/day_plan.py` para exibir o material na abertura da sessão: `[Material: Extensivo -> Calibração D10 / Deep-Research]`.

2. **Inferência Operacional de Harness (`revisao-calibrada-contract.md` — Solução 2):**
   - Solidificar a regra no contrato: tarefas com `tipo: "Teoria + Exercícios"` ou nota inferida $\ge 7$ são **automaticamente promovidas ao modo Extensivo/D10**, acionando o dever de varredura profunda e encadeamento causal do Degrau 0, independentemente de marcação manual.
   - Tarefas com `tipo: "Revisão"` com nota $< 7$ operam no modo Resumo Estratégico, consultando primariamente a base markdown em `resumos/`.

3. **Protocolo de Suprimento de Conhecimento (A Resposta sobre "Buscar a Apostila"):**
   - **Modo Padrão (Autônomo / Zero-Upload):** O usuário **NÃO precisará buscar nem anexar o PDF da apostila do extensivo** para o agente. O modelo fundamental possui em seus pesos e capacidade de raciocínio de profundidade (*Deep-Researchness*) o domínio enciclopédico necessário para emular a densidade do extensivo (mecanismos fisiopatológicos, diretrizes do ATLS 10, SBC, Febrasgo, Nelson, Towsend, etc.). O agente sintetizará a aula-base D10 diretamente de sua base de conhecimento canônica, alinhada com as armadilhas cadastradas em `ipub.db`.
   - **Modo Exceção (Fallback para Controvérsias):** O upload ou fornecimento de trechos de apostilas pelo usuário só será solicitado quando houver **divergência específica de edital regional** (ex: conduta divergente entre USP-SP, UNIFESP e ENARE) ou quando o usuário desejar que o agente audite um gráfico/tabela proprietária específica. Nesses casos pontuais, o usuário joga o trecho/arquivo no chat ou em `tmp/`.

## Success Criteria

- Execução do `python tools/cronograma.py --rebuild` gera um `grade.json` atualizado contendo o atributo `material_indicado` em 100% das 352 tasks do cronograma sem quebrar testes ou a interface de leitura.
- O script `tools/day_plan.py` expõe explicitamente o material indicado e a calibração sugerida ao abrir o dia.
- O agente, ao identificar uma tarefa de Extensivo/Teoria no cronograma, entrega uma aula-base em padrão D10 (Degrau 0, sem saltos lógicos, sem tabelas, com terminologia acadêmica) **sem solicitar que o usuário anexe arquivos PDF de apostilas**.
- Zero overhead para o usuário na preparação do ambiente de estudo de teoria.

## Scope v0

- Atualização de `tools/cronograma.py` para extração de `material_indicado` e regravação da grade em `core/cronograma/grade.json`.
- Atualização em `tools/day_plan.py` para refletir o material de estudo na saída do terminal e no objeto JSON retornado.
- Atualização em `core/contracts/revisao-calibrada-contract.md` formalizando a regra de promoção automática `Teoria -> Extensivo (D10)` e o protocolo **Zero-Upload** (conhecimento nativo do agente como fonte primária para extensivo).
- Teste de regressão garantindo que `grade.json` continua com `n_tasks: 352` e `total_questoes: 10218`.

## Anti-scope

- Ingestão, indexação ou armazenamento de PDFs completos do Estratégia MED ou outras apostilas de extensivo no repositório MedHub (violaria governança de peso do repositório, direitos autorais e regra de Zero PDF de longa duração).
- Alteração no schema do banco de dados SQLite (`ipub.db`).
- Modificações nas páginas do Streamlit (`app/`).
- Criação de scrapers para baixar apostilas da web.

## Technical Context

- `tools/cronograma.py` utiliza `PyPDF2` (não `pypdf` moderna) para parsear `Cronograma.pdf`. A extração do texto do PDF gera strings onde as instruções do livro digital aparecem no formato `Livro Digital: <tema> (<Tipo>)` ou menções a `Extensivo`.
- O arquivo `core/cronograma/grade.json` é versionado no git e serve como SSOT de leitura rápida para não parsear o PDF de 12 MB a cada invocação.
- O agente atua em calibração D10 seguindo a spec canônica `.agents/skills/source-command-estilo-resumo/SKILL.md` (regras estritas: bullets hierárquicos, proibido tabelas, proibido emojis em headers, foco 80/20 assertividade/didática clínica).

## Open Questions

- Nenhuma. O modelo operacional de suprimento de conhecimento (Zero-Upload / Autônomo com fallback para controvérsia de edital) resolve o trade-off de usabilidade sem comprometer a profundidade técnica exigida no D10.
