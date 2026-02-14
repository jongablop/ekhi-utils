"""
Step 04 — Check Number of Abstracts
=====================================
Pipeline: 2_coatings (Touloukian Vol. 9)

Purpose:
    Quality-assurance diagnostic that counts how many BibTeX entries in
    the filtered CSV contain an abstract field, printing the result to
    the console.

Input:
    - processed_data/Touloukian-coatings_bibliografia-updated-filtered.csv
      — filtered bibliography CSV from Step 03

Output:
    - Console output only (entries with abstract / total)

Dependencies:
    - pandas, re
"""
import pandas as pd
import re

# Load CSV
df = pd.read_csv("processed_data/Touloukian-coatings_bibliografia-updated-filtered.csv")

# Function to check if bibtex field contains an abstract
def has_abstract(bibtex):
    """Check whether a BibTeX string contains an abstract field.

    Args:
        bibtex: A BibTeX entry string, or NaN.

    Returns:
        True if the string contains an 'abstract = ' field, False otherwise.
    """
    if pd.isna(bibtex):
        return False
    # Match BibTeX abstract field (e.g. "abstract = {...")
    return bool(re.search(r'abstract\s*=', bibtex, re.IGNORECASE))

# Apply the function to the 'bibtex' column
df["has_abstract"] = df["bibtex"].apply(has_abstract)

# Count how many entries have abstract
num_with_abstract = df["has_abstract"].sum()
num_total = len(df)

print(f"Entries with abstract: {num_with_abstract} / {num_total}")
