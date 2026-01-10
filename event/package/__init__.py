from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    from .cog import EventCog

    await bot.add_cog(EventCog(bot))

LOGO = textwrap.dedent(r"""
    +---------------------------------------+
    |     Event Package by Haymooed        |
    |         Licensed under MIT           |
    +---------------------------------------+
""").strip()


async def setup(bot: "BallsDexBot"):
    print(LOGO)
    log.info("Loading event package...")
    await bot.add_cog(Event(bot))
    log.info("Event package loaded successfully!")
