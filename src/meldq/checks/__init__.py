import pandas as pd

from . import survey, training
from .base import ISSUE_COLS, REGISTRY


def run_all(tables):
    s, t, r = tables["survey"], tables["training_log"], tables["partner_reports"]
    parts = survey.record_checks(s) + survey.enumerator_checks(s) + survey.dataset_checks(s)
    tp, dup_ids = training.training_checks(t, tables["hh_roster"])
    rp, recon_detail = training.report_checks(r, t)
    parts += tp + rp
    issues = pd.concat([p for p in parts if len(p)], ignore_index=True).reindex(columns=ISSUE_COLS)
    recon = training.reconcile(r, tables["donor_report"], t, dup_ids)
    return issues, recon, recon_detail
