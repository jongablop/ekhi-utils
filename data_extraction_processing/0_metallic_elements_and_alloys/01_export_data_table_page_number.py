"""
Step 11 — Export Data Table Page Numbers
=========================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Scans the rotated PDF to locate pages whose headers contain "DATA TABLE NO."
    and extracts the table number, title, and zero-based page index into a CSV.
    Normalises OCR-spaced characters (e.g. "D A T A" becomes "DATA").

Input:
    - processed_data/touloukian-metals-rotated-2.pdf — rotated PDF

Output:
    - processed_data/extracted_table_titles.csv — CSV with page_index, table_number, title

Dependencies:
    - pdfplumber, re, csv
"""
import re
import csv
import pdfplumber

def normalize_line(line):
    """Collapse OCR-inserted spaces between capital letters (e.g. 'D A T A' becomes 'DATA').

    Args:
        line: A text line potentially containing spaced-out characters.

    Returns:
        The line with inter-letter spaces removed.
    """
    # Remove spaces between letters, e.g. "D A T A" -> "DATA"
    line = re.sub(r'(?<=[A-Z])\s(?=[A-Z])', '', line, flags=re.IGNORECASE)
    return line

def extract_table_numbers(lines):
    """Extract data table numbers and titles from lines matching 'DATA TABLE NO. N'.

    Args:
        lines: List of text lines to scan for table headers.

    Returns:
        A list of (table_number, title) tuples found in the lines.
    """
    table_entries = []
    # Match "DATA TABLE NO. 123 (optional qualifier) Title text"
    pattern = re.compile(r'DATATABLENO\.\s*(\d+)(?:\s*\(.*?\))?\s+(.*)', re.IGNORECASE)

    for line in lines:
        normalized = normalize_line(line)
        print(normalized)
        match = pattern.search(normalized)
        if match:
            number = int(match.group(1))
            title = match.group(2).strip()
            table_entries.append((number, title))
    return table_entries


def process_pdf_for_tables(pdf_path, output_csv_path):
    """Scan a PDF for pages containing 'DATA TABLE' headers and export a CSV of page indices.

    Args:
        pdf_path: Path to the rotated PDF to scan.
        output_csv_path: Path for the output CSV with page_index, table_number, and title columns.
    """
    extracted_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(95, len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if not text:
                continue

            # Normalize and check first few lines
            lines = text.splitlines()
            candidate_lines = lines[:5]

            for raw_line in candidate_lines:
                # Collapse all whitespace so OCR-spaced "D A T A T A B L E" becomes "DATATABLE"
                joined = "".join(raw_line.split()).upper()

                if 'DATATABLE' in joined:
                    matches = extract_table_numbers([raw_line])

                    for table_number, title in matches:

                        new_title = raw_line.split(str(table_number))[-1].strip()

                        extracted_data.append({
                            "page index (from 0)": page_num,
                            "table_number": table_number,
                            "title": new_title
                        })
                    break  # stop at first match per page

    # Optional: remove duplicate entries (by table_number)
    seen = set()
    unique_data = []
    for row in extracted_data:
        key = row["table_number"]
        if key not in seen:
            seen.add(key)
            unique_data.append(row)

    # Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["page index (from 0)", "table_number", "title"])
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"✅ Extracted {len(extracted_data)} table entries to {output_csv_path}")


# === Run ===
pdf_path = './processed_data/touloukian-metals-rotated-2.pdf'
output_csv = './processed_data/extracted_table_titles.csv'
process_pdf_for_tables(pdf_path, output_csv)
