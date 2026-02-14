"""
Step 28 — Specification Tables OCR (Tesseract)
===============================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Alternative OCR pipeline for specification tables using Tesseract via
    PyMuPDF. Rotates each page 90 degrees, renders at 300 DPI, and formats
    the extracted text as Markdown tables.

Input:
    - processed_data/split_spec_tables/*.pdf — individual specification table PDFs from step 25

Output:
    - processed_data_missing_entries/all_specification_tables.md — combined Markdown with all spec tables

Dependencies:
    - fitz (PyMuPDF), pytesseract, PIL, io, os, re
"""
import fitz  # PyMuPDF
import pytesseract
from pytesseract import Output
from PIL import Image
import io
import os
import re

def ocr_rotated_page(page, rotation=90):
    """Rotate the page and run OCR to extract text."""
    page.set_rotation(rotation)
    pix = page.get_pixmap(dpi=300)  # 300 DPI for high-quality OCR input
    img = Image.open(io.BytesIO(pix.tobytes()))
    text = pytesseract.image_to_string(img)
    return text

def format_tables_to_markdown(text, table_number, title):
    """Format OCR text into a Markdown table with a title."""
    lines = text.strip().split("\n")
    md_table = []
    for line in lines:
        columns = re.split(r"\s{2,}", line.strip())  # Split on 2+ spaces to separate table columns
        if len(columns) > 1:
            md_line = "| " + " | ".join(columns) + " |"
            md_table.append(md_line)

    if md_table:
        header_cols = md_table[0].count("|") - 1
        separator = "|" + " --- |" * header_cols
        md_table.insert(1, separator)
    
    md_output = f"## Table {table_number}: {title}\n\n" + "\n".join(md_table)
    return md_output

def pdf_to_markdown(pdf_path, table_number, title):
    """Process a single PDF and return Markdown text."""
    doc = fitz.open(pdf_path)
    all_md = []
    for page_num, page in enumerate(doc):
        ocr_text = ocr_rotated_page(page, rotation=90)
        md_table = format_tables_to_markdown(ocr_text, table_number, title)
        if md_table:
            all_md.append(f"### Page {page_num + 1}\n\n{md_table}")
    return "\n\n".join(all_md)

def process_folder(input_folder, output_md_file):
    """Process all PDFs in a folder and combine into one Markdown file."""
    pdf_files = sorted(f for f in os.listdir(input_folder) if f.lower().endswith(".pdf"))

    with open(output_md_file, "w", encoding="utf-8") as md_file:
        for pdf_filename in pdf_files:
            splitted_filename = pdf_filename.split('_')
            table_number = splitted_filename[1]
            title = ' '.join(splitted_filename[1:-1]).replace("_", " ").replace("-", " ").title()

            pdf_path = os.path.join(input_folder, pdf_filename)
            print(f"📄 Processing Table {table_number}: {title}")

            markdown_section = pdf_to_markdown(pdf_path, table_number, title)
            md_file.write(markdown_section + "\n\n")

    print(f"\n✅ Combined Markdown saved to: {output_md_file}")

# === Run ===
if __name__ == "__main__":

    import pytesseract

    # Add this line if Tesseract is not in PATH
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Users\\805849\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"


    input_folder = "./processed_data/split_spec_tables"  # Path to folder of PDFs
    output_md_file = "./processed_data_missing_entries/all_specification_tables.md"
    process_folder(input_folder, output_md_file)
