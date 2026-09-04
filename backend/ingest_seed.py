"""
Seed the RAG knowledge base: generate educational PDFs (if needed) and push
them through the live API pipeline (upload -> object storage -> process ->
FAISS index). Run once after the backend is up.

    python ingest_seed.py
"""
import os
import sys
import time
import glob
import requests

BASE = "http://localhost:8001/api"
ADMIN_KEY = os.getenv("ADMIN_SECRET_KEY", "tata-mitra-admin-2024")
HEADERS = {"X-Admin-Key": ADMIN_KEY}

PDF_DIR = os.path.join(os.path.dirname(__file__), "uploads_educational")


def ensure_pdfs():
    pdfs = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    if not pdfs:
        print("No PDFs found — generating educational seed PDFs...")
        import generate_all_seed_pdfs  # noqa: F401 (module runs generation on import? no)
        for fn in [
            generate_all_seed_pdfs.create_personal_loan_pdf,
            generate_all_seed_pdfs.create_home_loan_pdf,
            generate_all_seed_pdfs.create_financial_literacy_pdf,
            generate_all_seed_pdfs.create_loan_faq_pdf,
            generate_all_seed_pdfs.create_tata_mitra_guidelines_pdf,
            generate_all_seed_pdfs.create_education_loan_pdf,
            generate_all_seed_pdfs.create_gold_loan_pdf,
            generate_all_seed_pdfs.create_business_loan_pdf,
            generate_all_seed_pdfs.create_cibil_guide_pdf,
            generate_all_seed_pdfs.create_prepayment_pdf,
            generate_all_seed_pdfs.create_dti_guide_pdf,
            generate_all_seed_pdfs.create_ombudsman_pdf,
            generate_all_seed_pdfs.create_balance_transfer_pdf,
        ]:
            fn()
        pdfs = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    return sorted(pdfs)


def existing_names():
    r = requests.get(f"{BASE}/admin/documents", headers=HEADERS, timeout=30)
    if r.ok:
        return {d["original_name"] for d in r.json().get("documents", [])}
    return set()


def ingest():
    pdfs = ensure_pdfs()
    print(f"Found {len(pdfs)} PDFs to ingest.")
    have = existing_names()
    for path in pdfs:
        name = os.path.basename(path)
        if name in have:
            print(f"  SKIP {name} (already indexed)")
            continue
        with open(path, "rb") as f:
            up = requests.post(
                f"{BASE}/admin/documents/upload",
                headers=HEADERS,
                files={"file": (name, f, "application/pdf")},
                timeout=120,
            )
        if not up.ok:
            print(f"  FAIL upload {name}: {up.status_code} {up.text[:120]}")
            continue
        doc_id = up.json()["id"]
        pr = requests.post(f"{BASE}/admin/documents/{doc_id}/process", headers=HEADERS, timeout=300)
        if pr.ok and pr.json().get("status") == "indexed":
            print(f"  OK   {name}: {pr.json().get('chunk_count')} chunks")
        else:
            print(f"  FAIL process {name}: {pr.status_code} {pr.text[:160]}")
        time.sleep(0.5)

    stats = requests.get(f"{BASE}/search/stats").json()
    print(f"\nVector store now: {stats['total_documents']} docs, {stats['total_chunks']} chunks.")


if __name__ == "__main__":
    ingest()
