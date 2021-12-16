import discord
from discord.ext import commands

from datetime import datetime

from .useful import UserBadges, PollFlags
from .menus import PollMenu

class Utility(commands.Cog):
    """ Utility Commands that contain general information """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.todo_cache = {}
    
    @commands.command(name = "userinfo", aliases = ['ui'], brief = "Get User Info", ignore_extra = True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def userinfo(self, ctx: commands.Context, user: discord.Member = None):
        """ Get information about a user """
        user = user or ctx.author
        embed = discord.Embed(title = f"{user.display_name}\U000030fb{user}", colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour)
        embed.timestamp = ctx.message.created_at
        embed.set_thumbnail(url = user.display_avatar)
        join_position = [m for m in sorted(ctx.guild.members, key = lambda u: u.joined_at)].index(ctx.author) + 1
        embed.set_footer(text = f"Member #{join_position}\U000030fbID: {user.id}", icon_url = user.avatar if user.display_avatar != user.avatar else discord.Embed.Empty)

        embed.add_field(name = "Joined Discord:", value = f"<t:{round(user.created_at.timestamp())}:D>\n(<t:{round(user.created_at.timestamp())}:R>)\n\u200b")
        embed.add_field(name = "Joined Server:", value = f"<t:{round(user.joined_at.timestamp())}:D>\n(<t:{round(user.joined_at.timestamp())}:R>)\n\u200b")

        roles, extra = "", 0

        for role in sorted(user.roles, reverse = True):
            if role.id != ctx.guild.id:
                if len(roles) < 900:
                    roles += f"{role.mention} "
                    continue
                extra += 1
        
        roles = f"{roles}{f' and {extra} other roles . . .' if extra != 0 else ''}" if roles else "This user has no roles"
        embed.add_field(name = "User's Roles:", value = f"{roles}", inline = False)

        # Badges here
        embed = UserBadges(ctx, self.bot, user, embed)

        embed.add_field(name = "Servers:", value = f"{len([guild.id for guild in self.bot.guilds if guild.get_member(user.id)])} shared")

        await ctx.send(embed = embed)

    @commands.command(name = "avatar", brief = "Get User Avatar", aliases = ['av'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        """ Get a user's avatar """
        user = user or ctx.author
        colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour
        embed = discord.Embed(title = f"Avatar for {user}", colour = colour, timestamp = ctx.message.created_at)
        embed.set_footer(text = f"{ctx.guild}", icon_url = ctx.guild.icon)

        avatar = user.display_avatar.with_static_format('png')
        jpgav = user.display_avatar.with_static_format('jpg')
        webpav = user.display_avatar.with_static_format('webp')

        embed.set_image(url = avatar)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{avatar}", label = ".png"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{jpgav}", label = ".jpg"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{webpav}", label = ".webp"))

        await ctx.send(embed = embed, view = view)
    
    @commands.command(cooldown_after_parsing = True)
    @commands.is_owner()
    @commands.cooldown(3, 60, commands.BucketType.guild)
    async def poll(self, ctx: commands.Context, *, flags: PollFlags):
        """ 
        Start a poll with buttons which makes polling truly anonymous
        Input is done by entering using multiple flags.

        __**List of flags:**__

        **Question:**
        `--q <question>` 
        Enter the question or whatever you need a poll for

        **Time:**
        `--time <time>` 
        Enter the time duration for the poll. It's 10 minutes by default

        **Options:**
        `--o <option>`
        Enter the options for the poll. Can have a maximum of 10 options per poll

        **Yes or No:**
        `--yesno <True/False>`
        Entering True will make it a yes or no question with 2 options Yes or No. Other Input options are ignored


        **Webhook:**
        `--webhook <True/False>`
        Entering True will make the bot send the poll as a webhook if it has Manage Webhooks perms

        __**Example Usage:**__

        >>> `h!poll --question Hey there this is a poll --time 5m --option Option 1 --opt Option 2 --opt Option 3 --option Last one Lol`

        `h!poll --ques Hey look another poll --opt Option --opt Another Option --webhook True`
        """

        content = flags.question
        time = flags.time
        options = flags.opt
        yesno = flags.yesno
        webhook = None

        content = f"{ctx.author.mention} asks:\n{content}" if yesno else content

        if len(options) < 2 and not yesno:
            return await ctx.reply("You need to give atleast 2 options!")
        elif len(options) > 10 and not yesno:
            return await ctx.reply("You can only have a maximum of 10 options!")
        elif time > 36000:
            return await ctx.reply("Maximum duration for a poll has been set to 1 hour due to hosting limits")
        
        endtime = int(datetime.now().timestamp() + time)

        if not yesno:
            for index, option in enumerate(options):
                content += f"\n\n{self.bot.get_em(index + 1)} {option}"

            view = PollMenu(options = len(options), content = content, endtime = endtime, bot = self.bot, ctx = ctx, timeout = time, yesno = yesno)
            content += "\n\n" + "\U000030fb".join([f"{self.bot.get_em(num)}: `0` " for num in range(1, len(options) + 1)])
        
        else:
            view = PollMenu(options = 2, content = content, endtime = endtime, bot = self.bot, ctx = ctx, timeout = time, yesno = yesno)
            content += "\n\n" + "\U000030fb".join([f"{self.bot.get_em(f'{value}')}: `0` " for value in ['tick', 'cross']])
        
        content += f"\n\nPoll ends on <t:{endtime}:F> (<t:{endtime}:R>)"

        if len(content) > 1800:
            return await ctx.reply(f'Please shorten the length of your question{" and options!" if not yesno else ""}')
        
        if flags.webhook:
            try:
                webhook = await ctx.channel.webhooks()
            except commands.CommandInvokeError:
                return await ctx.reply("I need `Manage Webhooks` perms for you to use the `--webhook` flag")
    
            webhook = [w for w in webhook if w.user == self.bot.get_user(858335663571992618)]
            try:
                webhook = webhook[0]
            except:
                webhook = webhook = await ctx.channel.create_webhook(name = "Horus Webhook", reason = f"Webhook for Poll. Invoked by {ctx.author}")
            
            view.message = await webhook.send(
                content = f"{content}",
                username = f"{ctx.author.display_name}", 
                avatar_url = f"{ctx.author.avatar}" or f"{ctx.author.default_avatar}",
                allowed_mentions = discord.AllowedMentions.none(),
                view = view,
                wait = True
            )
        
        else:
            view.message = await ctx.send(f"{content}", allowed_mentions = discord.AllowedMentions.none(), view = view)