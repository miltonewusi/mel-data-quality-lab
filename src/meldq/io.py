import pandas as pd

from . import config as C

DATES = {"survey": ["interview_date", "submission_date"], "training_log": ["training_date"]}


def load_tables(raw=C.RAW):
    t = {}
    for name in ("survey", "training_log", "hh_roster", "partner_reports", "donor_report"):
        t[name] = pd.read_csv(raw / f"{name}.csv", parse_dates=DATES.get(name, []))
    return t


def load_answer_key(d=C.KEYDIR):
    return pd.read_csv(d / "answer_key.csv"), pd.read_csv(d / "truth_survey.csv", parse_dates=["interview_date", "submission_date"])
