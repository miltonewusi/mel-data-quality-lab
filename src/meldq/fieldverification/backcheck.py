"""Phase 3: risk-based back-check sample + SIMULATED re-interviews.

In a real project the re-interview comes from a supervisor visiting the household. Here the 'field'
is simulated by reading the hidden truth file and adding realistic recall/measurement noise.
"""
import numpy as np
import pandas as pd

from ..checks.base import emit
from ..schema import FCS_COLS, PRACTICE_COLS

BUDGET = 0.10          # share of submissions to re-interview (industry rule of thumb: 10%)
RISK_SHARE = 0.5       # half the budget goes to the highest-risk submissions, half is random


def design_sample(survey, issues, seed=1):
    rng = np.random.default_rng(seed)
    s = survey.drop_duplicates(["hh_id", "round"]).copy()
    rec = issues[issues.level == "record"]
    w = {"high": 3, "medium": 2, "low": 1}
    risk = rec[rec.table == "survey"].assign(w=lambda d: d.severity.map(w)).groupby("entity_key").w.sum()
    s["risk"] = s.submission_id.map(risk).fillna(0)
    enum = issues[(issues.level == "enumerator") & (issues.table == "survey")]
    flagged_er = set(zip(enum.entity_key, enum["round"]))
    s["enum_flag"] = [(e, r) in flagged_er for e, r in zip(s.enumerator_id, s["round"])]
    s["risk"] += 4 * s.enum_flag
    n = int(round(len(s) * BUDGET))
    n_risk = int(n * RISK_SHARE)
    top = s.sort_values("risk", ascending=False).head(n_risk)
    rest = s.drop(top.index)
    rnd = rest.sample(n - n_risk, random_state=int(rng.integers(1e9)))
    out = pd.concat([top.assign(stratum="risk-based"), rnd.assign(stratum="random")])
    return out[["submission_id", "hh_id", "round", "enumerator_id", "district", "risk", "stratum"]]


def simulate_reinterviews(sample, survey, truth, seed=2):
    rng = np.random.default_rng(seed)
    orig = survey.set_index("submission_id")
    tr = truth.set_index(["hh_id", "round"])
    rows = []
    for r in sample.itertuples():
        t = tr.loc[(r.hh_id, r.round)]
        o = orig.loc[r.submission_id]
        fcs_re = t["fcs_score"] + rng.normal(0, 3)
        prac_diff = sum(int(o[c] != (t[c] if rng.random() > 0.05 else 1 - t[c])) for c in PRACTICE_COLS)
        items = [abs(o["fcs_score"] - fcs_re) > 10,
                 abs(o["rcsi_score"] - (t["rcsi_score"] + rng.normal(0, 2))) > 6,
                 prac_diff >= 2,
                 o["hh_size"] != t["hh_size"],
                 abs(o["land_area_ha"] - t["land_area_ha"] * np.exp(rng.normal(0, .05))) > 0.5 * max(t["land_area_ha"], .2)]
        rows.append(dict(submission_id=r.submission_id, enumerator_id=r.enumerator_id, round=r.round,
                         items_failed=int(sum(items)), items_checked=len(items)))
    return pd.DataFrame(rows)


def enumerator_discrepancy(results, min_major=2, min_n=8):
    """Flag an enumerator when >=2 of their re-interviewed households show a MAJOR discrepancy (>=2 of 5 key items differ).
    Honest enumerators almost never produce a major discrepancy, so even one or two are diagnostic."""
    r = results.assign(major=results.items_failed >= 2)
    g = r.groupby("enumerator_id").agg(n=("submission_id", "count"), major=("major", "sum"),
                                       failed=("items_failed", "sum"), checked=("items_checked", "sum")).reset_index()
    g["discrepancy_rate"] = (g.failed / g.checked).round(3)
    g["major_share"] = (g.major / g.n).round(3)
    bad = g[(g.n >= min_n) & (g.major >= min_major)]
    return g, emit("B01", bad.enumerator_id, f">= {min_major} re-interviews with major discrepancies", "back-check items", [""] * len(bad))
