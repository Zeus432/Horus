from discord.ext import commands

class Admin(commands.Cog):
    """ Server Management """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name = "setprefix", brief = "Set Server prefix")
    async def setprefix(self, ctx: commands.Context, prefix: str):
        """
        Set a custom prefix for your server.
        User requires Administrator permissions in the guild to use this command
        """
        self.bot.prefix_cache[ctx.guild.id] = [f"{prefix}"]
        await self.bot.db.execute('UPDATE guilddata SET prefix = $2 WHERE guildid = $1', ctx.guild.id, self.bot.prefix_cache[ctx.guild.id])
        await ctx.send(f'Prefix changed to: `{prefix}`')