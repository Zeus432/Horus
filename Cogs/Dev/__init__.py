from discord.ext import commands
from .dev import Dev

def setup(bot: commands.Bot):
    bot.add_cog(Dev(bot))