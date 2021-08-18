from Useful.Useful import botemojis
from discord.ext import commands
import discord
from Useful.settings import *
import asyncio
from Cogs.CustomHelp import *
from Cogs.ErrorHandler import CommandErrorHandler

#dm buttons
class Choose(discord.ui.View):

    def __init__(self, msg):
        super().__init__(timeout=30)
        self.value = 3
        self.msg = msg
    

    @discord.ui.button(label= "Send via EB", style=discord.ButtonStyle.green)
    async def viaeb(self, button: discord.ui.Button, interaction: discord.Interaction):
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.green
        await self.msg.edit(view=self)
        self.value = 1
        self.stop()

    @discord.ui.button(label= "Send Private", style=discord.ButtonStyle.blurple)
    async def private(self, button: discord.ui.Button, interaction: discord.Interaction):
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.green
        button.style = discord.ButtonStyle.green
        await self.msg.edit(view=self)
        self.value = 2
        self.stop()

    @discord.ui.button(label= "Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.red
        await self.msg.edit(view=self)
        self.value = 3
        self.stop()
    
    async def on_timeout(self):
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            if item.label == "Cancel":
                item.style = discord.ButtonStyle.red
            item.disabled = True
        self.value = 3
        await self.msg.edit(view=self)

class Mun(commands.Cog): 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.chairs = {}

    async def cog_check(self, ctx):
        guild = self.bot.get_guild(876044372460838922)
        if ctx.command.qualified_name != 'send':
            return ctx.guild.id == 876044372460838922
        else:
            return guild.get_member(ctx.author.id)

    @commands.command(name = "send", help = "Send stuff to delegates", brief = "Send dm")
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.dm_only()
    async def send(self, ctx, *, member: discord.Member):
        """Send dm"""
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        guild = self.bot.get_guild(876044372460838922)
        member = guild.get_member(member.id)
        user = guild.get_member(ctx.author.id)
        chk = True
        if member:
            for i in [876703407551938580,876703436048044092,876703447083253770,876703642063896647]:
                if i in [r.id for r in user.roles]:
                    council,chk = i,False
                    if council not in [r.id for r in member.roles]:
                        await ctx.reply("You can only send messages to delegates in your own council!")
                        council = None
                    break
            if chk:
                await ctx.reply("You need to be a part of the council to use this command!")
        else:
            council = None
            await ctx.reply(f'You can only dm users who are a part of the councils in **{guild}**')

        if council and member:
            msg = await ctx.send(f"Enter the message you want to send to {member.mention}")
            try:
                msgcontent = await self.bot.wait_for(event='message', check=check, timeout=300)
            except asyncio.TimeoutError:
                await msg.reply("Response Timed Out!")
            else:
                msg2 = await msg.reply('Choose:', view = None)
                view = Choose(msg=msg2)
                await msg2.edit(view=view)
                await view.wait()
                if view.value == 1:
                    try:
                        embed = discord.Embed(title="New Message recieved!",description=f"You've been sent a new dm by {ctx.author.mention} (`{ctx.author.id}`)", color= 0x2F3136)
                        await member.send(embed= embed)
                        await member.send(msgcontent.content)
                        try:
                            for i in self.chairs[council]:
                                try:
                                    chair = self.bot.get_user(i)
                                    embed = discord.Embed(title="New Message Sent!",description=f"{ctx.author.mention} (`{ctx.author.id}`) has sent a message to {member.mention} (`{member.id}`)", color= 0x2F3136)
                                    await chair.send(embed=embed)
                                    await chair.send(msgcontent.content)
                                except:
                                    pass
                        except:
                            pass
                        await ctx.reply(f"Message has been sent via EB to {member.mention}")
                    except:
                        await ctx.reply("I was unable to dm this user. Make sure their dms isn't closed") 
                if view.value == 2:
                    try:
                        embed = discord.Embed(title="New Message recieved!",description=f"You've been sent a new dm by {ctx.author.mention} (`{ctx.author.id}`)", color= 0x2F3136)
                        await member.send(embed= embed)
                        await member.send(msgcontent.content)
                        await ctx.reply(f"Message has been sent privately to {member.mention}")
                    except:
                        await ctx.reply("I was unable to dm this user. Make sure their dms isn't closed")  
                if view.value == 3:
                    await ctx.send('Cancelled')

    async def cog_command_error(self, ctx, error):
        """This method will be called if a command in this cog raises an error.""" 
        if isinstance(error, commands.CheckFailure):
            if ctx.guild.id == 876044372460838922:
                await ctx.reply("This command can only be run in the bot's dms.")
                return
            await ctx.reply(f'This command is not available here', delete_after = 10)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply("You're in cooldown")

def setup(bot: commands.Bot):
    bot.add_cog(Mun(bot))