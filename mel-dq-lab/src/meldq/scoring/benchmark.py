"""Phase 6: score the checks against the hidden answer key."""
import numpy as np
import pandas as pd

from .. import config as C


def _maps(issues):
    m = issues.copy()
    m["maps"] = m.maps_to.fillna("").apply(lambda x: [int(i) for i in str(x).split(";") if i])
    return m


def benchmark(key, issues, recall_target=0.5):
    iss = _maps(issues)
    universe = {k: set(g.entity_key) for k, g in key.groupby(["table", "level"])}
    rows = []
    for eid, g in key.groupby("error_id"):
        name, dim, level, table = C.ERRORS[eid]
        sel = iss[iss.maps.apply(lambda m: eid in m) & (iss.table == table) & (iss.level == level)]
        flagged, truth = set(sel.entity_key), set(g.entity_key)
        if level == "dataset":
            rec, prec, tp = float(len(flagged) > 0), np.nan, int(len(flagged) > 0)
        else:
            tp = len(flagged & truth)
            rec = tp / len(truth)
            prec = len(flagged & universe[(table, level)]) / len(flagged) if flagged else np.nan
        rows.append(dict(error_id=eid, error=name, dimension=dim, level=level, injected=int(g.n_affected.sum()) if level == "dataset" else len(truth),
                         flagged=len(flagged), true_positives=tp, recall=round(rec, 3),
                         precision=None if np.isnan(prec) else round(prec, 3),
                         detected=rec >= recall_target, checks=",".join(sorted(sel.check_id.unique()))))
    return pd.DataFrame(rows)


def check_performance(key, issues):
    universe = {k: set(g.entity_key) for k, g in key.groupby(["table", "level"])}
    rows = []
    for cid, g in issues.groupby("check_id"):
        ents = set(g.entity_key)
        lvl, tbl = g.level.iloc[0], g.table.iloc[0]
        u = universe.get((tbl, lvl), set())
        rows.append(dict(check_id=cid, check_name=g.check_name.iloc[0], level=lvl, flagged=len(ents),
                         injected_issue_hits=len(ents & u) if lvl != "dataset" else np.nan,
                         precision=round(len(ents & u) / len(ents), 3) if (ents and lvl != "dataset") else np.nan))
    return pd.DataFrame(rows).sort_values("check_id")
