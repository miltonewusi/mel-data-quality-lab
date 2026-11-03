"""Step 2 of the generator: inject the 14 catalogued errors and record each one in the answer key."""
import numpy as np
import pandas as pd

from .. import config as C
from ..schema import FCS_COLS, RCSI_COLS
from .clean import derive, logistic, FCS_MU, RCSI_MU

R = C.RATES
FAB_FCS = [[6, 2, 4, 1, 1, 1, 4, 5], [7, 3, 4, 2, 1, 1, 3, 4], [6, 2, 5, 1, 0, 1, 4, 5], [7, 2, 4, 1, 1, 0, 3, 5]]
FAB_RCSI = [[3, 1, 3, 1, 2], [2, 1, 3, 0, 2], [3, 2, 3, 1, 2]]


class Key:
    def __init__(self):
        self.rows = []

    def add(self, eid, entity, field="", n=1, note=""):
        name, dim, level, table = C.ERRORS[eid]
        self.rows.append(dict(error_id=eid, error_name=name, dq_dimension=dim, table=table, level=level,
                              entity_key=entity, field=field, n_affected=n, note=note))

    def df(self):
        return pd.DataFrame(self.rows).sort_values(["error_id", "entity_key"]).reset_index(drop=True)


def _pick(rng, pool, rate=None, n=None):
    pool = np.asarray(pool)
    k = n if n is not None else int(round(len(pool) * rate))
    return rng.choice(pool, size=min(k, len(pool)), replace=False) if k > 0 else np.array([], dtype=int)


def inject_survey(obs, rng, key):
    s = obs.copy()
    sid = lambda i: s.at[i, "submission_id"]
    special = s["enumerator_id"].isin([C.FABRICATOR, C.SUBTLE_FAB, C.GPS_OFFICE_ENUM])
    used = set()

    def pool(extra=None):
        m = ~special & ~s.index.isin(list(used))
        if extra is not None:
            m &= extra
        return s.index[m]

    # E2 fabrication ------------------------------------------------------------------------------
    idx = s.index[(s.enumerator_id == C.FABRICATOR) & s["round"].isin(C.FAB_ROUNDS)]
    for i in idx:
        s.loc[i, FCS_COLS] = _vec(rng, FAB_FCS)
        s.loc[i, RCSI_COLS] = _vec(rng, FAB_RCSI, hi=7)
        s.loc[i, ["hhs_q1", "hhs_q2", "hhs_q3"]] = 0
        s.loc[i, ["hhs_f1", "hhs_f2", "hhs_f3"]] = np.nan
        s.at[i, "duration_min"] = round(float(rng.uniform(8, 13)), 1)
    key.add(2, C.FABRICATOR, "fcs_*, rcsi_*, duration_min", len(idx),
            f"Rounds {', '.join(C.FAB_ROUNDS)}: cloned response templates, 8-13 min interviews")

    # E2b subtle partial fabrication: ~35% of one enumerator's records, plausible but independent of the household
    from ..schema import PRACTICE_COLS
    cand = s.index[s.enumerator_id == C.SUBTLE_FAB]
    sel = _pick(rng, cand, C.SUBTLE_SHARE)
    for i in sel:
        s.loc[i, FCS_COLS] = np.clip(np.round(rng.normal(FCS_MU, 0.8)), 0, 7).astype(int)
        s.loc[i, RCSI_COLS] = np.clip(np.round(rng.normal(RCSI_MU, 1.0)), 0, 7).astype(int)
        s.loc[i, PRACTICE_COLS] = (rng.random(len(PRACTICE_COLS)) < 0.45).astype(int)
        s.at[i, "duration_min"] = round(float(rng.normal(27, 3)), 1)
    key.add(2, C.SUBTLE_FAB, "fcs_*, rcsi_*, prac_*", len(sel),
            f"{C.SUBTLE_SHARE:.0%} of records fabricated with plausible values; only detectable by field verification")

    # E8a GPS at office -----------------------------------------------------------------------------
    idx = s.index[(s.enumerator_id == C.GPS_OFFICE_ENUM) & s["round"].isin(C.GPS_OFFICE_ROUNDS)]
    for i in idx:
        o = C.DISTRICTS[s.at[i, "district"]]["office"]
        s.at[i, "gps_lat"], s.at[i, "gps_lon"] = round(o[0] + rng.normal(0, 2e-4), 5), round(o[1] + rng.normal(0, 2e-4), 5)
        key.add(8, sid(i), "gps_lat,gps_lon", note="Coordinates at field office")
    used.update(idx)

    # E3 heaping (dataset-level) ----------------------------------------------------------------------
    h = _pick(rng, pool(), R["heap"])
    land_new = np.maximum(0.5, np.round(s.loc[h, "land_area_ha"] * 2) / 2)
    scale = land_new / s.loc[h, "land_area_ha"]
    s.loc[h, "maize_area_ha"] = np.maximum(np.round(s.loc[h, "maize_area_ha"] * scale, 2), 0.05)
    s.loc[h, "land_area_ha"] = land_new
    s.loc[h, "maize_prod_kg"] = np.maximum(50, np.round(s.loc[h, "maize_prod_kg"] / 50) * 50).astype(int)
    key.add(3, "dataset", "land_area_ha, maize_prod_kg", len(h), "Land rounded to 0.5 ha, production to 50 kg")

    # E4 unit mix-ups -------------------------------------------------------------------------------------
    u = _pick(rng, pool(), R["unit"]); used.update(u)
    for j, i in enumerate(u):
        if j % 2 == 0:  # entered in acres, form assumes hectares
            s.at[i, "land_area_ha"] = round(s.at[i, "land_area_ha"] * 2.471, 2)
            s.at[i, "maize_area_ha"] = round(s.at[i, "maize_area_ha"] * 2.471, 2)
            key.add(4, sid(i), "land_area_ha,maize_area_ha", note="Acres entered as hectares")
        else:           # entered in 50-kg bags, form assumes kg
            s.at[i, "maize_prod_kg"] = max(1, int(round(s.at[i, "maize_prod_kg"] / 50)))
            key.add(4, sid(i), "maize_prod_kg", note="50-kg bags entered as kg")

    # E5 impossible values --------------------------------------------------------------------------------
    p5 = _pick(rng, pool(), R["impossible"]); used.update(p5)
    for i in p5:
        k = int(rng.integers(0, 4))
        if k == 0:
            c = str(rng.choice(FCS_COLS)); s.at[i, c] = int(rng.choice([8, 9, 10, 14, 77])); f = c
        elif k == 1:
            s.at[i, "maize_prod_kg"] = int(s.at[i, "maize_area_ha"] * rng.uniform(22000, 30000)); f = "maize_prod_kg"
        elif k == 2:
            s.at[i, "hh_size"] = int(rng.choice([0, 35, 99])); f = "hh_size"
        else:
            s.at[i, "resp_age"] = int(rng.choice([5, 150, 999])); f = "resp_age"
        key.add(5, sid(i), f, note="Out-of-range value")

    # E6 skip-logic ------------------------------------------------------------------------------------------
    males = pool(s.resp_sex == "M")
    for i in _pick(rng, males, R["skip_preg"]):
        s.at[i, "resp_pregnant"] = float(rng.integers(0, 2)); s.at[i, "form_version"] = "v1.0"
        used.add(i); key.add(6, sid(i), "resp_pregnant", note="Pregnancy module answered by male respondent (old form v1.0)")
    for i in _pick(rng, pool(s.hhs_q1 == 0), R["skip_hhs"] * 3):
        s.at[i, "hhs_f1"] = float(rng.integers(1, 4)); used.add(i)
        key.add(6, sid(i), "hhs_f1", note="HHS frequency answered though occurrence = No")

    # E7 straight-lining -------------------------------------------------------------------------------------
    for i in _pick(rng, pool(), R["straight"]):
        s.loc[i, RCSI_COLS] = int(rng.integers(3, 8)); used.add(i)
        key.add(7, sid(i), "rcsi_*", note="All five rCSI items identical")

    # E8b GPS outside district -------------------------------------------------------------------------------
    for i in _pick(rng, pool(), R["gps_out"]):
        other = [d for d in C.DISTRICTS if d != s.at[i, "district"]]
        b = C.DISTRICTS[str(rng.choice(other))]
        s.at[i, "gps_lat"], s.at[i, "gps_lon"] = round(rng.uniform(*b["lat"]), 5), round(rng.uniform(*b["lon"]), 5)
        used.add(i); key.add(8, sid(i), "gps_lat,gps_lon", note="Coordinates inside another district")

    # E12 dates ----------------------------------------------------------------------------------------------
    for i in _pick(rng, pool(s["round"] == "baseline"), R["date_pre"]):
        lag = (s.at[i, "submission_date"] - s.at[i, "interview_date"]).days
        s.at[i, "interview_date"] = pd.Timestamp("2022-08-01") + pd.Timedelta(days=int(rng.integers(0, 200)))
        s.at[i, "submission_date"] = s.at[i, "interview_date"] + pd.Timedelta(days=lag)
        used.add(i); key.add(12, sid(i), "interview_date", note="Interview before programme start")
    for i in _pick(rng, pool(), R["date_late"]):
        s.at[i, "submission_date"] = s.at[i, "interview_date"] + pd.Timedelta(days=int(rng.integers(10, 60)))
        used.add(i); key.add(12, sid(i), "submission_date", note="Late submission (>7 days)")
    for i in _pick(rng, pool(), R["date_after"]):
        s.at[i, "submission_date"] = s.at[i, "interview_date"] - pd.Timedelta(days=int(rng.integers(1, 10)))
        used.add(i); key.add(12, sid(i), "submission_date", note="Submitted before interview date")

    # E9 income missing-not-at-random (dataset-level) -----------------------------------------------------
    li = np.log(s["income_usd_month"])
    zi = (li - li.mean()) / li.std()
    miss = rng.random(len(s)) < logistic(-2.6 + 1.3 * zi)
    s.loc[miss, "income_usd_month"] = np.nan
    key.add(9, "dataset", "income_usd_month", int(miss.sum()), "Probability of missing rises with income")

    s = derive(s)

    # E1 duplicates (last, so copies are exact) -------------------------------------------------------------
    d = s.loc[_pick(rng, pool(), R["dup"])].copy()
    nxt = int(s["submission_id"].str[1:].astype(int).max())
    d["submission_id"] = [f"S{nxt + k + 1:06d}" for k in range(len(d))]
    d["submission_date"] = d["submission_date"] + pd.to_timedelta(rng.integers(1, 8, len(d)), unit="D")
    for x in d["submission_id"]:
        key.add(1, x, "all", note="Re-submission of an existing HH-round")
    s = pd.concat([s, d], ignore_index=True)
    return s.sort_values(["submission_date", "submission_id"]).reset_index(drop=True)


def _vec(rng, templates, hi=7):
    v = list(templates[int(rng.integers(len(templates)))])
    if rng.random() < 0.25:
        j = int(rng.integers(len(v))); v[j] = int(np.clip(v[j] + rng.choice([-1, 1]), 0, hi))
    return v


def name_variant(name, rng):
    first, last = name.split(" ")
    k = int(rng.integers(0, 5))
    if k == 0 and len(last) > 3:
        i = int(rng.integers(0, len(last) - 1)); last = last[:i] + last[i + 1] + last[i] + last[i + 2:]
    elif k == 1 and len(first) > 3:
        i = int(rng.integers(1, len(first) - 1)); first = first[:i] + first[i + 1:]
    elif k == 2:
        first = first + "h"
    elif k == 3:
        return f"{last.upper()} {first}"
    else:
        return f"{first[0]}. {last}"
    return f"{first} {last}"


def inject_training(t, roster, rng, key):
    t = t.copy()
    t["participant_id"] = ""
    # E11 cross-partner double counting (name variants, no common ID)
    overlap = [d for d in C.DISTRICTS if sum(d in v for v in C.PARTNER_DISTRICTS.values()) > 1]
    src = t[t.district.isin(overlap)].sample(C.RATES["dc_individuals"], random_state=int(rng.integers(1e9)))
    dups = []
    for r in src.itertuples():
        other = "Partner B" if r.partner == "Partner A" else "Partner A"
        gap = int(rng.integers(10, 200))
        date = min(r.training_date + pd.Timedelta(days=gap), pd.Timestamp(C.TRAINING_END))
        if date <= r.training_date:
            continue
        dups.append(dict(hh_id=np.nan, member_id=np.nan, sex=r.sex, age=int(r.age + rng.choice([-1, 0, 0, 1])),
                         district=r.district, partner=other, full_name=name_variant(r.full_name, rng),
                         training_date=date, topic=str(rng.choice([x for x in t.topic.unique()]))))
    t = pd.concat([t, pd.DataFrame(dups)], ignore_index=True)
    cnt = {"Partner A": 0, "Partner B": 0}
    ids = []
    for r in t.itertuples():
        cnt[r.partner] += 1
        ids.append(f"{r.partner[-1]}-{cnt[r.partner]:05d}")
    t["participant_id"] = ids
    for k in range(len(dups)):
        key.add(11, t.at[len(t) - len(dups) + k, "participant_id"], "full_name", note="Second partner registered same person (name variant)")
    # E14 sex flipped vs roster
    linked = t.index[t.hh_id.notna()]
    for i in _pick(rng, linked, R["sex_flip"]):
        t.at[i, "sex"] = "M" if t.at[i, "sex"] == "F" else "F"
        key.add(14, t.at[i, "participant_id"], "sex", note="Sex differs from household roster")
    t["quarter"] = t["training_date"].dt.to_period("Q").astype(str)
    t = t.sort_values(["training_date", "participant_id"]).reset_index(drop=True)
    return t[["participant_id", "partner", "district", "hh_id", "member_id", "full_name", "sex", "age",
              "training_date", "quarter", "topic"]]


def build_reports(t, rng, key):
    g = t.groupby(["partner", "quarter"]).agg(reported_total_trained=("participant_id", "count"),
                                              reported_female=("sex", lambda x: int((x == "F").sum())),
                                              reported_male=("sex", lambda x: int((x == "M").sum()))).reset_index()
    sel = rng.choice(len(g), 6, replace=False)
    for j, i in enumerate(sel):
        ent = f"{g.at[i, 'partner']}|{g.at[i, 'quarter']}"
        if j < 4:   # overstated totals, internally consistent
            f = 1 + rng.uniform(0.08, 0.15)
            for c in ("reported_total_trained", "reported_female", "reported_male"):
                g.at[i, c] = int(round(g.at[i, c] * f))
            key.add(13, ent, "reported_*", note=f"Overstated by ~{(f - 1) * 100:.0f}%")
        else:       # arithmetic error
            g.at[i, "reported_male"] += int(rng.integers(15, 40))
            key.add(13, ent, "reported_male", note="Female + male does not equal total")
    return g
