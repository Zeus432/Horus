from Useful.Useful import *
from discord.ext import commands
import discord
from Useful.settings import *
import datetime
from dateutil.relativedelta import relativedelta
import asyncio


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.bot.launch_time = bot.launch_time

    def get_uptime(self):
        delta_uptime = relativedelta(datetime.datetime.utcnow(), self.bot.launch_time)
        days, hours, minutes, seconds = delta_uptime.days, delta_uptime.hours, delta_uptime.minutes, delta_uptime.seconds

        uptimes = {x[0]: x[1] for x in [('days, ' if days != 1 else 'day, ', days), ('hours, ' if hours != 1 else 'hour, ', hours),
                                        ('minutes' if minutes != 1 else 'minute', minutes), ('seconds' if seconds != 1 else 'second', seconds)] if x[1]}

        last = " ".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes)-1)
        uptime_string = "".join(
            f"{v} {k}" if k != last else f" and {v} {k}" if len(uptimes) != 1 else f"{v} {k}"
            for k, v in uptimes.items()
        )
        return uptime_string


    @commands.command(name = "botinfo", help = "View some info about the bot", brief = "Get Bot Info", aliases = ['info'])
    @commands.guild_only()
    async def info(self, ctx):
        who = self.bot.get_user(760823877034573864)
        emb = discord.Embed(colour = discord.Colour(10263807))
        emb.add_field(name="Bot Dev:",value=f"**[{who}](https://www.youtube.com/watch?v=Uj1ykZWtPYI)**")
        emb.add_field(name="Coded in:",value=f"**Language:** [**`python 3.8.5`**](https://www.python.org/)\n**Library:** [**`discord.py 2.0`**](https://github.com/Rapptz/discord.py)\nㅤㅤㅤㅤ{botemojis('replyend')} Master Branch")
        emb.add_field(name="About Horus:",value=f"Horus is a private bot made for fun, has simple moderation, fun commands and is also called as Whorus <:YouWantItToMoveButItWont:873921001023500328>",inline = False)
        emb.add_field(name="Analytics:",value=f"**Servers:** {len([g.id for g in self.bot.guilds])} servers\n**Users:** {len([g.id for g in self.bot.users])}")
        emb.add_field(name="Bot Uptime:",value=self.get_uptime())
        emb.add_field(name="On Discord Since:",value=f"<t:{round(self.bot.get_user(858335663571992618).created_at.timestamp())}:D>")
        emb.set_thumbnail(url=self.bot.get_user(858335663571992618).avatar)
        view = discord.ui.View()
        button = discord.ui.Button(label= "Request Bot Invite", style=discord.ButtonStyle.grey)
        async def callback(interaction):
            em = discord.Embed(description=f"Sorry not giving invite rn, atleast not until I finish setting up the base of my bot <:hadtodoittoem:874263602897502208>\nBut here is something else {botemojis('shinobubully')}",colour = ctx.author.colour)
            await ctx.reply(embed = em, mention_author = False)
            await ctx.send("https://tenor.com/view/dance-moves-dancing-singer-groovy-gif-17029825")
        button.callback = callback
        view.add_item(button)
        await ctx.send(embed = emb, view=view)
    
    @commands.command(name = "ping", help = "View the ping of the bot", brief = "Take a wild guess")
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.author.trigger_typing() 
        await ctx.reply(f"Pong {round(self.bot.latency*1000)}ms")
    
    
    @commands.command(name = "userinfo", aliases = ['ui'], help = "Get information about a user", brief = "Get User Info", ignore_extra = True)
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member = None):
        if type(member) != discord.Member:
            member = ctx.author
        uiembed = discord.Embed(title=f"{member.display_name}・{member}",colour=member.color,timestamp=ctx.message.created_at, description=f"**User ID:** `{member.id}`")
        uiembed.set_thumbnail(url=member.avatar)
        uiembed.set_footer(text=f"{ctx.guild}", icon_url=ctx.guild.icon)
        uiembed.add_field(name="Joined Discord:", value= f"<t:{round(member.created_at.timestamp())}:D>\n(<t:{round(member.created_at.timestamp())}:R>)")
        uiembed.add_field(name="Joined Server:", value=f"<t:{round(member.joined_at.timestamp())}:D>\n(<t:{round(member.joined_at.timestamp())}:R>)")
        roles, extra = "",0
        for role in member.roles:
            if str(role) != "@everyone":
                if len(roles) < 900:
                    roles += f"{role.mention} "
                else:
                    extra += 1

        roles = roles + f" and {extra} other roles . . ." if extra != 0 and roles != "" else roles
        if roles == "":
            roles = "This user has no roles"
        uiembed.add_field(name="User Roles:", value=f"{roles}", inline=False)
        badge = ""
        if member.id in BotOwners:
            badge += f"{botemojis('dev')} [**Whorus Dev**]({member.avatar})\n"

        if member == ctx.guild.owner:
            badge += f"{botemojis('owner')} [**Server Owner**]({member.avatar})\n"

        for role in member.roles:
            try:
                if role.id == ctx.guild.premium_subscriber_role.id:
                    badge += f"{botemojis('boost')} **[Server Booster](https://cdn.discordapp.com/emojis/782210035329138698.gif?v=1)**\n"
            except:
                break   
        if 809632911690039307 == ctx.guild.id:
            badge += f"<:begone_thot:865247289391841310> **[{self.bot.get_guild(809632911690039307)}]({self.bot.get_guild(809632911690039307).icon})**\n"
        if member.id in memberbadges:
            badge += memberbadges[member.id] + f"({member.avatar})\n"
        if member.bot:
            badge = f"{botemojis('cogs')} **[Bots Supreme]({member.avatar})**\n"
        if badge != "":
            uiembed.add_field(name="Special Badges:", value=badge)
        uiembed.add_field(name="Servers:", value=f"{len([g.id for g in self.bot.guilds if g.get_member(member.id)])} shared")
        await ctx.send(embed=uiembed)

    @commands.command(name='uptime')
    @commands.guild_only()
    async def uptime(self, ctx: commands.Context):
        """Gets the uptime of the bot"""
        uptime_string = self.get_uptime()
        await ctx.channel.send(f'Whorus has been up for {uptime_string}.\nSince <t:{round(self.bot.launch_ts)}>')

def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))