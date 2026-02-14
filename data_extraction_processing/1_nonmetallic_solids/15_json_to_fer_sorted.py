"""
Step 15 — JSON to FER (Sorted Export)
======================================
Pipeline: 1_nonmetallic_solids (Touloukian Vol. 8)

Purpose:
    Exports the final enriched JSON into FER-format JSON files using the
    ferpy library. Each output file represents one measurement, named with
    reference number, experiment ordering, table, curve, and temperature
    range. Includes a Touloukian Vol. 8 citation in every source description.

Input:
    - processed_data/all_data_headers_cleaned_corrected_with_measurand.json
    - properties_symbols_units.csv — symbol/unit lookup
    - processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv — DOI lookup

Output:
    - processed_data/fer_json_sorted/*.json — one FER JSON per measurement curve

Dependencies:
    - json, re, os, csv, datetime, ferpy

Note:
    Experiment ordering tracks "Above" composition continuations to group
    related measurements under the same experiment ID.
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


# Load CSV into a nested dictionary for property-to-symbol/unit mapping
property_info = {}

with open("properties_symbols_units.csv", mode="r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        property_name = row["property"].strip()
        property_info[property_name] = {
            "symbol": row["symbol"].strip(),
            "units": row["units"].strip()
        }


output_dir = './processed_data/fer_json_sorted'
os.makedirs(output_dir, exist_ok=True)

warnings = []

headers_corpus = {}

# Load your JSON data (assuming loaded into `data` variable)
#with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "r", encoding="utf-8") as f:
with open("processed_data/all_data_headers_cleaned_corrected_with_measurand.json", "r", encoding="utf-8") as f:
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

                    if key.startswith('Composition'):
                        # "Above" indicates a continuation of the same experiment
                        if value.startswith('Above'):
                            experiment_order = experiment_order + 1
                        else:
                            experiment_order = 1
                            last_experiment = last_experiment + 1

                    if key.startswith('Temperature'):
                        # Parse temperature range "min-max" or single value; strip ~ prefix
                        try:
                            if '-' in value:
                                temperatures = [float(t) for t in value.split('-')]
                                t_min = min(temperatures)
                                t_max = max(temperatures)
                            else:
                                value = value.replace('~', '')
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

            # Fall back to cached headers for this property if current curve has none
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

            with open('./processed_data/Touloukian-ceramicos_refs_only_updated-filtered.csv', newline='', encoding='utf-8') as csvfile:

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
                f" Tabulated data extracted from Y. S. Touloukian and D. P. DeWitt, *Thermal Radiative Properties: Nonmetallic solids*, Thermophysical Properties of Matter - The TPRC Data Series, Volume 8, IFI/Plenum, New York, 1972;" \
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

