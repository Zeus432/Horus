from discord.ext import commands
from .utility import Utility

def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))