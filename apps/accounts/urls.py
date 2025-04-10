from django.urls import path
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from . import views


app_name = "accounts"

urlpatterns = [
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("<int:pk>/delete/", views.UserDeleteView.as_view(), name="delete"),
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", views.AccountLogoutView.as_view(), name="logout"),
]

# Password change
urlpatterns += [
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="accounts/password_change_form.html",
            success_url="/accounts/password_change_done/",
        ),
        name="password_change",
    ),
    path(
        "password_change_done/",
        PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
]

# Password reset
urlpatterns += [
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="accounts/password_reset_form.html",
            success_url="/accounts/password_reset_done/",
            email_template_name="accounts/password_reset_email.html",
            html_email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset_done/",
        PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/password_reset_complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
