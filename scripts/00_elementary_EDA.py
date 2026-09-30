# %% import necessary libraries
import pandas as pd
import numpy as np
from pathlib import Path

# %% Load in the raw data
DATA_DIR = Path.cwd().parent / "data" if "file" not in locals() else Path(__file__).resolve().parent.parent / "data"
coupa_raw = pd.read_csv(DATA_DIR / "raw" / "COUPA_AP_2000_202609.csv")
sap_raw = pd.read_csv(DATA_DIR / "raw" / "SAP_FI_AR_1000_202609.csv")

# %% Check raw coupa 
#nothing out of the ordinary for top and bottom
print('Coupa first 5 rows: ')
print(coupa_raw.head(5))
print('Coupa last 5 rows: ')
print(coupa_raw.tail(5))

#Num of rows and columns is less than in sap
print('Coupa num of rows and cols')
print('Rows: ',coupa_raw.shape[0])
print('Cols: ',coupa_raw.shape[1])

#no data missing
print('Coupa missing data: ')
print(coupa_raw.isna().sum())
# %%
print('Coupa basic info: ')
print(coupa_raw.info())
coupaColTypes = coupa_raw.dtypes.to_frame(name='column types')
print(coupaColTypes)

# %% Check raw sap
print('Sap first 5 rows: ')
print(sap_raw.head(5))
print('Sap last 5 rows: ')
print(sap_raw.tail(5))

#Num of rows and columns is bigger than the coupa one by 134
print('Sap num of rows and cols')
print('Rows: ',sap_raw.shape[0])
print('Cols: ',sap_raw.shape[1])

#no data missing
print('Sap missing data: ')
print(sap_raw.isna().sum())
# %%
print('Sap basic info: ')
print(sap_raw.info())
sapColTypes = sap_raw.dtypes.to_frame(name='column types')
print(sapColTypes)