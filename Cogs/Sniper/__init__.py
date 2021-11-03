from discord.ext import commands
from .sniper import Sniper

def setup(bot: commands.Bot):
    bot.add_cog(Sniper(bot))