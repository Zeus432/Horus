import discord
from discord.ext import commands

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

    @commands.group(name='permissions', aliases = ['perms'], invoke_without_command = True, brief = "Set Guild Permissions")
    async def permissions(self, ctx):
        """ Set up Bot Related Permissions for your guild (Unavailable at the moment)"""
        await ctx.send_help('permissions')
    @permissions.command()
    async def add(self, ctx):
        #await self.bot.db.execute("INSERT INTO users (id, data) VALUES (1111,'This is nice')")
        await ctx.send("This isn't available rn")

    @permissions.command()
    async def getserver(self, ctx):
        #users = await self.bot.db.fetch("SELECT * FROM users")
        #users2 = await self.bot.db.fetchrow("SELECT * FROM users")
        #users3 = await self.bot.db.fetchval("SELECT * FROM users")
        await ctx.send("This isn't available rn")
    
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name = "setprefix",
                      brief = "Set Server prefix",
                      help = "Set a custom prefix for your server.\nUser requires Administrator permissions in the guild to use this command"      
                    )
    async def setprefix(self, ctx, prefix: str):
        lst = []
        lst.append(prefix)
        prefix = lst
        self.bot.prefix_cache[ctx.guild.id] = prefix
        await self.bot.db.fetchval('UPDATE guilddata SET prefix = $2 WHERE guildid = $1', ctx.guild.id, prefix)
        await ctx.send(f'Prefix changed to: `{prefix[0]}`')

def setup(bot: commands.Bot):
    bot.add_cog(AdminCogs(bot))