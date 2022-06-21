from Core.bot import Horus
from .cog import BotStuff

async def setup(bot: Horus):
    await bot.add_cog(BotStuff(bot))