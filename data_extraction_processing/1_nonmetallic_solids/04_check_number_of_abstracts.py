"""
Step 04 — Check Number of Abstracts
====================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    QA diagnostic that counts how many BibTeX entries in the filtered
    reference CSV contain an abstract field.

Input:
    - processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv

Output:
    - Console output with abstract count vs total entries

Dependencies:
    - pandas, re
"""
import pandas as pd
import re

# Load CSV
df = pd.read_csv("processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv")

# Function to check if bibtex field contains an abstract
def has_abstract(bibtex):
    """Return True if the BibTeX string contains an 'abstract' field.

    Args:
        bibtex: A BibTeX entry string, or NaN.

    Returns:
        True if an abstract field is found, False otherwise.
    """
    if pd.isna(bibtex):
        return False
    return bool(re.search(r'abstract\s*=', bibtex, re.IGNORECASE))

# Apply the function to the 'bibtex' column
df["has_abstract"] = df["bibtex"].apply(has_abstract)

# Count how many entries have abstract
num_with_abstract = df["has_abstract"].sum()
num_total = len(df)

print(f"Entries with abstract: {num_with_abstract} / {num_total}")
