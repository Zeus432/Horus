from Useful.Useful import botemojis
from discord.ext import commands
import discord
from Useful.settings import *
import asyncio
from Cogs.CustomHelp import *

class Mun(commands.Cog): 
    def __init__(self, bot: commands.Bot):
        self.bot = bot 

    async def cog_check(self, ctx):
        return ctx.guild.id == 876044372460838922

    @commands.command(name = "senddm", help = "Send dm to delegates", brief = "Send dm")
    async def senddm(self, ctx, *, member: discord.Member):
        """Send dm"""
        member
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        msg = ctx.message
        await ctx.send("Enter context of the message")
        try:
            msgcontent = await self.bot.wait_for(event='message', check=check, timeout=30)
        except asyncio.TimeoutError:
            await msg.reply("Response Timed Out!")
        else:
            try:
                embed = discord.Embed(title="New Dm recieved!",description=f"You've been sent a new dm by {ctx.author.mention} (`{ctx.author.id}`)", color= 0x2F3136)
                await member.send(embed= embed)
                await member.send(msgcontent.content)
                await ctx.reply("message sent")
            except:
                await ctx.reply("I was unable to dm this user. Make sure their dms isn't closed")
            
    @senddm.error
    async def senddm_error(self, ctx, error):
        await ctx.send(f"{error}")

    async def cog_command_error(self, ctx, error):
        """This method will be called if a command in this cog raises an error."""
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(f'This command is not available here', delete_after = 10)

def setup(bot: commands.Bot):
    bot.add_cog(Mun(bot))