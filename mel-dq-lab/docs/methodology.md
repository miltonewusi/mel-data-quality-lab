# Methodology

## Generator
1. **Clean truth** (`generate/clean.py`): 1,200 households with a latent wealth score z. Food consumption, coping, hunger, practices, yield, income and savings are
   generated from z, a common trend and a programme effect (participants only) that grows to roughly +4 FCS points at endline.
   The full clean panel is stored in `data/answer_key/truth_survey.csv`.
2. **Attrition** (error 10): households leave with a hazard that falls with wealth (about 18% cumulative by endline).
3. **Injection** (`generate/inject.py`): 14 error types injected at the rates in `config.RATES`; every injection is logged in `answer_key.csv`.
   Record-level injections are mutually exclusive (a record carries one record-level error) so that scoring is unambiguous.
4. All randomness comes from one seeded NumPy generator: same seed, same data (tested).

## Detection
Rules are declared once in `checks/base.py` with their DQ dimension, severity and target error type. Three levels:
record (ranges, skip logic, GPS, dates), enumerator (duration, cloning, variance, back-check), dataset (heaping, missingness, attrition).
Training-register checks use fuzzy matching (`rapidfuzz` token-sort ratio >= 88, same district and sex, age +/-1, different partner).

## Scoring
- **Recall** per error type = injected entities flagged by a check mapped to that type / injected entities.
- **Precision** = flagged entities that coincide with *any* injected problem in the same table and level / flagged entities. Natural tails are therefore false positives.
- Dataset-level types are binary (detected or not).
- `meldq robustness --n 20` repeats generation and scoring over 20 seeds to avoid reporting a lucky draw.

## Impact analysis
Compares the baseline-to-endline FCS change and difference-in-differences under: A truth, B raw, C cleaned, D cleaned + inverse-probability attrition weights
(cells: participant status x baseline FCS quintile).

## Limitations
Synthetic errors are cleaner than real ones; checks were written knowing the error catalogue; thresholds are tuned to this dataset; the back-check is simulated.
Use the numbers as a teaching benchmark, not as expected real-world performance.

## Responsible data
No real persons, organisations or locations. Names are drawn from short generic lists; coordinates fall in fictional district boxes.
