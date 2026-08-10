import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from semantic_context_demo import ContextEngine, evaluate


class SemanticContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = Path(__file__).parents[1] / "data"
        load = lambda name: json.loads((data / name).read_text())
        cls.engine = ContextEngine(load("documents.json"), load("entities.json"), load("relationships.json"))
        cls.cases = load("evaluation.json")

    def test_context_retrieves_routing_runbook(self):
        result = self.engine.search("Why is checkout slow after the gateway change?")
        self.assertEqual(result[0].document_id, "doc-routing")
        self.assertGreater(result[0].context_score, 0)
        self.assertTrue(result[0].provenance)

    def test_baseline_is_available(self):
        result = self.engine.search("payments errors", use_context=False)
        self.assertEqual(result[0].document_id, "doc-payment")

    def test_context_does_not_reduce_mrr(self):
        metrics = evaluate(self.engine, self.cases)
        self.assertGreaterEqual(metrics["context_mrr"], metrics["baseline_mrr"])


if __name__ == "__main__":
    unittest.main()
