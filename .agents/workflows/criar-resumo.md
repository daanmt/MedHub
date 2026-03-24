---
description: Criar resumo clínico a partir de PDF de apostila
---

# Workflow: Criar Resumo de Tema

## Pré-requisitos
- PDF(s) da apostila na pasta do tema (ex: `Temas/Clínica Médica/Pneumologia/`)
- Saber a Área e o Tema (ex: Clínica Médica > Pneumologia > Asma)

## Passos

### 0. Preflight (Obrigatório)
Seguir o **Boot Sequence** definido em `AGENTE.md`.

// turbo-all

### 1. Extrair texto do(s) PDF(s)
```
python Tools/extract_pdfs.py "caminho/completo/Tema.pdf" "caminho/completo/Tema2.pdf"
```
- Saída: arquivos `.txt` temporários na pasta temp do sistema (`%TEMP%`)
- O script imprime no stdout o path de cada arquivo gerado — usar esses paths no passo 2
- Paths com espaços: usar aspas duplas

### 2. Ler o texto extraído
Abrir cada arquivo `.txt` gerado (usando os paths do passo 1) e ler o conteúdo completo.

### 3. Consultar o estilo de formatação
Ler `Tools/estilo-resumo.md` — OBRIGATÓRIO. Regras críticas:
- Bullets hierárquicos; sem tabelas; sem fluxogramas ASCII
- Emojis apenas: ⭐ (fundamental) | ⚠️ (padrão de prova) | 🔴 (armadilha final)
- Seção final obrigatória: "Armadilhas de Prova"

### 4. (Opcional) Consultar resumos existentes como referência
- `Temas/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md`
- `Temas/Clínica Médica/Neurologia/TCE.md`

### 5. Redigir o resumo
- Fonte primária: apenas os PDFs extraídos.
- **HARD REQUIREMENT: Benchmark MedHub 80/20 (20% Didática Clínica / 80% Assertividade)**:
  - **20% Didática Clínica:** O resumo DEVE incluir o raciocínio fisiopatológico e clínico com precisão acadêmica (ex: "A insuficiência de VD não apresenta crepitações pulmonares devido à deficiência de bomba prévia ao leito capilar pulmonar").
  - **80% Assertividade:** Foco absoluto em critérios diagnósticos (scores), algoritmos de conduta e definições do ATLS/Diretrizes.
- **Formatação de Ouro:**
  - NUNCA crie parágrafos lineares extensos. Use **bullets técnicos, curtos e lógicos** de forma encadeada.
  - **VETO AO COLOQUIALISMO:** É proibido o uso de jargões, metáforas informais ("encher balde") ou tom motivacional. O tom deve ser estritamente formal e cirúrgico.
  - Emojis apenas: ⭐ (Fundamental) | ⚠️ (Padrão de Prova) | 🔴 (Armadilha de Prova).

### 6. Salvar
Salvar em `Temas/{Área}/{Subespecialidade}/{Nome do Tema}.md`

### 7. Limpeza automática (pós-resumo)
```
# Deletar PDFs da pasta do tema e os arquivos temporários:
python Tools/extract_pdfs.py --delete-pdfs "pasta/do/tema/" --delete-temps "path/tmp1.txt" "path/tmp2.txt"
```
- `--delete-pdfs <pasta>`: remove todos os `.pdf`/`.PDF` da pasta indicada
- `--delete-temps <paths...>`: remove os arquivos `.txt` temporários gerados no passo 1

### 8. Fechamento (Obrigatório)
Seguir o **Protocolo de Fechamento** em `AGENTE.md` e executar o workflow `registrar-sessao.md`.