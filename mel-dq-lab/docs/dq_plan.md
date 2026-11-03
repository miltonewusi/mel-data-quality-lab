# Data Quality Plan

## 1. Standards and dimensions
| Dimension | Source | Operational definition in this lab |
|---|---|---|
| Validity | USAID ADS 201 | Data measure what the indicator intends: values in range, units correct, definitions followed |
| Integrity | USAID ADS 201; ISO/IEC 25012 (consistency, uniqueness) | Data protected from error and duplication; internally consistent; skip logic respected |
| Precision | USAID ADS 201 | Data have sufficient detail: no digit preference, adequate disaggregation |
| Reliability | USAID ADS 201 | Consistent collection over time and across enumerators; fabrication and satisficing detected |
| Timeliness | USAID ADS 201 | Collected within the planned window and submitted promptly |
| Completeness | ISO/IEC 25012 / DAMA-DMBOK | Required values present; missingness mechanism understood |
| Representativeness | Survey practice | Analytic sample still resembles the target population (attrition) |

Other anchors: DAMA-DMBOK data quality management cycle (plan-deploy-monitor-act); WFP VAM and FANTA indicator guidance (see PIRS);
KoboToolbox/ODK form constraints; IPA/J-PAL-style back-check protocols; responsible-data principles (synthetic data only).

## 2. Scorecard thresholds
GREEN >=98% of records pass; AMBER 95-98%; RED <95% or any dataset-level flag. Severity: **high** = value unusable until resolved;
**medium** = verify (back-check or supervisor review); **low** = informational.

## 3. Back-check protocol
- 10% of unique HH-rounds re-interviewed; 50% selected by risk score (flag severity + enumerator-level flags), 50% random.
- 5 key items compared: FCS (>10 points), rCSI (>6 points), practices (>=2 differ), household size, land area.
- A record has a **major discrepancy** when >=2 items differ. An enumerator is escalated when >=2 of their re-interviewed households show a major discrepancy (min. 8 re-interviews).
- Lesson from the simulation: random back-check samples of <10 per enumerator can miss partial fabrication; stratify by enumerator.

## 4. Roles
MEL lead (owner, escalation) / MEL data manager (form constraints, server rules) / Field supervisors (back-checks) / Partner M&E officers (registers and reports) / Technical advisor (measurement methods).

## 5. Check catalogue
| ID | Check | Table | Level | Dimension | Severity | Indicator | Rule |
|---|---|---|---|---|---|---|---|
| R01 | Duplicate HH-round | survey | record | Integrity | high | Cross-cutting (survey) | More than one submission for the same household and round |
| R02 | FCS/rCSI days out of range | survey | record | Validity | high | FCS | Food-group or coping days outside 0-7 |
| R03 | Demographics out of range | survey | record | Validity | high | Cross-cutting (survey) | HH size outside 1-20 or respondent age outside 15-95 |
| R04 | Yield outside plausible range | survey | record | Validity | high | Maize yield | Maize yield outside 150-8,000 kg/ha |
| R05 | Yield peer outlier | survey | record | Validity | medium | Maize yield | Robust z-score >3.5 vs district-round median |
| R06 | Panel land-area jump | survey | record | Validity | medium | Maize yield | Land area >40% from the household's own median across rounds |
| R07 | Pregnancy module skip-logic | survey | record | Integrity | medium | Cross-cutting (survey) | Pregnancy answer for non-eligible respondent |
| R08 | HHS frequency skip-logic | survey | record | Integrity | medium | HHS | Frequency answered when occurrence=No, or missing when Yes |
| R09 | rCSI straight-lining | survey | record | Reliability | medium | rCSI | All five rCSI items identical and non-zero |
| R10 | GPS outside assigned district | survey | record | Reliability | medium | Cross-cutting (survey) | Coordinates outside the district bounding box |
| R11 | GPS at field office | survey | record | Reliability | medium | Cross-cutting (survey) | Coordinates within 300 m of the district field office |
| R12 | Interview outside fieldwork window | survey | record | Timeliness | medium | Cross-cutting (survey) | Interview date outside round window (+/-7 days) or before programme start |
| R13 | Late submission | survey | record | Timeliness | low | Cross-cutting (survey) | Submitted >7 days after interview |
| R14 | Submission before interview | survey | record | Timeliness | medium | Cross-cutting (survey) | Submission date earlier than interview date |
| R15 | Outdated form version | survey | record | Integrity | low | Cross-cutting (survey) | Submission from a form version other than the latest |
| E01 | Short interview duration | survey | enumerator | Reliability | high | Cross-cutting (survey) | Enumerator-round median duration <60% of overall median |
| E02 | Cloned response vectors | survey | enumerator | Reliability | high | Cross-cutting (survey) | >20% of an enumerator-round's records share an identical FCS+rCSI answer vector with >=2 others |
| E03 | Abnormally low variance | survey | enumerator | Reliability | high | Cross-cutting (survey) | SD of FCS in an enumerator-round <50% of the pooled SD |
| B01 | Back-check discrepancy | survey | enumerator | Reliability | high | Cross-cutting (survey) | Re-interview disagrees with original on >=30% of key items |
| D01 | Digit preference (heaping) | survey | dataset | Precision | medium | Maize yield | Excess share of land at 0.5 ha multiples / production at 50 kg multiples |
| D02 | Income missingness pattern | survey | dataset | Completeness | high | Income / VSLA savings | >=5% missing and missingness varies with a wealth proxy |
| D03 | Panel attrition | survey | dataset | Representativeness | high | FCS | Cumulative attrition >10% or differential by baseline welfare |
| T01 | Fuzzy beneficiary duplicate | training_log | record | Integrity | high | Farmers trained | Similar name, same sex, age +/-1, same district, different partner |
| T02 | Sex differs from roster | training_log | record | Validity | medium | Farmers trained | Sex in training log differs from household roster |
| X01 | Partner report vs raw log | partner_reports | record | Integrity | high | Farmers trained | Reported total differs from raw count by >5% |
| X02 | Partner report arithmetic | partner_reports | record | Integrity | medium | Farmers trained | Female + male differs from reported total |

## 6. Cadence
Daily: submission and duration dashboard (R13, E01). Weekly: record-level checks and enumerator review. Per round: back-checks, dataset-level tests, scorecard.
Quarterly: partner report reconciliation and cross-partner de-duplication.
