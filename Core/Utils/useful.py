import discord
from discord.ext import commands

from dateutil.relativedelta import relativedelta
import asyncio
import datetime
import json

def load_json(file: str) -> dict:
    with open(file, encoding = 'utf-8') as newfile:
        return json.load(newfile)


def write_json(file: str, contents: dict) -> None:
    with open(file, 'w') as newfile:
        json.dump(contents, newfile, ensure_ascii = True, indent = 4)

def get_uptime(bot: commands.Bot) -> str:
    delta_uptime = relativedelta(datetime.datetime.now(), bot.launch_time)
    days, hours, minutes, seconds = delta_uptime.days, delta_uptime.hours, delta_uptime.minutes, delta_uptime.seconds

    uptimes = {x[0]: x[1] for x in [('day', days), ('hour', hours), ('minute', minutes), ('second', seconds)] if x[1]}
    l = len(uptimes) 

    last = " ".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes)-1)

    uptime_string = ", ".join(
        f"{uptimes[value]} {value}{'s' if uptimes[value] > 1 else ''}" for index, value in enumerate(uptimes.keys()) if index != l-1
    )
    uptime_string += f" and {uptimes[last]}" if l > 1 else f"{uptimes[last]}"
    uptime_string += f" {last}{'s' if uptimes[last] > 1 else ''}"
        
    return uptime_string

class CheckAsync(commands.Converter):
    async def isAsync(self, ctx: commands.Context, argument):
        if asyncio.iscoroutinefunction(self):
            return self
        raise commands.BadArgument("Argument is meant to be a coroutine function!")

async def try_add_reaction(message: discord.Message, emoji: str):
    try:
        await message.add_reaction(emoji)
    except:
        pass

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
            "us_west": "US West " + "\U0001F1FA\U0001F1F8",
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
            "MONETIZATION_ENABLED": "Monetisation is enabled",
            "MORE_EMOJI": "More Emojis",
            "MORE_STICKERS":"More Stickers",
            "NEWS": "News Channels",
            "PARTNERED": "Partnered",
            "PREVIEW_ENABLED": "Preview enabled",
            "PUBLIC_DISABLED": "Public disabled",
            "PRIVATE_THREADS": "Threads Private",
            "SEVEN_DAY_THREAD_ARCHIVE": "Threads Archive time - 7 Days",
            "THREE_DAY_THREAD_ARCHIVE": "Threads Archive time - 3 Days",
            "TICKETED_EVENTS_ENABLED": "Ticketed Events Enabled",
            "VANITY_URL": "Vanity URL",
            "VERIFIED": "Verified",
            "VIP_REGIONS": "VIP Voice Servers",
            "WELCOME_SCREEN_ENABLED": "Welcome Screen enabled",
            "THREADS_ENABLED":"Threads Enabled",
            "NEW_THREAD_PERMISSIONS":"New Thread Permissions Enabled"
        }

def get_em(emoji: str | int) -> str:
    emojis = load_json(f'Core/Assets/emojis.json')
    try:
        return emojis[emoji]
    except:
        return emojis["error"]

def guildanalytics(bot: commands.Bot, guild: discord.Guild, type: int = 0, **kwargs) -> discord.Embed:
    msg = "I've joined a new server" if type == 1 else f"I've left this server{' as it is blacklisted' if type == 3 else ''}"
    colour = discord.Color.green() if type == 1 else discord.Color.red()
    colour = discord.Colour(0x9c9cff) if not type  else colour

    description = f"Server was created on <t:{round(guild.created_at.timestamp())}:D>\n"
    description += f"I joined this server on <t:{round(guild.me.joined_at.timestamp())}:D>\n" if not type else ""
    description += f"\n{msg}\nI'm in **{len([g.id for g in bot.guilds])}** servers now\nI have **{len([g.id for g in bot.users])}** users now" if type else ""
    embed = discord.Embed(title = guild, colour = colour, description = description)

    owner,region = guild.owner, guild.region.name
    ifnsfw = len([c for c in guild.text_channels if c.is_nsfw()])
    ifgprem = guild.premium_tier
    gfl = [f"{bot.get_em('parrow')} {features[c]}" for c in guild.features] 
    if gfl == []:
        featurend = "No Features Available"
    else:
        threadinfo = ""
        if "THREADS_ENABLED" in  guild.features:
            threadinfo = f"\n{bot.get_em('parrow')} Threads Enabled"
            threadinfo = f"\nㅤㅤ{bot.get_em('replycont')} New Thread Permissions Enabled" if "NEW_THREAD_PERMISSIONS" in guild.features else ""
            threadinfo += f"\nㅤㅤ{bot.get_em('replycont')} Private Threads" if "PRIVATE_THREADS" in guild.features else ""
            threadinfo += f"\nㅤㅤ{bot.get_em('replyend')} Archive time limit: "
            threadinfo += "1 week" if "SEVEN_DAY_THREAD_ARCHIVE" in guild.features else "3 days" if "THREE_DAY_THREAD_ARCHIVE" in guild.features else "1 day"
        featurend = "\n".join([c for c in gfl if not c.startswith(f"{bot.get_em('parrow')} Thread") or not c.startswith(f"{bot.get_em('parrow')} New Thread")]) + threadinfo
            
    if ifnsfw > 0:
        ifnsfw = f"\nㅤㅤ{bot.get_em('replyend')} Nsfw ⤏ **{ifnsfw}**"
    else:
        ifnsfw = ""
    embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457879292152381443.png" if "VERIFIED" in guild.features else "https://cdn.discordapp.com/emojis/508929941610430464.png"if "PARTNERED" in guild.features else discord.Embed.Empty, text=guild.name if "VERIFIED" in guild.features or "PARTNERED" in guild.features else discord.Embed.Empty)
    embed.add_field(name="**Guild Info**", value=f"**Owner:** {owner.mention} (`{owner.id}`)\n**Region:** {vc_regions[region]}\n**Verif. Level:** {verif[str(guild.verification_level)]}\n**Server ID:** `{guild.id}`",inline=False)
    embed.add_field(name="**Members**",value=f"Humans: **{len([g.id for g in guild.members if not g.bot])}**\nBots: **{len([g.id for g in guild.members if g.bot])}**\nTotal: **{len([g.id for g in guild.members])}**")
    embed.add_field(name="**Channels**",value=f"{bot.get_em('text')} Text Channels: **{len(guild.text_channels)}** {ifnsfw}\n{bot.get_em('voice')} Voice Channels: **{len(guild.voice_channels)}**\n{bot.get_em('stage')} Stage Channels: **{len(guild.stage_channels)}**")
    embed.add_field(name="**Misc**",value=f"AFK channel: **{guild.afk_channel}**\nAFK timeout: **{(guild.afk_timeout)/60} minutes**\nCustom emojis: **{len(guild.emojis)}**\nRoles: **{len(guild.roles)}**", inline=False)
    if ifgprem > 0:
        nitro_boost = f"Tier **{str(guild.premium_tier)}** with **{guild.premium_subscription_count}** boosters\nFile size limit: **{_size(guild.filesize_limit)}**\nEmoji limit: **{str(guild.emoji_limit)}**\nVCs max bitrate: **{_bitsize(guild.bitrate_limit)}**"
        embed.add_field(name="**Nitro State**", value=nitro_boost)
    embed.add_field(name="**Server Features**", value=featurend, inline=False)
    embed.set_thumbnail(url=guild.icon if guild.icon else "https://cdn.discordapp.com/embed/avatars/1.png")
    if guild.banner:
        embed.set_image(url=guild.banner)
    return embed