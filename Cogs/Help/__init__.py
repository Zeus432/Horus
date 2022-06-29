from Core.bot import Horus
from .cog import Help

async def setup(bot: Horus):
    await bot.add_cog(Help(bot))