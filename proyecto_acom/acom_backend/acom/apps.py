from django.apps import AppConfig


class AcomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "acom"

    def ready(self):
        from . import receivers  # noqa: F401 — registra los receptores de signals
