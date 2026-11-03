# PIRS 07: Number of farmers trained (unique, sex/age disaggregated)

| Field | Content |
|---|---|
| Result level | Output |
| Definition | Count of unique individuals who completed >=1 programme training in the reporting period |
| Unit / scale | Count |
| Calculation | Unique participant_id after cross-partner de-duplication; disaggregate by sex and age band |
| Standard / reference | Partner monitoring system; aligned with donor standard-indicator guidance on unique beneficiaries |
| Data source | Household panel survey (ODK/Kobo-style form) unless stated; see `docs/data_dictionary.csv` |
| Fields | training_log.*, partner_reports.* |
| Valid values | One person counted once across partners |
| Frequency | Per survey round / quarterly for outputs |
| Disaggregation | Participant status, district, sex of respondent (outcomes); sex and age band (outputs) |
| Known DQ risks | No shared beneficiary ID; name spelling variants; aggregation errors; sex mis-coding |
| Automated checks | T01, T02, X01, X02 (see `docs/dq_plan.md`) |
| DQ dimensions most at risk | Validity, Reliability, Integrity |
| Responsible | MEL lead (owner); partner M&E officers (data entry) |
| Last reviewed | 2026-11 (synthetic example) |
