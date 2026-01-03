import os
import json
import glob
import time
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone

# Load environment variables
# Assuming the script is run from the project root, so app/.env is checking there.
# We also try to load from adjacent app/.env if run from script folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, 'app', '.env')

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback to just .env or app/.env relative to cwd
    load_dotenv(dotenv_path="app/.env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
INDEX_NAME = "college-consulting-index"

# Data directory configuration
# Assuming run from project root: app/data/json
DATA_DIR = os.path.join(project_root, 'app', 'data', 'json')
PROCESSED_LIST_FILE = os.path.join(DATA_DIR, "_processed_cds_lists.txt")

# Initialize Pinecone
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is not set in environment variables.")

pc = Pinecone(api_key=PINECONE_API_KEY)
# We assume the index already exists as per instructions.
index = pc.Index(INDEX_NAME)

# Initialize Gemini Embeddings via LangChain
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in environment variables.")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    output_dimensionality=768
)

def get_embedding(text: str) -> List[float]:
    """Generates embeddings for the given text using LangChain Google Generative AI."""
    if not text:
        return []
    try:
        return embeddings.embed_query(text)
    except Exception as e:
        print(f"Error embedding text: {e}")
        return []

def load_processed_files() -> set:
    """Loads the list of already processed files."""
    if not os.path.exists(PROCESSED_LIST_FILE):
        return set()
    with open(PROCESSED_LIST_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def mark_as_processed(filename: str):
    """Marks a file as processed by appending it to the list file."""
    # Ensure directory exists just in case
    os.makedirs(os.path.dirname(PROCESSED_LIST_FILE), exist_ok=True)
    with open(PROCESSED_LIST_FILE, 'a', encoding='utf-8') as f:
        f.write(filename + "\n")

def extract_structured_data(data: Any, filename: str) -> Any:
    """Extracts the relevant structured data from the raw JSON response."""
    structured_data = None
    
    # Structure 1: List of candidates with 'functionResponse' (완료된 응답)
    if isinstance(data, list):
        for item in data:
            parts = item.get('content', {}).get('parts', [])
            for part in parts:
                fn_response = part.get('functionResponse', {})
                if fn_response.get('name') == 'set_model_response':
                    return fn_response.get('response')
    
    # Structure 2: List of candidates with 'functionCall' (호출 시점에 저장된 경우)
    if isinstance(data, list):
        for item in data:
            parts = item.get('content', {}).get('parts', [])
            for part in parts:
                fn_call = part.get('functionCall', {})
                if fn_call.get('name') == 'set_model_response':
                    return fn_call.get('args')
    
    # Structure 3: Fallback, look for JSON string in 'text' parts
    if isinstance(data, list):
        for item in data:
            parts = item.get('content', {}).get('parts', [])
            for part in parts:
                text = part.get('text', '')
                if text.strip().startswith('{') and text.strip().endswith('}'):
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        continue
    
    # Structure 4: Maybe the file itself is the dict?
    if isinstance(data, dict):
        return data

    return None

def process_file(filepath: str, filename: str):
    print(f"Processing {filename}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        structured_data = extract_structured_data(data, filename)

        if not structured_data:
            print(f"Skipping {filename}: No structured data found.")
            return

        # Prepare vectors
        vectors = []
        source_file = structured_data.get('metadata', {}).get('source_file', filename)
        institution_name = structured_data.get('general_info', {}).get('institution_name', 'Unknown')
        
        # Keys to exclude from embedding directly as chunks (metadata is usually redundant as its own chunk)
        # But we surely want it as metadata for other chunks.
        
        for key, value in structured_data.items():
            if key == 'metadata':
                continue
            
            # Serialize the section to string
            chunk_text = json.dumps(value, ensure_ascii=False)
            
            embedding = get_embedding(chunk_text)
            if not embedding:
                print(f"  Warning: Failed to embed section '{key}'.")
                continue
            
            # Create a unique ID: filename + section key
            vector_id = f"{filename}#{key}"
            
            metadata = {
                "source_file": source_file,
                "institution_name": institution_name,
                "section": key,
                "text": chunk_text
            }
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
        
        if vectors:
            index.upsert(vectors=vectors)
            print(f"  Successfully upserted {len(vectors)} vectors for {filename}.")
            mark_as_processed(filename)
        else:
            print(f"  No vectors generated for {filename}.")

    except Exception as e:
        print(f"Error processing {filename}: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Starting Indexer Script...")
    processed_files = load_processed_files()
    
    # Glob pattern to find JSON files
    search_pattern = os.path.join(DATA_DIR, "*.json")
    json_files = glob.glob(search_pattern)
    
    print(f"Checking directory: {DATA_DIR}")
    print(f"Found {len(json_files)} JSON files in total.")
    print(f"Already processed: {len(processed_files)} files.")
    
    count = 0
    for filepath in json_files:
        filename = os.path.basename(filepath)
        if filename in processed_files:
            continue
            
        process_file(filepath, filename)
        count += 1
        # Simple rate limiting
        time.sleep(1)
        
    print(f"Indexing complete. Processed {count} new files.")

if __name__ == "__main__":
    main()
