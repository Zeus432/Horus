import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from Core.Utils.math import NumericStringParser


class Utility(commands.Cog):
    """ Utility Commands """

    def __init__(self, bot: Horus):
        self.bot = bot
    
    @commands.command(name = "math", aliases = ["m"], brief = "Do math")
    async def math(self, ctx: HorusCtx, *, equation: str):
        """ Do some math, most normal mathematical signs are allowed """
        NSP = NumericStringParser()
        try:
            result = NSP.eval(num_string = equation.strip(" "))
        except:
            await ctx.send("There was an error while trying to evaluate your equation.\nMake sure to check your input for any illegal characters and try again")
        else:
            await ctx.send(f"```coffeescript\n{equation}```\n> `{result}`")