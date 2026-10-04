# %% import necessary libraries
import pandas as pd
import numpy as np
from pathlib import Path
from clean_and_transform import match_date_format,normalize_column_names,normalize_column_types,match_coupa_sap_documents
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
lean_coupa['Document Number'] = lean_coupa['Document Number'].str[-5:].astype(int) - 10000 + 180000000
print(lean_coupa['Document Number'])

labeled_matching = pd.merge(lean_coupa,sap_wo_cleared[['Document Date','Document Number','Amount']],left_on=['Document Date','XDoc No.','Amount'],right_on=['Document Date','Document Number','Amount'],how='outer',suffixes=[' Coupa',' Sap'],indicator=True)
print(labeled_matching.shape)
print(labeled_matching.head())

# %% prepare dfs regarding unmatched documents
fully_matched = labeled_matching[labeled_matching['_merge'] == 'both'].copy()
unmatched_coupa = labeled_matching[labeled_matching['_merge'] == 'left_only'].copy()
unmatched_sap = labeled_matching[labeled_matching['_merge'] == 'right_only'].copy()
print(fully_matched.shape)
print(unmatched_coupa.shape)
print(unmatched_sap.shape)

# %% check what exactly is the problem from our match? Date/Amount/Invoice No.
unmatched_differences = pd.merge(unmatched_coupa[['Document Date', 'Document Number Coupa', 'XDoc No.', 'Amount']]
                                 ,unmatched_sap[['Document Date', 'Document Number Sap', 'Amount']],left_on=['XDoc No.'],right_on=['Document Number Sap'],suffixes=[' Coupa',' Sap'])
unmatched_differences['Date Difference'] = unmatched_differences['Document Date Coupa'] - unmatched_differences['Document Date Sap']

print(unmatched_differences.head())
print(unmatched_differences['Date Difference'].value_counts())

# %% after figuring out that for date difference its basically a system problem (documents have their posting date as invoice date) we can clear them for those that have matching values
matched_by_date = pd.merge(unmatched_coupa[['Document Date', 'Document Number Coupa', 'XDoc No.', 'Amount']]
                                 ,unmatched_sap[['Document Date', 'Document Number Sap', 'Amount']],left_on=['XDoc No.','Document Date'],right_on=['Document Number Sap', 'Document Date'],suffixes=[' Coupa',' Sap'])
matched_by_date['Amount Difference'] = matched_by_date['Amount Coupa'] - matched_by_date['Amount Sap']
matched_by_date['Amount Difference'] = matched_by_date['Amount Difference'].round(2)
print(matched_by_date['Amount Difference'].value_counts())
cleared_by_date = matched_by_date[matched_by_date['Amount Difference'].abs() < 1]
print(cleared_by_date['Amount Difference'])
# %% Now let's check if its so simple with amounts as well

unmatched_coupa_rem = unmatched_coupa[~unmatched_coupa['XDoc No.'].isin(cleared_by_date['XDoc No.'])]
unmatched_sap_rem = unmatched_sap[~unmatched_sap['Document Number Sap'].isin(cleared_by_date['Document Number Sap'])]
print(unmatched_coupa.shape)
print(unmatched_coupa_rem.shape)
print(unmatched_sap.shape)
print(unmatched_sap_rem.shape)
# %%
matched_by_price = pd.merge(unmatched_coupa_rem[['Document Date', 'Document Number Coupa', 'XDoc No.', 'Amount']]
                                 ,unmatched_sap_rem[['Document Date', 'Document Number Sap', 'Amount']],left_on=['XDoc No.','Amount'],right_on=['Document Number Sap', 'Amount'],suffixes=[' Coupa',' Sap'])
print(matched_by_price.shape)
# %% mid-check to see how much data we've cleared/if we can move on to case by case analysis


# %% prepare the matched dfs for concatenation
ready_matched_by_price = matched_by_price.rename(columns={'Document Date Sap': 'Document Date'}) 
ready_matched_by_date = cleared_by_date.rename(columns={'Amount Sap': 'Amount'})
ready_fully_matched = fully_matched[['Document Date','XDoc No.','Document Number Sap','Amount']]
all_matched = pd.concat([ready_fully_matched,ready_matched_by_price,ready_matched_by_date],join='inner',ignore_index=True)
print(all_matched.shape)
# %% now deal with columns that do not match directly
not_matched_coupa = lean_coupa[~lean_coupa['XDoc No.'].isin(all_matched['XDoc No.'])]
not_matched_sap = sap_wo_cleared[~sap_wo_cleared['Document Number'].isin(all_matched['XDoc No.'])]
print(all_matched.shape)
print(not_matched_coupa.shape)
print(not_matched_sap.shape)
print(sap_wo_cleared.shape)
print(lean_coupa.shape)

# %% now lets run it as a function from ETL


all_matched,sap_wo_cleared, not_matched_coupa, not_matched_sap, labeled_matching = match_coupa_sap_documents(coupa_raw_cpy,sap_raw_cpy)
print(all_matched.shape)
print(sap_wo_cleared.shape)
print(not_matched_coupa.shape)
print(not_matched_sap.shape)
print(labeled_matching.shape)

# %% Performed some eyeball checks for missing documents to see if there was anything sus about the data, everythning looks fine
# Save the data for analysis
all_matched.to_csv(DATA_DIR / 'processed' / 'all_matched.csv')
sap_wo_cleared.to_csv(DATA_DIR / 'processed' / 'sap_wo_cleared.csv')
not_matched_coupa.to_csv(DATA_DIR / 'processed' / 'not_matched_coupa.csv')
not_matched_sap.to_csv(DATA_DIR / 'processed' / 'not_matched_sap.csv')
labeled_matching.to_csv(DATA_DIR / 'processed' / 'labeled_matching.csv')

