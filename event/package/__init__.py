from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    from .cog import EventCog

    await bot.add_cog(EventCog(bot))
