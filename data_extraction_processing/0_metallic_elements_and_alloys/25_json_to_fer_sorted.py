"""
Step 22 — JSON to FER (Sorted)
===============================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Enhanced FER conversion with experiment ordering. Tracks last_experiment
    and experiment_order counters. Encodes temperature range in filenames.
    Uses Composition "Above" keyword logic to increment experiment order
    for related entries sharing the same base experiment.

Input:
    - processed_data_missing_entries_71-128/all_data_headers_cleaned_corrected_with_measurand-headers-manually.json — JSON with measurand
    - properties_symbols_units.csv — property-to-symbol/unit mapping
    - processed_data/touloukian-metals-alloys-references-filtered-cleaned-with-scopus-filtered.csv — reference DOIs

Output:
    - processed_data_missing_entries_71-128/fer_json_sorted/*.json — FER JSON files with enriched filenames

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


output_dir = './processed_data_missing_entries_71-128/fer_json_sorted'
os.makedirs(output_dir, exist_ok=True)

warnings = []

headers_corpus = {}

# Load your JSON data (assuming loaded into `data` variable)
#with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "r", encoding="utf-8") as f:
with open("processed_data_missing_entries_71-128/all_data_headers_cleaned_corrected_with_measurand-headers-manually.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

    last_experiment = 1

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

                    # "Above" in Composition indicates a continuation of the same experiment;
                    # otherwise, start a new experiment and reset the sub-order counter
                    if key.startswith('Composition'):
                        if value.startswith('Above'):
                            experiment_order = experiment_order + 1
                        else:
                            experiment_order = 1
                            last_experiment = last_experiment + 1

                    # Parse temperature range from "min-max" string for use in output filenames
                    if key.startswith('Temperature'):
                        try:
                            if '-' in value:
                                temperatures = [float(t) for t in value.split('-')]
                                t_min = min(temperatures)
                                t_max = max(temperatures)
                            else:
                                t_min, t_max = float(value), float(value)
                        except:
                            t_min, t_max = None, None

            # get the measurand
            measurands = [entry.get("measurand")]

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

            description = ' of '.join([prop, material])

            measurement = Measurement(
                description=description,
                changelog=[changelog],
                state=states,
                results=[result],
                measurands=measurands,
                source=source,
            )

            with open(output_dir + f'/ref_{reference_number}_exp_{last_experiment}_{experiment_order}_table_{table_number}_curve_{curve_number}-{t_min}_{t_max}.json', "w") as f:
                f.write(measurement.to_json())

