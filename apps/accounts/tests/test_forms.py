import pytest

from apps.accounts.forms import UserRegisterForm, UserUpdateForm
from apps.core.constants import PASSWORD_1


@pytest.mark.django_db(transaction=True)
class TestUserForms:
    def test_register_form(self, form_data: dict):
        form = UserRegisterForm(data=form_data)
        assert form.is_valid() is True
        assert form.cleaned_data["username"] == form_data["username"]
        assert form.cleaned_data["email"] == form_data["email"]
        assert form.cleaned_data["password1"] == PASSWORD_1
        assert form.cleaned_data["password2"] == PASSWORD_1

    def test_user_update_form(self, form_data: dict):
        del form_data["password1"], form_data["password2"]
        form = UserUpdateForm(data=form_data)
        assert form.is_valid() is True
        assert form.cleaned_data["first_name"] == form_data["first_name"]
        assert form.cleaned_data["last_name"] == form_data["last_name"]
        assert form.cleaned_data["email"] == form_data["email"]
        assert form.cleaned_data["username"] == form_data["username"]
        assert form.cleaned_data["phone_number"] == form_data["phone_number"]
