from sys import prefix
import discord
from Core.bot import Horus, HorusCtx
from discord.ext import commands


class Admin(commands.Cog):
    """ Guild Admin commands """
    def __init__(self, bot: Horus):
        self.bot = bot

    @commands.command(name = "setprefix", brief = "Set Server prefix")
    async def setprefix(self, ctx: HorusCtx, prefix: str):
        """
        Set a custom prefix for your server.
        User requires Administrator permissions in the guild to use this command
        """
        if len(prefix) > 25: # prefix limit to 25
            return await ctx.reply("I asked for prefix not a goddamn paragraph.")

        await self.bot.redis.hset("prefix", ctx.guild.id, prefix)
        await self.bot.db.execute('UPDATE guilddata SET prefix = $2 WHERE guildid = $1', ctx.guild.id, [prefix])
        await ctx.send(f'Prefix changed to: `{prefix}`')
