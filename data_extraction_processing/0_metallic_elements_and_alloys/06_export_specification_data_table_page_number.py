"""
Step 24 — Export Specification Data Table Page Numbers
=====================================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Finds SPECIFICATION TABLE page numbers in the rotated PDF by scanning
    the first few lines of each page for the characteristic header pattern.
    Parallel to step 11 in the pipeline.

Input:
    - processed_data/touloukian-metals-rotated-2.pdf — rotated source PDF

Output:
    - processed_data/extracted_spec_table_titles.csv — CSV with page index, table number, and title

Dependencies:
    - re, csv, pdfplumber
"""
import re
import csv
import pdfplumber

def normalize_line(line):
    """Collapse OCR-inserted spaces between capital letters (e.g. 'S P E C' becomes 'SPEC').

    Args:
        line: A text line potentially containing spaced-out characters.

    Returns:
        The line with inter-letter spaces removed.
    """
    # Collapse spaced-out letters, e.g., "S P E C I F I C A T I O N" -> "SPECIFICATION"
    line = re.sub(r'(?<=[A-Z])\s(?=[A-Z])', '', line, flags=re.IGNORECASE)
    return line

def extract_spec_table_numbers(lines):
    """Extract specification table numbers and titles from lines matching 'SPECIFICATION TABLE NO.'.

    Args:
        lines: List of text lines to scan for specification table headers.

    Returns:
        A list of (table_number, title) tuples found in the lines.
    """
    table_entries = []
    # Match "SPECIFICATIONTABLENO. <number> <title>", allowing optional parenthetical after the number
    pattern = re.compile(r'SPECIFICATIONTABLENO\.\s*(\d+)(?:\s*\(.*?\))?\s+(.*)', re.IGNORECASE)

    for line in lines:
        normalized = normalize_line(line)
        print(normalized)  # Debugging: See normalized lines
        match = pattern.search(normalized)
        if match:
            number = int(match.group(1))
            title = match.group(2).strip()
            table_entries.append((number, title))
    return table_entries

def process_pdf_for_spec_tables(pdf_path, output_csv_path):
    """Scan a PDF for 'SPECIFICATION TABLE' headers and export page indices to a CSV.

    Args:
        pdf_path: Path to the rotated PDF to scan.
        output_csv_path: Path for the output CSV with page_index, spec_table_number, and title.
    """
    extracted_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if not text:
                continue

            # Normalize and check first few lines
            lines = text.splitlines()
            candidate_lines = lines[:5]

            for raw_line in candidate_lines:
                # Strip all whitespace and uppercase to detect spaced-out "SPECIFICATION TABLE" headers
                joined = "".join(raw_line.split()).upper()

                if 'SPECIFICATIONTABLE' in joined:
                    matches = extract_spec_table_numbers([raw_line])

                    for table_number, title in matches:

                        new_title = raw_line.split(str(table_number))[-1].strip()

                        extracted_data.append({
                            "page index (from 0)": page_num,
                            "spec_table_number": table_number,
                            "title": new_title
                        })
                    break  # stop at first match per page

    # Optional: remove duplicate entries (by spec_table_number)
    seen = set()
    unique_data = []
    for row in extracted_data:
        key = row["spec_table_number"]
        if key not in seen:
            seen.add(key)
            unique_data.append(row)

    # Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["page index (from 0)", "spec_table_number", "title"])
        writer.writeheader()
        writer.writerows(unique_data)

    print(f"✅ Extracted {len(unique_data)} SPECIFICATION TABLE entries to {output_csv_path}")


# === Run ===
pdf_path = './processed_data/touloukian-metals-rotated-2.pdf'
output_csv = './processed_data/extracted_spec_table_titles.csv'
process_pdf_for_spec_tables(pdf_path, output_csv)
