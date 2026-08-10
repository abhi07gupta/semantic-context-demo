from __future__ import annotations

import math
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Iterable


TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


@dataclass(frozen=True)
class SearchResult:
    document_id: str
    title: str
    score: float
    lexical_score: float
    context_score: float
    matched_terms: tuple[str, ...]
    context_entities: tuple[str, ...]
    provenance: tuple[str, ...]


class ContextEngine:
    def __init__(self, documents: list[dict], entities: list[dict], relationships: list[dict]):
        self.documents = documents
        self.entities = {item["id"]: item for item in entities}
        self.aliases: dict[str, str] = {}
        for entity in entities:
            for alias in [entity["name"], *entity.get("aliases", [])]:
                self.aliases[alias.lower()] = entity["id"]
        self.graph: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for edge in relationships:
            self.graph[edge["source"]].append((edge["target"], edge["type"]))
            self.graph[edge["target"]].append((edge["source"], f"inverse:{edge['type']}"))
        self.doc_tokens = {d["id"]: tokenize(d["title"] + " " + d["text"]) for d in documents}
        self.document_frequency = Counter()
        for tokens in self.doc_tokens.values():
            self.document_frequency.update(set(tokens))
        self.avg_len = sum(map(len, self.doc_tokens.values())) / max(1, len(self.doc_tokens))

    def _entities_in_query(self, query: str) -> set[str]:
        lower = query.lower()
        return {entity_id for alias, entity_id in self.aliases.items() if alias in lower}

    def _expand(self, seeds: set[str], max_hops: int = 2) -> tuple[dict[str, float], list[str]]:
        weights = {seed: 1.0 for seed in seeds}
        provenance: list[str] = []
        queue = deque((seed, 0) for seed in seeds)
        visited = set(seeds)
        while queue:
            current, hops = queue.popleft()
            if hops >= max_hops:
                continue
            for neighbor, relation in self.graph.get(current, []):
                next_hop = hops + 1
                candidate = 0.65 ** next_hop
                weights[neighbor] = max(weights.get(neighbor, 0.0), candidate)
                provenance.append(f"{current} --{relation}--> {neighbor}")
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, next_hop))
        return weights, provenance

    def _bm25(self, query_terms: list[str], document_id: str) -> tuple[float, tuple[str, ...]]:
        tokens = self.doc_tokens[document_id]
        counts = Counter(tokens)
        score = 0.0
        matched: list[str] = []
        n = len(self.documents)
        k1, b = 1.2, 0.75
        for term in set(query_terms):
            if counts[term] == 0:
                continue
            matched.append(term)
            df = self.document_frequency[term]
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            tf = counts[term]
            denom = tf + k1 * (1 - b + b * len(tokens) / self.avg_len)
            score += idf * tf * (k1 + 1) / denom
        return score, tuple(sorted(matched))

    def search(self, query: str, *, use_context: bool = True, limit: int = 3) -> list[SearchResult]:
        terms = tokenize(query)
        seeds = self._entities_in_query(query) if use_context else set()
        weights, provenance = self._expand(seeds) if seeds else ({}, [])
        results: list[SearchResult] = []
        for doc in self.documents:
            lexical, matched = self._bm25(terms, doc["id"])
            entities = set(doc.get("entities", []))
            context = sum(weights.get(entity_id, 0.0) for entity_id in entities)
            score = lexical + (1.35 * context if use_context else 0.0)
            if score <= 0:
                continue
            path_evidence = tuple(path for path in provenance if any(entity_id in path for entity_id in entities))
            results.append(SearchResult(doc["id"], doc["title"], round(score, 6), round(lexical, 6), round(context, 6), matched, tuple(sorted(entities.intersection(weights))), path_evidence[:5]))
        return sorted(results, key=lambda item: (-item.score, item.document_id))[:limit]
