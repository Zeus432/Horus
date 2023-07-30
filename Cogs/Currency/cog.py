import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx


class Fun(commands.Cog):
    """ Fun Stuff """

    def __init__(self, bot: Horus):
        self.bot = bot
        self.emote = bot.get_em('fun')

    @commands.command(name = "whack-a-mole", aliases = ['whackamole', 'wam'], brief = "Play Whack a Mole", hidden = True)
    async def wam(self, ctx: HorusCtx):
        0