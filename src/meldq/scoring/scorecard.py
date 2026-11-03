"""Phase 5: DQ scorecard by indicator x dimension (green >=98%, amber 95-98%, red <95% or any dataset-level flag)."""
import pandas as pd

from ..checks.base import REGISTRY


def _rating(pass_rate, dataset_flags):
    if dataset_flags:
        return "RED"
    return "GREEN" if pass_rate >= 0.98 else ("AMBER" if pass_rate >= 0.95 else "RED")


def expand_enumerator_flags(issues, survey):
    en = issues[(issues.level == "enumerator") & (issues.table == "survey")]
    frames = []
    for r in en.itertuples():
        m = survey.enumerator_id == r.entity_key
        if r.round not in ("", None) and not pd.isna(r.round):
            m &= survey["round"] == r.round
        ids = survey.loc[m, "submission_id"]
        frames.append(pd.DataFrame({"check_id": r.check_id, "table": "survey", "entity_key": ids.values}))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["check_id", "table", "entity_key"])


def scorecard(tables, issues):
    pops = {"survey": len(tables["survey"]), "training_log": len(tables["training_log"]), "partner_reports": len(tables["partner_reports"])}
    rec = issues[issues.level == "record"][["check_id", "table", "entity_key"]]
    rec = pd.concat([rec, expand_enumerator_flags(issues, tables["survey"])], ignore_index=True)
    rec["indicator"] = rec.check_id.map(lambda c: REGISTRY[c].indicator)
    rec["dimension"] = rec.check_id.map(lambda c: REGISTRY[c].dimension)
    ds = issues[issues.level == "dataset"].copy()
    rows = []
    combos = {(c.table, c.indicator, c.dimension) for c in REGISTRY.values()}
    for tbl, ind, dim in sorted(combos):
        sub = rec[(rec.table == tbl) & (rec.indicator == ind) & (rec.dimension == dim)]
        n_flag = sub.entity_key.nunique()
        dflags = int(((ds.table == tbl) & (ds.indicator == ind) & (ds.dq_dimension == dim)).sum())
        pr = 1 - n_flag / pops[tbl]
        rows.append(dict(table=tbl, indicator=ind, dimension=dim, records_assessed=pops[tbl], records_flagged=n_flag,
                         pass_rate=round(pr, 4), dataset_level_flags=dflags, rating=_rating(pr, dflags)))
    return pd.DataFrame(rows)


def dimension_summary(card):
    g = card.groupby("dimension").agg(worst_pass_rate=("pass_rate", "min"), dataset_flags=("dataset_level_flags", "sum")).reset_index()
    g["rating"] = [_rating(a, b) for a, b in zip(g.worst_pass_rate, g.dataset_flags)]
    return g
