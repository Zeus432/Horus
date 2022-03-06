from bot import Horus
import discord
from discord.ext import commands

import random

class ImageApi(commands.Cog, name = "Image Api"):
    """ Image Api Commands """ 
    def __init__(self, bot: Horus):
        self.bot = bot
    
    @commands.command(name = "eject")
    @commands.bot_has_permissions(attach_files = True)
    async def eject(self, ctx: commands.Context, user: discord.Member):
        image = await self.bot.vac_api.ejected(f"{user.display_name}", 'random', f'{random.choice(["True", "False"])}')
        image_out = discord.File(fp = await image.read(), filename = "ejected.png")
        await ctx.send(file = image_out)
    
    @commands.command(name = "firsttime")
    @commands.bot_has_permissions(attach_files = True)
    async def first_time(self, ctx: commands.Context, user: discord.Member):
        image = await self.bot.vac_api.first_time(f"{user.display_avatar}")
        image_out = discord.File(fp = await image.read(), filename = "ejected.png")
        await ctx.send(file = image_out)
