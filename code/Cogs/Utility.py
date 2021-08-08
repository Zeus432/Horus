from Useful.Useful import botemojis
from discord.ext import commands
import discord
from Useful.settings import *
import datetime
from dateutil.relativedelta import relativedelta


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.bot.launch_time = bot.launch_time
    
    @commands.command(name = "ping", help = "View the ping of the bot", brief = "Take a wild guess")
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.author.trigger_typing() 
        await ctx.reply(f"Pong {round(self.bot.latency*1000)}ms")

    @commands.command(name = "userinfo", aliases = ['ui'], help = "Get information about a user", brief = "Get User Info")
    @commands.guild_only()
    async def userinfo(self, ctx, *, member: discord.Member = None):
        member = ctx.author if not member else member
        uiembed = discord.Embed(title=f"{member.display_name}・{member}",colour=member.color,timestamp=ctx.message.created_at, description=f"**User ID:** `{member.id}`")
        uiembed.set_thumbnail(url=member.avatar)
        uiembed.set_footer(text=f"{ctx.guild}", icon_url=ctx.guild.icon)
        uiembed.add_field(name="Joined Discord:", value= f"<t:{round(member.created_at.timestamp())}:D>\n(<t:{round(member.created_at.timestamp())}:R>)")
        uiembed.add_field(name="Joined Server:", value=f"<t:{round(member.joined_at.timestamp())}:D>\n(<t:{round(member.joined_at.timestamp())}:R>)")
        roles = ""
        for role in member.roles:
            if str(role) != "@everyone":
                roles += f"{role.mention} "
        if roles == "":
            roles = "None"
        uiembed.add_field(name="User Roles:", value=f"{roles}", inline=False)
        badge = ""
        if member.id in BotOwners:
            badge += f"{botemojis('dev')} **[Whorus Dev]({member.avatar})**\n"
        for role in member.roles:
            try:
                if role.id == ctx.guild.premium_subscriber_role.id:
                    badge += f"{botemojis('boost')} **[Server Booster](https://cdn.discordapp.com/emojis/782210035329138698.gif?v=1)**\n"
            except:
                break
        if 809632911690039307 in [g.id for g in self.bot.guilds if g.get_member(member.id)]:
            badge += f"<:begone_thot:865247289391841310> **[{self.bot.get_guild(809632911690039307)}]({self.bot.get_guild(809632911690039307).icon})**\n"
        if member.id == 728613015393533983:
            badge += f"<:BaldAditya:873289287142088724> **[Bald Aditya](https://cdn.discordapp.com/emojis/873289287142088724.png?v=1)**\n"
        if member.id == 786150805773746197:
            badge += f"<a:rooburn:873586500518948884> **[Fellintron Nab]({member.avatar})**"
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
        delta_uptime = relativedelta(datetime.datetime.utcnow(), self.bot.launch_time)
        delta_unix = datetime.datetime.utcnow() - self.bot.launch_time
        days, hours, minutes, seconds = delta_uptime.days, delta_uptime.hours, delta_uptime.minutes, delta_uptime.seconds

        uptimes = {x[0]: x[1] for x in [('days', days), ('hours', hours),
                                        ('minutes', minutes), ('seconds', seconds)] if x[1]}

        last = "".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes)-1)
        uptime_string = "".join(
            f"{v} {k}" if k != last else f" and {v} {k}" if len(uptimes) != 1 else f"{v} {k}"
            for k, v in uptimes.items()
        )
        await ctx.channel.send(f'Whorus has been up for {uptime_string}.\nSince <t:{round(self.bot.launch_ts)}>')

def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))
