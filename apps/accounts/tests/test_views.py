import pytest
from django.test import Client
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core import mail

from apps.core.tests.helpers import assert_message_present
from core.settings import LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL
from apps.accounts.models import User
from apps.core.constants import (
    HTTP_200_OK,
    HTTP_302_REDIRECT,
    USERNAME_1,
    PASSWORD_1,
)


@pytest.mark.django_db(transaction=True)
class TestLoginView:
    def test_page_access(self, client: Client, user_1: User):
        response = client.get(reverse("accounts:login"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/login.html"

    def test_form_submission(self, client: Client, user_1: User):
        credentials = {"username": USERNAME_1, "password": PASSWORD_1}
        response = client.post(reverse("accounts:login"), credentials)
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == LOGIN_REDIRECT_URL
        assert_message_present(response, "Connexion réussie ! Bienvenue")


@pytest.mark.django_db(transaction=True)
class TestLogoutView:
    def test_logout(self, client: Client, user_1_connected: User):
        response = client.post(reverse("accounts:logout"))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == LOGOUT_REDIRECT_URL
        # assert_message_present(response, "Déconnexion réussie ! A bientôt")


@pytest.mark.django_db(transaction=True)
class TestRegisterView:
    def test_page_access(self, client: Client):
        response = client.get(reverse("accounts:register"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/register.html"

    def test_valid_submission(self, client: Client, form_data: dict):
        response = client.post(
            reverse("accounts:register"), data=form_data, follow=True
        )
        assert response.status_code == HTTP_200_OK
        assert response.resolver_match.url_name == "login"

        user = User.objects.get(
            username=form_data["username"], email=form_data["email"]
        )
        assert user is not None
        assert_message_present(response, "Votre compte a été créé avec succès !")

    def test_invalid_submission(self, client: Client):
        data_invalid = {"first_name": "test"}
        response = client.post(reverse("accounts:register"), data_invalid)
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/register.html"


@pytest.mark.django_db(transaction=True)
class TestProfileView:
    def test_page_access(self, client: Client, user_1_connected: User):
        response = client.get(reverse("accounts:profile"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/profile.html"

    def test_valid_submission_update_profile(
        self, client: Client, user_1_connected: User
    ):
        response = client.post(
            reverse("accounts:profile"),
            {
                "username": "jane.doe",
                "email": "jane.doe@example.com",
            },
        )
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("accounts:profile")

        user_1_connected.refresh_from_db()
        assert user_1_connected.username == "jane.doe"
        assert user_1_connected.email == "jane.doe@example.com"
        assert_message_present(response, "Votre profil a été mis à jour avec succès !")

    def test_profile_invalid_data_update_profile(
        self, client: Client, user_1_connected: User
    ):
        data = {"first_name": "test"}
        response = client.post(reverse("accounts:profile"), data)
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/profile.html"


@pytest.mark.django_db(transaction=True)
class TestDeleteView:
    def test_page_access(self, client: Client, user_1_connected: User):
        response = client.get(
            reverse("accounts:delete", kwargs={"pk": user_1_connected.pk})
        )
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/user_confirm_delete.html"

    def test_delete_submission(self, client: Client, user_1_connected: User):
        response = client.post(
            reverse("accounts:delete", kwargs={"pk": user_1_connected.pk})
        )
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("index")
        assert_message_present(response, "Votre compte a été supprimé avec succès !")
        assert not User.objects.filter(username=user_1_connected.username).exists()


@pytest.mark.django_db(transaction=True)
class TestPasswordChange:
    def test_page_access_password_change(self, client: Client, user_1_connected: User):
        response = client.get(reverse("accounts:password_change"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/password_change_form.html"

    def test_submission_form_password_change(
        self, client: Client, user_1_connected: User
    ):
        data = {
            "old_password": PASSWORD_1,
            "new_password1": PASSWORD_1,
            "new_password2": PASSWORD_1,
        }
        response = client.post(reverse("accounts:password_change"), data)
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("accounts:password_change_done")

    def test_page_access_password_change_done(
        self, client: Client, user_1_connected: User
    ):
        response = client.get(reverse("accounts:password_change_done"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/password_change_done.html"


@pytest.mark.django_db(transaction=True)
class TestPasswordReset:
    def test_page_access_password_reset(self, client: Client, user_1_connected: User):
        response = client.get(reverse("accounts:password_reset"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/password_reset_form.html"

    def test_submission_form_password_reset(
        self, client: Client, user_1_connected: User
    ):
        response = client.post(
            reverse("accounts:password_reset"), data={"email": user_1_connected.email}
        )
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("accounts:password_reset_done")

        # Vérifier l'envoi de l'email
        emails = [
            email
            for email in mail.outbox
            if email.subject
            == "Réinitialisation de votre mot de passe - Action requise"
        ]
        assert len(emails) == 1
        assert emails[0].to == [user_1_connected.email]
        assert user_1_connected.username in emails[0].body
        assert "password_reset_confirm" in emails[0].body

    def test_page_access_password_reset_done(
        self, client: Client, user_1_connected: User
    ):
        response = client.get(reverse("accounts:password_reset_done"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/password_reset_done.html"

    def test_page_access_password_reset_confirm(
        self, client: Client, user_1_connected: User
    ):
        # Générer un UID et un token valides
        uid = urlsafe_base64_encode(force_bytes(user_1_connected.pk))
        token = default_token_generator.make_token(user_1_connected)
        kwargs = {"uidb64": uid, "token": token}
        url = reverse("accounts:password_reset_confirm", kwargs=kwargs)

        # follow=True pour suivre la redirection
        response = client.get(url, follow=True)
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/password_reset_confirm.html"

        # On vérifie que nous sommes sur la bonne URL finale (avec set-password)
        assert response.resolver_match.url_name == "password_reset_confirm"
        assert response.request["PATH_INFO"].endswith("/set-password/")

    def test_submission_form_password_reset_confirm(
        self, client: Client, user_1_connected: User
    ):
        # Générer un UID et un token valides
        uid = urlsafe_base64_encode(force_bytes(user_1_connected.pk))
        token = default_token_generator.make_token(user_1_connected)

        # Première étape : obtenir l'URL avec set-password
        url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": uid, "token": token},
        )
        response = client.get(url, follow=True)

        # Deuxième étape : soumettre le nouveau mot de passe
        response = client.post(
            response.request["PATH_INFO"],  # URL avec set-password
            data={"new_password1": "projo#123", "new_password2": "projo#123"},
            follow=True,
        )

        # Vérifier la redirection finale
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/password_reset_complete.html"

        # Vérifier que le mot de passe a bien été changé
        user_1_connected.refresh_from_db()
        assert user_1_connected.check_password("projo#123")

    def test_page_access_password_reset_complete(
        self, client: Client, user_1_connected: User
    ):
        response = client.get(reverse("accounts:password_reset_complete"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "accounts/password_reset_complete.html"
