"""
Step 03 — Filter References CSV by Scopus Metadata
===================================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Filters the reference CSV to keep only rows that have both a
    non-empty DOI and a non-empty BibTeX entry from Scopus.

Input:
    - processed_data/Touloukian-ceramicos_refs_only_updated.csv — full CSV

Output:
    - processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv — rows
      with valid DOI and BibTeX only

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
    """Return the input path with '-filtered' appended before the file extension."""
    base, ext = os.path.splitext(input_path)
    return f"{base}-filtered{ext}"

if __name__ == '__main__':
    # Customize the input path here
    csv_input = os.path.join('processed_data', 'Touloukian-ceramicos_refs_only_updated.csv')
    filter_csv_by_columns(csv_input)
