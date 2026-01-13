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
    if dt is None:
        return "N/A"
    return dt.strftime("%b %d, %Y at %I:%M %p")


async def event_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
    events = Event.objects.filter(enabled=True).order_by("name")
    event_list = await sync_to_async(list)(events.values_list("name", flat=True))

    if current:
        event_list = [name for name in event_list if current.lower() in name.lower()]

    return [app_commands.Choice(name=name, value=name) for name in event_list[:25]]


async def create_event_embed(event: Event) -> discord.Embed:
    """Create a Discord embed for an event."""
    status = event.get_status()
    status_map = {
        "permanent": ("Permanent Event", discord.Color.green()),
        "active": ("Active", discord.Color.green()),
        "upcoming": ("Upcoming", discord.Color.gold()),
        "ended": ("Ended", discord.Color.red()),
    }
    status_text, color = status_map.get(status, ("Unknown", discord.Color.default()))

    embed = discord.Embed(
        title=event.name,
        description=event.description or "No description provided.",
        color=color,
        timestamp=timezone.now(),
    )

    if event.image_url:
        embed.set_image(url=event.image_url)

    embed.add_field(name="Status", value=status_text, inline=True)

    if event.is_permanent:
        availability = "**Permanent Event**"
    else:
        start_str = format_datetime(event.start_date) if event.start_date else "Not set"
        end_str = format_datetime(event.end_date) if event.end_date else "Not set"
        availability = f"**Start:** {start_str}\n**End:** {end_str}"

    embed.add_field(name="Availability", value=availability, inline=True)

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

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        super().__init__()

    @property
    def qualified_name(self) -> str:
        return "event"

    async def _get_event_by_name(self, name: str) -> Event | None:
        try:
            return await Event.objects.aget(name__iexact=name, enabled=True)
        except Event.DoesNotExist:
            return None

    @app_commands.command(name="info", description="View detailed information about a specific event.")
    @app_commands.describe(event="Select an event to view")
    @app_commands.autocomplete(event=event_autocomplete)
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


__all__ = ["EventCog", "create_event_embed"]
