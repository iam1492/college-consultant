"""
Pinecone Query Tool for College Agent.

This tool searches college information from Pinecone vector database.
The query should already be in English (translated by query_analysis_agent).
"""

import os
import httpx
from typing import List
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
env_path = os.path.join(project_root, 'app', '.env')

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv(dotenv_path="app/.env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
INDEX_NAME = "college-consulting-index"


def _get_embedding(text: str) -> List[float]:
    """
    Generate embeddings using Gemini API via REST.
    
    Args:
        text: Text to generate embedding for.
        
    Returns:
        List of floats representing the embedding vector.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={GOOGLE_API_KEY}"
    payload = {
        "content": {"parts": [{"text": text}]},
        "output_dimensionality": 768
    }
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        return response.json()['embedding']['values']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []


def query_college_info(query: str, top_k: int = 5) -> str:
    """
    Search college information from Pinecone vector database.
    
    This tool searches for relevant college information based on the user's query.
    The query should already be optimized for RAG search (in English).
    
    Args:
        query: Optimized search query in English.
               This should be the analyzed and translated query from query_analysis_agent.
        top_k: Number of search results to return. Default is 5.
        
    Returns:
        A formatted string containing relevant college information from the search results.
        Each result includes the source file, institution name, section, and content.
    """
    print(f"🔍 Searching with query: {query}")
    
    # Generate embedding for the query
    query_embedding = _get_embedding(query)
    
    if not query_embedding:
        return "Failed to generate embedding for the query. Please try again."
    
    # Query Pinecone
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
    except Exception as e:
        return f"Error querying Pinecone: {e}"
    
    # Format and return results
    if not results['matches']:
        return "No relevant college information found for your query."
    
    formatted_results = []
    formatted_results.append(f"📊 Found {len(results['matches'])} relevant results:\n")
    
    for i, match in enumerate(results['matches'], 1):
        score = match['score']
        metadata = match['metadata']
        
        result_text = f"""
---
### Result #{i} (Relevance: {score:.2%})
- **Institution**: {metadata.get('institution_name', 'N/A')}
- **Section**: {metadata.get('section', 'N/A')}
- **Source**: {metadata.get('source_file', 'N/A')}

**Content**:
{metadata.get('text', 'N/A')}
"""
        formatted_results.append(result_text)
    
    return "\n".join(formatted_results)
