# src/semantic_matcher.py

from sentence_transformers import SentenceTransformer, util

class SemanticMatcher:
    def __init__(self, graph, model_name="all-MiniLM-L6-v2"):
        self.graph = graph
        self.model = SentenceTransformer(model_name)
        self.kg_terms = self.extract_terms()
        self.kg_embeddings = self.model.encode(self.kg_terms, convert_to_tensor=True)

    def extract_terms(self):
        terms = set()
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") in ["tagged_as", "about"]:
                terms.add(v.lower())
        return list(terms)

    def expand(self, term, top_k=5, threshold=0.4, verbose=False):
        query_embedding = self.model.encode(term, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.kg_embeddings)[0]
    
        top_indices = (scores >= threshold).nonzero().flatten().tolist()
        sorted_indices = sorted(top_indices, key=lambda i: scores[i], reverse=True)
    
        if verbose:
            print(f"\n🔍 Semantic matches for: '{term}' (threshold={threshold})")
            for i in sorted_indices[:top_k]:
                print(f"→ {self.kg_terms[i]} (score: {scores[i]:.3f})")
    
        return [self.kg_terms[i] for i in sorted_indices[:top_k]]