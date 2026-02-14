"""
Step 06 — Find Abstracts and BibTeX in Scopus
===============================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Fetches both abstracts and BibTeX entries from Scopus for each DOI.
    Logs DOIs that return no metadata to a separate file for manual review.

Input:
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned.csv — references with clean DOIs

Output:
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus.csv — references with abstract + bibtex_scopus columns
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned-missing_dois.txt — DOIs not found in Scopus

Dependencies:
    - os, csv, time (standard library)
    - pybliometrics

Note:
    Rate-limited at 0.5 s per request. Requires a valid Scopus API key.
"""

import os
import csv
import time
from pybliometrics.scopus import AbstractRetrieval

def fetch_metadata(doi):
    """
    Tries to retrieve abstract and BibTeX from Scopus.
    Returns a tuple: (abstract, bibtex)
    """
    try:
        abs_obj = AbstractRetrieval(doi, view='FULL')

        abstract = abs_obj.abstract or abs_obj.description or ''
        abstract = abstract.strip() if abstract else ''

        try:
            bibtex = abs_obj.get_bibtex()
        except Exception:
            bibtex = ''

        return abstract, bibtex

    except Exception as e:
        print(f"⚠️ Error retrieving {doi}: {e}")
        return '', ''

def enrich_csv_with_scopus_metadata(csv_path):
    """Add 'abstract' and 'bibtex_scopus' columns to a references CSV via Scopus lookups.

    Args:
        csv_path: Path to the input references CSV containing a 'DOI' column.
    """
    output_path = os.path.splitext(csv_path)[0] + '-with-scopus.csv'
    missing_dois_path = os.path.splitext(csv_path)[0] + '-missing_dois.txt'

    missing_entries = []
    missing_count = 0

    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames + ['abstract', 'bibtex_scopus']

    for i, row in enumerate(rows):
        doi = row.get('DOI', '').strip()
        touloukian_ref = row.get('Touloukian ref', '').strip()
        if not doi:
            row['abstract'] = ''
            row['bibtex_scopus'] = ''
            continue

        print(f"[{i+1}/{len(rows)}] Fetching Scopus metadata for DOI: {doi}")
        abstract, bibtex = fetch_metadata(doi)
        row['abstract'] = abstract
        row['bibtex_scopus'] = bibtex

        # Track DOIs where Scopus returned neither abstract nor BibTeX
        if not abstract and not bibtex:
            missing_count += 1
            missing_entries.append((doi, touloukian_ref))

        time.sleep(0.5)  # Rate-limit to avoid quota issues

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write missing DOIs to file
    with open(missing_dois_path, 'w', encoding='utf-8') as missing_file:
        missing_file.write("DOI\tTouloukian ref\n")
        for doi, tref in missing_entries:
            missing_file.write(f"{doi}\t{tref}\n")

    print(f"\n✅ Output written to: {output_path}")
    print(f"⚠️ {missing_count} entries were not found and logged to: {missing_dois_path}")

if __name__ == '__main__':
    import pybliometrics
    pybliometrics.init()
    input_csv = os.path.join('processed_data', 'touloukian-metals-alloys-references-filtered-cleaned.csv')
    enrich_csv_with_scopus_metadata(input_csv)
