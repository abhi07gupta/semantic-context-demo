from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .engine import ContextEngine
from .evaluation import evaluate


def load_engine(data_dir: Path) -> ContextEngine:
    load = lambda name: json.loads((data_dir / name).read_text(encoding="utf-8"))
    return ContextEngine(load("documents.json"), load("entities.json"), load("relationships.json"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explainable graph-augmented retrieval demo")
    parser.add_argument("query", nargs="?", default="Why is checkout slow after the gateway change?")
    parser.add_argument("--baseline", action="store_true", help="disable semantic context")
    parser.add_argument("--evaluate", action="store_true", help="run the synthetic evaluation set")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parents[2] / "data")
    args = parser.parse_args(argv)
    engine = load_engine(args.data_dir)
    if args.evaluate:
        cases = json.loads((args.data_dir / "evaluation.json").read_text())
        print(json.dumps(evaluate(engine, cases), indent=2))
    else:
        print(json.dumps([asdict(item) for item in engine.search(args.query, use_context=not args.baseline)], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
