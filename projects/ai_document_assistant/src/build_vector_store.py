import argparse
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
VECTOR_STORE_DIR = PROJECT_DIR / "vector_store"
ENV_PATH = PROJECT_DIR / ".env"


def find_pdfs() -> list[Path]:
    return sorted(RAW_DIR.glob("*.pdf"))


def load_documents(pdf_paths: list[Path]):
    documents = []
    for pdf_path in pdf_paths:
        print(f"Loading: {pdf_path.name}")
        loader = PyMuPDFLoader(str(pdf_path))
        documents.extend(loader.load())
    return documents


def reset_vector_store():
    resolved_store = VECTOR_STORE_DIR.resolve()
    resolved_project = PROJECT_DIR.resolve()
    if resolved_project not in resolved_store.parents:
        raise RuntimeError(f"Refusing to delete path outside project: {resolved_store}")

    if VECTOR_STORE_DIR.exists():
        print(f"Removing old vector store: {VECTOR_STORE_DIR}")
        shutil.rmtree(VECTOR_STORE_DIR)


def build_vector_store(reset: bool = False):
    load_dotenv(ENV_PATH)

    pdf_paths = find_pdfs()
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in {RAW_DIR}")

    if reset:
        reset_vector_store()

    documents = load_documents(pdf_paths)
    print(f"Loaded pages: {len(documents)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created chunks: {len(chunks)}")

    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("SUMOPOD_API_KEY"),
        openai_api_base=os.getenv("SUMOPOD_API_BASE"),
        model="text-embedding-3-small",
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    total = vectorstore.get()
    print(f"Vector store ready: {VECTOR_STORE_DIR}")
    print(f"Stored chunks: {len(total.get('ids', []))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Chroma vector store from local PDF files.")
    parser.add_argument("--reset", action="store_true", help="Delete the old vector store before rebuilding.")
    args = parser.parse_args()
    build_vector_store(reset=args.reset)
