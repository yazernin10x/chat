from django.db.models import (
    BooleanField,
    DateTimeField,
    EmailField,
)
from django.contrib.auth.models import AbstractUser

from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    class Meta:
        ordering = ["first_name", "last_name", "username"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    email = EmailField("Adresse email", unique=True, blank=False, null=False)
    phone_number: PhoneNumberField = PhoneNumberField(blank=True, null=True)
    date_updated: DateTimeField = DateTimeField(auto_now=True)
    is_online: BooleanField = BooleanField(default=False)

    def __repr__(self) -> str:
        return f"User(username='{self.username}', email='{self.email}')"

    def get_display_name(self) -> str:
        return self.get_full_name() or self.username

    def set_online_status(self, status: bool = True):
        """Met à jour le statut en ligne de l'utilisateur."""
        self.is_online = status
        self.save(update_fields=["is_online"])
