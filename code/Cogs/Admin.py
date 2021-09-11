from discord.ext import commands
import discord
from Core.settings import *
from Core.CustomHelp import *

class AdminCogs(commands.Cog, name = "Admin"):
    """ Management commands mostly for Setup """
    COLOUR = discord.Colour(0x9c9cff)
    def __init__(self, bot: commands.Bot):
        self.bot = bot 

    async def cog_check(self, ctx):
        user = ctx.guild.get_member(ctx.author.id)
        return user.guild_permissions.administrator

    @commands.group(name='permissions', aliases = ['perms'], invoke_without_command = True)
    async def permissions(self, ctx):
        await ctx.send_help('permissions')
    @permissions.command()
    async def add(self, ctx):
        await self.bot.db.execute("INSERT INTO users (id, data) VALUES (1111,'This is nice')")
        await ctx.send("Data Inserted!")

    @permissions.command()
    async def getserver(self, ctx):
        users = await self.bot.db.fetch("SELECT * FROM users")
        users2 = await self.bot.db.fetchrow("SELECT * FROM users")
        users3 = await self.bot.db.fetchval("SELECT * FROM users")
        await ctx.send(f"Here users:\n{users}\n{users2}\n{users3}")

def setup(bot: commands.Bot):
    bot.add_cog(AdminCogs(bot))