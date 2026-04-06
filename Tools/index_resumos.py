#!/usr/bin/env python3
"""
index_resumos — CLI para (re)indexar todos os resumos clínicos no ChromaDB.

Uso:
    python tools/index_resumos.py
    python tools/index_resumos.py --dir resumos

Pré-requisito: Ollama rodando com nomic-embed-text disponível.
    ollama pull nomic-embed-text
"""

import argparse
import sys
from pathlib import Path

# Raiz do projeto no path para imports absolutos (padrão dos CLIs em tools/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(
        description="Indexa resumos clínicos em ChromaDB via nomic-embed-text (Ollama)."
    )
    parser.add_argument(
        "--dir",
        default="resumos",
        help="Diretório raiz dos resumos (default: resumos)",
    )
    args = parser.parse_args()

    try:
        from app.engine.rag import index_all, _CHROMA_AVAILABLE
    except ImportError as e:
        print(f"Erro: ChromaDB não instalado.")
        print("Execute: pip install chromadb")
        print(f"Detalhe: {e}")
        sys.exit(1)

    if not _CHROMA_AVAILABLE:
        print("Erro: ChromaDB não disponível.")
        print("Execute: pip install chromadb")
        sys.exit(1)

    if not Path(args.dir).exists():
        print(f"Erro: diretório '{args.dir}' não encontrado.")
        sys.exit(1)

    print(f"Indexando resumos em '{args.dir}'...")
    print("(Requer Ollama rodando com nomic-embed-text)")
    print("  Se necessário: ollama pull nomic-embed-text\n")

    try:
        results = index_all(resumos_dir=args.dir)
    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ("connection", "ollama", "nomic", "refused")):
            print("Erro: não foi possível conectar ao Ollama.")
            print("Verifique se o Ollama está rodando e execute:")
            print("  ollama pull nomic-embed-text")
        else:
            print(f"Erro ao indexar: {e}")
        sys.exit(1)

    total_chunks = sum(results.values())
    print(f"{'Arquivo':<50} {'Chunks':>6}")
    print("-" * 58)
    for filename, count in sorted(results.items()):
        print(f"{filename:<50} {count:>6}")
    print("-" * 58)
    print(f"{'Total':<50} {total_chunks:>6}")
    print(f"\nConcluido: {len(results)} resumos, {total_chunks} chunks -> data/chroma/")


if __name__ == "__main__":
    main()
