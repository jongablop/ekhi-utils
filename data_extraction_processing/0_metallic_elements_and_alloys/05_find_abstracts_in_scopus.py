"""
Step 05 — Find Abstracts in Scopus
===================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Enriches the references CSV with abstracts fetched from Scopus via
    DOI lookup. Includes a 0.5 s delay between requests to respect rate limits.

Input:
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned.csv — references with clean DOIs

Output:
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-abstracts.csv — references plus abstract column

Dependencies:
    - os, csv, time (standard library)
    - pybliometrics

Note:
    Requires a valid Scopus API key configured via pybliometrics.init().
"""

import os
import csv
import time
from pybliometrics.scopus import AbstractRetrieval
#from pybliometrics.scopus.exception import Scopus404Error

def fetch_abstract_or_description(doi):
    """Fetch the abstract or description for a DOI from the Scopus API.

    Args:
        doi: A DOI string to look up in Scopus.

    Returns:
        The abstract or description text, or an empty string if not found.
    """
    try:
        abs_obj = AbstractRetrieval(doi, view='FULL')
        if abs_obj.abstract:
            return abs_obj.abstract.strip()
        elif abs_obj.description:
            return abs_obj.description.strip()
        else:
            return ''
    #except Scopus404Error:
    #    print(f"❌ DOI not found in Scopus: {doi}")
    #    return ''
    except Exception as e:
        print(f"⚠️ Error retrieving {doi}: {e}")
        return ''

def enrich_csv_with_abstracts(csv_path):
    """Add an 'abstract' column to a references CSV by querying Scopus for each DOI.

    Args:
        csv_path: Path to the input references CSV containing a 'DOI' column.
    """
    output_path = os.path.splitext(csv_path)[0] + '-with-abstracts.csv'

    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames + ['abstract']

    for i, row in enumerate(rows):
        doi = row.get('DOI', '').strip()
        if not doi:
            row['abstract'] = ''
            continue
        print(f"[{i+1}/{len(rows)}] Fetching abstract for DOI: {doi}")
        row['abstract'] = fetch_abstract_or_description(doi)
        time.sleep(0.5)  # Rate-limit: Scopus API allows ~2 req/s for standard keys

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Output written to: {output_path}")

if __name__ == '__main__':
    import pybliometrics
    pybliometrics.init()
    input_csv = os.path.join('processed_data', 'touloukian-metals-alloys-references-filtered-cleaned.csv')
    enrich_csv_with_abstracts(input_csv)
