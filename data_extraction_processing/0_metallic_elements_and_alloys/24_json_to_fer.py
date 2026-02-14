"""
Step 21 — JSON to FER
=====================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Converts corrected JSON data into FER format using the ferpy library.
    Creates Measurement objects with States, QuantityValues, Source (DOI +
    Touloukian Vol. 7 citation), and ChangelogEntry for each curve.

Input:
    - processed_data/all_data_headers_cleaned_corrected_with_measurand.json — JSON with measurand field
    - properties_symbols_units.csv — mapping of property names to symbols and units
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv — reference DOIs

Output:
    - processed_data/fer_json/table_<N>_curve_<M>.json — individual FER JSON files per curve

Dependencies:
    - json, re, os, csv, datetime, ferpy
"""
import json
import re
import os
import csv

from datetime import datetime

from ferpy.main.quantity_values import QuantityValues
from ferpy.main.measurement import Measurement
from ferpy.main.source import Source

from ferpy.auxiliary.changelog_entry import ChangelogEntry
from ferpy.auxiliary.state import State


# Load CSV into a nested dictionary
property_info = {}

with open("properties_symbols_units.csv", mode="r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        property_name = row["property"].strip()
        property_info[property_name] = {
            "symbol": row["symbol"].strip(),
            "units": row["units"].strip()
        }


output_dir = './processed_data/fer_json'
os.makedirs(output_dir, exist_ok=True)

warnings = []

headers_corpus = {}

# Load your JSON data (assuming loaded into `data` variable)
with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

    for table_entry in all_data:

        table_number = table_entry.get("table")

        # generate measurement description
        prop = table_entry.get("property")
        material = table_entry.get("material")
        description = ' of '.join([prop, material])

        entries = table_entry.get("table_data")

        for entry in entries:

            reference_number = entry.get("Ref. No.")
            curve_number = entry.get("Curve No.")

            # generate the States of the results
            states = []

            for key, value in entry.items():

                if key not in ("Curve No.", "Ref. No.", "Year", "data", "measurand"):

                    if value != "":

                        states.append(
                            State(
                                name=key,
                                description=value
                            )
                        )

            # get the measurand
            measurands = [entry.get("measurand")]

            # If no measurand was matched in step 20, derive it from the last word of the property name
            if entry.get("measurand") == "":
                measurand = prop.split()[-1].capitalize()
                measurands = [measurand]

            current_time = datetime.now()

            changelog = ChangelogEntry(
                timestamp=current_time,
                description="Initial generation of the fer data.",
            )

            # generate the QuantityValues for the result

            data = entry.get("data")
            quantities = data.get("column_headers")
            values = list(data.get("curve").values())

            # Fall back to previously seen headers for this property if current entry has none
            if quantities == []:
                quantities = headers_corpus.get(prop)

            else:
                if prop not in headers_corpus.keys():
                    headers_corpus[prop] = quantities


            # Truncate quantities list if it has more entries than the actual data columns
            if len(quantities) > len(values):
                quantities = quantities[:len(values)]

            try:
                units = [property_info.get(quantity).get("units") for quantity in quantities if quantity in property_info.keys()]
                symbols = [property_info.get(quantity).get("symbol") for quantity in quantities if quantity in property_info.keys()]
            except:
                print(quantities)

            result = QuantityValues(
                name=description,
                description="",
                changelog=[changelog],
                quantities=quantities,
                symbols=symbols,
                units=units,
                values=values,
            )

            for measurand in measurands:
                if measurand not in result.quantities:
                    print(f"there might be a problem in Table {table_number}, curve {curve_number}: measurand not in quantities")
                    warnings.append(f"there might be a problem in Table {table_number}, curve {curve_number}: measurand not in quantities")
                    break

            # Generate the Source

            with open('./processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv', newline='', encoding='utf-8') as csvfile:

                references_reader = csv.DictReader(csvfile)
                doi = ""
                for row in references_reader:
                    try:
                        if row["Reference"] == reference_number:
                            doi = row["DOI"]
                            break 
                    except:
                        continue

                if doi == "":
                    print(f"Table {table_number} not found in references.")

            description = f"Data originally published at {doi}." \
                f" Tabulated data extracted from Y. S. Touloukian and D. P. DeWitt, *Thermal Radiative Properties: Metallic Elements and Alloys*, Thermophysical Properties of Matter - The TPRC Data Series, Volume 7, IFI/Plenum, New York, 1970;" \
                f" table {table_number}, curve {curve_number}." \
                f" Digital version served at EKHI (URL)."

            source = Source(
                name=f"Digitalized data from {doi}.",
                description=description,
                input_quantities=[],
                influence_quantities=[]
            )

            measurement = Measurement(
                description=description,
                changelog=[changelog],
                state=states,
                results=[result],
                measurands=measurands,
                source=source,
            )

            with open(output_dir + f'/table_{table_number}_curve_{curve_number}.json', "w") as f:
                f.write(measurement.to_json())

