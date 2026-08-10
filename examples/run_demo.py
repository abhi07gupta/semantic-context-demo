import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from semantic_context_demo import SemanticContextEngine
engine=SemanticContextEngine(ROOT/'data/entities.json',ROOT/'data/documents.json')
query='battery issue for Nova X in Sweden'
print('QUERY:',query)
print('\nLEXICAL BASELINE')
for r in engine.lexical_search(query): print(f'{r.score:4.1f}  {r.title}  |  {"; ".join(r.reasons)}')
print('\nCONTEXT-AWARE')
for r in engine.context_search(query): print(f'{r.score:4.1f}  {r.title}  |  {"; ".join(r.reasons)}')
