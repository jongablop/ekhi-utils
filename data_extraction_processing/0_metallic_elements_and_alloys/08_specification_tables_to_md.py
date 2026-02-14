"""
Step 26 — Specification Tables to Markdown
==========================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Extracts specification tables from split PDFs using pdfplumber OCR and
    converts them to a combined Markdown file. Applies a fixed schema
    (Curve No., Ref. No., Year, etc.) and corrects common OCR errors
    (e.g., "autbors" -> "authors", "lo-s" -> "10^-5").

Input:
    - processed_data/split_spec_tables/*.pdf — individual specification table PDFs from step 25

Output:
    - processed_data_missing_entries/all_specification_tables.md — combined Markdown with all spec tables

Dependencies:
    - os, re, pdfplumber
"""
import os
import re
import pdfplumber

def clean_text(text):
    """Clean up common OCR mistakes."""
    # Map of known OCR misreadings to their corrections
    corrections = {
        "autbors": "authors",
        "tbick": "thick",
        "lo-s": "10^-5",
        "lo-7": "10^-7",
        "lo-s": "10^-5",
        "10-s": "10^-5",
        "10-7": "10^-7",
        "o/o": "%",
        "0. 001": "0.001",
        "0. 020": "0.020",
        "0 0015": "0.0015",
        "0 020": "0.020",
        "0!": "a",
        "0\!": "a",
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text.strip()

def parse_table_text(text):
    """Parse a raw table text block into structured rows."""
    rows = []
    current_row = None

    # Detect row start: CurveNo RefNo Year followed by 5 remaining fields separated by whitespace
    row_start_pattern = re.compile(
        r"^\s*(\d+)\s+(\d+)\s+(\d{4})\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*)$"
    )

    for line in text.splitlines():
        line = clean_text(line)
        if not line:
            continue

        match = row_start_pattern.match(line)
        if match:
            # Save previous row
            if current_row:
                rows.append(current_row)

            # Start new row
            current_row = {
                "Curve No.": match.group(1),
                "Ref. No.": match.group(2),
                "Year": match.group(3),
                "Wavelength μ or Temperature K": match.group(4),
                "Temperature Range, K or Wavelength Range, μ": match.group(5),
                "Geometry θ θ' ω'": match.group(6),
                "Reported Error, %": match.group(7),
                "Specifications and Remarks": match.group(8),
            }
        else:
            # Continuation of previous row
            if current_row:
                current_row["Specifications and Remarks"] += " " + line

    if current_row:
        rows.append(current_row)

    return rows

def pdf_to_markdown(pdf_path, table_number, title):
    """Extract and convert a single PDF to markdown."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    rows = parse_table_text(text)

    # Build markdown table
    markdown = f"## SPECIFICATION TABLE NO. {table_number}: {title}\n\n"
    markdown += "| Curve No. | Ref. No. | Year | Wavelength μ or Temperature K | Temperature Range, K or Wavelength Range, μ | Geometry θ θ' ω' | Reported Error, % | Composition (weight percent), Specifications and Remarks |\n"
    markdown += "| :-------- | :------- | :--- | :---------------------------- | :------------------------------------------- | :--------------- | :---------------- | :------------------------------------------------------- |\n"

    for row in rows:
        markdown += f"| {row['Curve No.']} | {row['Ref. No.']} | {row['Year']} | {row['Wavelength μ or Temperature K']} | {row['Temperature Range, K or Wavelength Range, μ']} | {row['Geometry θ θ\' ω\'']} | {row['Reported Error, %']} | {row['Specifications and Remarks']} |\n"

    return markdown

def process_folder(input_folder, output_md_file):
    """Process all PDFs in a folder and combine into one markdown file."""
    pdf_files = sorted(f for f in os.listdir(input_folder) if f.lower().endswith(".pdf"))

    with open(output_md_file, "w", encoding="utf-8") as md_file:
        for pdf_filename in pdf_files:

            splitted_filename = pdf_filename.split('_')

            # Extract table number and title from filename
            table_number = splitted_filename[1]
            title = ' '.join(splitted_filename[1:-1]).replace("_", " ").replace("-", " ").title()

            pdf_path = os.path.join(input_folder, pdf_filename)
            print(f"📄 Processing Table {table_number}: {title}")

            markdown_section = pdf_to_markdown(pdf_path, table_number, title)
            md_file.write(markdown_section + "\n\n")

    print(f"\n✅ Combined Markdown saved to: {output_md_file}")

# === Run ===
if __name__ == "__main__":
    input_folder = "./processed_data/split_spec_tables"  # Path to folder of PDFs
    output_md_file = "./processed_data_missing_entries/all_specification_tables.md"
    process_folder(input_folder, output_md_file)
