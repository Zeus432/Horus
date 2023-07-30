from Core.bot import Horus
from .cog import Fun

async def setup(bot: Horus):
    await bot.add_cog(Fun(bot))