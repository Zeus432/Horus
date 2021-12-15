from discord.ext import commands
from .gethelp import NewHelp

class CustomHelp(commands.Cog):
    """ Custom Help Handling for the Bot """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        help_command = NewHelp()
        help_command.cog = self
        #bot.help_command = help_command

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

def setup(bot: commands.Bot):
    bot.add_cog(CustomHelp(bot))