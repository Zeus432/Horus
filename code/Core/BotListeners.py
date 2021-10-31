import discord
from discord.ext import commands

from Utils.Useful import *
from Utils.Menus import *

class BotListeners(commands.Cog, name = "Listeners"):
    """ Bot Listeners for Major Bot Events """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if self.bot.devmode:
            return
        embed = discord.Embed(colour = discord.Color.random())
        embed.add_field(name="Command Used:", value=f"`{ctx.message.content}`", inline=False)
        embed.add_field(name="Author:", value=f"**{ctx.author}**\n (`{ctx.author.id}`)")
        if ctx.guild:
            embed.add_field(name="Channel:", value=f"**#{ctx.channel}**\n (`{ctx.channel.id}`)")
            embed.add_field(name="Guild:", value=f"**{ctx.guild}**\n (`{ctx.guild.id}`)")
        else:
            embed.add_field(name="Dm Channel:", value=f"**#{ctx.channel}**\n (`{ctx.channel.id}`)")
        embed.add_field(name="Message ID:", value=f"`{ctx.message.id}`")

        channel = self.bot.get_channel(889515203891449877)
        self.bot.cmdchannel = channel
        view = discord.ui.View()
        view.add_item(discord.ui.Button(url = f"{ctx.message.jump_url}", label = "Jump to Source", emoji = "\U0001f517"))
        await channel.send(embed = embed, view = view)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        channel = self.bot.get_channel(880294858600894494)
        if message.guild is None and not message.author.bot:
            final = message.content
            view = discord.ui.View()
            if len(message.content) > 1900:
                fl = await mystbin(data = message.content)
                final = f"Message too long to Display"
                view.add_item(discord.ui.Button(label="MystBin", style=discord.ButtonStyle.link, url=f"{fl}"))
            await channel.send(f"\u200b\n**{message.author}** (`{message.author.id}`) [<t:{round(message.created_at.timestamp())}:T>]\n{final}",view=view,files=[await attachment.to_file() for attachment in message.attachments])
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = self.bot.get_channel(874212184828297297)
        self.bot.log_channel = channel
        embed = guildanalytics(bot = self.bot, type = 1, guild = guild)
        await self.bot.log_channel.send(embed=embed)
        try:
            data = self.bot.blacklists[guild.id]
        except KeyError:
            data = await self.bot.db.fetchval('SELECT blacklists FROM guilddata WHERE guildid = $1', guild.id)
            if not data:
                blacklists = {'prevbl': 0, 'blacklisted': False}
                data = await self.bot.db.fetchval('INSERT INTO guilddata(guildid, blacklists) VALUES($1, $2) ON CONFLICT (guildid) DO UPDATE SET blacklists = $2 RETURNING blacklists', guild.id, blacklists)
                self.bot.blacklists[guild.id] = data
        if data["blacklisted"]:
            await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        try:
            embed = guildanalytics(bot = self.bot, type = 3 if self.bot.blacklists[guild.id]["blacklisted"] else 2, guild = guild)
        except KeyError:
            embed = guildanalytics(bot = self.bot, type = 2, guild = guild)
        channel = self.bot.get_channel(874212184828297297)
        self.bot.log_channel = channel
        await self.bot.log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(BotListeners(bot))
