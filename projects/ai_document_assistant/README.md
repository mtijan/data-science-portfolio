# AI Document Assistant (RAG)

A Retrieval-Augmented Generation (RAG) tool for querying unstructured PDF documents with source evidence.

## Goal

Provide an intelligent interface for searching and summarizing long documents like CVs, reports, and research papers, turning buried information into actionable, evidence-backed answers.

## Architecture

This project implements a standard RAG pipeline:
1. **Document Loading**: PDF processing using `PyMuPDF` or `pypdf`.
2. **Chunking**: Text splitting with LangChain.
3. **Embeddings**: Vector representation of text chunks.
4. **Vector Store**: Storage and retrieval via `ChromaDB`.
5. **Generation**: Intelligent answer generation using `SumoPod API` (GLM-5 Turbo).

## Interactive Dashboard

### Unified Portfolio Integration
The assistant is now **embedded directly** into the Django portfolio website.
- **Embedded URL**: `http://127.0.0.1:8052/projects/ai-document-assistant/`

### Features
- **Suggested Questions**: Quick-click prompts for candidate profiles, skills, and experience.
- **Source Evidence**: Displays the exact page and text snippets used to generate the answer.
- **Fast Page Lookup**: Direct retrieval for page-specific queries.

## Technical Workflow

1. Load PDFs from `data/raw/`.
2. Run `src/build_vector_store.py` to index the documents.
3. Run the dashboard or access it via the portfolio.

## Main Files
- `src/rag_pipeline.py`: Core RAG logic and LLM integration.
- `src/build_vector_store.py`: Script for indexing new documents.
- `dashboard/app.py`: Dash interface for Q&A.
