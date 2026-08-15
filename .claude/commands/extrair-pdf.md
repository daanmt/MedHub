---
description: "Extrai texto de PDFs para arquivos .txt temporários. Usar no início do workflow criar-resumo. Limpa apenas os .txt temporários — os PDFs-fonte do EMED são RETIDOS (política de retenção, s086)."
type: skill
layer: commands
status: canonical
---

# Skill: Extrair PDF

Wrapper para `tools/extract_pdfs.py`. O conhecimento permanece em Markdown, mas os **PDFs-fonte do EMED são retidos** (gitignored) — ver §Política de retenção abaixo. A limpeza automática cobre só os `.txt` temporários; deleção de PDF é ato explícito do usuário, nunca default do agente.

---

## Fluxo Completo (4 passos)

```bash
# 1. Extrair — paths dos .txt são impressos no stdout
python tools/extract_pdfs.py "Tema/Asma.pdf" "Tema/Asma_Complementar.pdf"

# 2. Ler — abrir cada arquivo .txt cujo path foi impresso
#    (os paths ficam em %TEMP% por padrão)

# 3. Redigir — escrever o resumo .md baseado no conteúdo extraído

# 4. Limpar — apagar PDFs originais e arquivos temporários
python tools/extract_pdfs.py --delete-pdfs "Tema/Pneumologia/" --delete-temps "C:/Temp/ipub_Asma_abc.txt" "C:/Temp/ipub_Asma_Complementar_xyz.txt"
```

---

## Argumentos

| Argumento | Uso | Exemplo |
|---|---|---|
| `"arquivo.pdf"` | Extrair um ou mais PDFs | `"Fichas/Cirurgia.pdf"` |
| `--delete-pdfs <pasta>` | Apagar todos os .pdf/.PDF de uma pasta | `--delete-pdfs "resumos/GO/"` |
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
python tools/extract_pdfs.py "Memorex/Memorex_Cirurgia/Trauma.pdf"
# → imprime: C:/Users/.../AppData/Local/Temp/ipub_Trauma_a1b2c3.txt

# Passo 4: após escrever o resumo, limpar
python tools/extract_pdfs.py --delete-pdfs "Memorex/Memorex_Cirurgia/" --delete-temps "C:/Users/.../ipub_Trauma_a1b2c3.txt"
```

### Verificar antes de deletar
```bash
python tools/extract_pdfs.py --dry-run --delete-pdfs "resumos/Pediatria/"
```

### Múltiplos PDFs de uma vez
```bash
python tools/extract_pdfs.py "arq1.pdf" "arq2.pdf" "arq3.pdf"
# → imprime 3 paths, um por linha
```

---

## Política de retenção de PDFs (s086 — substitui a antiga "Zero PDF")

🔴 **NÃO deletar os PDFs do EMED.** A política "Zero PDF" foi **revertida na s086**:
os PDFs-fonte são **retidos** (gitignored, fora do versionamento) porque alimentam
`tools/cobertura_conhecimento.py` (F16a) e o gate de lastro de
`tools/insert_questao.py::_tem_lastro` (F31) e são IP-fonte **não-reconstruível**.
O vault opera em Markdown; os PDFs ficam como matéria-prima local.

> Correção 2026-08-14 (auditoria de sistemas): esta seção instruía deletar os
> PDFs — norma morta cujo cumprimento causava perda irreversível (`AGENTE.md §6`
> já admitia o drift). Único caso: PDF temporário de terceiros sem valor de
> fonte pode ser removido a critério do usuário, nunca por default do agente.
>
> Correção 2026-08-14 (consolidacao-part-2): o tier bruto de RAG sobre PDF
> (`pdf_raw`, `tools/index_pdf_raw.py`) foi removido — o gold (`resumos/**/*.md`)
> satura antes do tier PDF contribuir. A retenção dos PDFs acima não depende
> mais de RAG.
