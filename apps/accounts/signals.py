from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.conf import settings

from apps.accounts.models import User
from apps.shared.logging import get_logger

logger = get_logger("accounts.signals")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(
        f"Connexion réussie pour l'utilisateur {user.username} depuis {request.META.get('REMOTE_ADDR')}"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"Déconnexion réussie pour l'utilisateur {user.username}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger.warning(
        f"Tentative de connexion échouée pour l'utilisateur {credentials.get('username')}"
    )


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """Envoie un email HTML de bienvenue après l'inscription"""
    if created:
        logger.info(f"Le compte de {instance.username} ({instance.email}) a été créé.")
        site_url = getattr(settings, "SITE_URL", "")
        login_url = f"{site_url}/login"

        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <h2 style="color: #2c3e50;">Bonjour {instance.username}, bienvenue sur notre site !</h2>
                <p>Nous sommes ravis de vous compter parmi nous. Voici ce que vous pouvez faire dès maintenant :</p>
                <ul>
                    <li>Complétez votre profil</li>
                    <li>Découvrez nos fonctionnalités</li>
                    <li>Profitez pleinement de votre expérience</li>
                </ul>
                <p style="text-align: center;">
                    <a href="{login_url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Se connecter
                    </a>
                </p>
                <p>À bientôt,<br> L'équipe de <strong>{site_url}</strong></p>
            </div>
        </body>
        </html>
        """

        send_mail(
            "Bienvenue sur notre site !",
            "",
            settings.EMAIL_HOST_USER,
            [instance.email],
            html_message=html_message,
            fail_silently=True,
        )
        logger.info(f"Email de bienvenue envoyé à {instance.email}")


@receiver(post_delete, sender=User)
def send_delete_account_email(sender, instance, **kwargs):
    """Enregistre la suppression d'un utilisateur et envoie un email HTML de confirmation."""
    logger.info(f"Le compte de {instance.username} ({instance.email}) a été supprimé.")

    site_url = getattr(settings, "SITE_URL", "")
    support_url = f"{site_url}/contact"

    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h2 style="color: #e74c3c;">Votre compte a été supprimé</h2>
            <p>Bonjour {instance.username},</p>
            <p>Nous vous confirmons que votre compte a bien été supprimé de notre plateforme.</p>
            <p>Si ce n'était pas vous ou si vous avez des questions, veuillez nous contacter immédiatement.</p>
            <p style="text-align: center;">
                <a href="{support_url}" style="background-color: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Contacter le support
                </a>
            </p>
            <p>À bientôt,<br> L'équipe de <strong>{site_url}</strong></p>
        </div>
    </body>
    </html>
    """

    send_mail(
        "Confirmation de la suppression de votre compte",
        "",
        settings.EMAIL_HOST_USER,
        [instance.email],
        html_message=html_message,
        fail_silently=True,
    )
    logger.info(f"Email de confirmation de suppression envoyé à {instance.email}")
