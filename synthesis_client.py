import google.generativeai as genai 
from config import GOOGLE_API_KEY

# Configuring the API client with key
genai.configure(api_key=GOOGLE_API_KEY)

class SynthesisClient:
    def __init__(self, model_name = "gemini-2.5-flash"):
        '''
        Initializes the client with specific gemini model. 
        '''
        self.model = genai.GenerativeModel(model_name)

    def _build_prompt(self, query: str, context: list[str]) -> str:
        """
        This is the most critical part. It creates the instructions for the LLM.
        """
        #format the context with clear markers for the LLM to understand.
        context_str = "\n---\n".join(context)
        
        # Instruction prompt 
        prompt = f"""
        You are a helpful AI research assistant. Your primary task is to answer a user's query based *only* on the provided sources. Do not use any external knowledge.

        USER QUERY:
        "{query}"

        PROVIDED SOURCES:
        ---
        {context_str}
        ---

        INSTRUCTIONS:
        1.  Carefully read the USER QUERY and the PROVIDED SOURCES.
        2.  Synthesize a clear and concise answer to the query.
        3.  Your answer MUST be based exclusively on the information within the PROVIDED SOURCES.
        4.  For every sentence in your answer, you must add a citation referencing the source number. For example: "The sky is blue [1]." If a sentence is supported by two sources, cite both: "The sun is bright [1, 3]."
        5.  If the sources do not contain enough information to answer the query, you must explicitly state: "I cannot answer the query based on the provided sources."
        6.  Do not introduce any information that is not present in the sources.
        """
        return prompt

    def generate_response(self, query: str, context_chunks: list[dict]) -> str:
        """
        Takes the user query and the raw search results from Tavily,
        formats them, and gets a synthesized response from the LLM.
        """
        # We create a numbered list of the context to make citation simple.
        # The prompt will see "Source [1]: ...", "Source [2]: ...", etc.
        numbered_context = [
            f"Source [{i+1}] (URL: {chunk['url']}):\n{chunk['content']}" 
            for i, chunk in enumerate(context_chunks)
        ]
        
        prompt = self._build_prompt(query, numbered_context)
        
        try:
            # Send the prompt to the Gemini model
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"An error occurred while generating the response: {e}")
            # Provide a user-friendly error message
            return "An error occurred while synthesizing the answer. Please try again."