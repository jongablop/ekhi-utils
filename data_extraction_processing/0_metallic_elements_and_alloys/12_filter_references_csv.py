"""
Step 01 — Filter References CSV
================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Filters the references CSV to keep only rows where both the DOI
    and bibtex columns are non-empty.

Input:
    - processed_data/touloukian-metals-alloys-references.csv — full reference table

Output:
    - processed_data/touloukian-metals-alloys-references-filtered.csv — rows with DOI + bibtex

Dependencies:
    - os, csv (standard library)
"""

import os
import csv

def filter_csv_by_columns(input_path, columns=('DOI', 'bibtex')):
    """Filter a CSV file to keep only rows where all specified columns are non-empty.

    Args:
        input_path: Path to the input CSV file.
        columns: Tuple of column names that must all contain non-empty values.
    """
    output_path = get_filtered_filename(input_path)

    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        # Keep only rows where every required column has a non-empty value
        rows = [row for row in reader if all(row.get(col, '').strip() for col in columns)]

    if not rows:
        print("⚠️ No rows matched the filtering criteria.")
        return

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Number of complete references: {len(rows)} with {columns}")
    print(f"✅ Filtered file saved to: {output_path}")

def get_filtered_filename(input_path):
    """Return a new file path with '-filtered' appended before the extension.

    Args:
        input_path: Original file path.

    Returns:
        Modified path string with '-filtered' inserted before the file extension.
    """
    base, ext = os.path.splitext(input_path)
    return f"{base}-filtered{ext}"

if __name__ == '__main__':
    # Customize the input path here
    csv_input = os.path.join('processed_data', 'touloukian-metals-alloys-references.csv')
    filter_csv_by_columns(csv_input)
