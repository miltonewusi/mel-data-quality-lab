# PIRS 03: Household Hunger Scale (HHS)

| Field | Content |
|---|---|
| Result level | Goal |
| Definition | Experience of household hunger in the past 30 days (3 questions, each with occurrence and frequency) |
| Unit / scale | Score 0-6; 0-1 little/no hunger, 2-3 moderate, 4-6 severe |
| Calculation | Per item: 0 = never; 1 = rarely/sometimes; 2 = often. HHS = sum of 3 items |
| Standard / reference | FANTA/USAID Household Hunger Scale Indicator Guide (v.4, 2011) |
| Data source | Household panel survey (ODK/Kobo-style form) unless stated; see `docs/data_dictionary.csv` |
| Fields | hhs_q1..3, hhs_f1..3, hhs_score |
| Valid values | Occurrence 0/1; frequency 1-3 only when occurrence = 1 |
| Frequency | Per survey round / quarterly for outputs |
| Disaggregation | Participant status, district, sex of respondent (outcomes); sex and age band (outputs) |
| Known DQ risks | Skip-logic errors on frequency follow-ups; low base rates make errors influential |
| Automated checks | R08, E02, B01 (see `docs/dq_plan.md`) |
| DQ dimensions most at risk | Validity, Reliability, Integrity |
| Responsible | MEL lead (owner); partner M&E officers (data entry) |
| Last reviewed | 2026-11 (synthetic example) |
