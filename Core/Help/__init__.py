from disnake.ext import commands
from .gethelp import NewHelp
from bot import Horus

class CustomHelp(commands.Cog):
    """ Custom Help Handling """
    def __init__(self, bot: Horus):
        self.bot = bot
        self._original_help_command = bot.help_command
        help_command = NewHelp()
        help_command.cog = self
        bot.help_command = help_command

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

def setup(bot: Horus):
    bot.add_cog(CustomHelp(bot))