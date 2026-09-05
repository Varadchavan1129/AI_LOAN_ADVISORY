import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()
from fastapi.testclient import TestClient

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

def test_questions():
    with TestClient(app) as client:
        questions = [
            ("A", "What are the eligibility requirements mentioned in the policy document?"),
            ("B", "What is the minimum age requirement mentioned in the policy?"),
            ("C", "What is the maximum personal loan amount available to an astronaut?"),
            ("D", "What are the rules mentioned in this policy?"),
        ]

        results = []
        
        for q_id, q_text in questions:
            print(f"\nTesting {q_id}: {q_text}")
            response = client.post("/api/chat/query", json={"message": q_text})
            
            if response.status_code == 200:
                data = response.json()
                # Handle RAG / Policy
                msg = data.get("message", "")
                res_type = data.get("type", "")
                sources = []
                verdict = ""
                if data.get("data"):
                    sources = data["data"].get("sources", [])
                    validation = data["data"].get("validation", {})
                    verdict = validation.get("verdict", data["data"].get("support_level", ""))
                    
                print(f"  Type: {res_type}")
                print(f"  Message Preview: {msg[:100]}...")
                print(f"  Verdict: {verdict}")
                print(f"  Sources: {len(sources)}")
                
                results.append({
                    "id": q_id,
                    "question": q_text,
                    "type": res_type,
                    "verdict": verdict,
                    "sources_count": len(sources),
                    "message": msg
                })
            else:
                print(f"  Error: {response.status_code} - {response.text}")
                results.append({
                    "id": q_id,
                    "error": response.status_code
                })
                
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    test_questions()
