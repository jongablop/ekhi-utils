"""
Step 13 — Find Unique Headers and Set Units/Symbols
====================================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Applies 30+ OCR corrections to column headers (e.g., "Refl.ectance"
    to "Reflectance"), maps corrected headers to Unicode mathematical
    italic symbols and SI units, and writes a properties CSV lookup table.

Input:
    - processed_data/all_data_headers_cleaned.json — cleaned header JSON

Output:
    - processed_data/all_data_headers_cleaned_corrected.json — corrected headers
    - properties_symbols_units.csv — property-to-symbol-to-unit mapping

Dependencies:
    - json, re

Note:
    Unicode symbols use Mathematical Italic block (U+1D400 range).
"""
import json
import re

def clean_header(header):
    """Remove parenthetical content from a column header string."""
    # Remove parenthetical content from headers
    return re.sub(r"\s*\(.*?\)", "", header).strip()

# First pass: collect all unique headers for inspection
with open("processed_data/all_data_headers_cleaned.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)
    all_headers = []
    for table_entry in all_data:
        data = table_entry.get("table_data")
        
        for elem in data:
            d = elem.get("data")     
            headers = d["column_headers"]

            for header in headers:
                all_headers.append(header)

    unique_headers = set(all_headers)

    print(unique_headers)

# OCR correction map: fixes common OCR misreadings and maps single-letter symbols
corrections = {
    "Emittance E)": "Emittance",
    "Refl.ectance": "Reflectance",
    "reflectancep": "Reflectance",
    "Wavelength X": "Wavelength",
    "Temperature T": "Temperature",
    "Tempera1ure": "Temperature",
    "Wavelength.": "Wavelength",
    "Wavelength..": "Wavelength",
    "Wavelength\"": "Wavelength",
    "Wavelength._": "Wavelength",
    "Reflectancep)": "Reflectance",
    ">._": "",  # remove weird junk
    2: "",
    "p": "Reflectance",
    "ρ": "Reflectance",
    "T": "Temperature",
    "α": "Absorptance",
    "λ": "Wavelength",
    "ε": "Emittance",
    "Temperature. T": "Temperature",
    "τ": "Transmittance"
}

# Load your JSON data (assuming loaded into `data` variable)
#with open("processed_data/all_data_headers_cleaned.json", "r", encoding="utf-8") as f:
with open("processed_data/all_data_headers_cleaned.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)
    all_headers = []
    for table_entry in all_data:
        data = table_entry.get("table_data")
        
        for elem in data:
            d = elem.get("data")     
            headers = d["column_headers"]
            new_headers = []
            for header in headers:

                if header in corrections:
                    header = corrections.get(header)
                all_headers.append(header)
                new_headers.append(header)

            d["column_headers"] = new_headers

    unique_headers = set(all_headers)

    print(unique_headers)

# Save back to JSON
#with open("processed_data/all_data_headers_cleaned_corrected.json", "w", encoding="utf-8") as f:
with open("processed_data/all_data_headers_cleaned_corrected.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=True)

# Unicode Mathematical Italic symbols for each property
# Ref: https://www.compart.com/en/unicode/search?q=Mathematical+Italic#characters
symbols = {
    "Transmittance": "𝜏",
    "Wavelength": "𝜆",
    "Temperature": "𝑇",
    "Reflectance": "𝜌",
    "Absorptance": "𝛼",
    "Angle": "𝜃",
    "Emittance": "𝜀",
}

units = {
    "Transmittance": "",
    "Wavelength": "𝜇m",
    "Temperature": "K",
    "Reflectance": "",
    "Absorptance": "",
    "Angle": "°",
    "Emittance": "",
}

with open("properties_symbols_units.csv", "w", encoding="utf-8") as f:

    f.write("property,symbol,units\n")

    for header in unique_headers:
        if header in symbols and header in units:
            line = [header, symbols.get(header), units.get(header)]
            f.write(','.join(line)+"\n")