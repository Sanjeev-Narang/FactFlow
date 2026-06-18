import os
import requests
from decouple import config

class TavilySearchService:
    def __init__(self):
        self.api_key = config("TAVILY_API_KEY", default=os.environ.get('TAVILY_API_KEY'))
        self.base_url = "https://api.tavily.com/search"

    def fetch_web_snippets(self, claim: str) -> str:
        """Searches the live web using Tavily and returns consolidated snippets."""
        # Tavily expects api_key in the payload body
        payload = {
            "api_key": self.api_key,
            "query": claim,
            "search_depth": "basic", 
            "max_results": 5,
            "include_answer": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            snippets = [f"- {r.get('title')}: {r.get('content')}" for r in results]
            
            return "\n".join(snippets) if snippets else "No relevant web results found."
            
        except requests.RequestException as e:
            return f"Search failed: {str(e)}"
