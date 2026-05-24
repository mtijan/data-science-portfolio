import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_DIR / ".env"
VECTOR_STORE_PATH = PROJECT_DIR / "vector_store"

DEFAULT_CHAT_MODEL = "glm-5-turbo"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


@dataclass
class SourceSnippet:
    page: int | str
    text: str
    source: str | None = None


@dataclass
class RagResult:
    question: str
    answer: str
    sources: list[SourceSnippet]
    mode: str


def detect_page_request(question: str) -> int | None:
    match = re.search(r"\bhal(?:aman|amaan)?\.?\s*(\d+)\b", question.lower())
    if not match:
        return None

    page_number = int(match.group(1))
    return page_number if page_number >= 1 else None


def build_llm(model: str = DEFAULT_CHAT_MODEL) -> ChatOpenAI:
    load_dotenv(ENV_PATH)
    return ChatOpenAI(
        openai_api_key=os.getenv("SUMOPOD_API_KEY"),
        openai_api_base=os.getenv("SUMOPOD_API_BASE"),
        model=model,
        temperature=0.0,
    )


def build_embeddings() -> OpenAIEmbeddings:
    load_dotenv(ENV_PATH)
    return OpenAIEmbeddings(
        openai_api_key=os.getenv("SUMOPOD_API_KEY"),
        openai_api_base=os.getenv("SUMOPOD_API_BASE"),
        model=DEFAULT_EMBEDDING_MODEL,
    )


def build_vectorstore() -> Chroma:
    embeddings = build_embeddings()
    return Chroma(persist_directory=str(VECTOR_STORE_PATH), embedding_function=embeddings)


class DocumentRagPipeline:
    def __init__(self, model: str = DEFAULT_CHAT_MODEL, search_k: int = 2):
        self.llm = build_llm(model=model)
        self.vectorstore = build_vectorstore()
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": search_k})
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Anda adalah asisten cerdas untuk menjawab pertanyaan berdasarkan dokumen.\n"
                    "Gunakan hanya konteks berikut untuk menjawab.\n"
                    "Jika jawaban tidak ada di konteks, katakan bahwa Anda tidak tahu.\n"
                    "Jawab ringkas, jelas, dan maksimal 3 parargraph 5 kalimat.\n\n"
                    "{context}",
                ),
                ("human", "{input}"),
            ]
        )

    def get_page_chunks(self, page_number: int) -> list[SourceSnippet]:
        page_index = page_number - 1
        results = self.vectorstore.get(where={"page": page_index})
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        sources = []
        for content, metadata in zip(documents, metadatas):
            if not content:
                continue
            metadata = metadata or {}
            sources.append(
                SourceSnippet(
                    page=page_number,
                    text=content,
                    source=metadata.get("source") or metadata.get("file_path"),
                )
            )
        return sources

    def answer_page_request(self, question: str, page_number: int) -> RagResult:
        sources = self.get_page_chunks(page_number)
        if not sources:
            return RagResult(
                question=question,
                answer=f"Tidak menemukan teks untuk halaman {page_number}.",
                sources=[],
                mode="page_lookup",
            )

        text = "\n\n".join(source.text for source in sources)
        return RagResult(
            question=question,
            answer=text[:2500],
            sources=sources,
            mode="page_lookup",
        )

    def answer_question(self, question: str) -> RagResult:
        page_number = detect_page_request(question)
        if page_number is not None:
            return self.answer_page_request(question, page_number)

        docs = self.retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        messages = self.prompt.format_messages(context=context, input=question)
        response = self.llm.invoke(messages)

        sources = [
            SourceSnippet(
                page=doc.metadata.get("page", "Unknown"),
                text=doc.page_content,
                source=doc.metadata.get("source") or doc.metadata.get("file_path"),
            )
            for doc in docs
        ]
        return RagResult(
            question=question,
            answer=response.content,
            sources=sources,
            mode="rag",
        )

