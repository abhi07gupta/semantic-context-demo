from __future__ import annotations
import json, re
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict, deque

TOKEN_RE=re.compile(r"[a-z0-9]+")
def tokens(text:str)->set[str]: return set(TOKEN_RE.findall(text.lower()))

@dataclass
class Result:
    doc_id:str
    title:str
    score:float
    reasons:list[str]

class SemanticContextEngine:
    def __init__(self, entities_path:Path, documents_path:Path):
        graph=json.loads(entities_path.read_text())
        self.docs=json.loads(documents_path.read_text())
        self.entity_by_id={e['id']:e for e in graph['entities']}
        self.aliases={e['name'].lower():e['id'] for e in graph['entities']}
        self.edges=defaultdict(set)
        for a,rel,b in graph['relations']:
            self.edges[a].add(b); self.edges[b].add(a)

    def _query_entities(self, query:str)->set[str]:
        q=query.lower(); found={eid for name,eid in self.aliases.items() if name in q}
        if 'battery' in q or 'shutdown' in q: found.add('issue:power')
        return found

    def _expand(self, seeds:set[str], depth:int=2)->dict[str,int]:
        dist={s:0 for s in seeds}; queue=deque(seeds)
        while queue:
            node=queue.popleft()
            if dist[node] >= depth: continue
            for nxt in self.edges[node]:
                if nxt not in dist:
                    dist[nxt]=dist[node]+1; queue.append(nxt)
        return dist

    def lexical_search(self, query:str, top_k:int=4)->list[Result]:
        q=tokens(query); out=[]
        for d in self.docs:
            overlap=q & tokens(d['title']+' '+d['text'])
            out.append(Result(d['id'],d['title'],float(len(overlap)),[f"lexical overlap: {', '.join(sorted(overlap))}" if overlap else 'no lexical overlap']))
        return sorted(out,key=lambda r:(-r.score,r.doc_id))[:top_k]

    def context_search(self, query:str, top_k:int=4)->list[Result]:
        q=tokens(query); seeds=self._query_entities(query); expanded=self._expand(seeds)
        out=[]
        for d in self.docs:
            lexical=len(q & tokens(d['title']+' '+d['text']))
            semantic=0.0; matched=[]
            for e in d.get('entities',[]):
                if e in expanded:
                    semantic += 3.0/(1+expanded[e]); matched.append(self.entity_by_id[e]['name'])
            score=lexical+semantic
            reasons=[f"lexical={lexical}"]
            if matched: reasons.append("context="+', '.join(matched))
            out.append(Result(d['id'],d['title'],score,reasons))
        return sorted(out,key=lambda r:(-r.score,r.doc_id))[:top_k]
