import discord
from discord.ext import commands

class Sniper(commands.Cog):
    """ Snipe the latest deleted or edited message """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delete_cache = {}
        self.edit_cache = {}
    
    @commands.command(name = "snipe", help = "Snipe the latest deleted message in the current or specified channel", brief = "Snipe Deleted Messges")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        channel = channel if channel else ctx.channel
    
    @commands.command(name = "esnipe", help = "Snipe the latest edited message in the current or specified channel", brief = "Snipe Edited Messges")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def esnipe(self, ctx, channel: discord.TextChannel = None):
        channel = channel if channel else ctx.channel

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        self.delete_cache[message.channel.id] = message
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return
        self.edit_cache[before.channel.id] = {"before":before,"after":after}
    
    def cog_unload(self):
        self.delete_cache = {}
        self.edit_cache = {}