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
# %% Function to execute full reconciliation matching process
def match_coupa_sap_documents(coupa_raw_cpy, sap_raw_cpy):
    
    ##let's rid ourselves of already cleared documents :) 
    sap_wo_cleared = sap_raw_cpy[sap_raw_cpy['Clearing Document'].isna()].copy()
    
    #set up lean df for direct matching
    lean_coupa = coupa_raw_cpy[['Document Date','Document Number','XDoc No.','Amount']].copy()
    
    lean_coupa['Document Number'] = (
        lean_coupa['Document Number'].str[-5:].astype(int) - 10000 + 180000000
    ).astype(str)
    
    labeled_matching = pd.merge(
        lean_coupa,
        sap_wo_cleared[['Document Date','Document Number','Amount']],
        left_on=['Document Date','XDoc No.','Amount'],
        right_on=['Document Date','Document Number','Amount'],
        how='outer',
        suffixes=[' Coupa',' Sap'],
        indicator=True
    )
    
    # prepare dfs regarding unmatched documents
    fully_matched = labeled_matching[labeled_matching['_merge'] == 'both'].copy()
    unmatched_coupa = labeled_matching[labeled_matching['_merge'] == 'left_only'].copy()
    unmatched_sap = labeled_matching[labeled_matching['_merge'] == 'right_only'].copy()
    
    # clear them for those that have matching values by date
    matched_by_date = pd.merge(
        unmatched_coupa[['Document Date', 'Document Number Coupa', 'XDoc No.', 'Amount']],
        unmatched_sap[['Document Date', 'Document Number Sap', 'Amount']],
        left_on=['XDoc No.','Document Date'],
        right_on=['Document Number Sap', 'Document Date'],
        suffixes=[' Coupa',' Sap']
    )
    
    matched_by_date['Amount Difference'] = matched_by_date['Amount Coupa'] - matched_by_date['Amount Sap']
    matched_by_date['Amount Difference'] = matched_by_date['Amount Difference'].round(2)
    cleared_by_date = matched_by_date[matched_by_date['Amount Difference'].abs() < 1].copy()
    
    # filter out already matched by date
    unmatched_coupa_rem = unmatched_coupa[~unmatched_coupa['XDoc No.'].isin(cleared_by_date['XDoc No.'])].copy()
    unmatched_sap_rem = unmatched_sap[~unmatched_sap['Document Number Sap'].isin(cleared_by_date['Document Number Sap'])].copy()
    
    # match by price
    matched_by_price = pd.merge(
        unmatched_coupa_rem[['Document Date', 'Document Number Coupa', 'XDoc No.', 'Amount']],
        unmatched_sap_rem[['Document Date', 'Document Number Sap', 'Amount']],
        left_on=['XDoc No.','Amount'],
        right_on=['Document Number Sap', 'Amount'],
        suffixes=[' Coupa',' Sap']
    )
    
    # prepare the matched dfs for concatenation
    ready_matched_by_price = matched_by_price.rename(columns={'Document Date Sap': 'Document Date'}) 
    ready_matched_by_date = cleared_by_date.rename(columns={'Amount Sap': 'Amount'})
    ready_fully_matched = fully_matched[['Document Date','XDoc No.','Document Number Sap','Amount']]
    
    all_matched = pd.concat([ready_fully_matched, ready_matched_by_price, ready_matched_by_date], join='inner', ignore_index=True)
    
    # deal with columns that do not match directly
    not_matched_coupa = lean_coupa[~lean_coupa['XDoc No.'].isin(all_matched['XDoc No.'])].copy()
    not_matched_sap = sap_wo_cleared[~sap_wo_cleared['Document Number'].isin(all_matched['XDoc No.'])].copy()
    
    return all_matched,sap_wo_cleared, not_matched_coupa, not_matched_sap, lean_coupa

# %%
