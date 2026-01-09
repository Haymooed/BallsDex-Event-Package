from django.apps import AppConfig


class EventConfig(AppConfig):
    """Django app configuration for the event package."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "event"
    verbose_name = "Event Info"
    dpy_package = "event.package"  # Path to the discord.py extension
