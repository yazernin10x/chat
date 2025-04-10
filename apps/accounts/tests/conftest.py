import pytest

from apps.core.constants import (
    FIRST_NAME_1,
    LAST_NAME_1,
    USERNAME_1,
    PHONE_NUMBER_1,
    EMAIL_1,
    PASSWORD_1,
)

from apps.core.tests.fixtures import user_1, user_1_connected


@pytest.fixture(scope="function")
def form_data():
    return {
        "first_name": FIRST_NAME_1,
        "last_name": LAST_NAME_1,
        "username": USERNAME_1,
        "phone_number": PHONE_NUMBER_1,
        "email": EMAIL_1,
        "password1": PASSWORD_1,
        "password2": PASSWORD_1,
    }
