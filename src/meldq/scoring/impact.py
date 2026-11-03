"""Phase 7: how much do uncorrected data-quality problems bias the headline FCS result?"""
import numpy as np
import pandas as pd

from .scorecard import expand_enumerator_flags


def _wmean(d, w=None):
    return np.average(d.fcs_score, weights=w) if w is not None else d.fcs_score.mean()


def _estimate(d, w=None):
    out = {}
    for p in (0, 1):
        for r in ("baseline", "endline"):
            sub = d[(d.programme_participant == p) & (d["round"] == r)]
            out[(p, r)] = _wmean(sub, None if w is None else w.loc[sub.index])
    change_p = out[(1, "endline")] - out[(1, "baseline")]
    change_c = out[(0, "endline")] - out[(0, "baseline")]
    return dict(participants_change=change_p, comparison_change=change_c, did=change_p - change_c)


def impact_analysis(survey, truth, issues, remove_severity=("high",)):
    rows = []
    t = truth[truth["round"].isin(["baseline", "endline"])]
    rows.append(("A. Truth (clean, complete panel)", t, None))
    raw = survey[survey["round"].isin(["baseline", "endline"])]
    rows.append(("B. Raw data as delivered (no cleaning)", raw, None))

    rec = issues[(issues.level == "record") & (issues.table == "survey") & issues.severity.isin(remove_severity)]
    bad = set(rec.entity_key) | set(expand_enumerator_flags(issues, survey).entity_key)
    clean = survey[~survey.submission_id.isin(bad)].drop_duplicates(["hh_id", "round"])
    clean = clean[clean["round"].isin(["baseline", "endline"])]
    both = set(clean[clean["round"] == "baseline"].hh_id) & set(clean[clean["round"] == "endline"].hh_id)
    rows.append(("C. Cleaned (flagged records removed, matched panel)", clean[clean.hh_id.isin(both)], None))

    # D. add inverse-probability weights for attrition: cell = participant x baseline FCS quintile
    base = survey[survey["round"] == "baseline"].drop_duplicates("hh_id")
    base_ok = base[~base.submission_id.isin(bad)].copy()
    base_ok["q"] = pd.qcut(base_ok.fcs_score.clip(0, 112), 5, labels=False, duplicates="drop")
    base_ok["kept"] = base_ok.hh_id.isin(both)
    ret = base_ok.groupby(["programme_participant", "q"]).kept.mean().rename("ret").reset_index()
    cell = base_ok[["hh_id", "programme_participant", "q"]].merge(ret, on=["programme_participant", "q"])
    cm = clean[clean.hh_id.isin(both)].merge(cell[["hh_id", "ret"]], on="hh_id", how="left")
    cm.index = clean[clean.hh_id.isin(both)].index
    rows.append(("D. Cleaned + attrition weights (IPW)", cm, 1 / cm["ret"]))

    res = []
    for name, d, w in rows:
        e = _estimate(d, w)
        res.append(dict(scenario=name, hh_rounds=len(d), **{k: round(v, 2) for k, v in e.items()}))
    out = pd.DataFrame(res)
    truth_did = out.iloc[0]["did"]
    out["did_bias_vs_truth"] = (out["did"] - truth_did).round(2)
    truth_pc = out.iloc[0]["participants_change"]
    out["participant_change_bias"] = (out["participants_change"] - truth_pc).round(2)
    return out
