"""
Step 03 — Filter References by Scopus Metadata
================================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Filters the bibliography CSV to keep only rows that have both a
    non-empty DOI and a non-empty bibtex field, producing a reduced
    reference list of Scopus-verified entries.

Input:
    - processed_data/Touloukian-coatings_bibliografia-updated.csv
      — full bibliography CSV from Step 02

Output:
    - processed_data/Touloukian-coatings_bibliografia-updated-filtered.csv
      — filtered CSV containing only rows with DOI and bibtex

Dependencies:
    - os, csv
"""
import os
import csv

def filter_csv_by_columns(input_path, columns=('DOI','bibtex')):
    """Filter a CSV file to keep only rows where all specified columns are non-empty.

    Args:
        input_path: Path to the input CSV file.
        columns: Tuple of column names that must all have non-empty values.
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

    print(f"✅ Filtered file saved to: {output_path}")

def get_filtered_filename(input_path):
    """Return a new file path with '-filtered' appended before the extension.

    Args:
        input_path: Original file path.

    Returns:
        Modified file path with '-filtered' suffix.
    """
    base, ext = os.path.splitext(input_path)
    return f"{base}-filtered{ext}"

if __name__ == '__main__':
    # Customize the input path here
    csv_input = os.path.join('processed_data', 'Touloukian-coatings_bibliografia-updated.csv')
    filter_csv_by_columns(csv_input)
