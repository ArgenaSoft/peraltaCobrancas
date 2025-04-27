import pytest

from app.controllers.payer_controller import PayerController
from app.models import Payer
from app.schemas import PayerSchema

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests by default.
    """
    pass

@pytest.fixture
def payer():
    schema = PayerSchema.In(
        name='teste',
        phone='44920029305',
        cpf='13469282072',
    )

    payer = PayerController.create(schema)
    yield payer
    payer.delete()
    assert not Payer.objects.filter(pk=payer.pk).exists(), "Teardown failed: Payer was not removed from the database."
