from sentence_transformers import SentenceTransformer, util
import numpy as np
import os
import json
from datetime import datetime, timezone

from structure_extractor import extract_structure
from utils import create_sample_pdfs

# --- Model Pre-loading and Caching ---
model_name = 'all-MiniLM-L6-v2'
model_path = './model'


if not os.path.exists(model_path):
    print(f"Model not found locally. Downloading and saving '{model_name}' to '{model_path}'...")
    model = SentenceTransformer(model_name)
    model.save(model_path)
    print("Model saved successfully.")
# --- End of model pre-loading section ---


def find_relevant_sections(pdf_paths: list, persona: str, job_to_be_done: str) -> dict:
    """
    Acts as an intelligent document analyst to find the most relevant sections.
    """
    try:
        model = SentenceTransformer(model_path)
    except Exception as e:
        return {"error": f"Failed to load model from '{model_path}'. Ensure the model exists. Error: {e}"}
    
    query = f"Persona: {persona}. Task: {job_to_be_done}"
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    all_chunks = []

    for pdf_path in pdf_paths:
        structure = extract_structure(pdf_path)
        if "error" in structure:
            print(f"Skipping file due to error: {structure['error']}")
            continue

        raw_blocks_by_page = structure["raw_blocks"]
        headings = [{"text": structure["title"], "page": 1, "bbox": (0,0,0,90)}] + structure["outline"]
        
        for i, heading in enumerate(headings):
            page_idx = heading["page"] - 1
            if page_idx >= len(raw_blocks_by_page):
                continue
            page_blocks = raw_blocks_by_page[page_idx]
            
            heading_y_pos = heading["bbox"][1]
            
            next_heading_y_pos = float('inf')
            if i + 1 < len(headings) and headings[i+1]["page"] == heading["page"]:
                next_heading_y_pos = headings[i+1]["bbox"][1]
            
            content_blocks = [
                block[4].replace('\n', ' ').strip() for block in page_blocks 
                if block[1] > heading_y_pos and block[1] < next_heading_y_pos and block[4].strip()
            ]
            
            full_content = heading["text"] + "\n" + "\n".join(content_blocks)
            
            all_chunks.append({
                "document": os.path.basename(pdf_path),
                "page": heading["page"],
                "section_title": heading["text"],
                "content": full_content,
                "content_blocks": content_blocks
            })

    if not all_chunks:
        return {"error": "Could not extract any content from the documents."}
        
    chunk_contents = [chunk["content"] for chunk in all_chunks]
    chunk_embeddings = model.encode(chunk_contents, convert_to_tensor=True)
    
    similarities = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
    
    ranked_chunks = sorted(zip(similarities.tolist(), all_chunks), key=lambda x: x[0], reverse=True)
    
    extracted_sections = []
    sub_section_analysis = []
    
    for i, (score, chunk) in enumerate(ranked_chunks[:5]):
        extracted_sections.append({
            "document": chunk["document"], "page_number": chunk["page"],
            "section_title": chunk["section_title"], "importance_rank": i + 1
        })
        
        section_text = " ".join(chunk["content_blocks"])
        sentences = section_text.split('. ')
        sentences = [s.strip() + '.' for s in sentences if len(s.strip().split()) > 5]
        
        if sentences:
            sent_embeddings = model.encode(sentences, convert_to_tensor=True)
            sent_similarities = util.pytorch_cos_sim(query_embedding, sent_embeddings)[0]
            most_relevant_sentence = sentences[np.argmax(sent_similarities.cpu().numpy())]
            sub_section_analysis.append({
                "document": chunk["document"], "page_number": chunk["page"],
                "refined_text": most_relevant_sentence
            })
        else:
            sub_section_analysis.append({
                "document": chunk["document"], "page_number": chunk["page"],
                "refined_text": chunk["section_title"]
            })

    return {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in pdf_paths],
            "persona": persona, "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now(timezone.utc).isoformat()
        },
        "extracted_sections": extracted_sections,
        "sub_section_analysis": sub_section_analysis
    }

if __name__ == '__main__':
    create_sample_pdfs()
    
    print("\n--- Running Task 1B: Persona-Driven Intelligence ---")

    pdf_paths_1b = ["gnn_report.pdf", "business_report.pdf"]
    persona_1b = "An investment analyst with expertise in the tech sector."
    job_1b = "Analyze revenue trends and R&D investments to understand market positioning."

    analysis_data = find_relevant_sections(pdf_paths_1b, persona_1b, job_1b)
    
    output_filename = "challenge1b_output.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=4)

    print(f"Successfully performed analysis and saved to '{output_filename}'")
    print("\n--- Analysis Report ---")
    print(json.dumps(analysis_data, indent=2))





# from sentence_transformers import SentenceTransformer, util
# import numpy as np
# import os
# import json
# from datetime import datetime, timezone

# from task_1a import extract_structure
# from utils import create_sample_pdfs

# def find_relevant_sections(pdf_paths: list, persona: str, job_to_be_done: str) -> dict:
#     """
#     Acts as an intelligent document analyst to find the most relevant sections.
#     """
#     try:
#         model = SentenceTransformer('all-MiniLM-L6-v2')
#     except Exception as e:
#         return {"error": f"Failed to load SentenceTransformer model. Error: {e}"}
    
#     query = f"Persona: {persona}. Task: {job_to_be_done}"
#     query_embedding = model.encode(query, convert_to_tensor=True)
    
#     all_chunks = []

#     for pdf_path in pdf_paths:
#         structure = extract_structure(pdf_path)
#         if "error" in structure:
#             print(f"Skipping file due to error: {structure['error']}")
#             continue

#         raw_blocks_by_page = structure["raw_blocks"]
#         headings = [{"text": structure["title"], "page": 1, "bbox": (0,0,0,90)}] + structure["outline"]
        
#         for i, heading in enumerate(headings):
#             page_idx = heading["page"] - 1
#             if page_idx >= len(raw_blocks_by_page):
#                 continue
#             page_blocks = raw_blocks_by_page[page_idx]
            
#             heading_y_pos = heading["bbox"][1]
            
#             next_heading_y_pos = float('inf')
#             if i + 1 < len(headings) and headings[i+1]["page"] == heading["page"]:
#                 next_heading_y_pos = headings[i+1]["bbox"][1]
            
#             content_blocks = [
#                 block[4].replace('\n', ' ').strip() for block in page_blocks 
#                 if block[1] > heading_y_pos and block[1] < next_heading_y_pos and block[4].strip()
#             ]
            
#             full_content = heading["text"] + "\n" + "\n".join(content_blocks)
            
#             all_chunks.append({
#                 "document": os.path.basename(pdf_path),
#                 "page": heading["page"],
#                 "section_title": heading["text"],
#                 "content": full_content,
#                 "content_blocks": content_blocks
#             })

#     if not all_chunks:
#         return {"error": "Could not extract any content from the documents."}
        
#     chunk_contents = [chunk["content"] for chunk in all_chunks]
#     chunk_embeddings = model.encode(chunk_contents, convert_to_tensor=True)
    
#     similarities = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
    
#     ranked_chunks = sorted(zip(similarities.tolist(), all_chunks), key=lambda x: x[0], reverse=True)
    
#     extracted_sections = []
#     sub_section_analysis = []
    
#     for i, (score, chunk) in enumerate(ranked_chunks[:5]):
#         extracted_sections.append({
#             "document": chunk["document"], "page_number": chunk["page"],
#             "section_title": chunk["section_title"], "importance_rank": i + 1
#         })
        
#         # --- FINAL FIX: Join all content blocks before sentence analysis ---
#         # This creates a complete text for the section, preventing truncation.
#         section_text = " ".join(chunk["content_blocks"])
        
#         sentences = section_text.split('. ')
#         sentences = [s.strip() + '.' for s in sentences if len(s.strip().split()) > 5]
        
#         if sentences:
#             sent_embeddings = model.encode(sentences, convert_to_tensor=True)
#             sent_similarities = util.pytorch_cos_sim(query_embedding, sent_embeddings)[0]
#             most_relevant_sentence = sentences[np.argmax(sent_similarities.cpu().numpy())]
#             sub_section_analysis.append({
#                 "document": chunk["document"], "page_number": chunk["page"],
#                 "refined_text": most_relevant_sentence
#             })
#         else:
#             sub_section_analysis.append({
#                 "document": chunk["document"], "page_number": chunk["page"],
#                 "refined_text": chunk["section_title"]
#             })

#     return {
#         "metadata": {
#             "input_documents": [os.path.basename(p) for p in pdf_paths],
#             "persona": persona, "job_to_be_done": job_to_be_done,
#             "processing_timestamp": datetime.now(timezone.utc).isoformat()
#         },
#         "extracted_sections": extracted_sections,
#         "sub_section_analysis": sub_section_analysis
#     }

# if __name__ == '__main__':
#     create_sample_pdfs()
    
#     print("\n--- Running Task 1B: Persona-Driven Intelligence ---")

#     pdf_paths_1b = ["gnn_report.pdf", "business_report.pdf"]
#     persona_1b = "An investment analyst with expertise in the tech sector."
#     job_1b = "Analyze revenue trends and R&D investments to understand market positioning."

#     analysis_data = find_relevant_sections(pdf_paths_1b, persona_1b, job_1b)
    
#     output_filename = "challenge1b_output.json"
#     with open(output_filename, 'w', encoding='utf-8') as f:
#         json.dump(analysis_data, f, indent=4)

#     print(f"Successfully performed analysis and saved to '{output_filename}'")
#     print("\n--- Analysis Report ---")
#     print(json.dumps(analysis_data, indent=2))
