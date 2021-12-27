import disnake
from bot import Horus
from disnake.ext import commands

class Sniper(commands.Cog):
    """ Snipe deleted messages """ 
    def __init__(self, bot: Horus):
        self.bot = bot
        self.delete_cache = {}
        self.edit_cache = {}

    @commands.command(name = "snipe", brief = "Snipe Deleted Messges")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def snipe(self, ctx: commands.Context, channel: disnake.TextChannel = None):
        """ Snipe the latest deleted message in the current or specified channel """
        channel = channel or ctx.channel

        try:
            message: disnake.Message = self.delete_cache[channel.id]
        except KeyError:
            return await ctx.reply("There are no messages to snipe!")

        embed = disnake.Embed(description = f"{message.content}", colour = disnake.Colour(0x2F3136))
        embed.set_author(icon_url = f"{message.author.display_avatar or message.author.default_avatar}", name = f"{message.author} ({message.author.id})")
        if message.attachments:
            embed.add_field(name = "Attachments:", value = "\n".join([f"\U000030fb **[{file.filename}]({file.url})**" for file in message.attachments]), inline = False)
        embed.add_field(name = "Sniped Deleted Message", value = f"Sent in {message.channel.mention} on <t:{int(message.created_at.timestamp())}>", inline = False)

        await ctx.reply(embed = embed)
    
    @commands.command(name = "esnipe", brief = "Snipe Edited Messges")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def esnipe(self, ctx: commands.Context, channel: disnake.TextChannel = None):
        """ Snipe the latest edited message in the current or specified channel """
        channel = channel or ctx.channel

        try:
            message: disnake.Message = self.edit_cache[channel.id]["before"]
        except KeyError:
            return await ctx.reply("There are no messages to snipe!")

        embed = disnake.Embed(description = f"{message.content}", colour = disnake.Colour(0x2F3136))
        embed.set_author(icon_url = f"{message.author.display_avatar or message.author.default_avatar}", name = f"{message.author} ({message.author.id})")
        if message.attachments:
            embed.add_field(name = "Attachments:", value = "\n".join([f"\U000030fb **[{file.filename}]({file.url})**" for file in message.attachments]), inline = False)
        embed.add_field(name = "Sniped Edited Message", value = f"Sent in {message.channel.mention} on <t:{int(message.created_at.timestamp())}>", inline = False)

        await ctx.reply(embed = embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        if message.author.bot:
            return

        self.delete_cache[message.channel.id] = message
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if before.author.bot:
            return

        self.edit_cache[before.channel.id] = {
            "before": before,
            "after": after
        }
    
    def cog_unload(self):
        self.delete_cache = {}
        self.edit_cache = {}