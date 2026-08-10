# Architecture note

The demo combines two signals:

1. BM25-style lexical relevance over document text.
2. Weighted graph proximity from entities named in the query to entities attached to each document.

The graph contribution decays by hop and is shown separately in each result.
Provenance paths explain why context changed the ranking. This is intentionally
small, transparent, and deterministic; a production semantic layer would also
need entity resolution quality, ontology governance, access controls, temporal
validity, retrieval evaluation, observability, and ownership for change.
