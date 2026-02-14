"""
Step 12 — Split PDF into Data Tables
======================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Splits the rotated PDF into individual per-table PDF files using the page
    index CSV produced by Step 11. Pages marked "continued" are appended to
    the preceding table's PDF rather than creating a new file.

Input:
    - processed_data/touloukian-metals-rotated-2.pdf — rotated PDF
    - processed_data/extracted_table_titles.csv — table page index CSV

Output:
    - processed_data/split_tables/Table_*.pdf — one PDF per data table

Dependencies:
    - pypdf, csv, os
"""
import csv
import os
from pypdf import PdfReader, PdfWriter

def sanitize_filename(name):
    """Replace non-alphanumeric characters (except spaces, underscores, hyphens) with underscores.

    Args:
        name: Raw string to sanitize for use as a filename component.

    Returns:
        A sanitized filename-safe string.
    """
    # Replace non-alphanumeric chars (except space, underscore, hyphen) with underscore
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name)

def split_pdf_by_table(input_pdf_path, table_csv_path, output_dir):
    """Split a PDF into individual per-table PDFs based on a page index CSV.

    Args:
        input_pdf_path: Path to the full rotated PDF.
        table_csv_path: Path to the CSV mapping table numbers to page indices.
        output_dir: Directory where individual table PDFs will be written.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(table_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        table_entries = list(reader)

    # Convert page indices to int and sort by page
    table_entries = sorted([
        {
            "page_index": int(entry["page index (from 0)"]),
            "table_number": entry["table_number"],
            "title": entry["title"].strip()
        }
        for entry in table_entries
    ], key=lambda x: x["page_index"])

    pdf = PdfReader(input_pdf_path)
    total_pages = len(pdf.pages)

    current_writer = None
    current_filename = None
    current_table_number = None

    for i, entry in enumerate(table_entries):
        page_idx = entry["page_index"]
        title = entry["title"]
        table_number = entry["table_number"]

        # If this is a continued page, add page to current PDF
        if "continued" in title.lower() and current_writer is not None:
            current_writer.add_page(pdf.pages[page_idx])
            print(f"➕ Added continued page {page_idx} to {current_filename}")
            continue

        # Otherwise, save previous writer (if any) and start a new one
        if current_writer is not None:
            output_path = os.path.join(output_dir, current_filename)
            with open(output_path, "wb") as out_f:
                current_writer.write(out_f)
            print(f"✅ Exported {current_filename}")

        # Start new PDF writer for the current table
        current_writer = PdfWriter()
        current_writer.add_page(pdf.pages[page_idx])

        # Generate new filename
        current_filename = f"Table_{int(table_number):0>2}_{sanitize_filename(title)}.pdf"
        current_table_number = table_number

    # Save the last writer after loop ends
    if current_writer is not None:
        output_path = os.path.join(output_dir, current_filename)
        with open(output_path, "wb") as out_f:
            current_writer.write(out_f)
        print(f"✅ Exported {current_filename}")

# === Example usage ===
split_pdf_by_table(
    input_pdf_path="./processed_data/touloukian-metals-rotated-2.pdf",
    table_csv_path="./processed_data/extracted_table_titles.csv",
    output_dir="./processed_data/split_tables"
)
