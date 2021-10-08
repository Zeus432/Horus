from Utils.Menus import senderror
from typing import List
from Utils.Useful import *
from Utils.Menus import *
from discord.ext import commands
import discord
from Core.settings import *
import unicodedata

class Utility(commands.Cog):
    """ Utility Commands that contain general information """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.bot.launch_time = bot.launch_time


    @commands.command(name = "userinfo", aliases = ['ui'], help = "Get information about a user", brief = "Get User Info", ignore_extra = True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member = None):
        if type(member) != discord.Member:
            member = ctx.author
        uiembed = discord.Embed(title=f"{member.display_name}・{member}",colour=member.colour if member.colour != discord.Colour(000000) else self.bot.colour,timestamp=ctx.message.created_at, description=f"**User ID:** `{member.id}`")
        uiembed.set_thumbnail(url=member.avatar or member.default_avatar)
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
        badge = ""
        if member.id in BotOwners:
            badge += f"{self.bot.emojislist('dev')} **[Horus Dev]({member.avatar})**\n"

        if member == ctx.guild.owner:
            badge += f"{self.bot.emojislist('owner')} **[Server Owner]({member.avatar})**\n"

        for role in member.roles:
            try:
                if role.id == ctx.guild.premium_subscriber_role.id:
                    badge += f"{self.bot.emojislist('boost')} **[Server Booster](https://cdn.discordapp.com/emojis/782210035329138698.gif?v=1)**\n"
            except:
                break   
        if 809632911690039307 == ctx.guild.id:
            badge += f"<:BegoneThot:856517206543171604> **[{self.bot.get_guild(809632911690039307)}]({self.bot.get_guild(809632911690039307).icon})**\n"
        if member.id in memberbadges:
            badge += memberbadges[member.id] + f"({member.avatar})\n"
        if member.bot:
            badge = f"{self.bot.emojislist('cogs')} **[Bots Supreme]({member.avatar})**\n"

        if badge != "":
            uiembed.add_field(name="Special Badges:", value=badge)
        uiembed.add_field(name="Servers:", value=f"{len([g.id for g in self.bot.guilds if g.get_member(member.id)])} shared")
        await ctx.send(embed=uiembed)


    @commands.command(name = "avatar", help = "Get a user's avatar", brief = "Get User Avatar", aliases = ['av'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.guild_only()
    async def avatar(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour
        embed = discord.Embed(colour=colour,timestamp=ctx.message.created_at)
        embed.set_footer(text=f"{ctx.guild}", icon_url=ctx.guild.icon)
        avatar = user.avatar.with_static_format('png') if user.avatar else user.default_avatar.with_static_format('png')
        jpgavatar = user.avatar.with_static_format('jpg') if user.avatar else user.default_avatar.with_static_format('jpg')
        webpavatar = user.avatar.with_static_format('webp') if user.avatar else user.default_avatar.with_static_format('webp')
        embed.set_image(url = avatar)
        embed.title = f"Avatar for {user}"
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, url=f"{avatar}", label=".png link"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, url=f"{jpgavatar}", label=".jpg link"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, url=f"{webpavatar}", label=".webp link"))
        await ctx.send(embed=embed,view=view)


    @commands.command()
    @commands.cooldown(2, 5, commands.BucketType.user)
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
    
    class PollFlags(commands.FlagConverter, prefix='--', delimiter=' ', case_insensitive=True):
        question: str = commands.flag(name='question', aliases=["q","ques"])
        time: TimeConverter = 600.0
        opt: List[str]  = commands.flag(name='option', aliases=["opt"])
        webhook: bool = False


    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def poll(self, ctx, *, flags: PollFlags):
        """ 
        Start a poll with buttons which makes polling truly anonymous
        Input is done by entering using multiple flags.

        __**List of flags:**__

        **Question:**
        `--question <question>` 
        Enter the question or whatever you need a poll for

        **Time:**
        `--time <time>` 
        Enter the time duration for the poll. It's 10 minutes by default

        **Options:**
        `--opt <option>`
        Enter the options for the poll. Can have a maximum of 10 options per poll

        **Webhook:**
        `--webhook <True/False>`
        Entering True will make the bot send the poll as a webhook if it has Manage Webhooks perms

        __**Example Usage:**__

        >>> `h!poll --question Hey there this is a poll --time 5m --option Option 1 --opt Option 2 --opt Option 3 --option Last one Lol`

        `h!poll --ques Hey look another poll --opt Option --opt Another Option --webhook True`
        """
        question = flags.question
        time = flags.time
        options = flags.opt
        webhook = None
        if len(options) < 2:
            await ctx.reply("You need to give atleast 2 options!")
            return
        elif len(options) > 10:
            await ctx.reply("You can only have a maximum of 10 options!")
            return
        elif time > 3600:
            await ctx.reply("Maximum duration for a poll has been set to 1 hour due to hosting limits")
            return
        sendem,count = f"{question}",1
        for opt in options:
            sendem += f"\n\n{self.bot.emojislist(str(count))} {opt}"
            count += 1
        if flags.webhook:
            webhook = await ctx.channel.webhooks()
            webhook = [w for w in webhook if w.user == self.bot.get_user(858335663571992618)]
            try:
                webhook = webhook[0]
            except:
                webhook = webhook = await ctx.channel.create_webhook(name = "Horus Webhook", reason = f"Webhook for Poll. Invoked by {ctx.author}" )
            message = await webhook.send(
                content=f"{sendem}",
                username= f"{ctx.author.display_name}", 
                avatar_url = f"{ctx.author.avatar}" or f"{ctx.author.default_avatar}",
                allowed_mentions = discord.AllowedMentions.none(),
                wait = True
            )
        else:
            message = await ctx.send(f"{ctx.author.mention} asks:\n{sendem}", allowed_mentions = discord.AllowedMentions.none())
        tm = int(datetime.datetime.timestamp(datetime.datetime.now()) + time)
        view = PollMenu(amount=len(options), bot=self.bot, timeout = time, timestring = f"{tm}", webhook = webhook, message = message, author = ctx.author)
        msg = message.content + "\n\n" + "\U000030fb".join([f"{self.bot.emojislist(i)}: `0` " for i in range(1,len(options)+ 1)]) + f"\n\nPoll ends on <t:{tm}:F> (<t:{tm}:R>)"
        await message.edit(content = msg, view = view, allowed_mentions = discord.AllowedMentions.none())


    @poll.error
    async def pollerror(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.reply(f'This command is disabled.')

        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.reply(f'Command is on cooldown, Try again in {round(error.retry_after, 2)} seconds')
        
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.reply(f"I need `Manage Webhooks` perms for you to use the `--webhook` flag")
        
        else:
            await senderror(bot=self.bot,ctx=ctx,error=error)


def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot))