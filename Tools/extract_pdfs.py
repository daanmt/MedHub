"""
extract_pdfs.py — Extrator de texto de PDFs para o projeto MedHub

Uso:
    # Extrair um PDF (arquivo temp criado automaticamente, path impresso no stdout):
    python extract_pdfs.py "caminho/para/arquivo.pdf"

    # Múltiplos PDFs de uma vez:
    python extract_pdfs.py "arq1.pdf" "arq2.pdf" "arq3.pdf"

    # Após usar os arquivos tmp, deletar com --cleanup:
    python extract_pdfs.py --cleanup "caminho/para/arquivo.pdf"

Fluxo completo esperado (executado pelo agente):
    1. Extrair:   python extract_pdfs.py "Tema/Asma.pdf" "Tema/Asma a.pdf"
    2. Ler:       o agente lê os paths impressos no stdout
    3. Redigir:   agente escreve o resumo .md
    4. Limpar:    python extract_pdfs.py --delete-pdfs "Tema/" --delete-temps caminho1.txt caminho2.txt

Import direto:
    from Tools.extract_pdfs import extract_pdf, delete_pdfs_in_folder
    tmp_path = extract_pdf("arq.pdf")   # retorna path do arquivo temp
    delete_pdfs_in_folder("Tema/Pneumologia/")
"""

import pdfplumber
import PyPDF2
import tempfile
import sys
import os
import glob


def extract_pdf(pdf_path: str, out_path: str = None) -> str | None:
    """
    Extrai texto de um PDF.
    - Se out_path for None, cria arquivo temporário no diretório temp do sistema.
    - Retorna o path do arquivo gerado, ou None em caso de falha.
    """
    pdf_path = os.path.normpath(pdf_path)

    if not os.path.exists(pdf_path):
        print(f"[ERRO] Arquivo não encontrado: {pdf_path}", file=sys.stderr)
        return None

    lines = []
    print(f"[INFO] Processando: {pdf_path}", file=sys.stderr)

    # Tentativa primária: pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text(x_tolerance=2, y_tolerance=3)
                if text and text.strip():
                    lines.append(f"\n# --- PAGINA {i+1} ---\n")
                    lines.append(text)
        if not lines:
            raise ValueError("Nenhum texto extraído pelo pdfplumber.")
    except Exception as e:
        print(f"[AVISO] pdfplumber falhou ({e}). Tentando PyPDF2...", file=sys.stderr)
        lines = []
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        lines.append(f"\n# --- PAGINA {i+1} (PyPDF2) ---\n")
                        lines.append(text)
        except Exception as e2:
            print(f"[ERRO] Falha total ao processar {pdf_path}: {e2}", file=sys.stderr)
            return None

    # Determinar destino
    if out_path:
        out_path = os.path.normpath(out_path)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        delete_after = False
    else:
        base = os.path.splitext(os.path.basename(pdf_path))[0].replace(" ", "_")
        tmp_fd, out_path = tempfile.mkstemp(suffix=".txt", prefix=f"ipub_{base}_")
        os.close(tmp_fd)
        delete_after = False  # o agente controla quando deletar

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[OK] {out_path}")  # impresso no stdout para o agente capturar
    return out_path


def delete_temps(*temp_paths: str):
    """Deleta arquivos temporários de extração."""
    for path in temp_paths:
        path = os.path.normpath(path)
        if os.path.exists(path):
            os.remove(path)
            print(f"[DEL] temp: {path}", file=sys.stderr)
        else:
            print(f"[AVISO] Não encontrado: {path}", file=sys.stderr)


def delete_pdfs_in_folder(folder: str):
    """
    Deleta todos os arquivos .pdf/.PDF na pasta indicada (não recursivo).
    Usar após consolidar o resumo .md.
    """
    folder = os.path.normpath(folder)
    pdfs = glob.glob(os.path.join(folder, "*.pdf")) + glob.glob(os.path.join(folder, "*.PDF"))
    if not pdfs:
        print(f"[INFO] Nenhum PDF encontrado em: {folder}", file=sys.stderr)
        return
    for pdf in pdfs:
        os.remove(pdf)
        print(f"[DEL] pdf: {pdf}", file=sys.stderr)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    # Modo limpeza de PDFs de uma pasta
    if args[0] == "--delete-pdfs":
        if len(args) < 2:
            print("[ERRO] Informe a pasta: --delete-pdfs <pasta>", file=sys.stderr)
            sys.exit(1)
        folder = args[1]
        temp_files = args[3:] if len(args) > 3 and args[2] == "--delete-temps" else []
        delete_pdfs_in_folder(folder)
        if temp_files:
            delete_temps(*temp_files)
        sys.exit(0)

    # Modo limpeza de arquivos temporários
    if args[0] == "--delete-temps":
        delete_temps(*args[1:])
        sys.exit(0)

    # Caso padrão: dois argumentos em que o segundo é .txt → PDF + saída explícita
    if len(args) == 2 and args[1].lower().endswith(".txt"):
        extract_pdf(args[0], args[1])
    else:
        # Um ou mais PDFs → saída em pasta temporária do sistema
        for pdf_arg in args:
            extract_pdf(pdf_arg)
