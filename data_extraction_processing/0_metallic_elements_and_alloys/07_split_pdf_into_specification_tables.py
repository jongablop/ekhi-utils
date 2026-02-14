"""
Step 25 — Split PDF into Specification Tables
==============================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Splits the full PDF into individual specification table files, one per
    table. Handles "continued" pages by appending them to the current table.
    Parallel to step 12 in the pipeline.

Input:
    - processed_data/touloukian-metals-rotated-2.pdf — rotated source PDF
    - processed_data/extracted_spec_table_titles.csv — CSV from step 24

Output:
    - processed_data/split_spec_tables/SpecTable_*.pdf — one PDF per specification table

Dependencies:
    - csv, os, pypdf
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
    # Replace any problematic filename characters
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name)

def split_pdf_by_spec_tables(input_pdf_path, spec_table_csv_path, output_dir):
    """Split a PDF into individual per-specification-table PDFs based on a page index CSV.

    Args:
        input_pdf_path: Path to the full rotated PDF.
        spec_table_csv_path: Path to the CSV mapping specification table numbers to page indices.
        output_dir: Directory where individual specification table PDFs will be written.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Read the CSV with SPECIFICATION TABLE info
    with open(spec_table_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        spec_table_entries = list(reader)

    # Convert page indices to int and sort by page
    spec_table_entries = sorted([
        {
            "page_index": int(entry["page index (from 0)"]),
            "spec_table_number": entry["spec_table_number"],
            "title": entry["title"].strip()
        }
        for entry in spec_table_entries
    ], key=lambda x: x["page_index"])

    pdf = PdfReader(input_pdf_path)
    total_pages = len(pdf.pages)

    current_writer = None
    current_filename = None

    for i, entry in enumerate(spec_table_entries):
        page_idx = entry["page_index"]
        title = entry["title"]
        spec_table_number = entry["spec_table_number"]

        # Continued pages (e.g., "Table 5 (continued)") get appended to the current table PDF
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

        # Start new PDF writer for the current SPECIFICATION TABLE
        current_writer = PdfWriter()
        current_writer.add_page(pdf.pages[page_idx])

        # Generate new filename
        current_filename = f"SpecTable_{int(spec_table_number):0>2}_{sanitize_filename(title)}.pdf"

    # Save the last writer after loop ends
    if current_writer is not None:
        output_path = os.path.join(output_dir, current_filename)
        with open(output_path, "wb") as out_f:
            current_writer.write(out_f)
        print(f"✅ Exported {current_filename}")

# === Example usage ===
split_pdf_by_spec_tables(
    input_pdf_path="./processed_data/touloukian-metals-rotated-2.pdf",
    spec_table_csv_path="./processed_data/extracted_spec_table_titles.csv",
    output_dir="./processed_data/split_spec_tables"
)
