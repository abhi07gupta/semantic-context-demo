import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from semantic_context_demo import SemanticContextEngine
class TestEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.e=SemanticContextEngine(ROOT/'data/entities.json',ROOT/'data/documents.json')
    def test_context_finds_power_doc_first(self): self.assertEqual(self.e.context_search('battery issue for Nova X in Sweden')[0].doc_id,'doc-1')
    def test_context_surfaces_nordics_policy(self): self.assertIn('doc-2',[r.doc_id for r in self.e.context_search('battery issue for Nova X in Sweden')[:3]])
    def test_lexical_returns_results(self): self.assertTrue(self.e.lexical_search('display Nova'))
if __name__=='__main__': unittest.main()
