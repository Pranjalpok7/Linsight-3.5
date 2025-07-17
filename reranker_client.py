# reranker_client.py
from sentence_transformers.cross_encoder import CrossEncoder

class RerankerClient:
    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L-6-v2'):
        # This model runs well on CPU
        
        self.model = CrossEncoder(model_name, max_length=512)

    def rerank(self, query: str, documents: list[dict]) -> list[dict]:
        # The model expects pairs of [query, document_content]
        pairs = [[query, doc['content']] for doc in documents]
        scores = self.model.predict(pairs)
        
        # Add scores to the original document dictionaries
        for doc, score in zip(documents, scores):
            doc['rerank_score'] = score
        
        # Sort documents by their new rerank score
        return sorted(documents, key=lambda x: x['rerank_score'], reverse=True)