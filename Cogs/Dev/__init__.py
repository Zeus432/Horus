from Core.bot import Horus
from .dev import Dev

async def setup(bot: Horus):
    await bot.add_cog(Dev(bot))