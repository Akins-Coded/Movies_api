import os
import pytest
from django.db import connections
from django.db.utils import OperationalError

@pytest.fixture(autouse=True, scope="session")
def _skip_if_database_unavailable(django_db_setup, django_db_blocker):
    """
    Skip the whole test session if the default DB can't be reached.
    Works with pytest-django by unblocking DB during the check.
    Disable by setting ALLOW_DB_SKIP=false.
    """
    if os.environ.get("ALLOW_DB_SKIP", "true").lower() not in {"1", "true", "yes"}:
        return

    with django_db_blocker.unblock():
        try:
            connections["default"].ensure_connection()
        except OperationalError as e:
            pytest.skip(f"Database not available for tests: {e}")
