import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector
import numpy as np

class DBClient:
    def __init__(self, db_name="ai_research_db", user="user", password="password", host="db", port="5432"):
        """
        Initializes the database client and connects to the database.
        The vector extension is enabled by the init.sql script via Docker Compose.
        """
        self.conn_str = f"dbname='{db_name}' user='{user}' password='{password}' host='{host}' port='{port}'"
        
        try:
            self.conn = psycopg2.connect(self.conn_str)
        except psycopg2.OperationalError as e:
            print(f"Could not connect to the database: {e}")
            raise

        register_vector(self.conn)
        self.create_table()

    def create_table(self):
        """
        Creates the 'documents' table if it doesn't already exist.
        Now includes a 'title' column to preserve metadata.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                url TEXT,
                title TEXT,
                content TEXT,
                embedding VECTOR(384)
            );
            """)
            self.conn.commit()

    def insert_document(self, url: str, title: str, content: str, embedding: np.ndarray):
        """
        Inserts a document chunk, including its title and vector embedding.
        """
        embedding_list = embedding.tolist()
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (url, title, content, embedding) VALUES (%s, %s, %s, %s)",
                (url, title, content, embedding_list)
            )
            self.conn.commit()

    def search_documents(self, query_embedding: np.ndarray, top_k: int = 25) -> list[dict]:
        """
        Performs a semantic search, retrieving the title along with other data.
        """
        query_embedding_list = query_embedding.tolist()
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                "SELECT url, title, content, 1 - (embedding <=> %s::vector) AS similarity FROM documents ORDER BY embedding <=> %s::vector LIMIT %s",
                (query_embedding_list, query_embedding_list, top_k)
            )
            results = cur.fetchall()
            return [dict(row) for row in results]

    def clear_documents(self):
        """
        Clears the 'documents' table for a new research query.
        """
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE documents RESTART IDENTITY;")
            self.conn.commit()