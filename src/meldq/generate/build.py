import hashlib

import numpy as np
import pandas as pd

from .. import config as C
from ..schema import SURVEY_COLS
from . import clean, inject


def generate_tables(seed=C.SEED):
    """Return (tables, answer_key, truth). Fully deterministic for a given seed."""
    rng = np.random.default_rng(seed)
    hh = clean.build_households(rng)
    roster = clean.build_roster(hh, rng)
    truth = clean.build_survey_truth(hh, rng)
    training_clean = clean.build_training(hh, roster, rng)

    key = inject.Key()
    # E10: attrition -> observed panel (clean truth keeps every row)
    rid = truth["round"].map({r: i for i, r in enumerate(C.ROUNDS)})
    keep = rid <= truth["last_round"]
    obs = truth[keep].copy().reset_index(drop=True)
    key.add(10, "dataset", "hh_id,round", int((~keep).sum()),
            "Household drop-out hazard decreases with wealth (poorer HHs leave)")
    survey = inject.inject_survey(obs, rng, key)

    training = inject.inject_training(training_clean, roster, rng, key)
    reports = inject.build_reports(training, rng, key)
    donor = pd.DataFrame([dict(indicator="Farmers trained (cumulative)", period="2023Q2-2025Q1",
                               reported_value=int(reports.reported_total_trained.sum()))])

    fmt = lambda d: d.assign(**{c: d[c].dt.strftime("%Y-%m-%d") for c in d.columns if str(d[c].dtype).startswith("datetime")})
    tables = dict(survey=survey[SURVEY_COLS], training_log=training, hh_roster=roster,
                  partner_reports=reports, donor_report=donor)
    truth_out = truth[SURVEY_COLS + ["wealth_z"]]
    return tables, key.df(), truth_out


def write(tables, key, truth):
    C.RAW.mkdir(parents=True, exist_ok=True); C.KEYDIR.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        _csv(df).to_csv(C.RAW / f"{name}.csv", index=False)
    key.to_csv(C.KEYDIR / "answer_key.csv", index=False)
    _csv(truth).to_csv(C.KEYDIR / "truth_survey.csv", index=False)


def _csv(df):
    df = df.copy()
    for c in df.columns:
        if str(df[c].dtype).startswith("datetime"):
            df[c] = df[c].dt.strftime("%Y-%m-%d")
    return df


def fingerprint(tables):
    h = hashlib.sha256()
    for k in sorted(tables):
        h.update(_csv(tables[k]).to_csv(index=False).encode())
    return h.hexdigest()[:16]
