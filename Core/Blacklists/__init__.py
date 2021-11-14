from discord.ext import commands
from .blacklists import Blacklists

def setup(bot: commands.Bot):
    bot.add_cog(Blacklists(bot))