from discord.ext import commands
from .fun import Fun

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))