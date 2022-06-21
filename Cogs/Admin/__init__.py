from Core.bot import Horus
from .cog import Admin

async def setup(bot: Horus):
    await bot.add_cog(Admin(bot))