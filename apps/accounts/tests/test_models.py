import pytest

from apps.accounts.models import User
from apps.core.constants import (
    PASSWORD_1,
    FIRST_NAME_1,
    LAST_NAME_1,
    USERNAME_1,
    EMAIL_1,
)


@pytest.mark.django_db(transaction=True)
class TestUserModel:
    def test_register(self, user_1: User):
        assert user_1.first_name == FIRST_NAME_1
        assert user_1.last_name == LAST_NAME_1
        assert user_1.username == USERNAME_1
        assert user_1.email == EMAIL_1
        assert user_1.check_password(PASSWORD_1)

    def test__repr__(self, user_1: User):
        assert repr(user_1) == f"User(username='{USERNAME_1}', email='{EMAIL_1}')"
