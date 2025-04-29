import pytest

from app.models import Payer
from tests.factories import PayerFactory

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests by default.
    """
    pass

@pytest.fixture
def payer():
    payer = PayerFactory.create()
    yield payer
    payer.delete()
    assert not Payer.objects.filter(pk=payer.pk).exists(), "Teardown failed: Payer was not removed from the database."

@pytest.fixture
def payer_generator():
    created_payers = []

    def _create_payers(n):
        payers = PayerFactory.create_batch(n)
        created_payers.extend(payers)
        return payers

    yield _create_payers

    # Teardown
    for payer in created_payers:
        payer.delete()

    assert not Payer.objects.filter(pk__in=[payer.pk for payer in created_payers]).exists(), "Teardown failed: Payers were not removed from the database."
