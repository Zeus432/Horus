import discord
from discord.ext import commands

import json
import toml


def load_json(file: str) -> dict:
    """ Load json content from the given file """
    with open(file, encoding = 'utf-8') as newfile:
        return json.load(newfile)


def write_json(file: str, contents: dict) -> None:
    """ Write json content on to the given file """
    with open(file, 'w') as newfile:
        json.dump(contents, newfile, ensure_ascii = True, indent = 4)

def load_toml(file: str) -> dict:
    """ Load toml content from the given file """
    with open(file, encoding = 'utf-8') as newfile:
        return toml.load(newfile)


def write_toml(file: str, contents: dict) -> None:
    """ Write toml content on to the given file """
    with open(file, 'w') as newfile:
        toml.dump(contents, newfile)

def _size(num):
    """ Convert Size from Bytes to appropriate size."""
    for unit in ['B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB']:
        if abs(num) < 1024.0:
            return f"{num:.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}YB"
            
def _bitsize(num):
    """ Convert from Bytes to appropriate size."""
    for unit in ['B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB']:
        if abs(num) < 1000.0:
            return f"{num:.1f}{unit}"
        num /= 1000.0
    return f"{num:.1f}YB"

def emojis(emoji: str) -> str:
    em = load_json(f'Core/Assets/emojis.json')
    try:
        return em[emoji]
    except:
        return em['error']

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

class GuildEmbed:
    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        embed = discord.Embed(colour = bot.colour)

        embed.description = f"Server was created on <t:{round(guild.created_at.timestamp())}:D>"
        embed.set_thumbnail(url = f"{guild.icon}" if guild.icon else "https://cdn.discordapp.com/embed/avatars/1.png")
        embed.set_image(url = guild.banner)

        if "VERIFIED" in guild.features:
            embed.set_footer(icon_url = "https://cdn.discordapp.com/emojis/457879292152381443.png", text = "Verified Discord Server")
        elif "PARTNERED" in guild.features:
            embed.set_footer(icon_url = "https://cdn.discordapp.com/emojis/508929941610430464.png", text = "Discord Partnered Server")
        
        embed.add_field(name = "Guild Info", value = f"Owner: {guild.owner.mention} (`{guild.owner.id}`)\nVerif. Level: **{verif[str(guild.verification_level)]}**\nServer ID: `{guild.id}`\n{'This guild has not been cached yet' if not guild.chunked else ''}", inline = False)
        embed.add_field(name = "Members", value = f"Humans: **{len([member for member in guild.members if not member.bot])}**\nBots: **{len([member for member in guild.members if member.bot])}**\nTotal: **{guild.member_count}**")
        embed.add_field(name = "Channels", value = f"{bot.get_em('text')} Text Channels: **{len(guild.text_channels)}**\n{bot.get_em('voice')} Voice Channels: **{len(guild.voice_channels)}**\n{bot.get_em('stage')} Stage Channels: **{len(guild.stage_channels)}**")
        embed.add_field(name = "Misc", value = f"AFK channel: **{guild.afk_channel}**\nAFK timeout: ** {(guild.afk_timeout)//60} minutes" + (f" {round(guild.afk_timeout%60)} seconds" if guild.afk_timeout%60 else "") + f"**\nCustom emojis: **{len(guild.emojis)}**\nRoles: **{len(guild.roles)}**", inline = False)
        if guild.premium_tier:
            embed.add_field(name = "**Server Boost**", value = f"Tier **{str(guild.premium_tier)}** with **{guild.premium_subscription_count}** boosters\nFile size limit: **{_size(guild.filesize_limit)}**\nEmoji limit: **{str(guild.emoji_limit)}**\nVCs max bitrate: **{_bitsize(guild.bitrate_limit)}**")
        embed.add_field(name = "**Server Features**", value = get_features(bot = bot, guild = guild), inline = False)

        self.embed = embed
    
    @classmethod
    async def join(cls, bot: commands.Bot, guild: discord.Guild) -> discord.Embed:
        embed = cls(bot, guild).embed
        add_user = "I don't know who invited me"

        try:
            async for entry in guild.audit_logs(limit = 10, action = discord.AuditLogAction.bot_add):
                if entry.target == bot.user:
                    add_user = f"I was invited by {entry.user}"
        except: pass

        embed.description += "\nI just joined this server! " + add_user + f"\nI am in **{len([g.id for g in bot.guilds])}** servers and I have **{len([g.id for g in bot.users])}** users now"
        embed.colour = discord.Colour.green()

        return embed
    
    @classmethod
    def leave(cls, bot: commands.Bot, guild: discord.Guild, blacklist: bool = False) -> discord.Embed:
        embed = cls(bot, guild).embed

        embed.description += f"\nI have left this server" + (" as it is blacklisted" if blacklist is True else "") + f"!\nI am in **{len([g.id for g in bot.guilds])}** servers and I have **{len([g.id for g in bot.users])}** users now"
        embed.colour = discord.Colour.dark_grey() if blacklist is True else discord.Color.red()

        return embed
    
    @classmethod
    def default(cls, bot: commands.Bot, guild: discord.Guild):
        embed = cls(bot, guild).embed
        embed.description += f"\nI joined this server on <t:{round(guild.me.joined_at.timestamp())}:D>"

        return embed


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
            "highest": "4 - Extreme"
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
            "TEXT_IN_VOICE_ENABLED": "Text in Voice Chat Enabled",
            "TICKETED_EVENTS_ENABLED": "Ticketed Events Enabled",
            "VANITY_URL": "Vanity URL",
            "VERIFIED": "Verified",
            "VIP_REGIONS": "VIP Voice Servers",
            "WELCOME_SCREEN_ENABLED": "Welcome Screen enabled",
            "THREADS_ENABLED":"Threads Enabled",
            "NEW_THREAD_PERMISSIONS":"New Thread Permissions Enabled",
            "HAD_EARLY_ACTIVITIES_ACCESS": "Early Access to Activities",
            "EXPOSED_TO_ACTIVITIES_WTP_EXPERIMENT": "Activities Experiment"
        }