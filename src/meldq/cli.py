import argparse
import sys

from . import config as C
from .generate import build
from . import io, pipeline, reporting


def _write_reports(res, key, tables):
    C.REPORTS.mkdir(parents=True, exist_ok=True)
    res["issues"].to_csv(C.REPORTS / "flags_detail.csv", index=False)
    log = reporting.issue_log(res["issues"])
    log.to_csv(C.REPORTS / "issue_log.csv", index=False)
    res["scorecard"].to_csv(C.REPORTS / "dq_scorecard.csv", index=False)
    res["benchmark"].to_csv(C.REPORTS / "benchmark.csv", index=False)
    res["check_perf"].to_csv(C.REPORTS / "check_performance.csv", index=False)
    res["impact"].to_csv(C.REPORTS / "impact_of_dq.csv", index=False)
    res["recon"].to_csv(C.REPORTS / "reconciliation.csv", index=False)
    res["bc_sample"].to_csv(C.REPORTS / "backcheck_sample.csv", index=False)
    res["enum_disc"].to_csv(C.REPORTS / "enumerator_backcheck_summary.csv", index=False)
    (C.REPORTS / "corrective_action_plan.md").write_text(reporting.corrective_action_plan(log))
    (C.REPORTS / "dqa_report.md").write_text(reporting.dqa_report(res, key, tables))


def main(argv=None):
    p = argparse.ArgumentParser(prog="meldq", description="MEL data-quality lab")
    p.add_argument("command", choices=["generate", "check", "all", "robustness"])
    p.add_argument("--seed", type=int, default=C.SEED)
    p.add_argument("--n", type=int, default=20, help="number of seeds for robustness")
    a = p.parse_args(argv)
    if a.command == "robustness":
        import pandas as pd
        out = []
        for sd in range(1, a.n + 1):
            tables, key, truth = build.generate_tables(sd)
            b = pipeline.run(tables, key, truth)["benchmark"].assign(seed=sd)
            out.append(b)
        allb = pd.concat(out)
        agg = allb.groupby(["error_id", "error"]).agg(mean_recall=("recall", "mean"), min_recall=("recall", "min"),
                                                      max_recall=("recall", "max"), mean_precision=("precision", "mean"),
                                                      detected_in_seeds=("detected", "sum")).round(3).reset_index()
        agg["seeds"] = a.n
        C.REPORTS.mkdir(parents=True, exist_ok=True)
        agg.to_csv(C.REPORTS / "robustness.csv", index=False)
        print(agg.to_string(index=False))
        return 0
    if a.command in ("generate", "all"):
        tables, key, truth = build.generate_tables(a.seed)
        build.write(tables, key, truth)
        print(f"generated data (fingerprint {build.fingerprint(tables)}) -> {C.RAW}")
    if a.command in ("check", "all"):
        tables = io.load_tables()
        key, truth = io.load_answer_key()
        res = pipeline.run(tables, key, truth)
        _write_reports(res, key, tables)
        b = res["benchmark"]
        print(b[["error_id", "error", "level", "recall", "precision", "detected", "checks"]].to_string(index=False))
        print(f"\nDetected {int(b.detected.sum())} of {len(b)} error types. Reports -> {C.REPORTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
