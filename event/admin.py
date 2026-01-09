from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin

from .models import Event

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin for events."""

    list_display = (
        "id",
        "name",
        "enabled",
        "is_permanent",
        "status_display",
        "ball_count",
        "important_ball_count",
        "created_at",
    )
    list_filter = ("enabled", "is_permanent", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at", "status_display", "ball_count", "important_ball_count")
    filter_horizontal = ("included_balls", "important_balls")

    fieldsets = [
        (
            "Basic Information",
            {
                "fields": ("name", "description", "image_url", "enabled"),
            },
        ),
        (
            "Event Type & Dates",
            {
                "fields": ("is_permanent", "start_date", "end_date"),
                "description": "Set is_permanent=True for permanent events, or use start_date/end_date for limited-time events.",
            },
        ),
        (
            "Balls",
            {
                "fields": ("included_balls", "important_balls"),
                "description": "Select all balls included in this event. Important balls are a subset that will be highlighted.",
            },
        ),
        (
            "Statistics",
            {
                "fields": ("status_display", "ball_count", "important_ball_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    ]

    @admin.display(description="Status")
    def status_display(self, obj: Event) -> str:
        """Display the current status of the event."""
        status = obj.get_status()
        status_map = {
            "permanent": "🟢 Permanent",
            "active": "🟢 Active",
            "upcoming": "🟡 Upcoming",
            "ended": "🔴 Ended",
        }
        return status_map.get(status, status.title())

    @admin.display(description="Included Balls")
    def ball_count(self, obj: Event) -> str:
        """Display the number of included balls."""
        count = obj.included_balls.count()
        return f"{count} ball{'s' if count != 1 else ''}"

    @admin.display(description="Important Balls")
    def important_ball_count(self, obj: Event) -> str:
        """Display the number of important balls."""
        count = obj.important_balls.count()
        return f"{count} ball{'s' if count != 1 else ''}"

    def get_queryset(self, request):
        """Optimize queryset with prefetch."""
        return super().get_queryset(request).prefetch_related("included_balls", "important_balls")
