from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import DeleteView, CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin


from .forms import UserRegisterForm, UserUpdateForm
from .models import User


class AccountLoginView(SuccessMessageMixin, LoginView):
    template_name = "accounts/login.html"
    success_message = "Connexion réussie ! Bienvenue"


class AccountLogoutView(SuccessMessageMixin, LogoutView):
    template_name = "accounts/logout.html"
    success_message = "Déconnexion réussie ! A bientôt"


class UserRegisterView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")
    success_message = "Votre compte a été créé avec succès !"


class ProfileUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    form_class = UserUpdateForm
    template_name = "accounts/profile.html"
    context_object_name = "user"
    success_url = reverse_lazy("accounts:profile")
    success_message = "Votre profil a été mis à jour avec succès !"

    def get_object(self):
        return self.request.user


class UserDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("index")
    context_object_name = "user"
    success_message = "Votre compte a été supprimé avec succès !"
