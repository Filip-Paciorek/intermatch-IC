import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path.cwd().parent / "data" if "file" not in locals() else Path(__file__).resolve().parent.parent / "data"
coupa_raw = pd.read_csv(DATA_DIR / "raw" / "COUPA_AP_2000_202609.csv")
sap_raw = pd.read_csv(DATA_DIR / "raw" / "SAP_FI_AR_1000_202609.csv")
print(coupa_raw.head())
print(sap_raw.head())