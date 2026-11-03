"""Write the deliverables a DQA team would hand over: issue log, scorecard, DQA report, corrective action plan."""
import numpy as np
import pandas as pd

from . import config as C
from .checks.base import REGISTRY

CAUSE_ACTION = {  # check_id: (likely root cause, corrective action, owner, timeline)
    "R01": ("Re-submission after poor connectivity", "Enable duplicate-instance detection on the server; train enumerators to confirm sync before re-sending", "MEL data manager", "2 weeks"),
    "R02": ("No hard constraints on numeric fields", "Add constraint 0<=days<=7 (and soft warnings on totals) to the XLSForm; redeploy", "MEL data manager", "1 week"),
    "R03": ("No constraints on household size / age", "Add range constraints; require confirmation for HH size >15", "MEL data manager", "1 week"),
    "R04": ("Unit confusion and typing errors", "Add explicit unit selectors, auto-convert, and a yield plausibility warning at entry", "MEL data manager", "2 weeks"),
    "R05": ("Unit confusion and typing errors", "Review outliers with supervisors; add soft yield-range warnings", "Field supervisors", "2 weeks"),
    "R06": ("Acres entered as hectares", "Pre-load baseline land area; flag >30% change at entry", "MEL data manager", "3 weeks"),
    "R07": ("Outdated form version still in use", "Force form-version update; block submissions from old versions", "MEL data manager", "1 week"),
    "R08": ("Missing relevance logic on HHS follow-ups", "Fix relevance conditions in the form; add server-side validation", "MEL data manager", "1 week"),
    "R09": ("Respondent fatigue / enumerator shortcutting", "Shorten the module, reorder items, spot-check audio audits on rCSI", "Field supervisors", "Next round"),
    "R10": ("GPS taken away from the household / fabrication", "Require GPS accuracy <20 m and geofence to the assigned district", "MEL data manager", "2 weeks"),
    "R11": ("GPS captured at the office", "Add geofence exclusion around offices; back-check affected interviews", "Field supervisors", "2 weeks"),
    "R12": ("Wrong device clock or backdated entry", "Lock date to device time; sync and verify device clocks daily", "MEL data manager", "2 weeks"),
    "R13": ("Submission delays", "Introduce a 72-hour sync rule and a daily submission dashboard", "Field supervisors", "1 week"),
    "R14": ("Device clock error", "Lock date to server time; flag mismatches at upload", "MEL data manager", "2 weeks"),
    "R15": ("Form update not rolled out to all devices", "Run a pre-fieldwork device audit", "MEL data manager", "1 week"),
    "E01": ("Targets / pressure; interviews not actually conducted", "Re-interview all affected households; suspend enumerator pending review; reassess incentives", "MEL lead", "Immediate"),
    "E02": ("Fabricated interviews", "Re-interview all affected households; suspend enumerator; exclude data from analysis until verified", "MEL lead", "Immediate"),
    "E03": ("Fabricated or copied responses", "Include in re-interview scope; review audio audits", "MEL lead", "Immediate"),
    "B01": ("Back-check confirms data cannot be reproduced", "Replace affected interviews; escalate per code of conduct", "MEL lead", "Immediate"),
    "D01": ("Respondent estimation of land/harvest", "Use crop-cutting or measured land for a sub-sample; use local-unit calibration", "Technical advisor", "Next round"),
    "D02": ("Sensitivity of income questions", "Use consumption/asset proxies, reorder question, report missingness rates; apply weighting or multiple imputation", "MEL analyst", "Before analysis"),
    "D03": ("Migration / non-tracking of poorer households", "Intensify tracking protocols; apply attrition weights; run bounds sensitivity analysis", "MEL lead", "Before analysis"),
    "T01": ("No unique beneficiary ID across partners", "Introduce a shared beneficiary ID (e.g., national ID or programme card); quarterly cross-partner de-duplication", "MEL lead + partners", "1 month"),
    "T02": ("Coding errors when transcribing sex from register", "Validate against registry at entry; train partner data clerks", "Partner M&E officers", "1 month"),
    "X01": ("Manual aggregation or optimistic reporting", "Require partners to submit disaggregated raw logs with every report; MEL team computes totals", "MEL lead", "Next quarter"),
    "X02": ("Spreadsheet arithmetic error", "Use locked report template with formula checks", "Partner M&E officers", "Next quarter"),
}
SEV = {"high": 3, "medium": 2, "low": 1}


def md(df, floatfmt=3):
    d = df.copy()
    head = "| " + " | ".join(map(str, d.columns)) + " |\n|" + "|".join(["---"] * len(d.columns)) + "|\n"
    body = ""
    for _, r in d.iterrows():
        cells = []
        for v in r:
            if v is None or (isinstance(v, float) and np.isnan(v)):
                cells.append("")
            elif isinstance(v, (float, np.floating)):
                cells.append(str(int(v)) if float(v).is_integer() else f"{v:.{floatfmt}f}".rstrip("0").rstrip("."))
            else:
                cells.append(str(v))
        body += "| " + " | ".join(cells) + " |\n"
    return head + body


def issue_log(issues):
    g = issues.groupby("check_id").agg(entities_flagged=("entity_key", "nunique")).reset_index()
    rows = []
    for r in g.itertuples():
        c = REGISTRY[r.check_id]
        cause, action, owner, when = CAUSE_ACTION[r.check_id]
        rows.append(dict(check_id=c.id, issue=c.name, description=c.description, table=c.table, level=c.level,
                         dq_dimension=c.dimension, indicator=c.indicator, severity=c.severity,
                         entities_flagged=r.entities_flagged,
                         priority_score=round(SEV[c.severity] * np.log1p(r.entities_flagged), 2),
                         likely_cause=cause, recommended_action=action))
    return pd.DataFrame(rows).sort_values("priority_score", ascending=False).reset_index(drop=True)


def corrective_action_plan(log):
    out = ["# Corrective Action Plan (auto-generated)\n",
           "Actions are ordered by priority score (severity x log of records affected). "
           "Owners/timelines are suggested defaults and should be agreed with the programme team.\n",
           "| # | Issue | Priority | Corrective action | Owner | Timeline | Verification |\n|---|---|---|---|---|---|---|\n"]
    for i, r in enumerate(log.itertuples(), 1):
        _, action, owner, when = CAUSE_ACTION[r.check_id]
        out.append(f"| {i} | {r.issue} ({r.check_id}) | {r.priority_score} | {action} | {owner} | {when} | Re-run `meldq all`; check flag rate falls below 2% |\n")
    return "".join(out)


def dqa_report(res, key, tables):
    b, card, imp, recon = res["benchmark"], res["scorecard"], res["impact"], res["recon"]
    det = int(b.detected.sum())
    rec_rows = b[b.level == "record"]
    s = tables["survey"]
    L = []
    L.append("# Data Quality Assessment Report: RLFSP (synthetic)\n")
    L.append(f"*Generated by `meldq` v0.1 on seed {C.SEED}. All data are synthetic; no real persons or organisations are represented.*\n")
    L.append("## 1. Scope and approach\n")
    L.append(f"The assessment covers {len(s):,} household survey submissions across three rounds "
             f"({s.hh_id.nunique():,} households), a training register of {len(tables['training_log']):,} entries, "
             f"{len(tables['partner_reports'])} partner-quarter reports and the donor-reported figure. "
             "Dimensions follow USAID ADS 201 (validity, integrity, precision, reliability, timeliness) with ISO/IEC 25012-style "
             "extensions (completeness, representativeness). See `docs/dq_plan.md`.\n")
    L.append("## 2. Headline results\n")
    L.append(f"- **{det} of {len(b)} seeded error types detected** (recall >= 50%).\n")
    L.append(f"- Mean recall on record-level error types: **{rec_rows.recall.mean():.0%}**; "
             f"enumerator fabrication {'detected' if b.loc[b.error_id == 2, 'detected'].iloc[0] else 'missed'} "
             f"(recall {b.loc[b.error_id == 2, 'recall'].iloc[0]:.0%}).\n")
    weak = b[b.recall < 0.9]
    if len(weak):
        L.append("- Types detected only partially (recall < 90%): " + "; ".join(f"{r.error} ({r.recall:.0%})" for r in weak.itertuples()) + ".\n")
    L.append(f"- Flags raised: {len(res['issues']):,} across {res['issues'].check_id.nunique()} checks.\n")
    L.append("\n## 3. Detection benchmark against the answer key\n")
    L.append(md(b.drop(columns=["detected"])) + "\n")
    L.append("*Recall = share of injected errors flagged. Precision = share of flags that hit any injected problem in the same table "
             "(natural data tails count as false positives). Dataset-level error types are scored detected / not detected.*\n")
    L.append("\n## 4. Data quality scorecard (indicator x dimension)\n")
    L.append(md(card) + "\n")
    L.append("Rating rule: GREEN >= 98% records pass; AMBER 95-98%; RED < 95% or any dataset-level flag.\n")
    L.append("\n## 5. Field verification (back-checks)\n")
    uniq = s.drop_duplicates(["hh_id", "round"]).shape[0]
    L.append(f"A risk-based sample of {len(res['bc_sample'])} submissions ({len(res['bc_sample']) / uniq:.0%} of unique household-rounds; "
             "50% risk-ranked, 50% random) was re-interviewed in simulation. Enumerators with >=2 major discrepancies are escalated.\n")
    worst = res["enum_disc"].sort_values(["major", "discrepancy_rate"], ascending=False).head(5)
    L.append("\nEnumerators with the most major discrepancies:\n\n" + md(worst) + "\n")
    L.append("\n## 6. Reporting reconciliation\n")
    L.append(md(recon) + "\n")
    L.append("\n## 7. Impact of data quality on the headline result (FCS)\n")
    L.append(md(imp) + "\n")
    a, braw, c = imp.iloc[0], imp.iloc[1], imp.iloc[2]
    L.append(f"In this run, leaving errors uncorrected shifts participants' FCS change by {braw.participant_change_bias:+.2f} points and the "
             f"difference-in-differences by {braw.did_bias_vs_truth:+.2f} (truth: {a.did:.2f}). Cleaning removes {1 - c.hh_rounds / a.hh_rounds:.0%} of household-rounds "
             "relative to the complete truth panel, which costs precision: data quality problems bias estimates *and* shrink usable sample.\n")
    L.append("*A = ground truth. B = what a naive analyst would report. C/D = after cleaning and attrition weighting. "
             "`participants_change` is the baseline-to-endline FCS change among participants; `did` is the difference-in-differences vs comparison households.*\n")
    L.append("\n## 8. Limitations\n")
    L.append("- Synthetic errors are cleaner and more independent than real ones; recall here is an upper bound on real-world performance.\n"
             "- Back-check noise is simulated from ground truth.\n"
             "- Fuzzy matching thresholds were tuned on this dataset; re-tune on real registers.\n"
             "- Dataset-level tests detect that a problem exists, not which records are affected.\n")
    return "\n".join(L)
