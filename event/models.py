from __future__ import annotations

from django.db import models
from django.utils import timezone

from bd_models.models import Ball


class Event(models.Model):
    """
    An event that groups balls together for informational purposes.
    Events can be permanent or limited-time.
    """

    name = models.CharField(
        max_length=128,
        help_text="Name of the event",
        unique=True,
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the event",
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Whether this event is visible to players",
    )
    is_permanent = models.BooleanField(
        default=False,
        help_text="If True, this is a permanent event. If False, use start_date and end_date.",
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Start date for limited-time events. Ignored if is_permanent=True.",
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="End date for limited-time events. Ignored if is_permanent=True.",
    )
    included_balls = models.ManyToManyField(
        Ball,
        related_name="events",
        blank=True,
        help_text="All balls included in this event",
    )
    important_balls = models.ManyToManyField(
        Ball,
        related_name="important_events",
        blank=True,
        help_text="Featured or important balls in this event (subset of included_balls)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.name

    def get_status(self) -> str:
        """
        Get the current status of the event.
        Returns: 'permanent', 'active', 'upcoming', or 'ended'
        """
        if self.is_permanent:
            return "permanent"

        now = timezone.now()

        if self.start_date and now < self.start_date:
            return "upcoming"
        elif self.end_date and now > self.end_date:
            return "ended"
        else:
            return "active"

    def is_currently_active(self) -> bool:
        """Check if the event is currently active (permanent or within date range)."""
        if self.is_permanent:
            return True

        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
