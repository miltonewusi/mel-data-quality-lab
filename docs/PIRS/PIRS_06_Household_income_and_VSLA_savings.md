# PIRS 06: Household income and VSLA savings (USD/month)

| Field | Content |
|---|---|
| Result level | Outcome |
| Definition | Self-reported monthly household income in the last 30 days and current VSLA savings balance |
| Unit / scale | USD, converted at the survey-period rate |
| Calculation | As reported |
| Standard / reference | Programme-defined (PIRS) |
| Data source | Household panel survey (ODK/Kobo-style form) unless stated; see `docs/data_dictionary.csv` |
| Fields | income_usd_month, vsla_member, vsla_savings_usd |
| Valid values | Income >0; savings only if VSLA member |
| Frequency | Per survey round / quarterly for outputs |
| Disaggregation | Participant status, district, sex of respondent (outcomes); sex and age band (outputs) |
| Known DQ risks | Sensitivity -> missing-not-at-random; seasonal volatility; currency conversion |
| Automated checks | D02, R01 (see `docs/dq_plan.md`) |
| DQ dimensions most at risk | Validity, Reliability, Integrity |
| Responsible | MEL lead (owner); partner M&E officers (data entry) |
| Last reviewed | 2026-11 (synthetic example) |
