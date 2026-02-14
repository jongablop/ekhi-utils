"""
Step 13 — PDF Data Table to JSON (Core OCR Extractor)
======================================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Extracts numerical curve data from each split-table PDF using pdfplumber's
    spatial extraction (within_bbox with ~84 px column widths). Merges split
    decimal fragments caused by OCR errors, cleans common OCR artefacts
    (e.g. 'o' -> '0', 'l' -> '1'), and writes per-page JSON files containing
    the table title, column headers, and curve data points.

Input:
    - processed_data/split_tables/Table_*.pdf — individual table PDFs

Output:
    - processed_data/extracted_json/*_page_*.json — per-page JSON with curves

Dependencies:
    - pdfplumber, json, re, os, collections
"""
import json
import re
import os
from collections import defaultdict
import pdfplumber
def extract_curves_from_pdf(file_path, page_no):
    """Extract table title, column headers, and curve data from one page of a table PDF.

    Args:
        file_path: Path to the split-table PDF file.
        page_no: Zero-based page index to extract.

    Returns:
        A dict with keys 'table_title', 'column_headers', and 'curves' (a defaultdict
        mapping curve IDs to their column data).
    """
    data = {
        "table_title": None,
        "column_headers": [],
        "curves": defaultdict(dict)
    }

    with pdfplumber.open(file_path) as pdf:
        #for page in pdf.pages[page_no]:
        page = pdf.pages[page_no]
        text = page.extract_text()
        #if not text:
        #    continue
        lines = text.splitlines()

        # 1. Table title
        if not data["table_title"]:
            title_line = next((l for l in lines if "DATA TABLE" in l.upper()), None)
            if title_line:
                title_match = re.search(r"DATA TABLE.*?\s+(.*)", title_line, re.IGNORECASE)
                if title_match:
                    data["table_title"] = title_match.group(1).strip()

        # 2. Column headers — parse bracketed line like "[T,K; lambda,um; rho]"
        if not data["column_headers"]:
            col_desc_line = next((l for l in lines if re.match(r"\[.*\]", l)), None)
            if col_desc_line:
                headers = col_desc_line.strip("[]").split(";")
                # Convert "T,K" to "T (K)" format for readability
                data["column_headers"] = [h.strip().replace(",", " (") + ")" for h in headers]

    # Spatial extraction: divide the data region into 8 fixed-width columns (84-85 px each)
    columns = extract_columns_from_regions(
        file_path,
        page_no,
        num_columns = 8,
        column_width = 85,
        margin = 25,
        top = 105,
        bottom = 530
    )         
    
    for column in columns:
        
        # 3. Extract curves and their data
        current_curve = None
        for line in column:
            # Detect new curve
            match = re.match(r"(CURVE\s+\d+\*?)", line.strip())
            if match:
                current_curve = match.group(1)
                continue

            if current_curve:
                # Extract numbers from the line
                try:
                    line = fix_broken_decimals(line)
                    line = line.replace('*', '')
                    line = line.replace('"', '')
                    nums = [clean_number(p) for p in line.strip().split()]
                    
                    for i, num in enumerate(nums):
                        if len(data["column_headers"]) < i+1:
                            data["column_headers"].append(i)

                        data["curves"][current_curve].setdefault(data["column_headers"][i], []).append(float(num))

                except Exception as e:
                    
                    print(e)
                    print(line)
                    print(nums)
                    print(current_curve)
                    continue

    return data

def merge_numeric_fragments(texts):
    """
    Merge split numeric fragments like '0999' + '9.' → '0.0999'
    """
    merged = []
    buffer = ''
    for part in texts:
        if re.match(r'^[\d\.,-]+$', part):  # Accept numeric fragments
            buffer += part
        else:
            if buffer:
                merged.append(buffer)
                buffer = ''
            merged.append(part)
    if buffer:
        merged.append(buffer)
    return merged

def clean_number(text):
    """Clean an OCR-extracted numeric string by fixing common misreads.

    Args:
        text: Raw text token expected to be a number.

    Returns:
        The cleaned numeric string, or None if it cannot be parsed as a number.
    """
    # Fix common OCR misreads: lowercase 'o' -> '0', European comma -> decimal point
    text = text.replace("o", "0").replace(",", ".").strip()
    if re.match(r"^\d*\.?\d+$", text):
        return text
    return None

def group_words_by_line(words, y_tol=10):
    """
    Group words into rows based on their vertical alignment.
    """
    rows = []
    for w in sorted(words, key=lambda w: w['top']):
        for row in rows:
            if abs(row[0]['top'] - w['top']) <= y_tol:
                row.append(w)
                break
        else:
            rows.append([w])
    return rows

def fix_broken_decimals(text):
    """Rejoin decimal numbers split by OCR-inserted spaces (e.g. '0. 618' becomes '0.618').

    Args:
        text: A line of text potentially containing broken decimal numbers.

    Returns:
        The text with broken decimals rejoined.
    """
    # OCR often inserts a space after the decimal point: "0. 618" -> "0.618"
    fixed_text = re.sub(r'(\d+)\.\s+(\d+)', r'\1.\2', text)
    return fixed_text


def merge_fragments_safely(words, gap_thresh=5):
    """
    Merge split numeric fragments safely:
    - Merge if both are numeric and very close horizontally
    - Special case: merge decimal fragments like '0.' + '1357' → '0.1357'
    Applies OCR cleanup to each final result.
    """
    if not words:
        return []

    merged = []
    i = 0

    while i < len(words):
        curr = words[i]
        text = curr['text']
        x1 = curr['x1']

        # Look ahead to next word if possible
        if i + 1 < len(words):
            next_word = words[i + 1]
            gap = next_word['x0'] - x1
            next_text = next_word['text']

            # Case 1: Decimal fix — '0.' + '1357'
            if re.match(r'^\d*\.$', text) and re.match(r'^\d+$', next_text) and gap <= gap_thresh:
                text += next_text
                i += 1  # skip next_word

            # Case 2: General numeric merging — both look numeric
            elif re.match(r'^[\d\.,\-]+$', text) and re.match(r'^[\d\.,\-]+$', next_text) and gap <= gap_thresh:
                text += next_text
                i += 1  # skip next_word

        merged.append(clean_text(text))
        i += 1

    return merged

def clean_text(text):
    """
    Cleans up common OCR and font misreads.
    """
    text = text.replace("o", "0").replace("O", "0")
    text = text.replace("l", "1").replace("I", "1")
    text = text.replace(",", ".")  # optional: European decimals
    text = text.strip()
    return text

def extract_columns_from_regions(
    pdf_path,
    page_no,
    num_columns = 8,
    column_width = 84,
    margin = 25,
    top = 105,
    bottom = 530,
    y_tolerance=3
):
    """Extract text from fixed-width column regions of a PDF page using spatial bounding boxes.

    Args:
        pdf_path: Path to the PDF file.
        page_no: Zero-based page index.
        num_columns: Number of columns to extract.
        column_width: Width of each column in PDF points.
        margin: Left margin offset in PDF points.
        top: Top boundary of the data region in PDF points.
        bottom: Bottom boundary of the data region in PDF points.
        y_tolerance: Vertical tolerance for grouping words into rows.

    Returns:
        A list of lists, where each inner list contains the text lines for one column.
    """
    columns_data = []

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no]
        width = page.width
        height = page.height
        bottom = bottom or height

        # Compute column bounding boxes
        column_bboxes = []
        for i in range(num_columns):
            x0 = margin + i * column_width
            x1 = min(x0 + column_width, page.width)
            column_bboxes.append((x0, top, x1, bottom))

        # Extract words in each column
        for bbox in column_bboxes:
            cropped = page.within_bbox(bbox)
            words = cropped.extract_words()

            # Group words by Y position
            rows_grouped = group_words_by_line(words, y_tol=3)


            # Sort rows and merge text left-to-right
            column_lines = []
            for row in rows_grouped:
                row_words = sorted(row, key=lambda w: w['x0'])
                cleaned_row = merge_fragments_safely(row_words)
                column_lines.append(' '.join(cleaned_row))

            columns_data.append(column_lines)

    return columns_data

def process_pdfs_in_folder(input_folder, output_folder):
    """Process all PDFs in a folder, extracting curve data to per-page JSON files.

    Args:
        input_folder: Directory containing split-table PDF files.
        output_folder: Directory where per-page JSON files will be written.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    
    for pdf_file in pdf_files:
        file_path = os.path.join(input_folder, pdf_file)
        print(f"Processing: {pdf_file}")
        
        with pdfplumber.open(file_path) as pdf:
            for page_no in range(len(pdf.pages)):
                print(f"  Extracting page {page_no}")
                data = extract_curves_from_pdf(file_path, page_no)
                
                base_name = os.path.splitext(pdf_file)[0]
                json_filename = f"{base_name}_page_{page_no + 1}.json"
                output_path = os.path.join(output_folder, json_filename)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                
                print(f"    Saved: {json_filename}")

# Example usage:
input_folder = './processed_data/split_tables'
output_folder = './processed_data/extracted_json'

process_pdfs_in_folder(input_folder, output_folder)
