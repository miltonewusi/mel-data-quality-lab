# Answer key (spoiler warning)

`answer_key.csv` lists every injected error (type, table, entity, field). `truth_survey.csv` is the clean, complete panel before attrition and errors.

**Training mode:** if you want to practise as a DQA analyst, do not open these files until you have written your own issue log from `data/raw/`.
The pipeline reads them only for scoring (`meldq check`), the simulated back-check, and the impact-of-bias analysis.
