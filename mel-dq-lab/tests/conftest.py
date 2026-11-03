import pytest

from meldq import pipeline
from meldq.generate.build import generate_tables


@pytest.fixture(scope="session")
def world():
    tables, key, truth = generate_tables(20260601)
    res = pipeline.run(tables, key, truth)
    return tables, key, truth, res
