from typing import Union, Tuple, Optional, Any
import discord
from discord.ext import commands
from datetime import datetime
import traceback
from loguru import logger

from Utils.Useful import *

# Base Embed

class BaseEmbed(discord.Embed):
    """Main purpose is to get the usual setup of Embed for a command or an error embed"""
    def __init__(self, color: Union[discord.Color, int] = 0xffcccb, timestamp: datetime = None,
                 fields: Tuple[Tuple[str, str]] = (), field_inline: Optional[bool] = False, **kwargs):
        super().__init__(color=color, timestamp=timestamp or discord.utils.utcnow(), **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def default(cls, ctx: commands.Context,color: Union[discord.Color, int] = discord.Color.red(), **kwargs) -> "BaseEmbed":
        instance = cls(color=color,**kwargs)
        instance.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar or ctx.author.default_avatar)
        return instance

    @classmethod
    def to_error(cls, title: Optional[str] = "Error",
                 color: Union[discord.Color, int] = discord.Color.red(), **kwargs) -> "BaseEmbed":
        return cls(title=title, color=color, **kwargs)

# Errorhandler Senderror

async def senderror(bot, ctx, error):
    async def send_del(*args: Any, **kwargs: Any) -> None:
        if bot.devmode and ctx.author.id != 760823877034573864:
                return
        if embed := kwargs.get("embed"):
            text = f"Spamming errored commands will result in a blacklist"
            embed.set_footer(icon_url=bot.user.avatar, text=text)
        try:
            await ctx.reply(*args, **kwargs)
        except:
            try:
                await ctx.author.send(*args, **kwargs)
            except:
                pass
    
    traceback_error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    serror,skip,lines,error_ = "",False,0,""
    for i in traceback_error.split('\n'):
        if skip:
            lines += 1

        elif len(serror + i) > 1900:
            skip = True
            error_ = serror
            lines += 1

        serror += f"\n{i}"

    error_ += serror if not error_ else f"\n\n... ({lines} lines left)"
    fulltraceback = f"{await mystbin(serror)}.python" if lines > 0 else None

    if await bot.is_owner(ctx.message.author):
        try:
            await ctx.message.add_reaction(botemojis('warning'))
        except:
            pass
        view0 = discord.ui.View(timeout = 600)
        async def on_timeout(view = view0):
            button.disabled = True
            await msg.edit("This command has errored, check your Error Logs (<#873252901726863441>) to see what happened", view = view)
        view0.on_timeout = on_timeout
        button = discord.ui.Button(label = "Error Traceback", style = discord.ButtonStyle.gray)
        async def callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(f"You can't use this button {interaction.user.mention}!", ephemeral = True)
                return
            errorview = discord.ui.View()
            if fulltraceback:
                errorview.add_item(discord.ui.Button(label= "Full Traceback", style=discord.ButtonStyle.link, url=f"{fulltraceback}", emoji = bot.emojislist('inspect')))
            await interaction.response.send_message(f"```py\n{error_}```", view = errorview, ephemeral = True)
            button.disabled = True
            await msg.edit("This command has errored, check your Error Logs (<#873252901726863441>) to see what happened", view = view0)
        button.callback = callback
        view0.add_item(button)
        try:
            msg = await ctx.reply("This command has errored, Click the button below to view traceback", view = view0)
        except:
            view0.add_item(discord.ui.Button(label= "Jump to Error", style=discord.ButtonStyle.link, url=f"{ctx.message.jump_url}", emoji = "\U0001f517"))
            msg = await ctx.author.send("I was unable to message in the channel! So here is the error message\nClick the first button to view traceback of the command and the second button to view traceback", view = view0)
    else:
        await bot.wait_until_ready()
        await send_del(embed=BaseEmbed.to_error("**Command Error!**",description=f"This error has been forwarded to the bot developer and will be fixed soon. Do not spam errored commands, doing so will get you blacklisted. If this isn't fixed feel free to dm me <@760823877034573864>\n\n**Error:**```py\n{error}```"), delete_after = 20)


    embed = BaseEmbed.default(ctx, title = "**Command Error!**")
    embed.add_field(name="Command Used:", value=f"`{ctx.message.content}`", inline=False)
    embed.add_field(name="Author:", value=f"{ctx.author.mention}\n (`{ctx.author.id}`)")
    if ctx.guild:
        embed.add_field(name="Channel:", value=f"{ctx.channel.mention}\n (`{ctx.channel.id}`)")
        embed.add_field(name="Guild:", value=f"**{ctx.guild}**\n (`{ctx.guild.id}`)")
    else:
        embed.add_field(name="Dm Channel:", value=f"<#{ctx.channel.id}>\n (`{ctx.channel.id}`)")
    embed.add_field(name="Message ID:", value=f"`{ctx.message.id}`")

    channel = bot.get_channel(873252901726863441)
    bot.error_channel = channel
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label= "Jump to Error", style=discord.ButtonStyle.link, url=f"{ctx.message.jump_url}", emoji = "\U0001f517"))
    if fulltraceback:
        view.add_item(discord.ui.Button(label= "Full Traceback", style=discord.ButtonStyle.link, url=f"{fulltraceback}", emoji = bot.emojislist('inspect')))

    await bot.error_channel.send(f"```py\n{error_}```", embed = embed, view = view)

    bot.latesterrors.append({"embed":embed,"error":error_,"view":view})
    logger.opt(exception=error).error(f"Ignoring exception in command {ctx.command}\nCommand Used - {ctx.message.content}\n")

# Guild Embed

def guildanalytics(bot, guild,join: bool = None, **kwargs) -> "BaseEmbed":
    colour = discord.Color.red() if join == False else discord.Color.green()
    colour = discord.Colour(0x9c9cff) if join == None else colour
    msg = "I've left this server" if join == False else "I've joined a new server"
    description = f"Server was created on <t:{round(guild.created_at.timestamp())}:D>\n"
    description += f"I joined this server on <t:{round(guild.me.joined_at.timestamp())}:D>\n" if join == None else ""
    description += f"{msg}\nI'm in **{len([g.id for g in bot.guilds])}** servers now\nI have **{len([g.id for g in bot.users])}** users now" if join != None else ""
    embed = discord.Embed(title = guild, colour = colour, description = description)
    owner,region = guild.owner, guild.region.name
    ifnsfw = len([c for c in guild.text_channels if c.is_nsfw()])
    ifgprem = guild.premium_tier
    gfl = [f"{botemojis('parrow')} {features[c]}" for c in guild.features] 
    if gfl == []:
        featurend = "No Features Available"
    else:
        threadinfo = ""
        if "THREADS_ENABLED" in  guild.features:
            threadinfo = f"\n{botemojis('parrow')} Threads Enabled"
            threadinfo = f"\nㅤㅤ{botemojis('replycont')} New Thread Permissions Enabled" if "NEW_THREAD_PERMISSIONS" in guild.features else ""
            threadinfo += f"\nㅤㅤ{botemojis('replycont')} Private Threads" if "PRIVATE_THREADS" in guild.features else ""
            threadinfo += f"\nㅤㅤ{botemojis('replyend')} Archive time limit: "
            threadinfo += "1 week" if "SEVEN_DAY_THREAD_ARCHIVE" in guild.features else "3 days" if "THREE_DAY_THREAD_ARCHIVE" in guild.features else "1 day"
        featurend = "\n".join([c for c in gfl if not c.startswith(f"{botemojis('parrow')} Thread") or not c.startswith(f"{botemojis('parrow')} New Thread")]) + threadinfo
            
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