from typing import Union, Tuple, Optional, Any
import discord
from discord.ext import commands
import datetime
from Useful.Useful import *
from loguru import logger
import traceback

botemojis = botemojis

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
            "THREADS_ENABLED":"Threads Enabled"
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
    def guildanalytics(cls, bot, guild: discord.Guild,join: bool = None, **kwargs) -> "BaseEmbed":
        colour = discord.Color.red() if join == False else discord.Color.green()
        colour = discord.Colour(0x9c9cff) if join == None else colour
        msg = "I've left this server" if join == False else "I've joined a new server"
        description = f"Server was created on <t:{round(guild.created_at.timestamp())}:D>\n"
        description += f"I joined this server on <t:{round(guild.me.joined_at.timestamp())}:D>\n" if join != True else ""
        description += f"{msg}\nI'm in **{len([g.id for g in bot.guilds])}** servers now\nI have **{len([g.id for g in bot.users])}** users now" if join != None else ""
        embed = discord.Embed(title = guild, colour = colour, description = description)
        owner,region = guild.owner, guild.region.name
        ifnsfw = len([c for c in guild.text_channels if c.is_nsfw()])
        ifgprem = guild.premium_tier
        gfl = [f"{botemojis('parrow')} {features[c]}" for c in guild.features ]
        if gfl == []:
            featurend = "No Features Available"
        else:
            threadinfo = ""
            if "THREADS_ENABLED" in  guild.features:
                threadinfo = f"\n{botemojis('parrow')} Threads Enabled"
                threadinfo += f"\nㅤㅤ{botemojis('replycont')} Private Threads" if "PRIVATE_THREADS" in guild.features else ""
                threadinfo += f"\nㅤㅤ{botemojis('replyend')} Archive time limit: "
                threadinfo += "1 week" if "SEVEN_DAY_THREAD_ARCHIVE" in guild.features else "3 days" if "THREE_DAY_THREAD_ARCHIVE" in guild.features else "1 day"
            #Threads
            featurend = "\n".join([c for c in gfl if not c.startswith(f"{botemojis('parrow')} Threads")]) + threadinfo
            
        if ifnsfw > 0:
            ifnsfw = f"\nㅤㅤ{botemojis('replyend')} Nsfw ⤏ **{ifnsfw}**"
        else:
            ifnsfw = ""
        embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457879292152381443.png" if "VERIFIED" in guild.features else "https://cdn.discordapp.com/emojis/508929941610430464.png"if "PARTNERED" in guild.features else discord.Embed.Empty, text=guild.name if "VERIFIED" in guild.features or "PARTNERED" in guild.features else discord.Embed.Empty)
        embed.add_field(name="**Guild Info**", value=f"**Owner:** {owner.mention} (`{owner.id}`)\n**Region:** {vc_regions[region]}\n**Verif. Level:** {verif[str(guild.verification_level)]}\n**Server ID:** `{guild.id}`",inline=False)
        embed.add_field(name="**Members**",value=f"Humans: **{len([g.id for g in guild.members if not g.bot])}**\nBots: **{len([g.id for g in guild.members if g.bot])}**\nTotal: **{len([g.id for g in guild.members])}**")
        embed.add_field(name="**Channels**",value=f"{botemojis('text')} Text Channels: **{len(guild.text_channels)}** {ifnsfw}\n{botemojis('voice')} Voice Channels: **{len(guild.voice_channels)}**\n{botemojis('stage')} Stage Channels: **{len(guild.stage_channels)}**")
        embed.add_field(name="**Misc**",value=f"AFK channel: **{guild.afk_channel}**\nAFK timeout: **{(guild.afk_timeout)/60} minutes**\nCustom emojis: **{len(guild.emojis)}**\nRoles: **{len(guild.roles)}**", inline=False)
        if ifgprem > 0:
            nitro_boost = f"Tier **{str(guild.premium_tier)}** with **{guild.premium_subscription_count}** boosters\nFile size limit: **{_size(guild.filesize_limit)}**\nEmoji limit: **{str(guild.emoji_limit)}**\nVCs max bitrate: **{_bitsize(guild.bitrate_limit)}**"
            embed.add_field(name="**Nitro State**", value=nitro_boost)
        embed.add_field(name="**Server Features**", value=featurend, inline=False)
        embed.set_thumbnail(url=guild.icon if guild.icon else "https://cdn.discordapp.com/embed/avatars/1.png")
        if guild.banner:
            embed.set_image(url=guild.banner)
        return embed

async def senderror(bot, ctx, error):
    async def send_del(*args: Any, **kwargs: Any) -> None:
        if embed := kwargs.get("embed"):
            text = f"Spamming errored commands will result in a blacklist"
            embed.set_footer(icon_url=bot.user.avatar, text=text)
        await ctx.reply(*args, **kwargs)
    if await bot.is_owner(ctx.message.author):
        try:
            await ctx.message.add_reaction(botemojis('error'))
        except:
            pass
        await ctx.reply("This command has errored, check your Error Logs to see what happened")
    else:
        await bot.wait_until_ready()
        await send_del(embed=BaseEmbed.to_error("**Command Error!**",description=f"This error has been forwarded to the bot developer and will be fixed soon. Do not spam errored commands, doing so will get you blacklisted. If this isn't fixed feel free to dm me <@760823877034573864>\n\n**Error:**```py\n{error}```"), delete_after = 20)
    traceback_error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    embed = BaseEmbed.default(ctx, title = "**Command Error!**")
    embed.add_field(name="Command Used:", value=f"`{ctx.message.content}`", inline=False)
    embed.add_field(name="Author:", value=f"{ctx.author.mention}\n (`{ctx.author.id}`)")
    if ctx.guild:
        embed.add_field(name="Channel:", value=f"{ctx.channel.mention}\n (`{ctx.channel.id}`)")
        embed.add_field(name="Guild:", value=f"**{ctx.guild}**\n (`{ctx.guild.id}`)")
    else:
        embed.add_field(name="Dm Channel:", value=f"<#{ctx.channel.id}>\n (`{ctx.channel.id}`)")
    embed.add_field(name="Message ID:", value=f"`{ctx.message.id}`")
    embed.add_field(name="Jump to Error", value=f"[**Message Link \U0001f517**]({ctx.message.jump_url})")
    channel = bot.get_channel(873252901726863441)
    bot.error_channel = channel
    await bot.error_channel.send(embed=embed)
    serror = ""
    for i in traceback_error.split('\n'):
        if len(serror + i) > 1900:
            await bot.error_channel.send(f"```py\n{serror}```")
            serror = ""
        serror += f"\n{i}"
    await bot.error_channel.send(f"```py\n{serror}```")
    logger.opt(exception=error).error(f"Ignoring exception in command {ctx.command}\nCommand Used - {ctx.message.content}\n")

class GuildButtons(discord.ui.View):
    def __init__(self,guild):
        super().__init__(timeout=10)
        self.value = 3
        self.guild = guild
    
    @discord.ui.button(label= "Join Guild", style=discord.ButtonStyle.green)
    async def joinguild(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        for chan in self.guild.text_channels:
            try:
                invite = await chan.create_invite()
                break
            except: pass
        if invite:
            await interaction.response.send_message(f"Invite Generated for [**{self.guild}**]( {invite} )", ephemeral=True)
        else:
            await interaction.response.send_message(f"I was unable to generate an invite to this guild {botemojis('error')}")
    
    @discord.ui.button(label= "Leave Guild", style=discord.ButtonStyle.red)
    async def leaveguild(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        button.disabled = True
        await interaction.message.edit("left guild", view=self)
        self.value = 1
    
    @discord.ui.button(emoji = botemojis("trash"), style=discord.ButtonStyle.blurple)
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):
        await self.message.edit(view=None)