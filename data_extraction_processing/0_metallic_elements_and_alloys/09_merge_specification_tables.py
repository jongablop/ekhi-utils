"""
Step 27 — Merge Specification Tables
=====================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Merges a range of individual specification table PDFs into a single
    combined PDF file, sorted by table number.

Input:
    - processed_data/split_spec_tables/SpecTable_*.pdf — individual table PDFs from step 25

Output:
    - processed_data/spec_tables_<start>_to_<end>.pdf — merged PDF for the specified range

Dependencies:
    - os, re, pypdf
"""
import os
import re
from pypdf import PdfReader, PdfWriter

def merge_specification_tables(input_folder, output_file, start_table, end_table):
    """
    Merge PDF files for specification tables in a given range into one PDF.

    Args:
        input_folder (str): Folder containing the table PDFs.
        output_file (str): Path for the combined PDF file.
        start_table (int): Starting table number (inclusive).
        end_table (int): Ending table number (inclusive).
    """
    writer = PdfWriter()

    # Collect and sort matching files by table number
    pdf_files = []
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(".pdf"):
            continue

        match = re.match(r"SpecTable[_ ](\d+)[_-]", filename, re.IGNORECASE)
        if match:
            table_number = int(match.group(1))
            if start_table <= table_number <= end_table:
                pdf_files.append((table_number, filename))

    pdf_files.sort()  # Sort by table number

    if not pdf_files:
        print(f"⚠️ No tables found in range {start_table}-{end_table}.")
        return

    print(f"📚 Merging tables {start_table} to {end_table}:")
    for table_number, filename in pdf_files:
        pdf_path = os.path.join(input_folder, filename)
        print(f"  ➕ Adding Table {table_number}: {filename}")
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)

    # Write merged PDF
    with open(output_file, "wb") as out_f:
        writer.write(out_f)

    print(f"\n✅ Merged PDF saved to: {output_file}")


# === Example usage ===
if __name__ == "__main__":
    # Folder with split specification tables
    input_folder = "./processed_data/split_spec_tables"
    # Output PDF file
    output_file = "./processed_data/spec_tables_261_to_310.pdf"
    # Range of table numbers to include
    start_table = 261
    end_table = 310

    merge_specification_tables(input_folder, output_file, start_table, end_table)
