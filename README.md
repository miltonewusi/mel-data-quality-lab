# mel-dq-lab

[![ci](https://github.com/YOUR-USER/mel-dq-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR-USER/mel-dq-lab/actions)
![python](https://img.shields.io/badge/python-3.10%2B-blue) ![license](https://img.shields.io/badge/code-MIT-green) ![docs](https://img.shields.io/badge/docs-CC--BY--4.0-lightgrey)

**A reproducible data-quality lab for food security, agriculture and livelihoods MEL.**
It simulates a donor-funded smallholder programme, deliberately seeds 14 realistic data-quality problems into the data, keeps a hidden answer key, and then runs a
real-world DQA workflow (automated validation, enumerator analysis, back-check design, reporting reconciliation, scorecard, corrective action plan) and **scores the workflow against the answer key**.

> All data are synthetic. No real persons, organisations or locations are represented.

## Why this exists
Real MEL data cannot be shared, and clean public datasets teach nothing about data quality. Here you can practise on messy data where the truth is known,
so detection performance (recall, precision) and the effect of errors on the headline result are *measurable*.

## The simulated programme
**RLFSP** (fictional): 4 districts, 2 implementing partners (overlapping in 2 districts), 1,200-household panel (baseline/midline/endline), 24 enumerators, partner training registers and a donor-reported figure.
Indicators: FCS, rCSI, HHS, practice adoption, maize yield, income/VSLA savings, farmers trained. See `docs/programme_logframe.md` and `docs/PIRS/`.

## Quick start
```bash
pip install -e ".[dev]"
meldq all            # generate data -> run checks -> score -> write reports/
pytest -q            # 22 tests
meldq robustness --n 20   # repeat over 20 seeds (about 1 minute)
```
Outputs: `data/raw/`, `data/answer_key/`, and in `reports/`: `dqa_report.md`, `dq_scorecard.csv`, `issue_log.csv`, `corrective_action_plan.md`, `benchmark.csv`, `impact_of_dq.csv`, `robustness.csv`.

### Use it as a training exercise (challenge mode)
1. Do **not** open `data/answer_key/`.
2. Open `data/raw/` and write your own issue log using `docs/dq_plan.md` and the data dictionary.
3. Run `meldq check`, then compare your findings with `reports/benchmark.csv`.

## The 14 seeded errors
Duplicates; enumerator fabrication (blatant *and* subtle partial); heaping; unit mix-ups; impossible values; skip-logic violations; straight-lining; implausible GPS;
income missing-not-at-random; differential attrition; cross-partner beneficiary double counting (name variants); date/timeliness problems; partner reports that do not match raw logs; sex inconsistent with roster.
Full catalogue with DQ dimension and level: `src/meldq/config.py` (`ERRORS`).

## Results
Default seed, plus a 20-seed robustness run (`reports/robustness.csv`):

| Error type | Level | Mean recall (20 seeds) | Range | Mean precision |
|---|---|---|---|---|
| Duplicate records | record | 100% | 100-100% | 100% |
| Impossible values | record | 100% | 100-100% | 96% |
| Skip-logic, GPS, dates, straight-lining, partner reports, sex vs roster | record | 100% | 100-100% | 97-100% |
| Unit mix-ups | record | 96% | 93-100% | 82% |
| Beneficiary double counting (fuzzy match) | record | 76% | 67-86% | 83% |
| Enumerator fabrication (2 enumerators: one blatant, one partial) | enumerator | 65% | 50-100% | 100% |
| Heaping, income MNAR, differential attrition | dataset | detected in 20/20 seeds | n/a | n/a |

What this shows:
- **Deterministic rules (ranges, skip logic, duplicates, dates) catch what they are designed to catch, by construction.** The interesting results are in the other rows.
- **Fuzzy matching misses name variants** such as initials-only entries, and the false-positive rate is not zero.
- **The partial fabricator is mostly invisible to automated checks** and is found only when enough of their interviews are back-checked: the number of re-interviews per enumerator matters.
- Errors also bias the headline: see `reports/dqa_report.md` section 7 for FCS under truth / raw / cleaned / attrition-weighted analysis. In the default run the raw FCS change among participants is overstated by roughly 0.3 points and cleaning removes about a quarter of usable household-rounds; effects are modest here and depend on the injection rates in `config.RATES`, which you can change.
- Cumulative donor-reported "farmers trained" exceeds the estimated unique count by about 6% (double counting plus inflated partner totals).

## Repository layout
```
docs/            logframe, PIRS x8, DQ plan (standards, thresholds, check catalogue), methodology, data dictionary
data/raw/        synthetic survey, training register, roster, partner and donor reports
data/answer_key/ injected-error key + clean truth panel (spoilers)
src/meldq/
  generate/      clean truth data + error injectors + answer key
  checks/        rule registry and record / enumerator / dataset / reconciliation checks
  fieldverification/  risk-based back-check sampling and simulated re-interviews
  scoring/       precision/recall benchmark, DQ scorecard, impact-of-bias analysis
  reporting.py   DQA report, issue log, corrective action plan
tests/           pytest suite (determinism, recall floors, no false positives on clean truth, dictionary coverage)
```

## Standards and references
USAID ADS 201 data quality dimensions (validity, integrity, precision, reliability, timeliness); ISO/IEC 25012 and DAMA-DMBOK (completeness, uniqueness, consistency);
Performance Indicator Reference Sheets; WFP VAM guidance (FCS, rCSI); FANTA Household Hunger Scale Indicator Guide; ODK/KoboToolbox-style form constraints;
10% back-check protocol; responsible-data principles. Verify indicator definitions against current official guidance before using them in real work.

## Limitations
Errors are cleaner and more independent than in real life; checks were written with knowledge of the error catalogue; thresholds are tuned on this data; the back-check is simulated from ground truth.
Treat the numbers as a teaching benchmark, not as expected real-world performance.

## Roadmap
Output 2 (inputs / post-distribution monitoring); Pandera or Great Expectations suite alongside the pandas rules; walkthrough notebooks; Streamlit scorecard; R port; enumerator-stratified back-check design; missing-data imputation exercise.

## Licence and citation
Code MIT; docs CC BY 4.0 (`LICENSE-DOCS.md`). Cite via `CITATION.cff`.
