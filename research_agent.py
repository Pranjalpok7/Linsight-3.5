import trafilatura
import asyncio 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np

from search_client import SearchEngine
from synthesis_client import SynthesisClient
from db_client import DBClient
from reranker_client import RerankerClient

class ResearchAgent:
    def __init__(self):
        self.search_client = SearchEngine()
        self.synthesis_client = SynthesisClient()
        self.db_client = DBClient()
        self.reranker_client = RerankerClient()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    async def run(self, query: str) -> dict:
        # Step 1: Clear previous documents for a fresh run
        self.db_client.clear_documents()
        
        # Step 2: Initial Web Search
        print("Step 1: Performing initial web search...")
        search_results = self.search_client.search(query, max_results=10)
        if not search_results:
            return None

        # Step 3: Content Extraction, Chunking, and Embedding
        print("Step 2: Extracting content, chunking, and embedding...")
        for result in search_results:
            downloaded = trafilatura.fetch_url(result['url'])
            if not downloaded:
                continue
            
            full_text = trafilatura.extract(downloaded)
            if not full_text:
                continue

            # Keep the title from the original search result
            title = result['title'] 
            chunks = self.text_splitter.split_text(full_text)
            
            # Step 4: Storing in DB
            for chunk in chunks:
                embedding = self.embedding_model.encode(chunk)
                # Pass the title along with other data to the database client
                self.db_client.insert_document(result['url'], title, chunk, embedding)
        
        # Step 5: Semantic Search (Vector Search)
        print("Step 3: Performing semantic search on stored documents...")
        query_embedding = self.embedding_model.encode(query)
        candidate_docs = self.db_client.search_documents(query_embedding, top_k=25)
        if not candidate_docs:
            return None

        # Step 6: Reranking
        print("Step 4: Reranking search results...")
        reranked_docs = self.reranker_client.rerank(query, candidate_docs)
        if not reranked_docs:
             return None # Handle case where reranking might fail or return empty
        
        # Step 7: Context Selection and Formatting
        # Select the top 5 reranked documents for the final context
        top_5_reranked_docs = reranked_docs[:5]

        # This list of dictionaries will be used as the 'sources' in the final output.
        # It must match the Pydantic 'SearchResult' model.
        final_sources = [
            {
                "title": doc['title'],
                "url": doc['url'],
                "content": doc['content'],
                "score": doc.get('rerank_score', doc.get('similarity', 0)) # Use rerank_score if available, else similarity
            } for doc in top_5_reranked_docs
        ]
        
        # This list is specifically for the synthesis client, containing just what it needs
        synthesis_context_chunks = [
             {"content": doc['content'], "url": doc['url']} for doc in top_5_reranked_docs
        ]

        # Step 8: Synthesis
        print("Step 5: Synthesizing final answer...")
        synthesized_answer = self.synthesis_client.generate_response(
            query=query,
            context_chunks=synthesis_context_chunks
        )
        
        # This dictionary's structure must match the Pydantic 'ResearchOutput' model
        return {
            "synthesized_answer": synthesized_answer,
            "sources": final_sources
        }
