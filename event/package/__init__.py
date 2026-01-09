from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    """Setup function for the event package."""
    # Import here to avoid Django app registry issues during module import
    from .cog import BallsEventCog, EventCog

    await bot.add_cog(EventCog(bot))

    # Try to add /balls event command
    # Note: This may conflict if the main bot already has a /balls command group.
    # If there's a conflict, you may need to manually integrate /balls event into the existing group.
    try:
        await bot.add_cog(BallsEventCog(bot))
    except Exception:
        # If adding BallsEventCog fails (e.g., due to existing /balls group),
        # that's okay - /event info will still work
        # The main bot can manually add the /balls event command if needed
        pass
