import os
import json
import re
import unicodedata
import pandas as pd

ROOT_FOLDER = "./folder_downloaded_from_figshare"
OUTPUT_CSV = "metadata_summary_clean_corrected_dataset.csv"

rows = []

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def normalize_text(text):
    """Normalize unicode and lowercase."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    return text.lower()

def extract_numbers(text):
    if not text:
        return []
    return [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", text)]

def extract_range(text, positive_only=True):
    import re
    if not text:
        return None, None
    numbers = [float(x) for x in re.findall(r"\d*\.?\d+", text)]  # ignore sign
    if not numbers:
        return None, None
    if positive_only:
        numbers = [x for x in numbers if x >= 0]
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return min(numbers), max(numbers)


# -------------------------------------------------------
# Walk JSON files
# -------------------------------------------------------

for root, dirs, files in os.walk(ROOT_FOLDER):
    for file in files:
        if not file.endswith(".json"):
            continue

        filepath = os.path.join(root, file)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue

        pub = data.get("publication_info", {})

        base_metadata = {
            "file_path": filepath,
            "doi": pub.get("doi", ""),
            "year": pub.get("year", ""),
            "title": pub.get("title", ""),
            "journal": pub.get("journal", ""),
            "material": data.get("material", ""),
            "properties": "; ".join(data.get("property", [])),
            "categories": "; ".join(data.get("category", [])),
        }

        for measurement in data.get("reported_measurements", []):

            temperature_vals = []
            wavelength_vals = []
            geometry_vals = []
            composition_vals = []
            error_vals = []

            for state in measurement.get("state", []):
                name = normalize_text(state.get("name", ""))
                desc = state.get("description", "").strip()

                if "temperature" in name:
                    temperature_vals.append(desc)

                elif "wavelength" in name:
                    wavelength_vals.append(desc)

                elif "angular" in name or "geometry" in name or "theta" in name:
                    geometry_vals.append(desc)

                elif "composition" in name:
                    composition_vals.append(desc)

                elif "error" in name or "%" in name:
                    error_vals.append(desc)

            temperature = " | ".join(temperature_vals)
            spectral_range = " | ".join(wavelength_vals)
            geometry = " | ".join(geometry_vals)
            composition = " | ".join(composition_vals)
            reported_error = " | ".join(error_vals)

            temp_min, temp_max = extract_range(temperature)
            wl_min, wl_max = extract_range(spectral_range)

            for result in measurement.get("results", []):
                values = result.get("values", [])
                n_datapoints = 0
                if values and isinstance(values, list) and len(values) > 0:
                    n_datapoints = len(values[0])

                row = base_metadata.copy()

                row.update({
                    "temperature": temperature,
                    "temperature_min_k": temp_min,
                    "temperature_max_k": temp_max,
                    "spectral_range": spectral_range,
                    "wavelength_min_um": wl_min,
                    "wavelength_max_um": wl_max,
                    "geometry": geometry,
                    "composition_remarks": composition,
                    "reported_error_percent": reported_error,
                    "result_name": result.get("name", ""),
                    "measurands": "; ".join(measurement.get("measurands", [])),
                    "n_datapoints": n_datapoints,
                })

                rows.append(row)

df = pd.DataFrame(rows)

df.to_csv(OUTPUT_CSV, index=False)

print(f"Clean CSV generated with {len(df)} rows.")
