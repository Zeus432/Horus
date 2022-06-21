from Core.bot import Horus
from .cog import Dev

async def setup(bot: Horus):
    await bot.add_cog(Dev(bot))