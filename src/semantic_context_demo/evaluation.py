from __future__ import annotations

from .engine import ContextEngine


def reciprocal_rank(results: list, relevant: str) -> float:
    for index, item in enumerate(results, 1):
        if item.document_id == relevant:
            return 1.0 / index
    return 0.0


def evaluate(engine: ContextEngine, cases: list[dict]) -> dict[str, object]:
    rows = []
    baseline, contextual = 0.0, 0.0
    for case in cases:
        lexical = engine.search(case["query"], use_context=False, limit=5)
        context = engine.search(case["query"], use_context=True, limit=5)
        b = reciprocal_rank(lexical, case["relevant"])
        c = reciprocal_rank(context, case["relevant"])
        baseline += b
        contextual += c
        rows.append({"query": case["query"], "relevant": case["relevant"], "baseline_rr": b, "context_rr": c, "baseline_top": lexical[0].document_id if lexical else None, "context_top": context[0].document_id if context else None})
    count = max(1, len(cases))
    return {"cases": rows, "baseline_mrr": round(baseline / count, 4), "context_mrr": round(contextual / count, 4), "delta": round((contextual - baseline) / count, 4)}
