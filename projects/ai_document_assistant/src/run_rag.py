from rag_pipeline import DocumentRagPipeline


if __name__ == "__main__":
    pipeline = DocumentRagPipeline()
    result = pipeline.answer_question("apa isi halaman 10")

    print("MODE:", result.mode)
    print("JAWABAN:")
    print(result.answer)
    print("\nBUKTI/SUMBER:")
    for source in result.sources:
        preview = source.text[:120].replace("\n", " ")
        print(f"- Halaman {source.page}: {preview}...")
