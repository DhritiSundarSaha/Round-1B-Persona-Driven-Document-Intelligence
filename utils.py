import fitz  # PyMuPDF
import os

def create_sample_pdfs():
    """Generates two sample PDFs for demonstration if they don't exist."""
    
    pdf1_path = "gnn_report.pdf"
    pdf2_path = "business_report.pdf"

    if os.path.exists(pdf1_path) and os.path.exists(pdf2_path):
        return # Files already exist

    print("Generating sample PDFs for testing...")
    
    # --- PDF 1: GNN Report ---
    try:
        doc1 = fitz.open()
        page1 = doc1.new_page()
        page1.insert_text((72, 72), "Graph Neural Networks for Drug Discovery", fontsize=24, fontname="helv-bold")
        page1.insert_text((72, 120), "1. Introduction", fontsize=18, fontname="helv-bold")
        page1.insert_text((72, 140), "The application of GNNs in computational biology is rapidly expanding. This report explores their use in drug discovery, focusing on methodologies and datasets. The primary challenge is representing complex molecular structures as graphs.", fontsize=12, fontname="helv")
        page1.insert_text((72, 200), "1.1 Prior Research", fontsize=14, fontname="helv-bold")
        page1.insert_text((72, 220), "Previous work by Smith et al. used convolutional networks. However, GNNs provide a more flexible framework for non-euclidean data like molecules. Our methodology builds upon this foundational research.", fontsize=12, fontname="helv")
        doc1.save(pdf1_path)
        doc1.close()

        # --- PDF 2: Business Analysis ---
        doc2 = fitz.open()
        page2 = doc2.new_page()
        page2.insert_text((72, 72), "TechCorp Annual Report 2024", fontsize=24, fontname="helv-bold")
        page2.insert_text((72, 120), "A. Executive Summary", fontsize=18, fontname="helv-bold")
        page2.insert_text((72, 140), "2024 was a year of significant growth. Total revenue increased by 20%, driven by our cloud division. We are analyzing revenue trends closely.", fontsize=12, fontname="helv")
        page2.insert_text((72, 200), "B. Financials", fontsize=18, fontname="helv-bold")
        page2.insert_text((72, 220), "R&D investments grew by 30% to fuel innovation in AI. This strategic investment is crucial for our market positioning against competitors.", fontsize=12, fontname="helv")
        doc2.save(pdf2_path)
        doc2.close()
        print(f"Sample PDFs '{pdf1_path}' and '{pdf2_path}' created.")
    except Exception as e:
        print(f"Error creating sample PDFs: {e}")
        print("Please ensure you have write permissions and PyMuPDF is installed correctly.")

