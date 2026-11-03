"""Programme design, geography and the error catalogue (single source of truth)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
KEYDIR = ROOT / "data" / "answer_key"
REPORTS = ROOT / "reports"

SEED = 20260601
N_HH = 1200
ROUNDS = ["baseline", "midline", "endline"]
PROGRAMME_START = "2023-03-01"
TRAINING_START, TRAINING_END = "2023-06-01", "2025-03-31"
WINDOWS = {  # planned fieldwork windows (grace of 7 days applied in checks)
    "baseline": ("2023-04-03", "2023-05-12"),
    "midline": ("2024-04-01", "2024-05-10"),
    "endline": ("2025-04-07", "2025-05-16"),
}
# Fictional districts: bounding boxes (lat range, lon range)
DISTRICTS = {
    "Northvale": dict(lat=(-12.5, -12.0), lon=(30.0, 30.5)),
    "Eastmere": dict(lat=(-12.5, -12.0), lon=(30.5, 31.0)),
    "Southridge": dict(lat=(-13.0, -12.5), lon=(30.0, 30.5)),
    "Westbrook": dict(lat=(-13.0, -12.5), lon=(30.5, 31.0)),
}
for _d in DISTRICTS.values():
    _d["office"] = (sum(_d["lat"]) / 2, sum(_d["lon"]) / 2)

ENUM_PER_DISTRICT = 6
ENUMERATORS = [f"ENUM_{i:02d}" for i in range(1, 4 * ENUM_PER_DISTRICT + 1)]
ENUM_DISTRICT = {e: list(DISTRICTS)[i // ENUM_PER_DISTRICT] for i, e in enumerate(ENUMERATORS)}
FABRICATOR, FAB_ROUNDS = "ENUM_07", ("midline", "endline")
SUBTLE_FAB, SUBTLE_SHARE = "ENUM_20", 0.35   # partial fabricator: plausible values, normal-ish duration
GPS_OFFICE_ENUM, GPS_OFFICE_ROUNDS = "ENUM_15", ("endline",)

# Two partners; Eastmere & Southridge are served by BOTH (source of double counting)
PARTNER_DISTRICTS = {
    "Partner A": ["Northvale", "Eastmere", "Southridge"],
    "Partner B": ["Eastmere", "Southridge", "Westbrook"],
}
N_TRAINED, N_LINKED = 2400, 700

LATEST_FORM = "v1.2"

# id: (name, DQ dimension, detection level, table)
ERRORS = {
    1: ("Duplicate survey records", "Integrity", "record", "survey"),
    2: ("Enumerator fabrication", "Reliability", "enumerator", "survey"),
    3: ("Digit preference / heaping (land, production)", "Precision", "dataset", "survey"),
    4: ("Unit mix-ups (acres vs ha, bags vs kg)", "Validity", "record", "survey"),
    5: ("Impossible values", "Validity", "record", "survey"),
    6: ("Skip-logic violations", "Integrity", "record", "survey"),
    7: ("Straight-lining on rCSI", "Reliability", "record", "survey"),
    8: ("Implausible GPS (outside district / at office)", "Reliability", "record", "survey"),
    9: ("Income missing not-at-random", "Completeness", "dataset", "survey"),
    10: ("Differential panel attrition", "Representativeness", "dataset", "survey"),
    11: ("Beneficiary double-counting across partners", "Integrity", "record", "training_log"),
    12: ("Date / timeliness problems", "Timeliness", "record", "survey"),
    13: ("Partner reports differ from raw data", "Integrity", "record", "partner_reports"),
    14: ("Sex inconsistent with household roster", "Validity", "record", "training_log"),
}
RATES = dict(dup=0.02, heap=0.40, unit=0.025, impossible=0.015, skip_preg=0.02, skip_hhs=0.015,
             straight=0.025, gps_out=0.015, date_pre=0.012, date_late=0.03, date_after=0.005,
             sex_flip=0.04, dc_individuals=70)
