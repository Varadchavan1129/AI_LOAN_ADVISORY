import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from app.services import vector_store

def test_search():
    vector_store.load()
    questions = [
        "What are the eligibility requirements mentioned in the policy document?",
        "What is the minimum age requirement mentioned in the policy?",
        "What is the maximum personal loan amount available to an astronaut?",
        "What are the rules mentioned in this policy?"
    ]
    
    for q in questions:
        print(f"\nQuery: {q}")
        res = vector_store.search(q, top_k=3)
        for i, c in enumerate(res.get("results", [])):
            print(f"  {i+1}. Score: {c['score']:.4f} | Doc: {c['document_name']}")

if __name__ == "__main__":
    test_search()
