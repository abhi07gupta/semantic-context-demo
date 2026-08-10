# Architecture notes

## Why structured context?
Raw retrieval answers “which text looks similar?” Structured context can additionally answer “which concepts, policies and relationships make this evidence relevant?”

## Production evolution
A real system might replace the simple graph and lexical scorer with:
- governed enterprise semantic models;
- graph databases or knowledge services;
- embedding / hybrid retrieval;
- provenance-aware context assembly;
- policy checks;
- LLM reasoning with evaluation and human oversight.

The architectural principle stays stable: keep enterprise meaning explicit enough to inspect, reuse and change independently of one model.
