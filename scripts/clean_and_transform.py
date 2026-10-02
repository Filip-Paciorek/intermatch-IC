# %% import necessary libraries

import pandas as pd
import numpy as np
from pathlib import Path

# %% Load in the raw data

DATA_DIR = Path.cwd().parent / "data" if "file" not in locals() else Path(__file__).resolve().parent.parent / "data"
coupa_raw = pd.read_csv(DATA_DIR / "raw" / "COUPA_AP_2000_202609.csv")
sap_raw = pd.read_csv(DATA_DIR / "raw" / "SAP_FI_AR_1000_202609.csv")
def normalize_column_names(coupa,sap):
    coupa.rename(columns={'recon_no': 'Recon No.','netting_id':'Netting ID','Invoice no.': 'Document Number','invoice date':'Document Date','amount': 'Amount','ccy.': 'Currency','due date': 'Due Date','comment': 'Comment','xdocno': 'XDoc No.'},inplace=True)
    sap.rename(columns={'Amount in doc. ccy.': 'Amount','Net Due Date': 'Due Date','Document Currency': 'Currency'},inplace=True)
def normalize_column_types(sap):
    sap['Document Number'] = sap['Document Number'].astype(str)
def match_date_format(coupa_raw,sap_raw):
    coupa_raw_cpy = coupa_raw.copy()
    sap_raw_cpy = sap_raw.copy()
    coupa_raw_cpy['Document Date'] = pd.to_datetime(coupa_raw['Document Date'],format='%m/%d/%Y').dt.date
    coupa_raw_cpy['Due Date'] = pd.to_datetime(coupa_raw['Due Date'],format='%m/%d/%Y').dt.date
    sap_raw_cpy['Document Date'] = pd.to_datetime(sap_raw['Document Date']).dt.date
    sap_raw_cpy['Due Date'] = pd.to_datetime(sap_raw['Due Date']).dt.date
    return coupa_raw_cpy,sap_raw_cpy

# %%
