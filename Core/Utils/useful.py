import discord
from discord.ext import commands

from datetime import datetime
import asyncio
import json
import re

def load_json(file: str) -> dict:
    """ Load json content from the given file """
    with open(file, encoding = 'utf-8') as newfile:
        return json.load(newfile)


def write_json(file: str, contents: dict) -> None:
    """ Write json content on to the given file """
    with open(file, 'w') as newfile:
        json.dump(contents, newfile, ensure_ascii = True, indent = 4)

class CheckAsync(commands.Converter):
    """ Check if given function is a coroutine """
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
    """ Convert Size from Bytes to appropriate size."""
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(num) < 1024.0:
            return f"{num:.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}YB"
            
def _bitsize(num):
    """ Convert from Bytes to appropriate size."""
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(num) < 1000.0:
            return f"{num:.1f}{unit}"
        num /= 1000.0
    return f"{num:.1f}YB"

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
    """ Get Emoji by providing its short key """
    emojis = load_json(f'Core/Assets/emojis.json')
    try:
        return emojis[emoji]
    except:
        return emojis["error"]

def get_features(bot: commands.Bot, guild: discord.Guild) -> str:
    featuresinfo = ""
    if "THREADS_ENABLED" in  guild.features:
        featuresinfo += f"{bot.get_em('parrow')} Threads Enabled"
        featuresinfo = f"\n{bot.get_em('parrow')} Threads Enabled"
        featuresinfo += f"\n\U00002005{bot.get_em('replycont')} New Thread Permissions Enabled" if "NEW_THREAD_PERMISSIONS" in guild.features else ""
        featuresinfo += f"\n\U00002005{bot.get_em('replycont')} Private Threads" if "PRIVATE_THREADS" in guild.features else ""
        featuresinfo += f"\n\U00002005{bot.get_em('replyend')} Archive time limit: "
        featuresinfo += "1 week" if "SEVEN_DAY_THREAD_ARCHIVE" in guild.features else "3 days" if "THREE_DAY_THREAD_ARCHIVE" in guild.features else "1 day"
    
    feature_list =  "\n".join(f"{bot.get_em('parrow')} {features[feature]}" for feature in guild.features if "THREAD" not in feature) + featuresinfo
    return feature_list or "No Features Availabe"

async def guildanalytics(bot: commands.Bot, guild: discord.Guild, type: int = 0, **kwargs) -> discord.Embed:
    """ An embed with useful information about a given guild """
    add_user = "Unknown"
    if type == 1: # Try to check who added the bot
        try:
            async for entry in guild.audit_logs(limit = 10, action = discord.AuditLogAction.bot_add):
                if entry.target == bot.user:
                    add_user = f"{entry.user}"
        except: pass

    message = f"I've joined this server. I was invited to it by {add_user}" if type == 1 else f"I've left this server{' as it is blacklisted' if type == 3 else ''}" if type >= 2 else f'I joined this server on <t:{round(guild.me.joined_at.timestamp())}:D>'
    colour = discord.Color.green() if type == 1 else discord.Color.red() if type == 2 else discord.Colour.dark_grey() if type == 3 else discord.Colour(0x9c9cff)
    description = f"Server was created on <t:{round(guild.created_at.timestamp())}:D>\n{message}\n{f'I am in **{len([g.id for g in bot.guilds])}** servers and I have **{len([g.id for g in bot.users])}** users now' if type else ''}"
    nsfw = len([chan for chan in guild.text_channels if chan.is_nsfw()])

    embed = discord.Embed(title = guild, colour = colour, description = description)

    embed.set_thumbnail(url = guild.icon if guild.icon else "https://cdn.discordapp.com/embed/avatars/1.png")
    embed.set_footer(icon_url = "https://cdn.discordapp.com/emojis/457879292152381443.png" if "VERIFIED" in guild.features else "https://cdn.discordapp.com/emojis/508929941610430464.png"if "PARTNERED" in guild.features else discord.Embed.Empty, text = "Verified Discord Server" if "VERIFIED" in guild.features else "Discord Partnered Server" if "PARTNERED" in guild.features else discord.Embed.Empty)
    if guild.banner:
        embed.set_image(url = guild.banner)

    embed.add_field(name = "Guild Info", value = f"Owner: {guild.owner.mention} (`{guild.owner.id}`)\nVerif. Level: **{verif[str(guild.verification_level)]}**\nServer ID: `{guild.id}`\n{'This guild has not been cached yet' if not guild.chunked else ''}", inline = False)
    embed.add_field(name = "Members", value = f"Humans: **{len([member for member in guild.members if not member.bot])}**\nBots: **{len([member for member in guild.members if member.bot])}**\nTotal: **{guild.member_count}**")
    embed.add_field(name = "Channels", value = f"{bot.get_em('text')} Text Channels: **{len(guild.text_channels)}**\n{bot.get_em('voice')} Voice Channels: **{len(guild.voice_channels)}**\n{bot.get_em('stage')} Stage Channels: **{len(guild.stage_channels)}**")
    embed.add_field(name = "Misc", value = f"AFK channel: **{guild.afk_channel}**\nAFK timeout: **{(guild.afk_timeout)//60} minutes {f'{round(guild.afk_timeout%60)} seconds' if guild.afk_timeout%60 else ''}**\nCustom emojis: **{len(guild.emojis)}**\nRoles: **{len(guild.roles)}**", inline = False)
    if guild.premium_tier:
        embed.add_field(name = "**Server Boost**", value = f"Tier **{str(guild.premium_tier)}** with **{guild.premium_subscription_count}** boosters\nFile size limit: **{_size(guild.filesize_limit)}**\nEmoji limit: **{str(guild.emoji_limit)}**\nVCs max bitrate: **{_bitsize(guild.bitrate_limit)}**")
    embed.add_field(name = "**Server Features**", value = get_features(bot = bot, guild = guild), inline = False)

    return embed

class TimeConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument) -> datetime:
        time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}

        matches = time_regex.findall(argument.lower())
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument(f"{k} is an invalid time-key! h/m/s/d are valid!")
            except ValueError:
                raise commands.BadArgument(f"{v} is not a number!")
        try:
            return float(argument)
        except: 
            return time