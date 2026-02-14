"""
Step 04 — Initialise pybliometrics
===================================
Pipeline: 0_metallic_elements_and_alloys (Touloukian Vol. 7)

Purpose:
    Initialises the pybliometrics library and creates the Scopus API
    configuration file if it does not already exist.

Input:
    - (none) — reads/creates ~/.pybliometrics/config.ini interactively

Output:
    - Prints the path to the generated configuration file

Dependencies:
    - pybliometrics

Note:
    Run this once before any Scopus API calls. Requires a valid Scopus API key.
"""

import pybliometrics

pybliometrics.init()

print(pybliometrics.utils.constants.CONFIG_FILE)