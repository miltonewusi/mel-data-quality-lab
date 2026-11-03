import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from .base import emit

NAME_THRESHOLD = 88


def training_checks(t, roster):
    out = []
    t = t.copy()
    t["name_norm"] = t.full_name.str.lower().str.replace(r"[^a-z ]", "", regex=True).str.strip()
    flagged = set()
    for (_, _), g in t.groupby(["district", "sex"]):
        g = g.reset_index(drop=True)
        if len(g) < 2:
            continue
        m = process.cdist(g.name_norm.tolist(), g.name_norm.tolist(), scorer=fuzz.token_sort_ratio, workers=1)
        for i, j in zip(*np.where(np.triu(m >= NAME_THRESHOLD, k=1))):
            a, b = g.loc[i], g.loc[j]
            if a.partner == b.partner or abs(int(a.age) - int(b.age)) > 1:
                continue
            later = a if (a.training_date, a.participant_id) > (b.training_date, b.participant_id) else b
            flagged.add(later.participant_id)
    out.append(emit("T01", sorted(flagged), "Probable same person registered by both partners", "full_name"))

    lk = t[t.hh_id.notna()].merge(roster, on=["hh_id", "member_id"], how="left", suffixes=("", "_roster"))
    bad = lk[lk.sex != lk.sex_roster]
    out.append(emit("T02", bad.participant_id, "Sex differs from household roster", "sex"))
    return out, sorted(flagged)


def report_checks(reports, t):
    out = []
    raw = t.groupby(["partner", "quarter"]).agg(raw_total=("participant_id", "count")).reset_index()
    m = reports.merge(raw, on=["partner", "quarter"], how="left")
    m["entity"] = m.partner + "|" + m.quarter
    m["rel"] = (m.reported_total_trained - m.raw_total) / m.raw_total
    bad = m[m.rel.abs() > 0.05]
    out.append(emit("X01", bad.entity, "Reported total differs from raw log by >5%", "reported_total_trained"))
    bad2 = m[m.reported_female + m.reported_male != m.reported_total_trained]
    out.append(emit("X02", bad2.entity, "Female + male != total", "reported_female,reported_male"))
    return out, m


def reconcile(reports, donor, t, dup_ids):
    raw_total = len(t)
    unique = raw_total - len(dup_ids)
    partner_sum = int(reports.reported_total_trained.sum())
    donor_val = int(donor.reported_value.iloc[0])
    return pd.DataFrame([
        dict(level="Raw training log (all rows)", value=raw_total),
        dict(level="Partner reports (sum of quarterly totals)", value=partner_sum),
        dict(level="Donor-reported figure", value=donor_val),
        dict(level="Estimated unique farmers (after fuzzy de-duplication)", value=unique),
        dict(level="Over-reporting vs unique (donor figure)", value=donor_val - unique),
        dict(level="Over-reporting vs unique (%)", value=round((donor_val - unique) / unique * 100, 1)),
    ])
