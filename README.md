### Objective
Build an automated, multi-tiered financial reconciliation engine to match accounts payable invoices between procurement (Coupa) and ERP ledger systems (SAP FI/AR).

### Description
Perform automated document matching across mismatched systems by resolving timing differences, document key shifts, and minor currency rounding variances. The pipeline isolates fully cleared transactions, applies multi-pass matching logic, and categorizes unmatched items to calculate overall financial risk exposure.

### Stack
| Technology |
| --- |
| Python |
| Pandas |

---

### Key Findings & Reconciliation Metrics

* **Match Success Rate:** Successfully reconciled 5,761 documents (~95.0% match rate for Coupa records) with the remaining documents left for manual matching.
* **System Inconsistency Handling:** Corrected systematic posting date shifts using a 2-day sliding window algorithm.
* **Tolerance Rules:** Resolved minor pricing variances using a €1.00 error margin.
* **Unmatched Exposure:**
  * **Coupa Unmatched:** 305 documents | €1,086,031.95 (4.96% of total uncleared volume).
  * **SAP Unmatched:** 141 documents | €562,144.73 (2.63% of total uncleared volume).
* **System Discrepancy:** Coupa contained 164 more unmatched documents than SAP, highlighting potential delayed entries or missing SAP interface transmissions.

---

### Conclusion

Automated multi-pass matching significantly streamlines the inter-system reconciliation process:

* **Operational Efficiency:** Automated reconciliation resolved ~95% of invoice volume without requiring manual ledger investigation.
* **Timing & Posting Differences:** The majority of initial non-matches were driven by posting date lags rather than missing invoices.
* **Risk Exposure:** Identified €1.65M in total unmatched exposure (€1.09M in Coupa, €0.56M in SAP) that requires targeted manual review by financial accountants.

---

### Project Structure

```text
├── data/
│   ├── raw/
│   │   ├── COUPA_AP_2000_202609.csv
│   │   └── SAP_FI_AR_1000_202609.csv
│   └── processed/
│       └── all_matched.csv
│       └── lean_coupa.csv
│       └── not_matched_coupa.csv
│       └── not_matched_sap.csv
│       └── sap_wo_cleared.csv
├── src/
│   ├── clean_and_transform.py
│   └── elementary_EDA.py
|   └── analysis.py
└── README.md
