from Core.bot import Horus
from .cog import ErrorHandler

async def setup(bot: Horus):
    await bot.add_cog(ErrorHandler(bot))