# AI Document Assistant Source Workflow

Panduan ini dipakai saat ingin mengganti atau menambah dokumen PDF untuk RAG pipeline.

## 1. Struktur Data

Raw PDF disimpan di:

```text
projects/ai_document_assistant/data/raw/
```

Vector store Chroma dibuat di:

```text
projects/ai_document_assistant/vector_store/
```

Folder `data/raw/` dan `vector_store/` bersifat lokal dan tidak perlu diupload ke GitHub.

## 2. Menambah PDF Baru

1. Masukkan file PDF baru ke folder:

```text
projects/ai_document_assistant/data/raw/
```

2. Jika dokumen lama tidak ingin ikut dipakai, hapus atau pindahkan PDF lama dari folder `data/raw/`.

Contoh PowerShell untuk melihat isi folder:

```powershell
Get-ChildItem projects/ai_document_assistant/data/raw
```

Contoh menghapus satu PDF lama:

```powershell
Remove-Item -LiteralPath "projects/ai_document_assistant/data/raw/nama_file_lama.pdf"
```

Jangan hapus seluruh folder `data/raw/` jika masih ada file yang ingin dipakai.

## 3. Stop Proses yang Masih Memakai Vector Store

Sebelum rebuild, stop dulu:

```text
Dashboard AI Document Assistant
Notebook kernel yang sedang membuka Chroma/vector store
```

Kalau tidak, Windows bisa menolak penghapusan vector store lama dengan error:

```text
PermissionError: The process cannot access the file because it is being used by another process
```

## 4. Rebuild Vector Store dari PDF Terbaru

Jalankan dari root project:

```powershell
uv run python projects/ai_document_assistant/src/build_vector_store.py --reset
```

Fungsi command ini:

```text
1. Menghapus vector_store lama
2. Membaca semua PDF di data/raw/
3. Memecah dokumen menjadi chunks
4. Membuat embeddings
5. Menyimpan Chroma vector store baru
```

Jika ada 3 PDF di `data/raw/`, maka semua akan masuk ke vector store.

## 5. Test Pipeline Setelah Rebuild

Jalankan:

```powershell
uv run python projects/ai_document_assistant/src/run_rag.py
```

Atau test manual dengan pertanyaan khusus:

```powershell
uv run python -c "import sys; sys.path.insert(0, 'projects/ai_document_assistant/src'); from rag_pipeline import DocumentRagPipeline; p=DocumentRagPipeline(); r=p.answer_question('Rangkum profil kandidat'); print(r.answer)"
```

## 6. Jalankan Dashboard

Setelah vector store berhasil dibuat:

```powershell
uv run python projects/ai_document_assistant/dashboard/app.py
```

Buka:

```text
http://127.0.0.1:8052/
```

## 7. File Penting di Folder src

```text
build_vector_store.py  -> rebuild Chroma dari PDF di data/raw/
rag_pipeline.py        -> pipeline utama untuk dashboard dan test
run_rag.py             -> test manual pipeline
test_rag.py            -> file eksperimen lama
```

## 8. Checklist Singkat

```text
[ ] Masukkan PDF baru ke data/raw/
[ ] Hapus atau pindahkan PDF lama yang tidak dipakai
[ ] Stop dashboard/notebook yang aktif
[ ] Jalankan build_vector_store.py --reset
[ ] Test dengan run_rag.py
[ ] Jalankan dashboard/app.py
[ ] Refresh browser di http://127.0.0.1:8052/
```
