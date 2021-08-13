from discord.ext import commands
from typing import Union, Tuple, Optional
import discord
import datetime
import traceback
import sys
import pathlib


def _size(num):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(num) < 1024.0:
            return "{0:.1f}{1}".format(num, unit)
        num /= 1024.0
        return "{0:.1f}{1}".format(num, "YB")
            
def _bitsize(num):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(num) < 1000.0:
            return "{0:.1f}{1}".format(num, unit)
        num /= 1000.0
        return "{0:.1f}{1}".format(num, "YB")

vc_regions = {
            "vip-us-east": "__VIP__ US East " + "\U0001F1FA\U0001F1F8",
            "vip-us-west": "__VIP__ US West " + "\U0001F1FA\U0001F1F8",
            "vip-amsterdam": "__VIP__ Amsterdam " + "\U0001F1F3\U0001F1F1",
            "eu-west": "EU West " + "\U0001F1EA\U0001F1FA",
            "eu-central": "EU Central " + "\U0001F1EA\U0001F1FA",
            "europe": "Europe " + "\U0001F1EA\U0001F1FA",
            "london": "London " + "\U0001F1EC\U0001F1E7",
            "frankfurt": "Frankfurt " + "\U0001F1E9\U0001F1EA",
            "amsterdam": "Amsterdam " + "\U0001F1F3\U0001F1F1",
            "us-west": "US West " + "\U0001F1FA\U0001F1F8",
            "us-east": "US East " + "\U0001F1FA\U0001F1F8",
            "us-south": "US South " + "\U0001F1FA\U0001F1F8",
            "us-central": "US Central " + "\U0001F1FA\U0001F1F8",
            "singapore": "Singapore " + "\U0001F1F8\U0001F1EC",
            "sydney": "Sydney " + "\U0001F1E6\U0001F1FA",
            "brazil": "Brazil " + "\U0001F1E7\U0001F1F7",
            "hongkong": "Hong Kong " + "\U0001F1ED\U0001F1F0",
            "russia": "Russia " + "\U0001F1F7\U0001F1FA",
            "japan": "Japan " + "\U0001F1EF\U0001F1F5",
            "southafrica": "South Africa " + "\U0001F1FF\U0001F1E6",
            "india": "India " + "\U0001F1EE\U0001F1F3",
            "south-korea": "South Korea " + "\U0001f1f0\U0001f1f7",
            'dubai':'\U0001f1e6\U0001f1ea'
        }
verif = {
            "none": "0 - None",
            "low": "1 - Low",
            "medium": "2 - Medium",
            "high": "3 - High",
            "extreme": "4 - Extreme",
        }
features = {
            "ANIMATED_ICON": "Animated Icon",
            "BANNER": "Banner Image",
            "COMMERCE": "Commerce",
            "COMMUNITY": "Community",
            "DISCOVERABLE": "Server Discovery",
            "FEATURABLE": "Featurable",
            "INVITE_SPLASH": "Splash Invite",
            "MEMBER_LIST_DISABLED": "Member list disabled",
            "MEMBER_VERIFICATION_GATE_ENABLED": "Membership Screening enabled",
            "MORE_EMOJI": "More Emojis",
            "NEWS": "News Channels",
            "PARTNERED": "Partnered",
            "PREVIEW_ENABLED": "Preview enabled",
            "PUBLIC_DISABLED": "Public disabled",
            "VANITY_URL": "Vanity URL",
            "VERIFIED": "Verified",
            "VIP_REGIONS": "VIP Voice Servers",
            "WELCOME_SCREEN_ENABLED": "Welcome Screen enabled"
        }

class BaseEmbed(discord.Embed):
    """Main purpose is to get the usual setup of Embed for a command or an error embed"""
    def __init__(self, color: Union[discord.Color, int] = 0xffcccb, timestamp: datetime.datetime = None,
                 fields: Tuple[Tuple[str, str]] = (), field_inline: Optional[bool] = False, **kwargs):
        super().__init__(color=color, timestamp=timestamp or discord.utils.utcnow(), **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def default(cls, ctx: commands.Context,color: Union[discord.Color, int] = discord.Color.red(), **kwargs) -> "BaseEmbed":
        instance = cls(color=color,**kwargs)
        instance.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar)
        return instance

    @classmethod
    def to_error(cls, title: Optional[str] = "Error",
                 color: Union[discord.Color, int] = discord.Color.red(), **kwargs) -> "BaseEmbed":
        return cls(title=title, color=color, **kwargs)

    @classmethod
    def guildanalytics(cls, bot, join: bool, guild: discord.Guild, **kwargs) -> "BaseEmbed":
        colour = discord.Color.red() if join == False else discord.Color.green()
        msg = "I've left this server" if join == False else "I've joined a new server"
        embed = discord.Embed(title = guild, colour = colour, description = f"{msg}\nI'm in **{len([g.id for g in bot.guilds])}** servers now\nI have **{len([g.id for g in bot.users])}** users now")
        owner,region = guild.owner, guild.region.name
        ifnsfw = len([c for c in guild.text_channels if c.is_nsfw()])
        ifgprem = guild.premium_tier
        gfl = [
            f"・ {features[c]}" for c in guild.features 
        ]
        if gfl == []:
            gfl = "No Features Available"
        if ifnsfw > 0:
            ifnsfw = "\n・\U0001F51E Nsfw: **{ifnshw}**"
        else:
            ifnsfw = ""
        embed.set_footer(url="https://cdn.discordapp.com/emojis/457879292152381443.png" if "VERIFIED" in guild.features else "https://cdn.discordapp.com/emojis/508929941610430464.png"if "PARTNERED" in guild.features else discord.Embed.Empty, text=guild.name)
        embed.add_field(name="**Guild Info**", value=f"**Owner:** {owner.mention} (`{owner.id}`)\n**Region:** {vc_regions[region]}\n**Verif. Level:** {verif[str(guild.verification_level)]}\n**Server ID:** `{guild.id}`",inline=False)
        embed.add_field(name="**Members**",value=f"Humans: **{len([g.id for g in guild.members if not g.bot])}**\nBots: **{len([g.id for g in guild.members if g.bot])}**\nTotal: **{len([g.id for g in guild.members])}**")
        embed.add_field(name="**Channels**",value=f"{botemojis('text')} Text Channels: **{len(guild.text_channels)}** {ifnsfw}\n{botemojis('voice')} Voice Channels: **{len(guild.voice_channels)}**\n{botemojis('stage')} Stage Channels: **{len(guild.stage_channels)}**")
        embed.add_field(name="**Misc**",value=f"AFK channel: **{guild.afk_channel}**\nAFK timeout: **{guild.afk_timeout}**\nCustom emojis: **{len(guild.emojis)}**\nRoles: **{len(guild.roles)}**")
        if ifgprem > 0:
            nitro_boost = f"Tier **{str(guild.premium_tier)}** with **{guild.premium_subscription_count}** boosters\nFile size limit: **{_size(guild.filesize_limit)}**\nEmoji limit: **{str(guild.emoji_limit)}**\nVCs max bitrate: **{_bitsize(guild.bitrate_limit)}**"
            embed.add_field(name="**Nitro State**", value=nitro_boost)
        embed.add_field(name="**Server Features**", value=gfl, inline=False)
        embed.set_thumbnail(url=guild.icon if guild.icon else "https://cdn.discordapp.com/embed/avatars/1.png")
        if guild.banner:
            embed.set_image(url=guild.banner)
        return embed

def print_exception(text: str, error: Exception, *, _print: bool = False) -> str:
        """Prints the exception with proper traceback."""
        if _print:
            print(text, file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        etype = type(error)
        trace = error.__traceback__
        lines = traceback.format_exception(etype, error, trace)
        return "".join(lines)

def botemojis(emoji = None):
    listemoji =  {"menu":"<:HelpMenu:873859534651809832>","error":"<:Error:874511415086551080>","cogs":"<:Cogs:873861289343090718>","tick":"<:tickyes:873865975441813534>",
                  "boost":"<a:BoostBadge:873866459451904010>","pray":"<:angelpray:873863602023596082>","study":"<:Study:873863650471981107>","dev":"<a:DevBadge:873866720530534420>",
                  "trash":"<:TrashCan:873917151961026601>","kermitslap":"<a:kermitslap:873919390117158922>","tokitosip":"<a:TokitoSip:875425433980645416>",
                  "text":"<:Text:875775212648529950>","voice":"<:Voice:875775169375903745>","stage":"<:Stage:875775175965167708>"}
    try:
        return listemoji[emoji]
    except:
        return "<:Error:873859732044136469>"

class HelpButtons(discord.ui.View):
    def __init__(self, timeout:int, **kwargs):
        super().__init__(timeout=timeout, **kwargs)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji = botemojis("trash"))
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()

def fileanalytics():
    p = pathlib.Path('./')
    cm = cr = fn = cl = ls = fc = 0
    for f in p.rglob('*.py'):
        if str(f).startswith("venv"):
            continue
        fc += 1
        with f.open() as of:
            for l in of.readlines():
                l = l.strip()
                if l.startswith('class'):
                    cl += 1
                if l.startswith('def'):
                    fn += 1
                if l.startswith('async def'):
                    cr += 1
                if '#' in l:
                    cm += 1
                ls += 1
    return [fc,ls,cl,fn,cr,cm,f"file: {fc}\nline: {ls:,}\nclass: {cl}\nfunction: {fn}\ncoroutine: {cr}\ncomment: {cm:,}"]
    #returns in order 1. Files, 2. Lines, 3. Classes, 4.Functions, 5.Coroutines, 6.Comments, 7.The whole thing together

def woodlands_only(ctx):
    hidecmd = True if ctx.guild.id in [809632911690039307,844164205418512424] else False
    return hidecmd