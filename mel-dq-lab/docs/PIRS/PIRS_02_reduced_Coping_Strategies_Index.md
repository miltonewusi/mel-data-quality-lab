# PIRS 02: reduced Coping Strategies Index (rCSI)

| Field | Content |
|---|---|
| Result level | Goal |
| Definition | Frequency and severity of food-based coping behaviours in the past 7 days |
| Unit / scale | Score 0-56; higher = more severe coping |
| Calculation | rCSI = 1*less-preferred foods + 2*borrow food + 1*limit portions + 3*restrict adult consumption + 1*reduce meals (days 0-7 each) |
| Standard / reference | WFP/CARE Coping Strategies Index Field Methods Manual; WFP Technical Guidance Note |
| Data source | Household panel survey (ODK/Kobo-style form) unless stated; see `docs/data_dictionary.csv` |
| Fields | rcsi_*, rcsi_score |
| Valid values | Valid days 0-7 per item |
| Frequency | Per survey round / quarterly for outputs |
| Disaggregation | Participant status, district, sex of respondent (outcomes); sex and age band (outputs) |
| Known DQ risks | Straight-lining from fatigue; social desirability; incorrectly applied weights |
| Automated checks | R02, R09, E02, E03, B01 (see `docs/dq_plan.md`) |
| DQ dimensions most at risk | Validity, Reliability, Integrity |
| Responsible | MEL lead (owner); partner M&E officers (data entry) |
| Last reviewed | 2026-11 (synthetic example) |
