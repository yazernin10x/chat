from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat_messages"
    verbose_name = "Messages"

    def ready(self):
        try:
            import apps.chat_messages.signals  # noqa
        except ImportError:
            pass
