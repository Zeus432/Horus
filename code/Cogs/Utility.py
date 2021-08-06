from discord.ext import commands
import discord
from discord.ext.commands.core import has_role
from settings import *


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
    
    @commands.command(name = "ping", help = "View the ping of the bot", brief = "Take a wild guess")
    async def ping(self, ctx):
        await ctx.author.trigger_typing() 
        await ctx.reply(f"Pong {round(self.bot.latency*1000)}ms")

    @commands.command(name = "userinfo", aliases = ['ui'], help = "Get information about a user", brief = "Get User Info")
    async def userinfo(self, ctx, *, member: discord.Member = None):
        member = ctx.author if not member else member
        uiembed = discord.Embed(title=f"{member}・{member.display_name}",colour=member.color,timestamp=ctx.message.created_at, description=f"**User ID:** `{member.id}`")
        uiembed.set_thumbnail(url=member.avatar)
        uiembed.set_footer(text=f"{ctx.guild}", icon_url=ctx.guild.icon)
        uiembed.add_field(name="Created on:", value= f"<t:{round(member.created_at.timestamp())}:D>\n(<t:{round(member.created_at.timestamp())}:R>)")
        uiembed.add_field(name="Joined on:", value=f"<t:{round(member.joined_at.timestamp())}:D>\n(<t:{round(member.joined_at.timestamp())}:R>)")
        roles = ""
        for role in member.roles:
            if str(role) != "@everyone":
                roles += f"{role.mention} "
        if roles == "":
            roles = "None"
        uiembed.add_field(name="User Roles:", value=f"{roles}", inline=False)
        badge = ""
        if member.id in BotOwners:
            badge += f"<a:ShinyBadge:873222765937832027> **[Bot Owner]({member.avatar})**\n"
        if 809632911690039307 in [g.id for g in self.bot.guilds if g.get_member(member.id)]:
            badge += f"<:okmom:868033943901986836> **[{self.bot.get_guild(809632911690039307)}]({self.bot.get_guild(809632911690039307).icon})**\n"
        for role in member.roles:
            try:
                if role.id == ctx.guild.premium_subscriber_role.id:
                    badge += "<a:booster:873218832326594590> **[Server Booster](https://cdn.discordapp.com/emojis/782210035329138698.gif?v=1)**"
            except:
                break
        if member.bot:
            badge = f"<:cogsred:873220470416236544> **[Bots Supreme]({member.avatar})**"
        if badge != "":
            uiembed.add_field(name="Special Badges:", value=badge)
        uiembed.add_field(name="Servers:", value=f"{len([g.id for g in self.bot.guilds if g.get_member(ctx.author.id)])} shared")
        await ctx.send(embed=uiembed)

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MemberNotFound):
            await ctx.send(error)
        else:
            await ctx.send(f"```py\n{error}```")

def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))
