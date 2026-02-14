"""
Step 03 — Clean DOIs in Reference Table
========================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Normalises the DOI column by stripping URL prefixes, whitespace, and
    extracting the bare DOI identifier using a regex pattern.

Input:
    - processed_data/touloukian-metals-alloys-references-filtered.csv — references with raw DOI strings

Output:
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned.csv — references with normalised DOIs

Dependencies:
    - os, csv, re (standard library)

Note:
    Key regex: r'(10\\.\\d{4,9}/[^\\s]+)' captures the DOI from any surrounding URL or whitespace.
"""

import os
import csv
import re

def extract_bare_doi(doi_str):
    """
    Extracts just the DOI identifier from a DOI string or URL.
    E.g., 'https://doi.org/10.1000/xyz' → '10.1000/xyz'
    """
    if not doi_str:
        return ''
    doi_str = doi_str.strip()
    # Extract bare DOI via regex: matches "10.XXXX/..." pattern from any URL or string
    match = re.search(r'(10\.\d{4,9}/[^\s]+)', doi_str, re.IGNORECASE)
    return match.group(1) if match else doi_str  # return original if regex fails

def clean_doi_column(csv_path):
    """Normalise the DOI column in a CSV file by extracting bare DOI identifiers.

    Args:
        csv_path: Path to the input CSV file containing a 'DOI' column.
    """
    output_path = os.path.splitext(csv_path)[0] + '-cleaned.csv'

    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames

    for row in rows:
        row['DOI'] = extract_bare_doi(row.get('DOI', ''))

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Cleaned DOI column written to: {output_path}")

if __name__ == '__main__':
    input_csv = os.path.join('processed_data', 'touloukian-metals-alloys-references-filtered.csv')
    clean_doi_column(input_csv)
