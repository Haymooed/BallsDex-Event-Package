from django.apps import AppConfig


class EventConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"
    name = "event"
    verbose_name = "Event Info"
    dpy_package = "event.package"