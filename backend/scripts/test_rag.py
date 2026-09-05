import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app, vector_store

vector_store.load()
client = TestClient(app)

print('=== TEST 1: Eligibility Requirements Question ===')
r1 = client.post('/rag/ask', json={'question': 'What are the eligibility requirements mentioned in the policy document?', 'top_k': 5})
d1 = r1.json()
print('status_code:', r1.status_code)
print('support_level:', d1.get('support_level'))
print('is_verified:', d1.get('is_verified'))
print('sources count:', len(d1.get('sources', [])))
for src in d1.get('sources', []):
    print('  source:', src.get('document_name'), 'page', src.get('page_number'), 'score', src.get('relevance_score'))
print('validation verdict:', d1.get('validation', {}).get('verdict'))
print('answer:', str(d1.get('answer', '')))

print()
print('=== TEST 2: Minimum Age Requirement Question ===')
r2 = client.post('/rag/ask', json={'question': 'What is the minimum age requirement mentioned in the policy?', 'top_k': 5})
d2 = r2.json()
print('status_code:', r2.status_code)
print('support_level:', d2.get('support_level'))
print('is_verified:', d2.get('is_verified'))
print('sources:', [{'doc': s.get('document_name'), 'page': s.get('page_number')} for s in d2.get('sources', [])])
print('answer:', str(d2.get('answer', '')))

print()
print('=== TEST 3: NOT_IN_EVIDENCE (Astronaut) Question ===')
r3 = client.post('/rag/ask', json={'question': 'What is the maximum personal loan amount available to an astronaut?', 'top_k': 5})
d3 = r3.json()
print('status_code:', r3.status_code)
print('support_level:', d3.get('support_level'))
print('is_verified:', d3.get('is_verified'))
print('validation:', d3.get('validation', {}).get('verdict'))
print('answer:', str(d3.get('answer', '')))

