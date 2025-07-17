# main.py (Final Hand-off Version)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Import the high-level components we need
from research_agent import ResearchAgent
from cache_client import CacheClient
from search_client import SearchEngine

# --- Pydantic Models (Defines the structured JSON output) ---
class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: float = 0

class ResearchOutput(BaseModel):
    synthesized_answer: str
    sources: List[SearchResult] 

class ResearchResponse(BaseModel):
    query: str
    result: ResearchOutput

# --- App and Client Instances ---
app = FastAPI(
    title="AI Research Assistant",
    description="An API for a RAG pipeline with search, reranking, and synthesis.",
    version="3.5.0" # Versioning as a polished Level 3
)

cache_client = CacheClient()
research_agent = ResearchAgent()

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "online", "pipeline_version": "3.5"}

# A simple search endpoint for debugging, hidden from the main public docs.
@app.get("/search", include_in_schema=False)
def perform_simple_search(q: str):
    search_engine = SearchEngine()
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return search_engine.search(query=q)

@app.post("/research", response_model=ResearchResponse)
async def research_endpoint(q: str):
    """
    Takes a query, runs it through the full RAG pipeline (Search -> Extract ->
    Chunk -> Vectorize -> Rerank -> Synthesize), and returns a
    synthesized answer with structured source information.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    # 1. Check Cache
    cached_result = cache_client.get(q)
    if cached_result:
        print(f"CACHE HIT: {q}")
        return ResearchResponse(query=q, result=ResearchOutput(**cached_result))
    
    # 2. Run the ResearchAgent's pipeline if Cache Miss
    print(f"PIPELINE START: {q}")
    research_result_data = await research_agent.run(query=q)
    if not research_result_data:
        raise HTTPException(status_code=500, detail="Research pipeline failed to produce a result.")
        
    research_output = ResearchOutput(**research_result_data)
    
    # 3. Store the new result in the Cache
    cache_client.set(q, research_output.model_dump())
    
    return ResearchResponse(query=q, result=research_output)