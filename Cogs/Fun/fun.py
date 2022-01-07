from bot import Horus
import disnake as discord
from disnake.ext import commands

from Core.Utils.converters import ModeConverter
from .views import Guess, MatchView, RpsView

class Fun(commands.Cog):
    """ Fun commands """ 
    def __init__(self, bot: Horus):
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
        if opponent.bot:
            return await ctx.send(f"You can't play with bots dude, they'll never respond {self.bot.get_em('yikes')}")

        if ctx.author.id == opponent.id:
            return await ctx.send(f"You can't play against yourself {self.bot.get_em('cringepepe')}")
        
        view = RpsView(ctx, opponent, timeout = 30)
        view.message = await ctx.send(f"{ctx.author.mention} vs {opponent.mention}", view = view)
        await view.wait()
    
    @commands.command(name = "memorygame", aliases = ["memory"], brief = "Play memory game")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def memorygame(self, ctx: commands.Context, mode: ModeConverter = "easy"):
        """ 
        Play memory game
        __Modes__: `easy`, `medium` and `hard`
        """
        total = {"easy": 10, "medium": 20, "hard": 30}[mode]
        view = MatchView(user = ctx.author, mode = mode, total = total)
        view.message = await ctx.send(content = f"Here is your `{mode}` memory game. You have **{30 + total * 2}** seconds to finish it!", view = view)
        await view.wait()