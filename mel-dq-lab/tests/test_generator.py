import pandas as pd

from meldq import config as C
from meldq.generate.build import fingerprint, generate_tables


def test_same_seed_same_data():
    a = fingerprint(generate_tables(7)[0])
    b = fingerprint(generate_tables(7)[0])
    c = fingerprint(generate_tables(8)[0])
    assert a == b and a != c


def test_answer_key_covers_all_error_types(world):
    _, key, _, _ = world
    assert set(key.error_id) == set(C.ERRORS)


def test_answer_key_entities_exist(world):
    tables, key, _, _ = world
    ids = {"survey": set(tables["survey"].submission_id), "training_log": set(tables["training_log"].participant_id)}
    rec = key[(key.level == "record") & key.table.isin(ids)]
    assert all(e in ids[t] for t, e in zip(rec.table, rec.entity_key))


def test_attrition_is_skewed_to_poorer_households(world):
    tables, _, truth, _ = world
    s = tables["survey"]
    b = truth[truth["round"] == "baseline"].set_index("hh_id").wealth_z
    gone = ~b.index.isin(s.loc[s["round"] == "endline", "hh_id"])
    assert 0.12 < gone.mean() < 0.25
    assert b[gone].mean() < b[~gone].mean() - 0.2
