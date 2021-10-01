from discord.ext import commands


class Misc(commands.Cog):
    """ Miscellaneous Bot Info and Stats commands """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.bot.launch_time = bot.launch_time
    
def setup(bot: commands.Bot):
    bot.add_cog(Misc(bot))