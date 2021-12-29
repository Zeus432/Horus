import discord
from discord.ext import commands

import humanize
import psutil
import time
import os

from Core.Utils.useful import _size
from .useful import total_stuff, pie_gen
from .menus import InfoButtons

class BotStuff(commands.Cog):
    """ Bot Stats and Stuff """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name = "info", help = "View some info about the bot", brief = "Get Bot Info", aliases = ['about','botinfo'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def info(self, ctx):
        embed = discord.Embed(title = "About Horus",  description = f"Horus is a private bot written in about `{total_stuff('.')[1]}` lines. It was initially made for testing but now includes a lot more now\nIt has Simple Utility, Fun Commands. Run `{ctx.clean_prefix}help` to get started. For bot support join the support server by clicking the button below\n\u200b", colour = self.bot.colour)
        embed.add_field(name = "Developed By", value = f"**[{self.bot.zeus}](https://www.youtube.com/watch?v=Uj1ykZWtPYI)**")
        embed.add_field(name = "Coded in", value = f"**Language:** **[`python 3.10.0`](https://www.python.org/)**\n**Library:** **[`discord.py 2.3.0`](https://github.com/DisnakeDev/disnake)**")
        embed.add_field(name = "\u200b", value = "**Bot Analytics**", inline = False)
        embed.add_field(name = "Running On", value = f"{self.bot.get_em('horus')} `{self.bot.config['version']}`\n\u200b")
        embed.add_field(name = "On Discord Since", value = f"<t:{round(self.bot.user.created_at.timestamp())}:D>")
        embed.add_field(name = "Bot Uptime", value = f"{self.bot.get_uptime()}")
        embed.add_field(name = "Statistics", value = f"```yaml\nUsers:    {len([g.id for g in self.bot.users])}\nServers:  {len([g.id for g in self.bot.guilds])}\nChannels: {sum([len([chan.id for chan in guild.channels]) for guild in self.bot.guilds])}\nCommands: {len(list(self.bot.walk_commands()))}```")
        embed.add_field(name = "System", value = f"```yaml\nSystem OS:{' '*6}macOS\nCPU Usage:{' '*6}{round(psutil.getloadavg()[2]/os.cpu_count()*100, 2)}%\nRAM Usage:{' '*6}{round(psutil.virtual_memory()[2], 2)}%\nMemory Usage:   {humanize.naturalsize(psutil.Process().memory_full_info().uss)}```")
        embed.set_thumbnail(url = self.bot.user.display_avatar)

        view = InfoButtons(ctx = ctx, bot = self.bot)

        view.message = await ctx.send(embed = embed, view = view)

    @commands.command(name = "ping", help = "View the ping of the bot", brief = "Take a wild guess")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        async with ctx.typing():
            start = time.perf_counter()
            msg = await ctx.send(f"Pinging...")
            end = time.perf_counter()
        typing_ping = (end - start) * 1000

        start = time.perf_counter()
        await self.bot.db.execute('SELECT 1')
        end = time.perf_counter()
        postgres_ping = (end - start) * 1000

        embed = discord.Embed(description = f"```yaml\nTyping: {round(typing_ping, 1)} ms\nWebsocket: {round(self.bot.latency*1000)} ms\nDatabase: {round(postgres_ping, 1)} ms```", colour = discord.Colour(0x2F3136))

        await msg.edit(content = "Pong \U0001f3d3", embed = embed)

    @commands.command(name = 'uptime', brief = "Bot Uptime")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def uptime(self, ctx: commands.Context):
        """Gets the uptime of the bot"""
        uptime_string = self.bot.get_uptime()
        await ctx.channel.send(f'**{self.bot.user.name}** has been up for {uptime_string}.\nSince <t:{round(self.bot.launch_ts)}>')
    
    @commands.command(name = 'support', brief = "Bot Support")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def support(self, ctx: commands.Context):
        """ Get an Invite to Horus' Support Server """
        msg = "<#892767470379749456>: For bot support and For reporting bugs" if ctx.guild.id == 873127663840137256 else "Here is an invite to my Support Server.\n**[ https://discord.gg/8BQMHAbJWk ]**"
        await ctx.reply(msg)
    
    @commands.command(name = "pie-bot", brief = "Bot/Member ratio")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def pie_bot(self, ctx: commands.Context):
        """Make a pie chart of server bots."""

        fp, prc = await pie_gen(ctx)

        fp = discord.File(fp, filename = "piechart.png")

        await ctx.send(f"{self.bot.get_em('tick')} {prc}% of the server's members are bots.", file = fp)
    
    @commands.is_owner()
    @commands.command(name = "prefix", brief = "Get Server prefix")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def prefix(self, ctx: commands.Context):
        """ Get a list of server prefixes """
        embed = discord.Embed(colour = self.bot.colour, description = "`" + "`\n`".join([f'@{self.bot.user.name}', *(prefix for index, prefix in enumerate(await self.bot.getprefix(self.bot, ctx.message)) if index > 1) ]) + "`")
        embed.set_author(name = f"{ctx.guild}", icon_url = ctx.guild.icon.url or discord.Embed.Empty)
        embed.set_footer(text = f"Set prefix with `{ctx.clean_prefix}setprefix <prefix>`")

        await ctx.reply(embed = embed, allowed_mentions = discord.AllowedMentions.none())