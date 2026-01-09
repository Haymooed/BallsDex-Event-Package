from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import discord
from asgiref.sync import sync_to_async
from discord import app_commands
from discord.ext import commands
from django.utils import timezone

from ..models import Event

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

Interaction = discord.Interaction["BallsDexBot"]


def format_datetime(dt: datetime) -> str:
    """Format a datetime for display in Discord."""
    if dt is None:
        return "N/A"
    # Format as: Jan 1, 2024 at 12:00 PM
    return dt.strftime("%b %d, %Y at %I:%M %p")


async def create_event_embed(event: Event) -> discord.Embed:
    """Create a Discord embed for an event."""
    status = event.get_status()
    status_map = {
        "permanent": ("🟢 Permanent Event", discord.Color.green()),
        "active": ("🟢 Active", discord.Color.green()),
        "upcoming": ("🟡 Upcoming", discord.Color.gold()),
        "ended": ("🔴 Ended", discord.Color.red()),
    }
    status_text, color = status_map.get(status, ("Unknown", discord.Color.default()))

    embed = discord.Embed(
        title=event.name,
        description=event.description or "No description provided.",
        color=color,
        timestamp=timezone.now(),
    )

    # Status field
    embed.add_field(name="Status", value=status_text, inline=True)

    # Availability field
    if event.is_permanent:
        availability = "**Permanent Event**"
    else:
        start_str = format_datetime(event.start_date) if event.start_date else "Not set"
        end_str = format_datetime(event.end_date) if event.end_date else "Not set"
        availability = f"**Start:** {start_str}\n**End:** {end_str}"

    embed.add_field(name="Availability", value=availability, inline=True)

    # Included Balls
    included_balls = await sync_to_async(list)(event.included_balls.all())
    if included_balls:
        ball_names = [ball.country for ball in included_balls[:20]]  # Limit to 20 for display
        ball_text = ", ".join(ball_names)
        if len(included_balls) > 20:
            ball_text += f" *(+{len(included_balls) - 20} more)*"
        embed.add_field(
            name=f"Included Balls ({len(included_balls)})",
            value=ball_text or "None",
            inline=False,
        )
    else:
        embed.add_field(name="Included Balls", value="No balls included.", inline=False)

    # Important/Featured Balls
    important_balls = await sync_to_async(list)(event.important_balls.all())
    if important_balls:
        important_names = [ball.country for ball in important_balls[:10]]  # Limit to 10 for display
        important_text = "⭐ " + ", ".join(important_names)
        if len(important_balls) > 10:
            important_text += f" *(+{len(important_balls) - 10} more)*"
        embed.add_field(
            name=f"⭐ Featured Balls ({len(important_balls)})",
            value=important_text or "None",
            inline=False,
        )

    embed.set_footer(text=f"Event ID: {event.id}")

    return embed


class EventCog(commands.GroupCog, name="event"):
    """View information about events and their associated balls."""

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        super().__init__()

    @property
    def qualified_name(self) -> str:
        return "event"

    async def _get_event_by_name(self, name: str) -> Event | None:
        """Get an event by name (case-insensitive)."""
        try:
            return await Event.objects.aget(name__iexact=name, enabled=True)
        except Event.DoesNotExist:
            return None

    # ---- Player commands ----

    @app_commands.command(name="info", description="View detailed information about a specific event.")
    @app_commands.describe(event="The name of the event to view")
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    async def event_info(self, interaction: Interaction, event: str):
        """View information about a specific event."""
        await interaction.response.defer(ephemeral=False)

        event_obj = await self._get_event_by_name(event)
        if not event_obj:
            await interaction.followup.send(
                f"Event '{event}' not found or is disabled. Please check the event name and try again.",
                ephemeral=True,
            )
            return

        embed = await create_event_embed(event_obj)
        await interaction.followup.send(embed=embed)


class BallsEventCog(commands.GroupCog, name="balls"):
    """
    Integration point for /balls event command.
    Note: This may conflict if the main bot already has a /balls command group.
    In that case, the main bot should handle /balls event routing manually.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        super().__init__()

    @property
    def qualified_name(self) -> str:
        return "balls"

    @app_commands.command(name="event", description="View detailed information about a specific event.")
    @app_commands.describe(event="The name of the event to view")
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    async def balls_event(self, interaction: Interaction, event: str):
        """View information about a specific event via /balls event."""
        await interaction.response.defer(ephemeral=False)

        try:
            event_obj = await Event.objects.aget(name__iexact=event, enabled=True)
        except Event.DoesNotExist:
            await interaction.followup.send(
                f"Event '{event}' not found or is disabled. Please check the event name and try again.",
                ephemeral=True,
            )
            return

        embed = await create_event_embed(event_obj)
        await interaction.followup.send(embed=embed)


# Export the helper function and cogs for potential use by the main bot
__all__ = ["EventCog", "BallsEventCog", "create_event_embed"]
