import discord
from Core.bot import Horus
from discord.ext import commands

import time

class BotStuff(commands.Cog):
    """ Bot Related Stuff """

    def __init__(self, bot: Horus):
        self.bot = bot
    
    @commands.command(name = "info", aliases = ['about','botinfo'], brief = "Get Bot Info")
    async def info(self, ctx: commands.Context):
        """ View some info about the bot """
        await ctx.send(f"Hello there, I'm {self.bot.user.name}") # develop this later
    
    @commands.command(name = "ping", brief = "Take a wild guess")
    async def ping(self, ctx: commands.Context):
        """ View the ping of the bot """
        async with ctx.typing():
            start = time.perf_counter()
            msg = await ctx.send(f"Pinging...")
            end = time.perf_counter()
            typing_ping = (end - start) * 1000

            start = time.perf_counter()
            await self.bot.db.execute('SELECT 1')
            end = time.perf_counter()
            postgres_ping = (end - start) * 1000

            start = time.perf_counter()
            await self.bot.redis.ping()
            end = time.perf_counter()
            redis_ping = (end - start) * 1000

        embed = discord.Embed(description = f"```yaml\nTyping: {round(typing_ping, 1)} ms\n"
        f"Websocket: {round(self.bot.latency*1000)} ms\n"
        f"Postgres: {round(postgres_ping, 1)} ms\n"
        f"Redis: {round(redis_ping, 1)} ms```",
        colour = discord.Colour(0x2F3136))

        await msg.edit(content = "Pong \U0001f3d3", embed = embed)
    
    @commands.command(name = 'uptime', aliases = ["ut"], brief = "Bot Uptime")
    async def uptime(self, ctx: commands.Context):
        """Gets the uptime of the bot"""
        uptime_string = self.bot.get_uptime()
        await ctx.channel.send(f'**{self.bot.user.name}** has been up for {uptime_string}.\nSince <t:{round(self.bot._launch.timestamp())}>')
    
    @commands.command(name = "prefix", brief = "Get Server prefix")
    async def prefix(self, ctx: commands.Context):
        """ Get a list of server prefixes """
        embed = discord.Embed(colour = self.bot.colour, description = "`" + "`\n`".join([f'@{self.bot.user.name}', *(prefix if prefix else '\u200b' for index, prefix in enumerate(await self.bot.getprefix(self.bot, ctx.message)) if index > 1) ]) + "`")
        embed.set_author(name = f"{ctx.guild}", icon_url = f"{ctx.guild.icon}")

        if ctx.author.guild_permissions.administrator:
            embed.set_footer(text = f"Set prefix with `{ctx.clean_prefix}prefix set <prefix>`")

        await ctx.reply(embed = embed, mention_author = False)