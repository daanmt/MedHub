---
description: "Extrai texto de PDFs para arquivos .txt temporários. Usar no início do workflow criar-resumo. Também faz limpeza de PDFs e temps após uso (política Zero PDF)."
type: skill
layer: commands
status: canonical
---

# Skill: Extrair PDF

Wrapper para `Tools/extract_pdfs.py`. Implementa a **política Zero PDF** do MedHub: PDFs são temporários, o conhecimento permanece em Markdown.

---

## Fluxo Completo (4 passos)

```bash
# 1. Extrair — paths dos .txt são impressos no stdout
python Tools/extract_pdfs.py "Tema/Asma.pdf" "Tema/Asma_Complementar.pdf"

# 2. Ler — abrir cada arquivo .txt cujo path foi impresso
#    (os paths ficam em %TEMP% por padrão)

# 3. Redigir — escrever o resumo .md baseado no conteúdo extraído

# 4. Limpar — apagar PDFs originais e arquivos temporários
python Tools/extract_pdfs.py --delete-pdfs "Tema/Pneumologia/" --delete-temps "C:/Temp/ipub_Asma_abc.txt" "C:/Temp/ipub_Asma_Complementar_xyz.txt"
```

---

## Argumentos

| Argumento | Uso | Exemplo |
|---|---|---|
| `"arquivo.pdf"` | Extrair um ou mais PDFs | `"Fichas/Cirurgia.pdf"` |
| `--delete-pdfs <pasta>` | Apagar todos os .pdf/.PDF de uma pasta | `--delete-pdfs "Temas/GO/"` |
| `--delete-temps <paths...>` | Apagar arquivos .txt temporários específicos | `--delete-temps "C:/Temp/ipub_x.txt"` |
| `--dry-run` | Simular deleções sem executar | Para verificar antes de deletar |
| `--out <path>` | Salvar extração em path específico (apenas 1 PDF) | `--out "saida.txt"` |

---

## Comportamento

- **Extrator primário:** `pdfplumber` (melhor qualidade, preserva formatação)
- **Fallback:** `PyPDF2` (ativado automaticamente se pdfplumber falhar)
- **Output:** path do arquivo .txt impresso no **stdout** — capturar para uso nos passos seguintes
- **Logs/erros:** impressos no stderr (não interferem com a captura do path)
- **Formato do arquivo gerado:** `ipub_{nome_do_pdf}_{hash}.txt` em `%TEMP%`

---

## Casos de uso típicos

### Criar resumo de um tema novo
```bash
# Passo 1: extrair
python Tools/extract_pdfs.py "Memorex/Memorex_Cirurgia/Trauma.pdf"
# → imprime: C:/Users/.../AppData/Local/Temp/ipub_Trauma_a1b2c3.txt

# Passo 4: após escrever o resumo, limpar
python Tools/extract_pdfs.py --delete-pdfs "Memorex/Memorex_Cirurgia/" --delete-temps "C:/Users/.../ipub_Trauma_a1b2c3.txt"
```

### Verificar antes de deletar
```bash
python Tools/extract_pdfs.py --dry-run --delete-pdfs "Temas/Pediatria/"
```

### Múltiplos PDFs de uma vez
```bash
python Tools/extract_pdfs.py "arq1.pdf" "arq2.pdf" "arq3.pdf"
# → imprime 3 paths, um por linha
```

---

## Política Zero PDF

Após consolidar o resumo .md, os PDFs **devem ser deletados**. O MedHub opera exclusivamente em Markdown. PDFs são fontes temporárias de extração, não documentos permanentes do vault.
