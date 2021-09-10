from Utils.Useful import *
from discord.ext import commands
import discord
from Core.settings import *
import unicodedata
import time


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.bot.launch_time = bot.launch_time


    @commands.command(name = "botinfo", help = "View some info about the bot", brief = "Get Bot Info", aliases = ['info'])
    @commands.guild_only()
    async def info(self, ctx):
        who = self.bot.get_user(760823877034573864)
        emb = discord.Embed(colour = discord.Colour(10263807))
        emb.add_field(name="Bot Dev:",value=f"**[{who}](https://www.youtube.com/watch?v=Uj1ykZWtPYI)**")
        emb.add_field(name="Coded in:",value=f"**Language:** **[`python 3.8.5`](https://www.python.org/)**\n**Library:** **[`discord.py 2.0`](https://github.com/Rapptz/discord.py)**\nㅤㅤㅤㅤ{botemojis('replyend')} Master Branch")
        emb.add_field(name="About Horus:",value=f"Horus is a private bot made for fun, has simple moderation, fun commands and is also called as Whorus' <:YouWantItToMoveButItWont:873921001023500328>",inline = False)
        emb.add_field(name="Analytics:",value=f"**Servers:** {len([g.id for g in self.bot.guilds])} servers\n**Users:** {len([g.id for g in self.bot.users])}")
        emb.add_field(name="Bot Uptime:",value=get_uptime(self.bot))
        emb.add_field(name="On Discord Since:",value=f"<t:{round(self.bot.get_user(858335663571992618).created_at.timestamp())}:D>")
        emb.set_thumbnail(url=self.bot.get_user(858335663571992618).avatar)
        view = discord.ui.View()
        button = discord.ui.Button(label= "Request Bot Invite", style=discord.ButtonStyle.blurple)
        async def callback(interaction):
            em = discord.Embed(description=f"Bot isn't fully set up yet <:hadtodoittoem:874263602897502208>",colour = self.bot.colour)
            await ctx.reply(embed = em, mention_author = False)
            await ctx.send("https://tenor.com/view/dance-moves-dancing-singer-groovy-gif-17029825")
        button.callback = callback
        view.add_item(button)
        await ctx.send(embed = emb, view=view)
    
    @commands.command(name = "ping", help = "View the ping of the bot", brief = "Take a wild guess")
    @commands.guild_only()
    async def ping(self, ctx):
        start = time.perf_counter()
        msg = await ctx.send(f"{botemojis('loading')} Pinging")
        await ctx.author.trigger_typing()
        end = time.perf_counter()
        typing_ping = (end - start) * 1000

        start = time.perf_counter()
        await self.bot.db.execute('SELECT 1')
        end = time.perf_counter()
        sql_ping = (end - start) * 1000
        await msg.edit(content=f"Pong {botemojis('catpong')}\n**Typing**: `{round(typing_ping, 1)} ms`\n**Websocket**: `{round(self.bot.latency*1000)} ms`\n**Database**: `{round(sql_ping, 1)} ms`")
    
    
    @commands.command(name = "userinfo", aliases = ['ui'], help = "Get information about a user", brief = "Get User Info", ignore_extra = True)
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member = None):
        if type(member) != discord.Member:
            member = ctx.author
        uiembed = discord.Embed(title=f"{member.display_name}・{member}",colour=member.colour if member.colour != discord.Colour(000000) else self.bot.colour,timestamp=ctx.message.created_at, description=f"**User ID:** `{member.id}`")
        uiembed.set_thumbnail(url=member.avatar)
        uiembed.set_footer(text=f"{ctx.guild}", icon_url=ctx.guild.icon)
        uiembed.add_field(name="Joined Discord:", value= f"<t:{round(member.created_at.timestamp())}:D>\n(<t:{round(member.created_at.timestamp())}:R>)")
        uiembed.add_field(name="Joined Server:", value=f"<t:{round(member.joined_at.timestamp())}:D>\n(<t:{round(member.joined_at.timestamp())}:R>)")
        roles, extra = "",0
        for role in sorted(member.roles, reverse=True):
            if str(role) != "@everyone":
                if len(roles) < 900:
                    roles += f"{role.mention} "
                else:
                    extra += 1

        roles = roles + f" and {extra} other roles . . ." if extra != 0 and roles != "" else roles
        if roles == "":
            roles = "This user has no roles"
        uiembed.add_field(name="User Roles:", value=f"{roles}", inline=False)
        if 876044372460838922 == ctx.guild.id:
            mun = ""
            guild = self.bot.get_guild(876044372460838922)
            user = guild.get_member(member.id)
            mun += f"{botemojis('mod')} **[Organiser]({user.avatar})**\n" if user.id in [760823877034573864,401717120918093846] else ""
            mun += f"{botemojis('judge')} **[Council Chair]({user.avatar})**\n" if 876704912149475378 in [r.id for r in user.roles] else ""
            mun += f"{botemojis('staff')} **[Volunteer]({user.avatar})**\n" if 876700774082695198 in [r.id for r in user.roles] else ""
            for i in [876703407551938580,876703436048044092,876703447083253770]:
                if i in [r.id for r in user.roles]:
                    mun += f"{botemojis(str(guild.get_role(i)))} **[{guild.get_role(i)}](https://discord.gg/GYqqjQeZKs)**\n"
            uiembed.add_field(name="GT Model United Nations", value=mun if mun != "" else "\U0001f465 **[Participant](https://discord.gg/GYqqjQeZKs)**",inline=False)
        badge = ""
        if member.id in BotOwners:
            badge += f"{botemojis('dev')} **[{'H' if 876044372460838922 == ctx.guild.id else 'Wh'}orus Dev]({member.avatar})**\n"

        if member == ctx.guild.owner:
            badge += f"{botemojis('owner')} **[Server Owner]({member.avatar})**\n"

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
    
    @commands.command(name = "avatar", help = "Get a user's avatar", brief = "Get User Avatar", aliases = ['av'])
    @commands.guild_only()
    async def avatar(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour
        embed = discord.Embed(colour=colour,timestamp=ctx.message.created_at)
        embed.set_footer(text=f"{ctx.guild}", icon_url=ctx.guild.icon)
        avatar = user.avatar.with_static_format('png')
        jpgavatar = user.avatar.with_static_format('jpg')
        webpavatar = user.avatar.with_static_format('webp')
        embed.set_image(url=avatar)
        embed.title = f"Avatar for {user}"
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, url=f"{avatar}", label=".png link"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, url=f"{jpgavatar}", label=".jpg link"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, url=f"{webpavatar}", label=".webp link"))
        await ctx.send(embed=embed,view=view)

    @commands.command(name='uptime')
    @commands.guild_only()
    async def uptime(self, ctx: commands.Context):
        """Gets the uptime of the bot"""
        uptime_string = get_uptime(self.bot)
        await ctx.channel.send(f'Whorus has been up for {uptime_string}.\nSince <t:{round(self.bot.launch_ts)}>')
    
    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'
        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg)

def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))