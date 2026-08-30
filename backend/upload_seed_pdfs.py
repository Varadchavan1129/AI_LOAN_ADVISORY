"""
Auto-upload and process all seed PDFs into Tata Mitra.
Run AFTER starting the backend server.

Usage:
  cd backend
  source venv/bin/activate
  python upload_seed_pdfs.py
"""
import os
import time
import requests

BASE_URL    = "http://localhost:8000"
ADMIN_KEY   = "tata-mitra-admin-2024"   # matches ADMIN_SECRET_KEY in .env
SEED_DIR    = os.path.join(os.path.dirname(__file__), "..", "uploads_seed")
HEADERS     = {"X-Admin-Key": ADMIN_KEY}

def upload_and_process(pdf_path: str):
    name = os.path.basename(pdf_path)
    print(f"\n{'='*55}")
    print(f"Processing: {name}")

    # 1. Upload
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/admin/documents/upload",
            headers=HEADERS,
            files={"file": (name, f, "application/pdf")},
        )
    if resp.status_code != 200:
        print(f"  UPLOAD FAILED: {resp.status_code} {resp.text}")
        return

    doc_id = resp.json().get("id")
    print(f"  Uploaded  -> doc_id: {doc_id}")

    # 2. Process (embed into vector store)
    time.sleep(1)
    resp2 = requests.post(
        f"{BASE_URL}/admin/documents/{doc_id}/process",
        headers=HEADERS,
    )
    if resp2.status_code != 200:
        print(f"  PROCESS FAILED: {resp2.status_code} {resp2.text}")
        return

    result = resp2.json()
    print(f"  Processed -> {result.get('chunk_count')} chunks from {result.get('page_count')} pages")
    if result.get("warnings"):
        print(f"  Warnings: {result['warnings']}")
    print(f"  Status: {result.get('status')}")


if __name__ == "__main__":
    pdfs = sorted([
        os.path.join(SEED_DIR, f)
        for f in os.listdir(SEED_DIR)
        if f.endswith(".pdf")
    ])

    if not pdfs:
        print("No PDFs found in uploads_seed/. Run generate_pdfs.py first.")
        exit(1)

    print(f"Found {len(pdfs)} PDFs to upload:")
    for p in pdfs:
        print(f"  - {os.path.basename(p)}")

    print("\nStarting upload and processing...")
    for pdf_path in pdfs:
        upload_and_process(pdf_path)
        time.sleep(2)  # avoid rate-limiting between API calls

    print(f"\n{'='*55}")
    print("All done! Check the Admin panel to confirm all documents are indexed.")
