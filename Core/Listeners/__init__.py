from discord.ext import commands
from .listeners import Listeners

def setup(bot: commands.Bot):
    bot.add_cog(Listeners(bot))