# PIRS 05: Maize yield (kg/ha)

| Field | Content |
|---|---|
| Result level | Outcome |
| Definition | Farmer-reported maize production divided by farmer-reported maize area for the main season |
| Unit / scale | kg per hectare; plausible range 150-8,000 for rainfed smallholders in this setting |
| Calculation | maize_prod_kg / maize_area_ha |
| Standard / reference | Feed the Future-style productivity indicator; FAO guidance on yield estimation |
| Data source | Household panel survey (ODK/Kobo-style form) unless stated; see `docs/data_dictionary.csv` |
| Fields | maize_area_ha, maize_prod_kg, maize_yield_kg_ha |
| Valid values | Area >0; production >0 |
| Frequency | Per survey round / quarterly for outputs |
| Disaggregation | Participant status, district, sex of respondent (outcomes); sex and age band (outputs) |
| Known DQ risks | Unit confusion (acres/ha, bags/kg); digit preference; recall error; crop-cutting not used so values are self-reported |
| Automated checks | R04, R05, R06, D01 (see `docs/dq_plan.md`) |
| DQ dimensions most at risk | Validity, Reliability, Integrity |
| Responsible | MEL lead (owner); partner M&E officers (data entry) |
| Last reviewed | 2026-11 (synthetic example) |
