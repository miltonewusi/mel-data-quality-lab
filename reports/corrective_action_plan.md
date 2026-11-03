# Corrective Action Plan (auto-generated)
Actions are ordered by priority score (severity x log of records affected). Owners/timelines are suggested defaults and should be agreed with the programme team.
| # | Issue | Priority | Corrective action | Owner | Timeline | Verification |
|---|---|---|---|---|---|---|
| 1 | Fuzzy beneficiary duplicate (T01) | 12.57 | Introduce a shared beneficiary ID (e.g., national ID or programme card); quarterly cross-partner de-duplication | MEL lead + partners | 1 month | Re-run `meldq all`; check flag rate falls below 2% |
| 2 | Duplicate HH-round (R01) | 11.74 | Enable duplicate-instance detection on the server; train enumerators to confirm sync before re-sending | MEL data manager | 2 weeks | Re-run `meldq all`; check flag rate falls below 2% |
| 3 | Yield outside plausible range (R04) | 11.49 | Add explicit unit selectors, auto-convert, and a yield plausibility warning at entry | MEL data manager | 2 weeks | Re-run `meldq all`; check flag rate falls below 2% |
| 4 | Demographics out of range (R03) | 9.89 | Add range constraints; require confirmation for HH size >15 | MEL data manager | 1 week | Re-run `meldq all`; check flag rate falls below 2% |
| 5 | HHS frequency skip-logic (R08) | 9.44 | Fix relevance conditions in the form; add server-side validation | MEL data manager | 1 week | Re-run `meldq all`; check flag rate falls below 2% |
| 6 | rCSI straight-lining (R09) | 8.47 | Shorten the module, reorder items, spot-check audio audits on rCSI | Field supervisors | Next round | Re-run `meldq all`; check flag rate falls below 2% |
| 7 | Yield peer outlier (R05) | 8.25 | Review outliers with supervisors; add soft yield-range warnings | Field supervisors | 2 weeks | Re-run `meldq all`; check flag rate falls below 2% |
| 8 | Panel land-area jump (R06) | 8.01 | Pre-load baseline land area; flag >30% change at entry | MEL data manager | 3 weeks | Re-run `meldq all`; check flag rate falls below 2% |
| 9 | GPS outside assigned district (R10) | 7.38 | Require GPS accuracy <20 m and geofence to the assigned district | MEL data manager | 2 weeks | Re-run `meldq all`; check flag rate falls below 2% |
| 10 | GPS at field office (R11) | 7.28 | Add geofence exclusion around offices; back-check affected interviews | Field supervisors | 2 weeks | Re-run `meldq all`; check flag rate falls below 2% |
| 11 | Sex differs from roster (T02) | 6.73 | Validate against registry at entry; train partner data clerks | Partner M&E officers | 1 month | Re-run `meldq all`; check flag rate falls below 2% |
| 12 | FCS/rCSI days out of range (R02) | 6.59 | Add constraint 0<=days<=7 (and soft warnings on totals) to the XLSForm; redeploy | MEL data manager | 1 week | Re-run `meldq all`; check flag rate falls below 2% |
| 13 | Pregnancy module skip-logic (R07) | 6.18 | Force form-version update; block submissions from old versions | MEL data manager | 1 week | Re-run `meldq all`; check flag rate falls below 2% |
| 14 | Submission before interview (R14) | 5.13 | Lock date to server time; flag mismatches at upload | MEL data manager | 2 weeks | Re-run `meldq all`; check flag rate falls below 2% |
| 15 | Interview outside fieldwork window (R12) | 4.97 | Lock date to device time; sync and verify device clocks daily | MEL data manager | 2 weeks | Re-run `meldq all`; check flag rate falls below 2% |
| 16 | Partner report vs raw log (X01) | 4.83 | Require partners to submit disaggregated raw logs with every report; MEL team computes totals | MEL lead | Next quarter | Re-run `meldq all`; check flag rate falls below 2% |
| 17 | Late submission (R13) | 4.47 | Introduce a 72-hour sync rule and a daily submission dashboard | Field supervisors | 1 week | Re-run `meldq all`; check flag rate falls below 2% |
| 18 | Outdated form version (R15) | 2.94 | Run a pre-fieldwork device audit | MEL data manager | 1 week | Re-run `meldq all`; check flag rate falls below 2% |
| 19 | Partner report arithmetic (X02) | 2.77 | Use locked report template with formula checks | Partner M&E officers | Next quarter | Re-run `meldq all`; check flag rate falls below 2% |
| 20 | Income missingness pattern (D02) | 2.08 | Use consumption/asset proxies, reorder question, report missingness rates; apply weighting or multiple imputation | MEL analyst | Before analysis | Re-run `meldq all`; check flag rate falls below 2% |
| 21 | Short interview duration (E01) | 2.08 | Re-interview all affected households; suspend enumerator pending review; reassess incentives | MEL lead | Immediate | Re-run `meldq all`; check flag rate falls below 2% |
| 22 | Abnormally low variance (E03) | 2.08 | Include in re-interview scope; review audio audits | MEL lead | Immediate | Re-run `meldq all`; check flag rate falls below 2% |
| 23 | Back-check discrepancy (B01) | 2.08 | Replace affected interviews; escalate per code of conduct | MEL lead | Immediate | Re-run `meldq all`; check flag rate falls below 2% |
| 24 | Cloned response vectors (E02) | 2.08 | Re-interview all affected households; suspend enumerator; exclude data from analysis until verified | MEL lead | Immediate | Re-run `meldq all`; check flag rate falls below 2% |
| 25 | Panel attrition (D03) | 2.08 | Intensify tracking protocols; apply attrition weights; run bounds sensitivity analysis | MEL lead | Before analysis | Re-run `meldq all`; check flag rate falls below 2% |
| 26 | Digit preference (heaping) (D01) | 1.39 | Use crop-cutting or measured land for a sub-sample; use local-unit calibration | Technical advisor | Next round | Re-run `meldq all`; check flag rate falls below 2% |
