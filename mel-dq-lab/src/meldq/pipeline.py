from . import checks
from .fieldverification import backcheck
from .scoring import benchmark as bm, impact as im, scorecard as sc
import pandas as pd


def run(tables, key, truth):
    issues, recon, recon_detail = checks.run_all(tables)
    sample = backcheck.design_sample(tables["survey"], issues)
    results = backcheck.simulate_reinterviews(sample, tables["survey"], truth)
    enum_disc, b01 = backcheck.enumerator_discrepancy(results)
    issues = pd.concat([issues, b01], ignore_index=True)
    card = sc.scorecard(tables, issues)
    return dict(issues=issues, recon=recon, recon_detail=recon_detail, bc_sample=sample, bc_results=results,
                enum_disc=enum_disc, benchmark=bm.benchmark(key, issues), check_perf=bm.check_performance(key, issues),
                scorecard=card, dim_summary=sc.dimension_summary(card),
                impact=im.impact_analysis(tables["survey"], truth, issues))
