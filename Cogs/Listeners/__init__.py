from Core.bot import Horus
from .cog import Listeners

async def setup(bot: Horus):
    await bot.add_cog(Listeners(bot))