# %% import necessary libraries
import pandas as pd
import numpy as np
from pathlib import Path
from clean_and_transform import match_date_format,normalize_column_names,normalize_column_types
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

# %% Mixed analysis
normalize_column_names(coupa_raw,sap_raw)
#normalize_column_types(sap_raw)
# %% check the format of the dates
coupa_raw_cpy,sap_raw_cpy = match_date_format(coupa_raw,sap_raw)
print('Max dates: ')
print('Coupa: ',coupa_raw_cpy['Document Date'].max())
print('Sap: ',sap_raw_cpy['Document Date'].max())

print('Min dates: ')
print('Coupa: ', coupa_raw_cpy['Document Date'].min())
print('Sap: ', sap_raw_cpy['Document Date'].min())

print(coupa_raw_cpy['Due Date'].min())
print(sap_raw_cpy['Due Date'].min())



# %% Check the Amount formats and currencies

#only Euro
print(coupa_raw_cpy['Currency'].unique())
print(sap_raw_cpy['Currency'].unique())
#separated by the . in both cases - same Amount fomratting
print('Coupa: ')
print(coupa_raw_cpy['Amount'].head(3))
print(coupa_raw_cpy['Amount'].max())
print(coupa_raw_cpy['Amount'].min())
print('Sap: ')
print(sap_raw_cpy['Amount'].head(3))
print(sap_raw_cpy['Amount'].max())
print(sap_raw_cpy['Amount'].min())

# %% with usual formatting differences taken care of, now lets look at some less repeatable patterns

##let's rid ourselves of already cleared documents :) 
print(sap_raw_cpy['Clearing Document'].nunique())
sap_wo_cleared = sap_raw_cpy[sap_raw_cpy['Clearing Document'].isna()]
print(sap_wo_cleared.shape[0])
# %% 
#set up lean df for direct matching
lean_coupa = coupa_raw_cpy[['Document Date','Document Number','XDoc No.','Amount']]
print(lean_coupa)

direct_match = pd.merge(lean_coupa,sap_raw_cpy[['Document Date','Document Number','Amount']],left_on=['Document Date','XDoc No.','Amount'],right_on=['Document Date','Document Number','Amount'],suffixes=['_coupa','_sap'])
print(direct_match.shape)
print(direct_match.head())


# %%
print(sap_raw.columns)
