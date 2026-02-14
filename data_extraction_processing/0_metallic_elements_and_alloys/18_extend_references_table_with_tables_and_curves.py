"""
Step 23 — Extend References Table with Tables and Curves
========================================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Enriches the reference CSV by cross-referencing with specification JSON
    to add Table_Curve association strings and DOI columns for each reference.

Input:
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv — reference CSV
    - processed_data/specification_tables_metals-filtered-clean.json — specification JSON with table/curve data

Output:
    - output_with_table_curve_doi.csv — enriched CSV with Table_Curve and DOI_JSON columns

Dependencies:
    - csv, json
"""
import csv
import json

# Input files
csv_file = "./processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv"         # your original CSV file
json_file = "./processed_data/specification_tables_metals-filtered-clean.json"      # your JSON metadata file

# Output file
output_file = "output_with_table_curve_doi.csv"

# Load JSON data
with open(json_file, "r", encoding="utf-8") as jf:
    tables_data = json.load(jf)

# Build a reverse lookup: reference number -> list of (table, curve, doi) associations
ref_to_table_curve_doi = {}
for table_entry in tables_data:
    table_no = table_entry.get("table")
    for curve in table_entry.get("table_data", []):
        ref_no = curve.get("Ref. No.")
        curve_no = curve.get("Curve No.")
        doi = curve.get("DOI", "")  # Add DOI if available
        if ref_no:
            ref_to_table_curve_doi.setdefault(ref_no, []).append(
                (table_no, curve_no, doi)
            )

# Process CSV and add new columns
with open(csv_file, "r", encoding="utf-8") as csv_in, \
     open(output_file, "w", encoding="utf-8", newline="") as csv_out:
    
    reader = csv.DictReader(csv_in)
    # Add new columns: Table_Curve and DOI_JSON
    fieldnames = reader.fieldnames + ["Table_Curve", "DOI_JSON"]
    writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        ref_no = row["Reference"].strip()  # Use "TPRC" as the key (or "Reference" if needed)
        table_curve_info = ref_to_table_curve_doi.get(ref_no, [])
        
        if table_curve_info:
            # Join all matching (table, curve) pairs as a string
            table_curve_str = "; ".join(
                [f"Table {t}, Curve {c}" for t, c, _ in table_curve_info]
            )
            # Combine DOIs if multiple
            doi_str = "; ".join(
                [doi for _, _, doi in table_curve_info if doi]
            )
        else:
            table_curve_str = ""
            doi_str = ""
        
        row["Table_Curve"] = table_curve_str
        row["DOI_JSON"] = doi_str
        writer.writerow(row)

print(f"✅ Done! Output written to {output_file}")
