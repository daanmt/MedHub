#!/usr/bin/env python3
"""
index_pdf_raw -- CLI para (re)indexar o TIER BRUTO (pdf_raw) no ChromaDB (F17).

Indexa o texto extraido dos PDFs-fonte em resumos/**/*.pdf numa collection
SEPARADA (`pdf_raw`), sem tocar no gold (`resumos`). Incremental por mtime:
re-rodar sem PDFs novos/alterados nao re-embedda. `--clear` limpa SOMENTE a
collection pdf_raw.

Uso:
    python tools/index_pdf_raw.py
    python tools/index_pdf_raw.py --dir resumos
    python tools/index_pdf_raw.py --clear

Pre-requisito: Ollama rodando com nomic-embed-text. PDFs NAO sao deletados.
"""

import argparse
import sys
from pathlib import Path

# Raiz do projeto no path para imports absolutos (padrao dos CLIs em tools/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(
        description="Indexa o tier bruto (pdf_raw) dos PDFs-fonte em ChromaDB."
    )
    parser.add_argument("--dir", default="resumos",
                        help="Diretorio raiz dos PDFs (default: resumos)")
    parser.add_argument("--clear", action="store_true",
                        help="Deleta SOMENTE a collection pdf_raw e reindexa do zero")
    args = parser.parse_args()

    try:
        from app.engine.rag import index_pdfs_raw, _CHROMA_AVAILABLE
    except ImportError as e:
        print("Erro: ChromaDB nao instalado.")
        print("Execute: pip install chromadb")
        print(f"Detalhe: {e}")
        sys.exit(1)

    if not _CHROMA_AVAILABLE:
        print("Erro: ChromaDB nao disponivel.")
        print("Execute: pip install chromadb")
        sys.exit(1)

    if not Path(args.dir).exists():
        print(f"Erro: diretorio '{args.dir}' nao encontrado.")
        sys.exit(1)

    print(f"Indexando tier bruto (pdf_raw) de '{args.dir}'...")
    print("(Requer Ollama rodando com nomic-embed-text; PDFs nao sao deletados)\n")

    try:
        results = index_pdfs_raw(resumos_dir=args.dir, clear=args.clear)
    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ("connection", "ollama", "nomic", "refused")):
            print("Erro: nao foi possivel conectar ao Ollama.")
            print("Verifique se o Ollama esta rodando e execute:")
            print("  ollama pull nomic-embed-text")
        else:
            print(f"Erro ao indexar: {e}")
        sys.exit(1)

    total_chunks = sum(results.values())
    indexados = sum(1 for v in results.values() if v > 0)
    pulados = sum(1 for v in results.values() if v == 0)
    print(f"{'PDF':<60} {'Chunks':>6}")
    print("-" * 68)
    for pdf_path, count in sorted(results.items()):
        nome = Path(pdf_path).name
        marca = "" if count > 0 else "  (pulado: mtime inalterado ou sem texto)"
        print(f"{nome:<60} {count:>6}{marca}")
    print("-" * 68)
    print(f"{'Total':<60} {total_chunks:>6}")
    print(f"\nConcluido: {len(results)} PDFs ({indexados} indexados, {pulados} pulados), "
          f"{total_chunks} chunks -> data/chroma/ (collection pdf_raw)")


if __name__ == "__main__":
    main()
