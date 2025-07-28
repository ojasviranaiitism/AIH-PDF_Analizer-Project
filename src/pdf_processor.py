import fitz  # PyMuPDF
import os
import re

def clean_text(text: str) -> str:
    """
    Cleans a text string by removing special characters and extra whitespace.
    """
    # Remove common ligatures and special characters
    text = text.replace('\ufb01', 'fi').replace('\ufb02', 'fl').replace('•', '').replace('·', '')
    # Use a regex to remove any other non-standard characters, keeping basic punctuation
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Normalize whitespace for clean JSON and NLP processing
    text = text.replace('\n', ' ').replace('  ', ' ').strip()
    return text

def extract_content_from_pdf(pdf_path: str) -> list:
    """
    Extracts structured content from a PDF, distinguishing between short, styled
    titles and longer paragraph blocks.

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        list: A list of page objects, each containing titles and paragraphs.
    """
    doc_name = os.path.basename(pdf_path)
    document_content = []
    
    try:
        pdf_document = fitz.open(pdf_path)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Use the integer value 16 for the TEXTFLAGS_FONT flag for compatibility
            page_dict = page.get_text("dict", flags=16)
            
            page_titles = []
            page_paragraphs = []
            
            # Heuristic: Find the median font size to identify normal paragraph text
            font_sizes = [span['size'] for block in page_dict['blocks'] if block['type'] == 0 for line in block['lines'] for span in line['spans']]
            if not font_sizes:
                continue
            
            paragraph_font_size = sorted(font_sizes)[len(font_sizes) // 2]
            
            # Process each text block on the page
            for block in page_dict['blocks']:
                if block['type'] == 0:  # This is a text block
                    block_text_reconstructed = ""
                    is_title_candidate = False
                    
                    # Reconstruct the full text of the block
                    for line in block['lines']:
                        for span in line['spans']:
                            # Heuristic for titles: Larger font size or bold font
                            if span['size'] > paragraph_font_size * 1.15 or (span['flags'] & 2**4): # 2**4 is the bold flag
                                is_title_candidate = True
                            block_text_reconstructed += span['text']
                        block_text_reconstructed += " "
                    
                    cleaned_text = clean_text(block_text_reconstructed)

                    # Skip very short or empty text blocks
                    if not cleaned_text or len(cleaned_text) < 10:
                        continue
                    
                    # Classify as title or paragraph based on styling and length
                    # A title is short and has title-like font properties.
                    if is_title_candidate and len(cleaned_text.split()) <= 12:
                        page_titles.append(cleaned_text)
                    # Everything else that is long enough is considered a paragraph.
                    elif len(cleaned_text) > 50:
                        page_paragraphs.append({
                            "text": cleaned_text, # The full, untruncated paragraph
                            "doc_name": doc_name,
                            "page_num": page_num + 1
                        })
            
            if page_titles or page_paragraphs:
                document_content.append({
                    "page_num": page_num + 1,
                    "doc_name": doc_name,
                    "titles": page_titles,
                    "paragraphs": page_paragraphs
                })

        pdf_document.close()
        
    except Exception as e:
        print(f"Error processing {doc_name}: {e}")

    return document_content