from discord.ext import commands
from .admin import Admin

def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))