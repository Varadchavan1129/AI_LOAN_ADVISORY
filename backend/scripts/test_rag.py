import requests
import json

BASE = 'http://127.0.0.1:8000'

print('=== TEST 1: Demo Question ===')
r = requests.post(f'{BASE}/rag/ask', json={'question': 'What are the eligibility requirements mentioned in this policy?', 'top_k': 5})
d = r.json()
print('support_level:', d.get('support_level'))
print('is_verified:', d.get('is_verified'))
print('retrieved_chunks:', d.get('retrieved_chunks'))
print('sources count:', len(d.get('sources', [])))
if d.get('sources'):
    for src in d['sources']:
        print('  source:', src.get('document_name'), 'page', src.get('page_number'), 'score', src.get('relevance_score'))
print('validation verdict:', d.get('validation', {}).get('verdict'))
print('answer:', str(d.get('answer', '')))

print()
print('=== TEST 2: NOT_IN_EVIDENCE ===')
r2 = requests.post(f'{BASE}/rag/ask', json={'question': 'What is the weather in Mumbai today?', 'top_k': 5})
d2 = r2.json()
print('support_level:', d2.get('support_level'))
print('is_verified:', d2.get('is_verified'))
print('answer:', str(d2.get('answer', ''))[:200])

print()
print('=== TEST 3: Another valid question ===')
r3 = requests.post(f'{BASE}/rag/ask', json={'question': 'What documents are required to apply for a loan?', 'top_k': 5})
d3 = r3.json()
print('support_level:', d3.get('support_level'))
print('sources:', [s.get('document_name') for s in d3.get('sources', [])])
print('answer:', str(d3.get('answer', ''))[:300])
