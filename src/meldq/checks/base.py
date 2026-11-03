"""Check registry: every rule is declared once, with the DQ dimension and the seeded error(s) it targets."""
from dataclasses import dataclass

import pandas as pd

ISSUE_COLS = ["check_id", "check_name", "table", "level", "entity_key", "round", "field", "severity",
              "dq_dimension", "indicator", "maps_to", "message"]


@dataclass(frozen=True)
class Check:
    id: str
    name: str
    table: str
    level: str          # record | enumerator | dataset
    dimension: str      # USAID DQA dimension (+ ISO 25012-style extensions)
    severity: str       # high = value unusable until resolved; medium = verify; low = informational
    maps_to: tuple      # seeded error ids this rule is designed to catch
    indicator: str
    description: str


X = "Cross-cutting (survey)"
_C = [
    Check("R01", "Duplicate HH-round", "survey", "record", "Integrity", "high", (1,), X, "More than one submission for the same household and round"),
    Check("R02", "FCS/rCSI days out of range", "survey", "record", "Validity", "high", (5,), "FCS", "Food-group or coping days outside 0-7"),
    Check("R03", "Demographics out of range", "survey", "record", "Validity", "high", (5,), X, "HH size outside 1-20 or respondent age outside 15-95"),
    Check("R04", "Yield outside plausible range", "survey", "record", "Validity", "high", (4, 5), "Maize yield", "Maize yield outside 150-8,000 kg/ha"),
    Check("R05", "Yield peer outlier", "survey", "record", "Validity", "medium", (4, 5), "Maize yield", "Robust z-score >3.5 vs district-round median"),
    Check("R06", "Panel land-area jump", "survey", "record", "Validity", "medium", (4,), "Maize yield", "Land area >40% from the household's own median across rounds"),
    Check("R07", "Pregnancy module skip-logic", "survey", "record", "Integrity", "medium", (6,), X, "Pregnancy answer for non-eligible respondent"),
    Check("R08", "HHS frequency skip-logic", "survey", "record", "Integrity", "medium", (6,), "HHS", "Frequency answered when occurrence=No, or missing when Yes"),
    Check("R09", "rCSI straight-lining", "survey", "record", "Reliability", "medium", (7,), "rCSI", "All five rCSI items identical and non-zero"),
    Check("R10", "GPS outside assigned district", "survey", "record", "Reliability", "medium", (8,), X, "Coordinates outside the district bounding box"),
    Check("R11", "GPS at field office", "survey", "record", "Reliability", "medium", (8,), X, "Coordinates within 300 m of the district field office"),
    Check("R12", "Interview outside fieldwork window", "survey", "record", "Timeliness", "medium", (12,), X, "Interview date outside round window (+/-7 days) or before programme start"),
    Check("R13", "Late submission", "survey", "record", "Timeliness", "low", (12,), X, "Submitted >7 days after interview"),
    Check("R14", "Submission before interview", "survey", "record", "Timeliness", "medium", (12,), X, "Submission date earlier than interview date"),
    Check("R15", "Outdated form version", "survey", "record", "Integrity", "low", (6,), X, "Submission from a form version other than the latest"),
    Check("E01", "Short interview duration", "survey", "enumerator", "Reliability", "high", (2,), X, "Enumerator-round median duration <60% of overall median"),
    Check("E02", "Cloned response vectors", "survey", "enumerator", "Reliability", "high", (2,), X, ">20% of an enumerator-round's records share an identical FCS+rCSI answer vector with >=2 others"),
    Check("E03", "Abnormally low variance", "survey", "enumerator", "Reliability", "high", (2,), X, "SD of FCS in an enumerator-round <50% of the pooled SD"),
    Check("B01", "Back-check discrepancy", "survey", "enumerator", "Reliability", "high", (2,), X, "Re-interview disagrees with original on >=30% of key items"),
    Check("D01", "Digit preference (heaping)", "survey", "dataset", "Precision", "medium", (3,), "Maize yield", "Excess share of land at 0.5 ha multiples / production at 50 kg multiples"),
    Check("D02", "Income missingness pattern", "survey", "dataset", "Completeness", "high", (9,), "Income / VSLA savings", ">=5% missing and missingness varies with a wealth proxy"),
    Check("D03", "Panel attrition", "survey", "dataset", "Representativeness", "high", (10,), "FCS", "Cumulative attrition >10% or differential by baseline welfare"),
    Check("T01", "Fuzzy beneficiary duplicate", "training_log", "record", "Integrity", "high", (11,), "Farmers trained", "Similar name, same sex, age +/-1, same district, different partner"),
    Check("T02", "Sex differs from roster", "training_log", "record", "Validity", "medium", (14,), "Farmers trained", "Sex in training log differs from household roster"),
    Check("X01", "Partner report vs raw log", "partner_reports", "record", "Integrity", "high", (13,), "Farmers trained", "Reported total differs from raw count by >5%"),
    Check("X02", "Partner report arithmetic", "partner_reports", "record", "Integrity", "medium", (13,), "Farmers trained", "Female + male differs from reported total"),
]
REGISTRY = {c.id: c for c in _C}


def emit(cid, entities, message="", field="", rounds=None):
    c = REGISTRY[cid]
    ents = list(entities)
    rnd = list(rounds) if rounds is not None else [""] * len(ents)
    df = pd.DataFrame({"check_id": cid, "check_name": c.name, "table": c.table, "level": c.level,
                       "entity_key": ents, "round": rnd, "field": field, "severity": c.severity,
                       "dq_dimension": c.dimension, "indicator": c.indicator,
                       "maps_to": ";".join(map(str, c.maps_to)), "message": message})
    return df.reindex(columns=ISSUE_COLS)
