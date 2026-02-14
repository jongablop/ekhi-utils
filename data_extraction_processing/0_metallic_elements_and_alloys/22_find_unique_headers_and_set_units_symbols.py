"""
Step 19 — Find Unique Headers and Set Units/Symbols
=====================================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Builds a property vocabulary by collecting all unique column headers,
    applying an OCR-corrections dictionary (e.g. "Refl.ectance" -> "Reflectance"),
    and mapping each property to its Unicode mathematical italic symbol
    and SI unit. Outputs a corrected JSON and a properties CSV.

Input:
    - processed_data/all_data_headers_cleaned.json — cleaned JSON from Step 18

Output:
    - processed_data/all_data_headers_cleaned_corrected.json — corrected JSON
    - properties_symbols_units.csv — property, symbol, unit lookup table

Dependencies:
    - json, re

Note:
    Unicode symbols reference: https://www.compart.com/en/unicode/search?q=Mathematical+Italic
"""
import json
import re

def clean_header(header):
    """Remove parenthetical content from a column header string.

    Args:
        header: A column header string potentially containing parenthesised units.

    Returns:
        The header with all parenthetical substrings removed and whitespace stripped.
    """
    # Remove anything inside parentheses, including the parentheses themselves
    # Also strip whitespace around the remaining text
    return re.sub(r"\s*\(.*?\)", "", header).strip()

# Load your JSON data (assuming loaded into `data` variable)
#with open("processed_data/all_data_headers_cleaned.json", "r", encoding="utf-8") as f:
with open("processed_data_missing_entries_71-128/all_data_headers_cleaned.json", "r", encoding="utf-8") as f:
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

# OCR correction dictionary: maps common misreads to canonical property names
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
    2: ""
}

# Load your JSON data (assuming loaded into `data` variable)
#with open("processed_data/all_data_headers_cleaned.json", "r", encoding="utf-8") as f:
with open("processed_data_missing_entries_71-128/all_data_headers_cleaned.json", "r", encoding="utf-8") as f:
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
with open("processed_data_missing_entries_71-128/all_data_headers_cleaned_corrected.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=True)

# ref: https://www.compart.com/en/unicode/search?q=Mathematical+Italic#characters

# Unicode Mathematical Italic symbols for each thermophysical property
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