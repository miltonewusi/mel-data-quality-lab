# PIRS 04: % households adopting >=2 improved practices

| Field | Content |
|---|---|
| Result level | Outcome |
| Definition | Share of surveyed households reporting adoption of at least 2 of 5 programme-promoted practices in the last season |
| Unit / scale | Percentage |
| Calculation | Numerator: HHs with practices_n >= 2. Denominator: HHs interviewed in the round |
| Standard / reference | Programme-defined (PIRS); practice list agreed with technical team |
| Data source | Household panel survey (ODK/Kobo-style form) unless stated; see `docs/data_dictionary.csv` |
| Fields | prac_*, practices_n, adopted_2plus |
| Valid values | Binary 0/1 |
| Frequency | Per survey round / quarterly for outputs |
| Disaggregation | Participant status, district, sex of respondent (outcomes); sex and age band (outputs) |
| Known DQ risks | Ambiguous definition of 'adoption'; enumerator leading questions; duplicate households inflate the denominator |
| Automated checks | R01, E02, B01 (see `docs/dq_plan.md`) |
| DQ dimensions most at risk | Validity, Reliability, Integrity |
| Responsible | MEL lead (owner); partner M&E officers (data entry) |
| Last reviewed | 2026-11 (synthetic example) |
