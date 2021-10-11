from typing import Union, Tuple, Optional, Any
import discord
from discord.ext import commands

from Utils.Useful import *
from loguru import logger
import traceback

# Index:
# - minor stuff: _size, _bitsize, vc_regions, verif, features
# - Embeds: BaseEmbed
# - Errorhandler Senderror

# minor stuff

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


# Base Embeds

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
        if ctx.author.avatar:
            instance.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar)
        else:
            instance.set_footer(text=f"User: {ctx.author}", icon_url="https://cdn.discordapp.com/emojis/837015478799040533.png?v=1")
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


# Guild Embed Confirm Buttons

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        self.value = True
        for item in self.children:
            item.disabled = True
        try:
            await self.guild.leave()
            await interaction.message.edit(view=self,embed=discord.Embed(description=f"I have left **[{self.guild}]({self.guild.icon})**, sucks for them {botemojis('shinobubully')}",color=discord.Colour.green()))
        except:
            await interaction.message.edit(view=self,embed=discord.Embed(description=f"I was unable to leave **[{self.guild}]({self.guild.icon})** {botemojis('error')}",color=discord.Colour.red()))
            button.style = discord.ButtonStyle.red
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        self.value = False
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.red
        await interaction.message.edit(view=self,embed=discord.Embed(description=f"Guess I'm not leaving **[{self.guild}]({self.guild.icon})** today",color=discord.Colour.red()))
        self.stop()
    
    async def on_timeout(self):
        self.value = False
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            if item.label == "Cancel":
                item.style = discord.ButtonStyle.red
            item.disabled = True
        await self.msg.edit(view=self,embed=discord.Embed(description=f"You took too long to respond!",color=discord.Colour.blurple()))
        self.stop()

# Guild Embed Buttons

class GuildButtons(discord.ui.View):
    def __init__(self,guild,ctx,bot,user):
        super().__init__(timeout=90)
        self.guild = guild
        self.ctx = ctx
        self.bot = bot
        self.user = user
    
    @discord.ui.button(label= "Join Guild", style=discord.ButtonStyle.green)
    async def joinguild(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        for chan in self.guild.text_channels:
            try:
                invite = await chan.create_invite()
                break
            except: pass
        if invite or None:
            await interaction.response.send_message(f"Invite Generated for **[{self.guild}]( {invite} )**", ephemeral=True)
        else:
            await interaction.response.send_message(f"I was unable to generate an invite to this guild {botemojis('error')}", ephemeral=True)
    
    @discord.ui.button(label= "Leave Guild", style=discord.ButtonStyle.red)
    async def leaveguild(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        if not self.bot.get_guild(self.guild.id):
            await self.ctx.send(embed = discord.Embed(description=f"Error Bot is not in **[{self.guild}]({self.guild.icon})**",color=discord.Color.red()))
            return
        await interaction.response.defer()
        embed = discord.Embed(description=f"Are you sure you want to leave **[{self.guild}]({self.guild.icon})**?",colour=self.bot.colour)
        confview = Confirm()
        confview.msg = await self.ctx.send(embed=embed,view=confview)
        confview.user,confview.guild = self.user,self.guild
    
    @discord.ui.button(emoji = botemojis("trash"), style=discord.ButtonStyle.blurple)
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):
        await self.message.edit(view=None)


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

# Errors Pagination

class ErrorsPagination(discord.ui.View):
    def __init__(self, start, pages, oldview: discord.ui.View, lastmsg):
        super().__init__(timeout=300)
        for item in oldview.children:
            item.disabled = False
            self.add_item(item)
        self.pages = pages
        self.tpage = len(pages)
        self.cpage = pages[0]
        self.page = start
        self.add_item(discord.ui.Button(label= "Error Logs Channel", style=discord.ButtonStyle.link, url=f"{lastmsg}", emoji = "<:channel:869062202131382292>"))
        self.children[2].label = f'{self.page}/{self.tpage}'

        if self.page <= 1:
            for item in self.children:
                if "\N{BLACK LEFT-POINTING TRIANGLE}" in item.label:
                    item.disabled = True
        
        if self.page >= self.tpage:
            for item in self.children:
                if "\N{BLACK RIGHT-POINTING TRIANGLE}" in item.label:
                    item.disabled = True
        
            
    
    async def button_pressed(self, button, interaction: discord.Interaction, change: int = 0):
        if interaction.user != self.user:
            return
        
        self.page += change
        current = self.pages[self.page - 1]
        embed = current['embed'].copy()
        embed.title = f"Error #{self.page}"

        for item in self.children:
            item.disabled = False

        if self.page <= 1:
            for item in self.children:
                if "\N{BLACK LEFT-POINTING TRIANGLE}" in item.label:
                    item.disabled = True
        
        if self.page >= self.tpage:
            for item in self.children:
                if "\N{BLACK RIGHT-POINTING TRIANGLE}" in item.label:
                    item.disabled = True
        
        for item in self.children:
            if "/" in item.label:
                item.label = f'{self.page}/{self.tpage}'

        await interaction.message.edit(f"```py\n{current['error']}```", embed = embed, view = self)


    @discord.ui.button(label='\N{BLACK LEFT-POINTING TRIANGLE}\N{BLACK LEFT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction, change=int(f"{1-self.page}"))
    
    @discord.ui.button(label='\N{BLACK LEFT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction, change=-1)
    
    @discord.ui.button(label=f'1/1', style=discord.ButtonStyle.blurple, row=1)
    async def cpage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return
        await interaction.message.delete()
    
    @discord.ui.button(label='\N{BLACK RIGHT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction, change=+1)
    
    @discord.ui.button(label='\N{BLACK RIGHT-POINTING TRIANGLE}\N{BLACK RIGHT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def end(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction, change=+int(f"{self.tpage-self.page}"))
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

# Poll Buttons for Menu

class PollButton(discord.ui.Button):
    def __init__(self, number:int):
        self.num = number
        self.em = botemojis(str(number+1))
        super().__init__(style=discord.ButtonStyle.gray, emoji=self.em)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.view.lst:
            self.view.count[self.view.lst[interaction.user.id]-1] -= 1
            if self.view.lst[interaction.user.id] == self.num + 1:
                del self.view.lst[interaction.user.id]
                await interaction.response.send_message(f"Your vote for option:{self.em} has been removed", ephemeral = True)
                content = self.view.originalmessage + "\n\n" + "\U000030fb".join([f"{botemojis(i)}: `{self.view.count[i-1]}` " for i in range(1,self.view.num + 1)]) + f"\n\nPoll ends on <t:{self.view.tm}:F> (<t:{self.view.tm}:R>)"
                await self.view.message.edit(content = content, allowed_mentions = discord.AllowedMentions.none())
                return
            await interaction.response.send_message(f"Your vote has been changed from option:{botemojis(str(self.view.lst[interaction.user.id]))} to option:{self.em}", ephemeral = True)
        else:
            await interaction.response.send_message(f"Your vote for option:{self.em} has been counted", ephemeral = True)
        self.view.count[self.num] += 1
        self.view.lst[interaction.user.id] = self.num + 1
        content = self.view.originalmessage + "\n\n" + "\U000030fb".join([f"{botemojis(i)}: `{self.view.count[i-1]}` " for i in range(1,self.view.num + 1)]) + f"\n\nPoll ends on <t:{self.view.tm}:F> (<t:{self.view.tm}:R>)"
        await self.view.message.edit(content = content, allowed_mentions = discord.AllowedMentions.none())

# Poll Menu

class PollMenu(discord.ui.View):
    def __init__(self, amount:int ,bot:commands.Bot, message:discord.Message, author, timestring:str, webhook:discord.Webhook = None, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.num = amount
        self.count = []
        self.webhook = webhook
        self.message = message
        self.user = author
        self.tm = timestring
        self.originalmessage = message.content
        for c in range(amount):
            self.count.append(0)
        self.disable = False
        self.bot = bot
        self.lst = {}
        for i in range(amount):
            self.add_item(PollButton(number = i))
    
    async def endpoll(self):
        for item in self.children:
            item.disabled = True
        i = int(datetime.datetime.timestamp(datetime.datetime.now()))
        content = self.originalmessage + "\n\n" + "\U000030fb".join([f"{botemojis(i)}: `{self.count[i-1]}` " for i in range(1,self.num + 1)]) + f"\n\nPoll closed on <t:{i}:F> (<t:{i}:R>)"
        await self.message.edit(content = content, view = self, allowed_mentions = discord.AllowedMentions.none())
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{self.message.jump_url}", label = "Jump to Poll"))
        await self.message.reply(f"Poll closed on <t:{i}:F> (<t:{i}:R>)\n\n**Final Results:**\n\n" + "\U000030fb".join([f"{botemojis(i)}: `{self.count[i-1]}` " for i in range(1,self.num + 1)]) + "\n\u200b", view = view) 
    
    @discord.ui.button(label= "Close Poll", style=discord.ButtonStyle.red, row = 3)
    async def ClosePoll(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(f"Only the owner of this poll ({self.user.mention}) can close this poll", ephemeral = True)
            return
        self.disable = True
        await self.endpoll()

    async def on_timeout(self):
        if not self.disable:
            await self.endpoll()
