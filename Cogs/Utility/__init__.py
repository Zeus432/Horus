from Core.bot import Horus
from .utility import Utility

async def setup(bot: Horus):
    await bot.add_cog(Utility(bot))