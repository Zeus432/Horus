from Core.bot import Horus
from .botstuff import BotStuff


async def setup(bot: Horus):
    await bot.add_cog(BotStuff(bot))
