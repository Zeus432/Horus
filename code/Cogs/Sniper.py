import discord
from discord import message
from discord.ext import commands

from Utils.Menus import *

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
        try:
            message = self.delete_cache[channel.id]
        except KeyError:
            return await ctx.reply("There are no messages to snipe!")
        embed = discord.Embed(description = f"{message.content}", colour = discord.Colour(0x2F3136))
        embed.set_author(icon_url = f"{message.author.display_avatar or message.author.default_avatar}", name = f"{message.author} ({message.author.id})")
        if message.attachments:
            embed.add_field(name = "Attachments:", value = "\n".join([f"\U000030fb **[{file.filename}]({file.url})**" for file in message.attachments]), inline = False)
        embed.add_field(name = "Sniped Deleted Message", value = f"Sent in {message.channel.mention} on <t:{int(message.created_at.timestamp())}>", inline = False)
        await ctx.reply(embed = embed)
    
    @commands.command(name = "esnipe", help = "Snipe the latest edited message in the current or specified channel", brief = "Snipe Edited Messges")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def esnipe(self, ctx, channel: discord.TextChannel = None):
        channel = channel if channel else ctx.channel
        try:
            message = self.edit_cache[channel.id]["before"]
        except KeyError:
            return await ctx.reply("There are no messages to snipe!")
        embed = discord.Embed(description = f"{message.content}", colour = discord.Colour(0x2F3136))
        embed.set_author(icon_url = f"{message.author.display_avatar or message.author.default_avatar}", name = f"{message.author} ({message.author.id})")
        if message.attachments:
            embed.add_field(name = "Attachments:", value = "\n".join([f"\U000030fb **[{file.filename}]({file.url})**" for file in message.attachments]), inline = False)
        embed.add_field(name = "Sniped Edited Message", value = f"Sent in {message.channel.mention} on <t:{int(message.created_at.timestamp())}>", inline = False)
        await ctx.reply(embed = embed)


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

def setup(bot: commands.Bot):
    bot.add_cog(Sniper(bot))