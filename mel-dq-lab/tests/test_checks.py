import pandas as pd
import pytest

from meldq import config as C
from meldq.checks import survey as S


def bm(world):
    return world[3]["benchmark"].set_index("error_id")


@pytest.mark.parametrize("eid,min_recall", [(1, 1.0), (5, 0.95), (6, 0.95), (7, 0.95), (8, 0.95), (12, 0.95), (13, 1.0), (14, 0.95), (4, 0.85)])
def test_record_level_recall(world, eid, min_recall):
    assert bm(world).loc[eid, "recall"] >= min_recall


def test_fuzzy_dedup_recall_is_good_but_imperfect(world):
    r = bm(world).loc[11, "recall"]
    assert 0.6 <= r < 1.0   # initials-only variants are expected misses


@pytest.mark.parametrize("eid", [3, 9, 10])
def test_dataset_level_detected(world, eid):
    assert bm(world).loc[eid, "detected"]


def test_blatant_fabricator_caught(world):
    issues = world[3]["issues"]
    assert C.FABRICATOR in set(issues[issues.level == "enumerator"].entity_key)


def test_no_honest_enumerator_flagged_by_automated_enumerator_checks(world):
    issues = world[3]["issues"]
    auto = issues[issues.check_id.isin(["E01", "E02", "E03"])]
    assert set(auto.entity_key) <= {C.FABRICATOR, C.SUBTLE_FAB}


def test_deterministic_rules_have_no_false_positives_on_clean_truth(world):
    _, _, truth, _ = world
    out = pd.concat(S.record_checks(truth))
    for cid in ["R02", "R03", "R04", "R07", "R08", "R10", "R11", "R12", "R13", "R14", "R15"]:
        assert (out.check_id == cid).sum() == 0, cid


def test_data_dictionary_covers_every_column(world):
    tables = world[0]
    dd = pd.read_csv(C.ROOT / "docs" / "data_dictionary.csv")
    for name in ("survey", "training_log", "hh_roster", "partner_reports", "donor_report"):
        assert set(tables[name].columns) <= set(dd[dd.table == name].column), name


def test_reconciliation_shows_overreporting(world):
    rc = world[3]["recon"].set_index("level").value
    assert rc["Donor-reported figure"] > rc["Estimated unique farmers (after fuzzy de-duplication)"]
