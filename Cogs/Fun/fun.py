import discord
from discord.ext import commands

from .views import Guess, RpsView

class Fun(commands.Cog):
    """ Fun commands for everyone to use """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name = "gtn", aliases = ['guess','guessthenumber'], brief = "Guess the Number")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def gtn(self, ctx: commands.Context):
        """ Play a fun game of guess the correct number """
        view = Guess(self.bot, ctx)
        view.message = await ctx.reply('Guess the Number!', view = view)
        await view.wait()
    
    @commands.command(name = "rps", aliases = ['rockpaperscissors'], brief = "Play Rps")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def rps(self, ctx, opponent: discord.Member):
        """ Play a game of Rock Paper Scissors with someone """
        if opponent.bot or (ctx.author.id == opponent.id):
            return await ctx.send(f"You can't play with bots dude, they'll never respond {self.bot.get_em('yikes')}")

        if ctx.author.id == opponent.id:
            return await ctx.send(f"You can't play against yourself {self.bot.get_em('cringepepe')}")
        
        view = RpsView(ctx, opponent, timeout = 30)
        view.message = await ctx.send(f"{ctx.author.mention} vs {opponent.mention}", view = view)
        await view.wait()