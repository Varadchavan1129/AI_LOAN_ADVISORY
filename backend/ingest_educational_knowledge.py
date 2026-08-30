"""
Ingest all 13 Educational Knowledge PDFs into the vector store (FAISS).
Run: python ingest_educational_knowledge.py
"""
import os
import uuid
import sys
from dotenv import load_dotenv

# Add backend to sys.path
sys.path.insert(0, os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app.services.pdf_processor import process_pdf
from app.services import vector_store

EDU_DIR = os.path.join(os.path.dirname(__file__), "uploads_educational")

def ingest_all():
    if not os.path.exists(EDU_DIR):
        print(f"Error: Directory {EDU_DIR} does not exist. Run generate_all_seed_pdfs.py first.")
        return

    pdfs = sorted([f for f in os.listdir(EDU_DIR) if f.endswith(".pdf")])
    print(f"Found {len(pdfs)} educational PDFs in uploads_educational/\n")

    vector_store.load()
    total_added_chunks = 0

    for pdf_name in pdfs:
        path = os.path.join(EDU_DIR, pdf_name)
        doc_id = str(uuid.uuid4())
        doc_name = pdf_name.replace(".pdf", "").replace("_", " ")

        print(f"Processing: {doc_name}...")
        res = process_pdf(path, doc_id, doc_name)
        chunks = res.get("chunks", [])
        if chunks:
            added = vector_store.add_document(doc_id, doc_name, chunks)
            total_added_chunks += added
            print(f"  Indexed {added} chunks into FAISS vector store.\n")

    print("=" * 65)
    print(f"🎉 SUCCESS: Ingested {total_added_chunks} new educational knowledge chunks!")
    print("=" * 65)

if __name__ == "__main__":
    ingest_all()
