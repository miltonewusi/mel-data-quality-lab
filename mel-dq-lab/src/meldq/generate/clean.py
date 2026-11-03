"""Step 1 of the generator: produce CLEAN 'truth' data (no errors)."""
import numpy as np
import pandas as pd

from .. import config as C
from ..schema import (FCS_COLS, FCS_W, RCSI_COLS, RCSI_W, PRACTICE_COLS, SURVEY_COLS)

FCS_MU = [6.4, 2.6, 4.2, 1.6, 1.3, 1.3, 3.6, 4.6]
FCS_SENS = [0.2, 1, 1, 1, 1, 1, 0.5, 0.5]
RCSI_MU = [3.0, 1.4, 3.0, 1.0, 2.4]
TREND = [0.0, 0.10, 0.15]   # secular improvement (all households)
TAU = [0.0, 0.15, 0.30]     # programme effect on the latent welfare shift (participants only)

FIRST_F = ["Amina", "Grace", "Fatuma", "Esther", "Mary", "Zawadi", "Chipo", "Naledi", "Joyce", "Agnes",
           "Rehema", "Beatrice", "Lucia", "Halima", "Ruth", "Sarah", "Tendai", "Mercy", "Edith", "Florence"]
FIRST_M = ["Joseph", "Daniel", "Mohamed", "Peter", "Samuel", "Juma", "Emmanuel", "Isaac", "Charles", "Moses",
           "Yusuf", "Patrick", "Simon", "Hassan", "Thomas", "Kelvin", "Albert", "Benson", "Felix", "Gideon"]
SURNAMES = ["Banda", "Mwale", "Phiri", "Tembo", "Moyo", "Zulu", "Mulenga", "Chanda", "Kunda", "Sakala",
            "Lungu", "Nkhoma", "Mumba", "Daka", "Bwalya", "Chola", "Mutale", "Kapata", "Musonda", "Siame",
            "Ngoma", "Zimba", "Kalaba", "Simwanza", "Chilufya", "Mbewe", "Nyirenda", "Ngulube", "Sichone", "Hamoonga"]
TOPICS = ["Improved seed & row planting", "Composting & soil fertility", "Post-harvest handling",
          "Intercropping", "VSLA & financial literacy"]


def logistic(x):
    return 1 / (1 + np.exp(-x))


def derive(df):
    """Recompute calculated fields exactly as the (simulated) form would."""
    df = df.copy()
    df["fcs_score"] = sum(w * df[c] for w, c in zip(FCS_W, FCS_COLS))
    df["rcsi_score"] = sum(w * df[c] for w, c in zip(RCSI_W, RCSI_COLS))
    h = 0
    for i in (1, 2, 3):
        h = h + np.where(df[f"hhs_q{i}"] == 1, np.where(df[f"hhs_f{i}"] == 3, 2, 1), 0)
    df["hhs_score"] = h
    df["practices_n"] = df[PRACTICE_COLS].sum(axis=1)
    df["adopted_2plus"] = (df["practices_n"] >= 2).astype(int)
    df["maize_yield_kg_ha"] = (df["maize_prod_kg"] / df["maize_area_ha"]).round(0)
    return df


def build_households(rng):
    n = C.N_HH
    hh = pd.DataFrame({"hh_id": [f"HH{i:04d}" for i in range(1, n + 1)]})
    hh["district"] = rng.choice(list(C.DISTRICTS), n)
    hh["programme_participant"] = (rng.random(n) < 0.5).astype(int)
    hh["z"] = rng.normal(size=n)                                  # latent wealth
    hh["hh_size"] = np.clip(rng.poisson(3.5, n) + 2, 2, 12)
    hh["resp_sex"] = rng.choice(["F", "M"], n, p=[0.68, 0.32])
    hh["resp_age_base"] = rng.integers(20, 66, n)
    hh["land_base"] = np.clip(np.exp(rng.normal(0.25 * hh["z"], 0.45)), 0.2, 6)
    hh["maize_share"] = rng.uniform(0.4, 0.8, n)
    lat, lon = [], []
    for d in hh["district"]:
        b = C.DISTRICTS[d]
        lat.append(rng.uniform(b["lat"][0] + .02, b["lat"][1] - .02))
        lon.append(rng.uniform(b["lon"][0] + .02, b["lon"][1] - .02))
    hh["lat0"], hh["lon0"] = lat, lon
    # attrition process (poorer households drop out more) -> applied later as the 'observed' panel
    h = np.clip(0.075 * np.exp(-0.6 * hh["z"]), 0, 0.6)
    s1 = rng.random(n) >= h
    s2 = s1 & (rng.random(n) >= h)
    hh["last_round"] = np.where(s2, 2, np.where(s1, 1, 0))
    return hh


def build_roster(hh, rng):
    rows = []
    for r in hh.itertuples():
        for m in range(1, r.hh_size + 1):
            if m == 1:
                sex, age = r.resp_sex, int(r.resp_age_base)
            else:
                sex, age = str(rng.choice(["F", "M"])), int(rng.integers(0, 70))
            rows.append((r.hh_id, m, sex, age))
    return pd.DataFrame(rows, columns=["hh_id", "member_id", "sex", "age"])


def build_survey_truth(hh, rng):
    frames, counter = [], 0
    for r, rnd in enumerate(C.ROUNDS):
        d = hh.copy()
        n = len(d)
        d["round"] = rnd
        s = 0.4 * d["z"] + TREND[r] + d["programme_participant"] * TAU[r]
        for c, mu, sens in zip(FCS_COLS, FCS_MU, FCS_SENS):
            d[c] = np.clip(np.round(rng.normal(mu + sens * s, 1.4)), 0, 7).astype(int)
        for c, mu in zip(RCSI_COLS, RCSI_MU):
            d[c] = np.clip(np.round(rng.normal(mu - 1.2 * s, 1.8)), 0, 7).astype(int)
        p_occ = [(-2.0, 1.0), (-2.4, 0.9), (-3.2, 0.8)]
        for i, (b0, b1) in enumerate(p_occ, start=1):
            occ = rng.random(n) < logistic(b0 - b1 * d["z"] - 1.5 * (TREND[r] + d["programme_participant"] * TAU[r]))
            d[f"hhs_q{i}"] = occ.astype(int)
            d[f"hhs_f{i}"] = np.where(occ, rng.choice([1, 2, 3], n, p=[.5, .35, .15]), np.nan)
        pr = d["programme_participant"] * [0, 1.0, 1.4][r] + 0.2 * r
        for j, c in enumerate(PRACTICE_COLS):
            d[c] = (rng.random(n) < logistic(-1.1 + 0.3 * d["z"] + pr - 0.1 * j)).astype(int)
        d["land_area_ha"] = np.round(d["land_base"] * np.exp(rng.normal(0, 0.03, n)), 2)
        d["maize_area_ha"] = np.maximum(np.round(d["land_area_ha"] * d["maize_share"], 2), 0.05)
        gain = 0.03 * r + d["programme_participant"] * [0, .12, .22][r]
        y = np.clip(1300 * np.exp(0.15 * d["z"] + gain) * np.exp(rng.normal(0, 0.25, n)), 250, 5500)
        d["maize_prod_kg"] = np.maximum(np.round(y * d["maize_area_ha"]), 10).astype(int)
        d["income_usd_month"] = np.round(np.exp(rng.normal(np.log(55) + 0.45 * d["z"] + 0.1 * r
                                                           + d["programme_participant"] * [0, .05, .12][r], 0.4)), 1)
        mem = rng.random(n) < logistic(-0.5 + 0.2 * d["z"] + d["programme_participant"] * [0, .8, 1.0][r])
        d["vsla_member"] = mem.astype(int)
        sav = np.round(np.exp(rng.normal(np.log(25) + 0.4 * d["z"] + 0.2 * r, 0.5)), 1)
        d["vsla_savings_usd"] = np.where(mem & (rng.random(n) > 0.01), sav, np.nan)
        d["resp_age"] = d["resp_age_base"] + r
        elig = (d["resp_sex"] == "F") & d["resp_age"].between(15, 49)
        d["resp_pregnant"] = np.where(elig & (rng.random(n) < 0.10), 1.0, np.where(elig, 0.0, np.nan))
        # fieldwork metadata
        w0, w1 = (pd.Timestamp(x) for x in C.WINDOWS[rnd])
        d["interview_date"] = w0 + pd.to_timedelta(rng.integers(0, (w1 - w0).days + 1, n), unit="D")
        d["enumerator_id"] = [str(rng.choice([e for e in C.ENUMERATORS if C.ENUM_DISTRICT[e] == x])) for x in d["district"]]
        d["form_version"] = C.LATEST_FORM
        hour, minute = rng.integers(7, 17, n), rng.integers(0, 60, n)
        d["start_time"] = [f"{a:02d}:{b:02d}" for a, b in zip(hour, minute)]
        d["duration_min"] = np.round(np.clip(rng.normal(42, 8, n), 22, 75), 1)
        lag = rng.choice([0, 1, 2, 3, 4, 5], n, p=[.35, .30, .15, .10, .06, .04])
        d["submission_date"] = d["interview_date"] + pd.to_timedelta(lag, unit="D")
        d["gps_lat"] = np.round(d["lat0"] + rng.normal(0, 0.0005, n), 5)
        d["gps_lon"] = np.round(d["lon0"] + rng.normal(0, 0.0005, n), 5)
        d["last_round_flag"] = d["last_round"]
        frames.append(d)
    t = pd.concat(frames, ignore_index=True)
    t = t.sort_values(["interview_date", "hh_id"]).reset_index(drop=True)
    t["submission_id"] = [f"S{i:06d}" for i in range(1, len(t) + 1)]
    t = derive(t)
    t["wealth_z"] = t["z"]
    return t


def build_training(hh, roster, rng):
    """Programme-wide training register (N_TRAINED people). N_LINKED are linkable to the survey roster."""
    adults = roster.merge(hh[["hh_id", "district", "programme_participant"]], on="hh_id")
    adults = adults[(adults.age >= 18) & (adults.programme_participant == 1)]
    linked = adults.sample(C.N_LINKED, random_state=int(rng.integers(1e9)))
    rows = []
    for r in linked.itertuples():
        rows.append(dict(hh_id=r.hh_id, member_id=r.member_id, sex=r.sex, age=r.age, district=r.district))
    for _ in range(C.N_TRAINED - C.N_LINKED):
        rows.append(dict(hh_id=np.nan, member_id=np.nan, sex=str(rng.choice(["F", "M"], p=[.62, .38])),
                         age=int(rng.integers(18, 70)), district=str(rng.choice(list(C.DISTRICTS)))))
    t = pd.DataFrame(rows)
    partners = []
    for d in t["district"]:
        opts = [p for p, ds in C.PARTNER_DISTRICTS.items() if d in ds]
        partners.append(str(rng.choice(opts)))
    t["partner"] = partners
    t["full_name"] = [f"{rng.choice(FIRST_F if s == 'F' else FIRST_M)} {rng.choice(SURNAMES)}" for s in t["sex"]]
    t0, t1 = pd.Timestamp(C.TRAINING_START), pd.Timestamp(C.TRAINING_END)
    t["training_date"] = t0 + pd.to_timedelta(rng.integers(0, (t1 - t0).days + 1, len(t)), unit="D")
    t["topic"] = rng.choice(TOPICS, len(t))
    return t
