from discord.ext.commands.cog import Cog
from Useful.Useful import botemojis
from discord.ext import commands
import discord
from Useful.settings import *
import datetime
from dateutil.relativedelta import relativedelta
import asyncio
from Cogs.CustomHelp import *

class AdminCogs(commands.Cog, name = "Admin"):
    COLOUR = discord.Colour(0x9c9cff)
    def __init__(self, bot: commands.Bot):
        self.bot = bot 

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.group(pass_context=True, name='permissions', aliases = ['perms'], invoke_without_command = True)
    async def permissions(self, ctx):
        await ctx.send_help('permissions')
    @permissions.command()
    async def add(self, ctx):
        print(2)

def setup(bot: commands.Bot):
    bot.add_cog(AdminCogs(bot))