import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path.cwd().parent / "data" if "file" not in locals() else Path(__file__).resolve().parent.parent / "data"
# %% Load clean datasets
all_matched = pd.read_csv(DATA_DIR / 'processed' / 'all_matched.csv')
lean_coupa = pd.read_csv(DATA_DIR / 'processed' / 'lean_coupa.csv')
not_matched_coupa = pd.read_csv(DATA_DIR / 'processed' / 'not_matched_coupa.csv')
not_matched_sap = pd.read_csv(DATA_DIR / 'processed' / 'not_matched_sap.csv')
sap_wo_cleared = pd.read_csv(DATA_DIR / 'processed' / 'sap_wo_cleared.csv')
sap_diff_sum = round(not_matched_sap['Amount'].sum(),2)
sap_diff_sum_percentage = round((sap_diff_sum / sap_wo_cleared['Amount'].sum()) * 100,2)
coupa_diff_sum = round(not_matched_coupa['Amount'].sum(),2)
coupa_diff_sum_percentage = round((coupa_diff_sum / lean_coupa['Amount'].sum()) * 100,2)
coupa_match_rate =  round((all_matched.shape[0] / lean_coupa.shape[0]) * 100,2)
# %%
print('Conclusions: ')
print('The matching was performed using invoice numbers, their dates, and amounts. \n' \
'Due to caught system inconsistency, most dates were treated as posting dates instead of invoice dates, thus a 2 day sliding window was applied to the matching \n' \
'Invoices within that timeframe, with amount and price matching were considered as a match. \n' \
'There was a 1 Euro error margin for amounts, all Invoices withing that margin were considered a match')
print(f'Documents from Coupa matched: {all_matched.shape[0]}')
print(f'Documents from Coupa still missing: {not_matched_coupa.shape[0]} ')
print(f'Documents left not matched from Sap: {not_matched_sap.shape[0]}')
print(f'Matching rate: {coupa_match_rate} % \n')
print(f'There were {lean_coupa.shape[0] - sap_wo_cleared.shape[0] } documents more in coupa than in Sap.')
print(f'The total amount of the unmatched invoices from Sap is {sap_diff_sum} Euro, which corresponds to {sap_diff_sum_percentage} % of the amount from uncleared items.')
print(f'As for Coupa, the total amount of unmatched invoices is {coupa_diff_sum} Euro, which corresponds to {coupa_diff_sum_percentage} % of the amount from uncleared items.')
