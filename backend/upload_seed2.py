"""
Upload and process all PDFs from uploads_seed2 folder.
Run AFTER backend is running on port 8000.
"""
import os, time, requests

BASE_URL  = "http://localhost:8000"
ADMIN_KEY = "tata-mitra-admin-2024"
SEED_DIR  = os.path.join(os.path.dirname(__file__), "..", "uploads_seed2")
HEADERS   = {"X-Admin-Key": ADMIN_KEY}

def upload_and_process(pdf_path):
    name = os.path.basename(pdf_path)
    print(f"\n{'='*55}\nProcessing: {name}")
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/admin/documents/upload",
            headers=HEADERS,
            files={"file": (name, f, "application/pdf")},
        )
    if resp.status_code != 200:
        print(f"  UPLOAD FAILED: {resp.status_code} {resp.text[:200]}")
        return
    doc_id = resp.json().get("id")
    print(f"  Uploaded -> doc_id: {doc_id}")
    time.sleep(1)
    resp2 = requests.post(f"{BASE_URL}/admin/documents/{doc_id}/process", headers=HEADERS)
    if resp2.status_code != 200:
        print(f"  PROCESS FAILED: {resp2.status_code} {resp2.text[:200]}")
        return
    r = resp2.json()
    print(f"  Indexed  -> {r.get('chunk_count')} chunks | Status: {r.get('status')}")
    if r.get("warnings"):
        print(f"  Warnings: {r['warnings']}")

if __name__ == "__main__":
    pdfs = sorted([os.path.join(SEED_DIR, f) for f in os.listdir(SEED_DIR) if f.endswith(".pdf")])
    if not pdfs:
        print("No PDFs found in uploads_seed2/")
        exit(1)
    print(f"Found {len(pdfs)} PDFs to upload:")
    for p in pdfs:
        print(f"  - {os.path.basename(p)}")
    print("\nStarting upload...")
    for pdf_path in pdfs:
        upload_and_process(pdf_path)
        time.sleep(2)
    print(f"\n{'='*55}")
    print("Done! Check /search/stats for updated index.")
