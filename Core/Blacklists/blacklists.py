import discord
from discord.ext import commands

from Core.settings import BOTMODS

class Blacklists(commands.Cog):
    """ Blacklist dumb people and probably don't unblacklist them """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._mc = commands.MaxConcurrency(1, per = commands.BucketType.user, wait = False)

        for command in self.walk_commands():
            command._max_concurrency = self._mc # Set Concurrency to all the commands
    
    def cog_check(self, ctx: commands.Context) -> bool:
        return True if (ctx.author.id in BOTMODS) or self.bot.is_owner(ctx.author) else False
