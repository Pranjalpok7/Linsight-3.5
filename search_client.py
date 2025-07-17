from tavily import TavilyClient
from config import TAVILY_API_KEY

class SearchEngine:
    def __init__(self):
        if not TAVILY_API_KEY:
            raise ValueError("Tavily API key is not set.")
        self.client = TavilyClient(api_key=TAVILY_API_KEY)

    def search(self,query: str, max_results: int=5):
        '''
        Performs a search using Tavily API
        '''
        try:
            # For now, only basic search
            # 'include_answer' would use LLM, which we'll save
            # for later
            response = self.client.search(
                query=query,
                search_depth= "basic",
                max_results=max_results
            )
            return response['results']
        except Exception as e:
            print(f"An error occurred during search: {e}")
            return []


'''
if __name__ == "__main__":
    engine = SearchEngine()
    query = input("Enter your search query: ")
    results = engine.search(query)

    for idx, result in enumerate(results, start=1):
        print(f"\nResult {idx}:")
        print(f"Title: {result.get('title')}")
        print(f"URL: {result.get('url')}")
        print(f"Content: {result.get('content')[:200]}...")
'''