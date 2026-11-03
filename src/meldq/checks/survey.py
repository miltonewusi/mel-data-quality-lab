import numpy as np
import pandas as pd
from scipy.stats import binomtest, chi2_contingency

from .. import config as C
from ..schema import FCS_COLS, RCSI_COLS
from .base import emit


def record_checks(s):
    out = []

    def flag(cid, mask, msg, field=""):
        sub = s.loc[mask]
        out.append(emit(cid, sub["submission_id"], msg, field, sub["round"]))

    o = s.sort_values(["submission_date", "submission_id"])
    d = o.duplicated(["hh_id", "round"], keep="first")
    out.append(emit("R01", o.loc[d, "submission_id"], "Repeat submission for same HH and round", "hh_id,round", o.loc[d, "round"]))

    cols = FCS_COLS + RCSI_COLS
    flag("R02", ((s[cols] > 7) | (s[cols] < 0)).any(axis=1), "Days outside 0-7", "fcs_*/rcsi_*")
    flag("R03", ~s.hh_size.between(1, 20) | ~s.resp_age.between(15, 95), "HH size or respondent age implausible", "hh_size,resp_age")
    y = s.maize_yield_kg_ha
    flag("R04", (y < 150) | (y > 8000), "Yield outside 150-8,000 kg/ha", "maize_yield_kg_ha")

    ly = np.log(y.clip(lower=1))
    g = [s.district, s["round"]]
    med = ly.groupby(g).transform("median")
    mad = (ly - med).abs().groupby(g).transform("median")
    z = 0.6745 * (ly - med) / mad.replace(0, np.nan)
    flag("R05", z.abs() > 3.5, "Yield is a robust outlier vs district-round", "maize_yield_kg_ha")

    gl = s.groupby("hh_id").land_area_ha
    lmed, cnt = gl.transform("median"), gl.transform("count")
    flag("R06", (cnt >= 3) & ((s.land_area_ha / lmed - 1).abs() > 0.4), "Land area deviates >40% from household median", "land_area_ha")

    flag("R07", s.resp_pregnant.notna() & ((s.resp_sex != "F") | ~s.resp_age.between(15, 49)),
         "Pregnancy question answered by ineligible respondent", "resp_pregnant")
    m8 = pd.Series(False, index=s.index)
    for i in (1, 2, 3):
        m8 |= ((s[f"hhs_q{i}"] == 0) & s[f"hhs_f{i}"].notna()) | ((s[f"hhs_q{i}"] == 1) & s[f"hhs_f{i}"].isna())
    flag("R08", m8, "HHS frequency inconsistent with occurrence", "hhs_f*")
    flag("R09", (s[RCSI_COLS].nunique(axis=1) == 1) & (s.rcsi_less_pref > 0), "All rCSI items identical", "rcsi_*")

    b = lambda k, j: s.district.map(lambda d: C.DISTRICTS[d][k][j])
    outside = (s.gps_lat < b("lat", 0)) | (s.gps_lat > b("lat", 1)) | (s.gps_lon < b("lon", 0)) | (s.gps_lon > b("lon", 1))
    flag("R10", outside, "GPS outside assigned district", "gps_lat,gps_lon")
    olat = s.district.map(lambda d: C.DISTRICTS[d]["office"][0])
    olon = s.district.map(lambda d: C.DISTRICTS[d]["office"][1])
    km = np.hypot((s.gps_lat - olat) * 111.0, (s.gps_lon - olon) * 111.0 * np.cos(np.radians(s.gps_lat)))
    flag("R11", km < 0.3, "GPS within 300 m of field office", "gps_lat,gps_lon")

    w0 = s["round"].map(lambda r: pd.Timestamp(C.WINDOWS[r][0])) - pd.Timedelta(days=7)
    w1 = s["round"].map(lambda r: pd.Timestamp(C.WINDOWS[r][1])) + pd.Timedelta(days=7)
    flag("R12", (s.interview_date < w0) | (s.interview_date > w1) | (s.interview_date < pd.Timestamp(C.PROGRAMME_START)),
         "Interview outside fieldwork window", "interview_date")
    lag = (s.submission_date - s.interview_date).dt.days
    flag("R13", lag > 7, "Submitted >7 days after interview", "submission_date")
    flag("R14", lag < 0, "Submitted before interview", "submission_date")
    flag("R15", s.form_version != C.LATEST_FORM, "Outdated form version", "form_version")
    return out


def enumerator_checks(s):
    out = []
    grp = s.groupby(["enumerator_id", "round"])
    med = s.duration_min.median()
    dur = grp.duration_min.median()
    bad = dur[dur < 0.6 * med]
    out.append(emit("E01", [e for e, _ in bad.index], f"Median interview duration <60% of overall median ({med:.0f} min)", "duration_min", [r for _, r in bad.index]))
    clones, lowvar = [], []
    fcs = s.fcs_score.clip(0, 112)
    pooled = fcs.std()
    for (e, r), g in grp:
        if len(g) < 15:
            continue
        vec = g[FCS_COLS + RCSI_COLS].astype(str).agg("|".join, axis=1)
        share = (vec.map(vec.value_counts()) >= 3).mean()
        if share > 0.20:
            clones.append((e, r))
        if fcs.loc[g.index].std() < 0.5 * pooled:
            lowvar.append((e, r))
    out.append(emit("E02", [e for e, _ in clones], "Identical answer vectors repeated", "fcs_*,rcsi_*", [r for _, r in clones]))
    out.append(emit("E03", [e for e, _ in lowvar], "FCS variance far below peers", "fcs_score", [r for _, r in lowvar]))
    return out


def dataset_checks(s):
    out = []
    msgs = []
    land = (s.land_area_ha.dropna() * 100).round().astype("int64")
    prod = s.maize_prod_kg.dropna().round().astype("int64")
    for name, v, mod in (("land_area_ha (0.5 ha multiples)", land, 50), ("maize_prod_kg (50 kg multiples)", prod, 50)):
        k, n = int((v % mod == 0).sum()), len(v)
        p = binomtest(k, n, 1 / mod, alternative="greater").pvalue
        if k / n > 0.06 and p < 0.001:
            msgs.append(f"{name}: {k / n:.0%} of values vs ~{1 / mod:.0%} expected (p={p:.1e})")
    if msgs:
        out.append(emit("D01", ["dataset"], "; ".join(msgs), "land_area_ha,maize_prod_kg"))

    miss = s.income_usd_month.isna()
    t = pd.qcut(s.fcs_score.clip(0, 112), 3, labels=False, duplicates="drop")
    p = chi2_contingency(pd.crosstab(t, miss))[1]
    rates = miss.groupby(t).mean()
    if miss.mean() >= 0.05 and p < 0.01:
        out.append(emit("D02", ["dataset"], f"{miss.mean():.1%} income missing; rate by FCS tercile "
                        f"{rates.iloc[0]:.1%} / {rates.iloc[1]:.1%} / {rates.iloc[-1]:.1%} (p={p:.1e}) - missingness depends on welfare",
                        "income_usd_month"))

    base = s[s["round"] == "baseline"].drop_duplicates("hh_id").copy()
    end_ids = set(s.loc[s["round"] == "endline", "hh_id"])
    base["gone"] = ~base.hh_id.isin(end_ids)
    base["terc"] = pd.qcut(base.fcs_score.clip(0, 112), 3, labels=False, duplicates="drop")
    attr = base.gone.mean()
    pr = chi2_contingency(pd.crosstab(base.terc, base.gone))[1]
    by = base.groupby("terc").gone.mean()
    if attr > 0.10 or pr < 0.05:
        out.append(emit("D03", ["dataset"], f"Cumulative attrition {attr:.1%}; poorest tercile {by.iloc[0]:.1%} vs best-off "
                        f"{by.iloc[-1]:.1%} (p={pr:.1e})", "hh_id,round"))
    return out
