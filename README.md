# Linsight-3.5

# AI Research Assistant - RAG Pipeline (v3.5)

This repository contains the backend service for an AI Research Assistant. It implements a sophisticated Retrieval-Augmented Generation (RAG) pipeline designed to answer user queries by synthesizing information from real-time web search results.

This version (3.5) represents a robust, non-agentic pipeline that focuses on high-quality information retrieval through a multi-stage process including vector search and relevance reranking.

## Core Features

-   **Real-time Web Search:** Uses the Tavily Search API to fetch up-to-date information from the web.
-   **Full Content Extraction:** Pulls the full text content from source URLs for deep analysis, not just snippets.
-   **Semantic Search:** Chunks documents and uses a vector database (`PostgreSQL` with `pgvector`) to find the most semantically relevant passages.
-   **Relevance Reranking:** Employs a Cross-Encoder model to re-rank the semantically similar passages, ensuring the most directly relevant context is prioritized.
-   **LLM Synthesis:** Uses Google's Gemini model to generate a coherent, synthesized answer based *only* on the provided, high-quality context.
-   **Source Citation:** Automatically includes citations in the response, linking back to the original source documents.
-   **Caching:** Uses Redis to cache results for repeated queries, improving speed and reducing API costs.

---

## Project Architecture & Data Flow

The system is a containerized application managed by Docker Compose, consisting of three main services: the Python API, a PostgreSQL database, and a Redis cache.

The RAG pipeline follows these steps when a query is received at the `/research` endpoint:

1.  **Cache Check:** Redis is checked to see if a result for this exact query already exists. If yes, it's returned immediately.
2.  **Initial Retrieval:** The `SearchEngine` calls the Tavily API to get a list of relevant web pages.
3.  **Content Processing:**
    -   The `ResearchAgent` downloads the full text from each source URL using `trafilatura`.
    -   The text is split into smaller, manageable chunks using `langchain-text-splitters`.
4.  **Embedding & Storage:**
    -   Each chunk is converted into a vector embedding using a `sentence-transformers` model.
    -   The chunk's text, source URL, title, and vector embedding are stored in the PostgreSQL (`pgvector`) database.
5.  **Semantic Search:** The user's query is also embedded, and a vector similarity search is performed against the database to retrieve the top 25 most relevant chunks.
6.  **Reranking:** The `RerankerClient` takes these 25 candidate chunks and uses a Cross-Encoder model to re-score and re-sort them based on direct relevance to the query.
7.  **Synthesis:** The top 5 reranked chunks are selected as the final context. This context, along with the original query and a carefully crafted prompt, is sent to the `SynthesisClient` (using the Gemini API).
8.  **Final Response & Caching:** The synthesized answer and structured source information are formatted into a JSON object, stored in the Redis cache for future requests, and returned to the user.

---

## Technology Stack

-   **Backend Framework:** FastAPI
-   **Web Search:** Tavily Search API
-   **LLM for Synthesis:** Google Gemini
-   **Vector Database:** PostgreSQL with the `pgvector` extension
-   **Embedding Model:** `all-MiniLM-L6-v2` (from `sentence-transformers`)
-   **Reranker Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2` (from `sentence-transformers`)
-   **Caching:** Redis
-   **Containerization:** Docker & Docker Compose

---

## Setup and Installation

### Prerequisites

-   Docker and Docker Compose installed on your local machine.
-   Git installed.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Pranjalpok7/AI-research-assistant.git
cd AI-research-assistant
```

### Step 2: Configure Environment Variables

The application requires API keys for Tavily and Google Gemini.

1.  In the root of the project, find the file `.env.example` (or create a new file named `.env`).
2.  Rename it to `.env`.
3.  Open the `.env` file and add your secret keys:

    ```
    TAVILY_API_KEY="your_tavily_api_key_here"
    GOOGLE_API_KEY="your_google_gemini_api_key_here"
    ```

### Step 3: Build and Run the Application

This single command will build the custom Docker image for the API, download the images for PostgreSQL and Redis, and start all three services in a networked environment.

```bash
docker compose up --build
```

-   The first time you run this, it will take several minutes to download the models and build the container. Subsequent runs will be much faster.
-   The services will run in the foreground, and you will see logs from all containers in your terminal.
-   To stop all services, press `Ctrl + C` in the terminal where they are running.

---

## How to Use the API

Once the application is running, the API is available at `http://localhost:8000`.

### Interactive Documentation (Swagger UI)

The best way to interact with the API is through the automatically generated documentation.

1.  Open your web browser and navigate to **`http://localhost:8000/docs`**.

2.  You will see the interactive Swagger UI. Find the `/research` endpoint.

3.  Click on the `/research` endpoint to expand it, then click the **"Try it out"** button.

4.  In the `q` parameter field, enter your research query (e.g., "What is the difference between supervised and unsupervised machine learning?").

5.  Click the **"Execute"** button.

### Example Response

The API will return a structured JSON object like this:

```json
{
  "query": "What is the difference between supervised and unsupervised machine learning?",
  "result": {
    "synthesized_answer": "Supervised learning involves training a model on labeled data, where both the input and the desired output are known... [1]. In contrast, unsupervised learning works with unlabeled data, and the model tries to find patterns and structures on its own... [3, 4].",
    "sources": [
      {
        "title": "A Guide to Machine Learning - TechCrunch",
        "url": "https://techcrunch.com/...",
        "content": "Supervised learning is a task-driven process...",
        "score": 9.123
      },
      // ... 4 more source objects
    ]
  }
}
```

---
## Project File Structure

A brief overview of the key files in this project:

-   `main.py`: The entry point for the FastAPI application. Defines the API endpoints.
-   `research_agent.py`: The core orchestrator for the RAG pipeline.
-   `search_client.py`: Manages communication with the Tavily Search API.
-   `synthesis_client.py`: Manages communication with the Google Gemini API.
-   `reranker_client.py`: Handles the relevance reranking logic.
-   `db_client.py`: Manages all communication with the PostgreSQL database.
-   `cache_client.py`: Manages all communication with the Redis cache.
-   `Dockerfile`: Instructions for building the Python API container.
-   `docker-compose.yml`: Defines and orchestrates all the services (`api`, `db`, `redis`).
-   `init.sql`: A setup script to enable the `pgvector` extension in the database on first run.
-   `requirements.txt`: A list of all the Python dependencies.

---

You can now commit this `README.md` file to your GitHub repository. It will be the first thing your friend sees, and it should give them everything they need to get up and running smoothly.
