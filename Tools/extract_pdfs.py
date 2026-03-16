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


def sanitize_path(path: str) -> str:
    """Remove aspas e espaços extras que podem surgir de erros de escape no shell."""
    return path.replace('"', '').replace("'", "").strip()


def delete_temps(*temp_paths: str, dry_run: bool = False):
    """Deleta arquivos temporários de extração."""
    for path in temp_paths:
        path = os.path.normpath(sanitize_path(path))
        if os.path.exists(path):
            if dry_run:
                print(f"[DRY-RUN] Deletaria temp: {path}", file=sys.stderr)
            else:
                os.remove(path)
                print(f"[DEL] temp: {path}", file=sys.stderr)
        else:
            print(f"[AVISO] Não encontrado: {path}", file=sys.stderr)


def delete_pdfs_in_folder(folder: str, dry_run: bool = False):
    """
    Deleta todos os arquivos .pdf/.PDF na pasta indicada (não recursivo).
    Usar após consolidar o resumo .md.
    """
    folder = os.path.normpath(sanitize_path(folder))
    if not os.path.isdir(folder):
        print(f"[ERRO] Diretório não encontrado: {folder}", file=sys.stderr)
        return

    # glob no Windows costuma ser case-insensitive, mas garantimos ambos.
    # Usamos set() para evitar duplicatas se o SO for case-insensitive.
    pdfs = set(glob.glob(os.path.join(folder, "*.pdf"))) | set(glob.glob(os.path.join(folder, "*.PDF")))
    
    if not pdfs:
        print(f"[INFO] Nenhum PDF encontrado em: {folder}", file=sys.stderr)
        return

    for pdf in pdfs:
        if dry_run:
            print(f"[DRY-RUN] Deletaria pdf: {pdf}", file=sys.stderr)
        else:
            try:
                os.remove(pdf)
                print(f"[DEL] pdf: {pdf}", file=sys.stderr)
            except Exception as e:
                print(f"[ERRO] Falha ao deletar {pdf}: {e}", file=sys.stderr)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extrator de texto de PDFs para MedHub")
    parser.add_argument("pdfs", nargs="*", help="Arquivos PDF para extrair")
    parser.add_argument("--delete-pdfs", metavar="PASTA", help="Deleta todos os PDFs em uma pasta")
    parser.add_argument("--delete-temps", nargs="+", metavar="ARQUIVO", help="Deleta arquivos temporários específicos")
    parser.add_argument("--dry-run", action="store_true", help="Simula as ações de deleção sem executá-las")
    parser.add_argument("--out", help="Path de saída para extração (apenas se extrair um único PDF)")

    args = parser.parse_args()

    # Executar deleções primeiro se solicitadas
    if args.delete_pdfs:
        delete_pdfs_in_folder(args.delete_pdfs, dry_run=args.dry_run)
    
    if args.delete_temps:
        delete_temps(*args.delete_temps, dry_run=args.dry_run)

    # Executar extrações se houver PDFs
    if args.pdfs:
        if args.out and len(args.pdfs) > 1:
            print("[ERRO] --out só pode ser usado com um único PDF.", file=sys.stderr)
            sys.exit(1)
        
        for pdf_path in args.pdfs:
            extract_pdf(pdf_path, args.out)
    
    if not args.pdfs and not args.delete_pdfs and not args.delete_temps:
        parser.print_help()
