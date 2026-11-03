# PIRS 01: Food Consumption Score (FCS)

| Field | Content |
|---|---|
| Result level | Goal |
| Definition | Weighted frequency of consumption of 8 food groups in the past 7 days |
| Unit / scale | Score 0-112; categories Poor <=21, Borderline 21.5-35, Acceptable >35 (standard WFP thresholds; 28/42 where oil and sugar are consumed daily) |
| Calculation | FCS = 2*staples + 3*pulses + 1*vegetables + 1*fruit + 4*meat/fish + 4*dairy + 0.5*sugar + 0.5*oil (days 0-7 per group) |
| Standard / reference | WFP VAM Technical Guidance; WFP Food Consumption Analysis (2008) |
| Data source | Household panel survey (ODK/Kobo-style form) unless stated; see `docs/data_dictionary.csv` |
| Fields | fcs_staples ... fcs_oil, fcs_score |
| Valid values | Valid days 0-7 per group |
| Frequency | Per survey round / quarterly for outputs |
| Disaggregation | Participant status, district, sex of respondent (outcomes); sex and age band (outputs) |
| Known DQ risks | Recall bias; respondent not the household food preparer; fabricated or cloned responses; attrition of food-insecure households |
| Automated checks | R02, R03, E01-E03, D03, B01 (see `docs/dq_plan.md`) |
| DQ dimensions most at risk | Validity, Reliability, Integrity |
| Responsible | MEL lead (owner); partner M&E officers (data entry) |
| Last reviewed | 2026-11 (synthetic example) |
