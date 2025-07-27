import fitz  # PyMuPDF
import json
import os
import re
import statistics
from collections import defaultdict
from utils import create_sample_pdfs

def analyze_font_profile(doc):
    """
    Performs a baseline pass to determine the most common font size (body text).
    """
    font_sizes = defaultdict(int)
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block.get("lines"):
                for line in block["lines"]:
                    if line.get("spans"):
                        for span in line["spans"]:
                            font_sizes[round(span["size"])] += len(span["text"].strip())
    
    if not font_sizes:
        return 12.0

    return float(max(font_sizes, key=font_sizes.get))

def classify_headings(scored_headings):
    """
    Classifies scored headings into Title, H1, H2, H3 using a more robust method.
    """
    if not scored_headings:
        return "Untitled Document", []

    title_info = scored_headings.pop(0)
    title = title_info['text']
    
    if not scored_headings:
        return title, []

    size_groups = defaultdict(list)
    for h in scored_headings:
        size_groups[h['size']].append(h)

    sorted_sizes = sorted(size_groups.keys(), reverse=True)
    
    outline = []
    level_map = {0: "H1", 1: "H2", 2: "H3"}

    for i, size in enumerate(sorted_sizes):
        level = level_map.get(i, "H3")
        for h in size_groups[size]:
            # Include the bbox for task_1b to use
            outline.append({"level": level, "text": h["text"], "page": h["page"], "bbox": h["bbox"]})
            
    return title, outline

def extract_structure(pdf_path: str) -> dict:
    """
    Main function to orchestrate the PDF structure extraction process.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {"error": f"Could not open or process PDF {pdf_path}: {e}"}

    body_text_size = analyze_font_profile(doc)
    
    potential_headings = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0 and block.get("lines") and len(block.get("lines")) == 1:
                line = block["lines"][0]
                full_block_text = " ".join(span["text"] for span in line["spans"]).strip().replace("ﬁ", "fi").replace("ﬂ", "fl")

                if not full_block_text or len(full_block_text.split()) > 15:
                    continue
                
                first_span = line["spans"][0]
                font_size = round(first_span["size"])
                is_bold = "bold" in first_span["font"].lower()

                score = 1.0
                if font_size > body_text_size:
                    score *= (font_size / body_text_size)
                if is_bold:
                    score *= 1.2
                if re.match(r'^((\d+\.)*\d+|[A-Z]\.)\s', full_block_text):
                    score *= 1.5
                if full_block_text.endswith('.'):
                    score *= 0.8

                if score > 1.25:
                    potential_headings.append({
                        "score": score, "text": full_block_text, "size": font_size,
                        "page": page_num + 1, "bbox": block["bbox"]
                    })

    sorted_headings = sorted(potential_headings, key=lambda x: x["score"], reverse=True)
    
    title, outline = classify_headings(sorted_headings)
    
    if not title and doc.metadata.get('title'):
        title = doc.metadata['title']

    final_outline = sorted(outline, key=lambda x: (x["page"], x["bbox"][1]))
    
    # Store the raw blocks for task_1b to use
    all_blocks = [page.get_text("blocks") for page in doc]
    doc.close()
    
    return {"title": title, "outline": final_outline, "raw_blocks": all_blocks}


if __name__ == '__main__':
    create_sample_pdfs()
    
    pdf_to_process = "gnn_report.pdf"
    print(f"\n--- Running Task 1A: Structure Extraction for '{pdf_to_process}' ---")
    
    structure_data = extract_structure(pdf_to_process)
    
    # Remove the temporary 'bbox' key before final output
    clean_outline = []
    for item in structure_data.get("outline", []):
        clean_item = item.copy()
        clean_item.pop("bbox", None)
        clean_outline.append(clean_item)

    output_json = {
        "title": structure_data.get("title", ""),
        "outline": clean_outline
    }

    output_filename = f"{os.path.splitext(pdf_to_process)[0]}_outline.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_json, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully extracted structure and saved to '{output_filename}'")
    print("\n--- Extracted Data ---")
    print(json.dumps(output_json, indent=2))










# import fitz  # PyMuPDF
# import json
# import os
# import re
# import statistics
# from collections import defaultdict
# from utils import create_sample_pdfs

# def analyze_font_profile(doc):
#     """
#     Performs a baseline pass to determine the most common font size (body text).
#     """
#     font_sizes = defaultdict(int)
#     for page in doc:
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             if block.get("lines"):
#                 for line in block["lines"]:
#                     if line.get("spans"):
#                         for span in line["spans"]:
#                             font_sizes[round(span["size"])] += len(span["text"].strip())
    
#     if not font_sizes:
#         return 12.0

#     return float(max(font_sizes, key=font_sizes.get))

# def classify_headings(scored_headings):
#     """
#     Classifies scored headings into Title, H1, H2, H3 using a more robust method.
#     """
#     if not scored_headings:
#         return "Untitled Document", []

#     title_info = scored_headings.pop(0)
#     title = title_info['text']
    
#     if not scored_headings:
#         return title, []

#     size_groups = defaultdict(list)
#     for h in scored_headings:
#         size_groups[h['size']].append(h)

#     sorted_sizes = sorted(size_groups.keys(), reverse=True)
    
#     outline = []
#     level_map = {0: "H1", 1: "H2", 2: "H3"}

#     for i, size in enumerate(sorted_sizes):
#         level = level_map.get(i, "H3")
#         for h in size_groups[size]:
#             # Include the bbox for task_1b to use
#             outline.append({"level": level, "text": h["text"], "page": h["page"], "bbox": h["bbox"]})
            
#     return title, outline

# def extract_structure(pdf_path: str) -> dict:
#     """
#     Main function to orchestrate the PDF structure extraction process.
#     """
#     try:
#         doc = fitz.open(pdf_path)
#     except Exception as e:
#         return {"error": f"Could not open or process PDF {pdf_path}: {e}"}

#     body_text_size = analyze_font_profile(doc)
    
#     potential_headings = []
#     for page_num, page in enumerate(doc):
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             if block['type'] == 0 and block.get("lines") and len(block.get("lines")) == 1:
#                 line = block["lines"][0]
#                 full_block_text = " ".join(span["text"] for span in line["spans"]).strip().replace("ﬁ", "fi").replace("ﬂ", "fl")

#                 if not full_block_text or len(full_block_text.split()) > 15:
#                     continue
                
#                 first_span = line["spans"][0]
#                 font_size = round(first_span["size"])
#                 is_bold = "bold" in first_span["font"].lower()

#                 score = 1.0
#                 if font_size > body_text_size:
#                     score *= (font_size / body_text_size)
#                 if is_bold:
#                     score *= 1.2
#                 if re.match(r'^((\d+\.)*\d+|[A-Z]\.)\s', full_block_text):
#                     score *= 1.5
#                 if full_block_text.endswith('.'):
#                     score *= 0.8

#                 if score > 1.25:
#                     potential_headings.append({
#                         "score": score, "text": full_block_text, "size": font_size,
#                         "page": page_num + 1, "bbox": block["bbox"]
#                     })

#     sorted_headings = sorted(potential_headings, key=lambda x: x["score"], reverse=True)
    
#     title, outline = classify_headings(sorted_headings)
    
#     if not title and doc.metadata.get('title'):
#         title = doc.metadata['title']

#     final_outline = sorted(outline, key=lambda x: (x["page"], x["bbox"][1]))
    
#     # Store the raw blocks for task_1b to use
#     all_blocks = [page.get_text("blocks") for page in doc]
#     doc.close()
    
#     return {"title": title, "outline": final_outline, "raw_blocks": all_blocks}


# if __name__ == '__main__':
#     create_sample_pdfs()
    
#     pdf_to_process = "gnn_report.pdf"
#     print(f"\n--- Running Task 1A: Structure Extraction for '{pdf_to_process}' ---")
    
#     structure_data = extract_structure(pdf_to_process)
    
#     # Remove the temporary 'bbox' key before final output
#     clean_outline = []
#     for item in structure_data.get("outline", []):
#         clean_item = item.copy()
#         clean_item.pop("bbox", None)
#         clean_outline.append(clean_item)

#     output_json = {
#         "title": structure_data.get("title", ""),
#         "outline": clean_outline
#     }

#     output_filename = f"{os.path.splitext(pdf_to_process)[0]}_outline.json"
#     with open(output_filename, 'w', encoding='utf-8') as f:
#         json.dump(output_json, f, indent=4, ensure_ascii=False)
    
#     print(f"Successfully extracted structure and saved to '{output_filename}'")
#     print("\n--- Extracted Data ---")
#     print(json.dumps(output_json, indent=2))
