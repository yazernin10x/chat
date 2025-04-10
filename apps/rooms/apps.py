from django.apps import AppConfig


class RoomsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rooms"

    def ready(self):
        try:
            import apps.rooms.signals  # noqa
        except ImportError:
            pass
