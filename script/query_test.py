"""
Pinecone Query Test Script
사용법: python script/query_test.py "하버드 학비 얼마야?"
"""
import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, 'app', '.env')

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv(dotenv_path="app/.env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
INDEX_NAME = "college-consulting-index"

# Initialize
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    output_dimensionality=768
)

def query_pinecone(query_text: str, top_k: int = 3):
    """Query Pinecone with a text query."""
    print(f"\n🔍 Query: {query_text}")
    print("-" * 50)
    
    # Generate embedding for query
    query_embedding = embeddings.embed_query(query_text)
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    print(f"\n📊 Top {top_k} Results:\n")
    for i, match in enumerate(results['matches'], 1):
        score = match['score']
        metadata = match['metadata']
        
        print(f"#{i} Score: {score:.4f}")
        print(f"   📁 Source: {metadata.get('source_file', 'N/A')}")
        print(f"   🏫 Institution: {metadata.get('institution_name', 'N/A')}")
        print(f"   📑 Section: {metadata.get('section', 'N/A')}")
        print(f"   📝 Text Preview: {metadata.get('text', 'N/A')[:200]}...")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Default test queries
        test_queries = [
            "하버드 학비 얼마야?",
            "스탠포드 합격률",
            "윌리엄스 입학 마감일",
        ]
        for q in test_queries:
            query_pinecone(q)
        sys.exit(0)
    
    query_pinecone(query)
