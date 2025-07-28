import os
import json
import datetime
from pdf_processor import extract_content_from_pdf
from relevance_engine import RelevanceEngine

# --- Configuration ---
# Detects if running in Docker and sets paths accordingly.
IS_DOCKER = os.path.exists("/app/input")
INPUT_DIR = "/app/input" if IS_DOCKER else "test_run/input"
OUTPUT_DIR = "/app/output" if IS_DOCKER else "test_run/output"
MODEL_PATH = "/app/models" if IS_DOCKER else "models/"
PDFS_DIR = os.path.join(INPUT_DIR, "PDFs")

# --- Stop list for filtering out generic, unhelpful section titles ---
GENERIC_TITLE_STOP_LIST = {
    "introduction", "conclusion", "abstract", "references", "contents",
    "acknowledgements", "appendix", "summary", "methodology", "discussion",
    "results", "background", "methods"
}

def generate_output_json(ranked_paragraphs: list, page_content_map: dict, input_data: dict, output_path: str):
    """
    Formats the top 5 ranked results into the required JSON structure,
    applying advanced filtering for high-quality section titles.
    """
    print("\n--- Phase 4: Generating Final JSON with Advanced Title Filtering ---")

    # --- 1. Sub-section Analysis: Top 5 most relevant paragraphs ---
    sub_sections = []
    # Strictly take the top 5 most relevant paragraphs from the entire collection
    for para in ranked_paragraphs[:5]:
        sub_sections.append({
            "Document": para['doc_name'],
            "Refined Text": para['text'], # This is the full, original paragraph text
            "Page Number": para['page_num']
        })

    # --- 2. Extracted Section Analysis: Top 5 most relevant unique sections ---
    extracted_sections = []
    seen_sections = set()
    rank = 1
    
    for para in ranked_paragraphs:
        # Stop once we have found 5 unique sections
        if len(extracted_sections) >= 5:
            break

        section_id = (para['doc_name'], para['page_num'])
        if section_id not in seen_sections:
            page_titles = page_content_map.get(section_id, {}).get('titles', [])
            
            # --- Advanced Title Selection Logic ---
            best_title = None
            for title in page_titles:
                # Rule 1: Must be a short title
                if len(title.split()) > 8:
                    continue
                # Rule 2: Must not be in our generic stop list (case-insensitive)
                if title.lower().strip() in GENERIC_TITLE_STOP_LIST:
                    continue
                # Rule 3: Must not contain a colon
                if ':' in title:
                    continue
                
                # If it passes all checks, it's a good title.
                best_title = title
                break  # We found a good one, so we stop looking.
            
            # If no suitable title was found, create a smart fallback from the relevant text.
            if not best_title:
                fallback_title = ' '.join(para['text'].split()[:7]) + "..."
                best_title = fallback_title

            extracted_sections.append({
                "Document": para['doc_name'],
                "Section title": best_title,
                "Importance_rank": rank,
                "Page number": para['page_num']
            })
            
            seen_sections.add(section_id)
            rank += 1

    # --- 3. Construct the final JSON object ---
    output_data = {
        "Metadata": {
            "Input documents": [os.path.basename(f) for f in os.listdir(PDFS_DIR) if f.lower().endswith('.pdf')],
            "Persona": input_data.get("persona", {}),
            "Job to be done": input_data.get("job_to_be_done", {}),
            "Processing timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        },
        "Extracted Section": extracted_sections,
        "Sub-section Analysis": sub_sections
    }

    # --- 4. Write the JSON file ---
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Successfully wrote Top 5 results to {output_path}")


def process_documents():
    """
    Main orchestration function: reads data, processes PDFs, ranks content,
    and generates the final output file.
    """
    print(f"--- Starting Pipeline (Environment: {'Docker' if IS_DOCKER else 'Local'}) ---")
    
    # Read the main input file
    input_json_path = os.path.join(INPUT_DIR, "input.json")
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: input.json not found at {input_json_path}"); return

    # Process all PDFs to extract titles and paragraphs
    all_paragraphs, page_content_map = [], {}
    pdf_files = [os.path.join(PDFS_DIR, f) for f in os.listdir(PDFS_DIR) if f.lower().endswith('.pdf')]
    for pdf_path in pdf_files:
        print(f"Processing: {os.path.basename(pdf_path)}")
        document_content = extract_content_from_pdf(pdf_path)
        for page_data in document_content:
            all_paragraphs.extend(page_data['paragraphs'])
            map_key = (page_data['doc_name'], page_data['page_num'])
            page_content_map[map_key] = page_data
    
    print(f"\nTotal paragraphs extracted for ranking: {len(all_paragraphs)}")
    if not all_paragraphs:
        print("No content extracted. Writing an empty output file.")
        generate_output_json([], {}, input_data, os.path.join(OUTPUT_DIR, "output.json")); return

    # Rank the extracted paragraphs based on relevance
    try:
        engine = RelevanceEngine(model_path=MODEL_PATH)
        persona = input_data.get("persona", {})
        job_to_be_done = input_data.get("job_to_be_done", {})
        ranked_paragraphs = engine.rank_chunks(all_paragraphs, persona, job_to_be_done)
    except Exception as e:
        print(f"An error occurred during relevance ranking: {e}"); return

    # Generate the final JSON output file from the ranked results
    output_file_path = os.path.join(OUTPUT_DIR, "output.json")
    generate_output_json(ranked_paragraphs, page_content_map, input_data, output_file_path)


if __name__ == "__main__":
    process_documents()