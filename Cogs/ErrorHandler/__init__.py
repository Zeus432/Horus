from discord.ext import commands
from .errorhandler import ErrorHanlder

def setup(bot: commands.Bot):
    bot.add_cog(ErrorHanlder(bot))