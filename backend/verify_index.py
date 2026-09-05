import os
import json
import faiss

VECTOR_DIR = os.path.join(os.path.dirname(__file__), "vector_store")
INDEX_PATH = os.path.join(VECTOR_DIR, "combined.faiss")
META_PATH = os.path.join(VECTOR_DIR, "combined.json")

def verify():
    with open(META_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    index = faiss.read_index(INDEX_PATH)
    
    print(f"Index total vectors: {index.ntotal}")
    print(f"Metadata chunks count: {len(chunks)}")
    print(f"Dimensions: {index.d}")
    
    if index.ntotal == len(chunks):
        print("PASS: Vector count matches metadata count.")
    else:
        print("FAIL: Vector count does not match metadata count.")
        
    if index.d == 3072:
        print("PASS: Dimension is 3072.")
    else:
        print(f"FAIL: Dimension is {index.d}, expected 3072.")
    
    if len(chunks) > 0:
        c = chunks[0]
        required_keys = ["document_name", "page_number", "chunk_index"]
        missing_keys = [k for k in required_keys if k not in c]
        if not missing_keys:
            print("PASS: Required metadata fields preserved.")
        else:
            print(f"FAIL: Missing metadata fields: {missing_keys}")
        
if __name__ == "__main__":
    verify()
