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
import httpx

# ... (API Keys setup is above)

def get_embedding(text: str) -> List[float]:
    """Generates embeddings using Gemini API via REST to support output_dimensionality."""
    if not text:
        return []
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={GOOGLE_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": {
            "parts": [{"text": text}]
        },
        "output_dimensionality": 768
    }
    
    try:
        # Using synchronous httpx for simplicity in this script
        response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        return result['embedding']['values']
    except Exception as e:
        print(f"Error embedding text: {e}")
        # Print detailed error if possible
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response: {response.text}")
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

def process_file(filepath: str, filename: str) -> bool:
    print(f"Processing {filename}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        structured_data = extract_structured_data(data, filename)

        if not structured_data:
            print(f"Skipping {filename}: No structured data found.")
            return False

        # Prepare vectors
        vectors = []
        source_file = structured_data.get('metadata', {}).get('source_file', filename)
        institution_name = structured_data.get('general_info', {}).get('institution_name', 'Unknown University')
        
        for key, value in structured_data.items():
            if key == 'metadata':
                continue
            
            # Convert section to natural language text
            chunk_text = format_section_to_text(institution_name, key, value)
            
            # if format_section_to_text returns empty (e.g. unknown key), fallback to JSON
            if not chunk_text:
                chunk_text = f"INFO FOR {institution_name} - SECTION {key}: " + json.dumps(value, ensure_ascii=False)

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
            print(f"  Successfully upserted {len(vectors)} vectors.")
            return True
        else:
            print(f"  No vectors generated for {filename}.")
            return False
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        # traceback.print_exc()
        return False

def format_section_to_text(institution_name: str, key: str, value: Any) -> str:
    """Converts a structured data section into a natural language string using templates."""
    
    if key == "general_info":
        return (
            f"General Information for {institution_name}:\n"
            f"- Institution Name: {value.get('institution_name', 'N/A')}\n"
            f"- Type: {value.get('school_type', 'N/A')}\n"
            f"- Category: {value.get('school_category', 'N/A')}\n"
            f"- Location: {value.get('city', 'N/A')}, {value.get('state', 'N/A')}\n"
            f"- Website: {value.get('website', 'N/A')}\n"
            f"- Academic Calendar: {value.get('academic_calendar', 'N/A')}"
        )

    elif key == "admission_factors":
        # Arrays to string
        very_imp = ", ".join(value.get('very_important', [])) or "None"
        imp = ", ".join(value.get('important', [])) or "None"
        cons = ", ".join(value.get('considered', [])) or "None"
        not_cons = ", ".join(value.get('not_considered', [])) or "None"
        
        return (
            f"Admission Factors for {institution_name}:\n"
            f"- Very Important: {very_imp}\n"
            f"- Important: {imp}\n"
            f"- Considered: {cons}\n"
            f"- Not Considered: {not_cons}"
        )

    elif key == "admissions_statistics":
        stats = value
        applicants = stats.get('applicants', {})
        admitted = stats.get('admitted', {})
        enrolled = stats.get('enrolled', {})
        waitlist = stats.get('waitlist', {})
        
        return (
            f"Admissions Statistics for {institution_name} ({stats.get('cohort_year', 'N/A')}):\n"
            f"- Acceptance Rate: {stats.get('acceptance_rate', 'N/A')}%\n"
            f"- Yield Rate: {stats.get('yield_rate', 'N/A')}%\n"
            f"- Total Applicants: {applicants.get('total', 'N/A')}\n"
            f"- Total Admitted: {admitted.get('total', 'N/A')}\n"
            f"- Total Enrolled: {enrolled.get('total', 'N/A')}\n"
            f"- Waitlist Policy: {'Yes' if waitlist.get('has_policy') else 'No'}\n"
            f"  * Offered Spot: {waitlist.get('offered_spot', 'N/A')}\n"
            f"  * Accepted Spot: {waitlist.get('accepted_spot', 'N/A')}\n"
            f"  * Admitted from Waitlist: {waitlist.get('admitted_from_waitlist', 'N/A')}"
        )

    elif key == "test_scores":
        sat = value.get('sat', {})
        act = value.get('act', {})
        
        return (
            f"Standardized Test Scores for {institution_name}:\n"
            f"- Policy: {value.get('policy', 'N/A')}\n"
            f"- SAT Submission Rate: {value.get('submission_rate_sat', 'N/A')}\n"
            f"- ACT Submission Rate: {value.get('submission_rate_act', 'N/A')}\n"
            f"- SAT Scores (25th-75th percentile):\n"
            f"  * Composite: {sat.get('composite_25th', 'N/A')} - {sat.get('composite_75th', 'N/A')}\n"
            f"  * Math: {sat.get('math_25th', 'N/A')} - {sat.get('math_75th', 'N/A')}\n"
            f"  * EBRW: {sat.get('ebrw_25th', 'N/A')} - {sat.get('ebrw_75th', 'N/A')}\n"
            f"- ACT Scores (25th-75th percentile):\n"
            f"  * Composite: {act.get('composite_25th', 'N/A')} - {act.get('composite_75th', 'N/A')}\n"
            f"  * Math: {act.get('math_25th', 'N/A')} - {act.get('math_75th', 'N/A')}\n"
            f"  * English: {act.get('english_25th', 'N/A')} - {act.get('english_75th', 'N/A')}"
        )

    elif key == "high_school_profile":
        return (
            f"High School Profile for {institution_name}:\n"
            f"- Average GPA: {value.get('average_gpa', 'N/A')}\n"
            f"- Percent in Top 10% of Class: {value.get('percent_top_10', 'N/A')}\n"
            f"- Percent in Top 25% of Class: {value.get('percent_top_25', 'N/A')}\n"
            f"- Percent in Top 50% of Class: {value.get('percent_top_50', 'N/A')}\n"
            f"- GPA Submission Rate: {value.get('gpa_submission_rate', 'N/A')}\n"
            f"- Class Rank Submission Rate: {value.get('class_rank_submission_rate', 'N/A')}"
        )

    elif key == "cost_and_financial_aid":
        expenses = value.get('expenses', {})
        aid = value.get('financial_aid', {})
        
        return (
            f"Cost and Financial Aid for {institution_name}:\n"
            f"- Tuition Structure: {value.get('tuition_structure', 'N/A')}\n"
            f"- Expenses (Annual):\n"
            f"  * Tuition (In-state): ${expenses.get('tuition_in_state', 'N/A')}\n"
            f"  * Tuition (Out-of-state): ${expenses.get('tuition_out_of_state', 'N/A')}\n"
            f"  * Fees: ${expenses.get('fees', 'N/A')}\n"
            f"  * Room and Board: ${expenses.get('room_and_board', 'N/A')}\n"
            f"  * Books and Supplies: ${expenses.get('books_and_supplies', 'N/A')}\n"
            f"  * Other Expenses: ${expenses.get('other_expenses', 'N/A')}\n"
            f"- Financial Aid:\n"
            f"  * International Students Eligible: {'Yes' if aid.get('international_students_eligible') else 'No'}\n"
            f"  * Average Need-based Package: ${aid.get('average_need_based_package', 'N/A')}\n"
            f"  * Percent of Need Met: {aid.get('percent_need_met', 'N/A')}"
        )

    elif key == "student_life_and_faculty":
        demo = value.get('demographics', {})
        return (
            f"Student Life and Faculty at {institution_name}:\n"
            f"- Student-Faculty Ratio: {value.get('student_faculty_ratio', 'N/A')}\n"
            f"- Undergraduate Enrollment: {value.get('undergraduate_enrollment', 'N/A')}\n"
            f"- Class Size under 20: {value.get('class_size_under_20_percent', 'N/A')}\n"
            f"- Demographics:\n"
            f"  * Out-of-state Students: {demo.get('out_of_state_percent', 'N/A')}\n"
            f"  * International Students: {demo.get('international_percent', 'N/A')}"
        )

    elif key == "deadlines":
        text = f"Application Deadlines for {institution_name}:\n"
        
        # Helper for deadline details
        def format_deadline(label, data):
            if not data: return ""
            return (
                f"- {label}:\n"
                f"  * Deadline: {data.get('deadline', 'N/A')}\n"
                f"  * Notification: {data.get('notification_date', 'N/A')}\n"
                f"  * Binding: {'Yes' if data.get('is_binding') else 'No'}\n"
                f"  * Type: {data.get('type', 'N/A')}\n"
            )

        text += format_deadline("Early Decision 1", value.get('early_decision_1'))
        text += format_deadline("Early Decision 2", value.get('early_decision_2'))
        text += format_deadline("Early Action", value.get('early_action'))
        text += format_deadline("Regular Decision", value.get('regular_decision'))
        
        transfer = value.get('transfer_admission', {})
        if transfer:
             text += (
                f"- Transfer Admission:\n"
                f"  * Deadline: {transfer.get('deadline', 'N/A')}\n"
                f"  * Rolling: {'Yes' if transfer.get('is_rolling') else 'No'}\n"
            )
        return text

    return ""

def main():
    print("Starting Indexer Script...")
    
    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory not found at {DATA_DIR}")
        return

    print(f"Checking directory: {DATA_DIR}")
    
    # Check if we should re-process all files
    # If the user wants to re-process, they should empty the list file manually or we can do it here if needed.
    # For now, we respect the existing logic.

    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    print(f"Found {len(files)} JSON files in total.")
    
    processed_files = load_processed_files()
    print(f"Already processed: {len(processed_files)} files.")
    
    new_files_count = 0
    
    for filename in files:
        if filename in processed_files:
            continue
            
        if process_file(os.path.join(DATA_DIR, filename), filename):
            mark_as_processed(filename)
            new_files_count += 1
        
    print(f"Indexing complete. Processed {new_files_count} new files.")

if __name__ == "__main__":
    main()
