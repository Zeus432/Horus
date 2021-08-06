from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.author.trigger_typing() 
        await ctx.reply(f"Pong {round(self.bot.latency*1000)}ms")

def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))
