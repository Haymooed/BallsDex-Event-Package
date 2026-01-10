import logging
import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger(__name__)

LOGO = textwrap.dedent(r"""
    +---------------------------------------+
    |     Event Package by Haymooed        |
    |         Licensed under MIT           |
    +---------------------------------------+
""").strip()


async def setup(bot: "BallsDexBot"):
    print(LOGO)
    log.info("Loading event package...")
    from .cog import EventCog
    await bot.add_cog(EventCog(bot))
    log.info("Event package loaded successfully!")
