import disnake as discord
from matplotlib.pyplot import title
from Core.Utils.pagination import TestPagination
from bot import Horus
from disnake.ext import commands

from datetime import datetime

from Core.Utils.useful import verif
from .useful import UserBadges, PollFlags
from .menus import PollMenu, ConfirmClear

class Utility(commands.Cog):
    """ Utility Commands """ 
    def __init__(self, bot: Horus):
        self.bot = bot
        self.todo_cache = {}
    
    @commands.command(name = "userinfo", aliases = ['ui'], brief = "Get User Info", ignore_extra = True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def userinfo(self, ctx: commands.Context, *, user: discord.Member = None):
        """ Get information about a user """
        user = user or ctx.author
        embed = discord.Embed(title = f"{user.display_name}\U000030fb{user}", colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour)
        embed.timestamp = ctx.message.created_at
        embed.set_thumbnail(url = user.display_avatar)
        join_position = [m for m in sorted(ctx.guild.members, key = lambda u: u.joined_at)].index(user) + 1
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
        embed.add_field(name = "User's Roles:", value = f"{roles}\n\u200b", inline = False)

        # Badges here
        embed = UserBadges(ctx, self.bot, user, embed)

        embed.add_field(name = "Servers:", value = f"{len([guild.id for guild in self.bot.guilds if guild.get_member(user.id)])} shared")

        await ctx.send(embed = embed)
    
    @commands.user_command(name = "View User Info", default_permission = True)
    async def user_data(self, interaction: discord.MessageCommandInteraction, user: discord.User):
        embed = discord.Embed(title = f"{user.display_name}\U000030fb{user}", colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour)
        embed.set_thumbnail(url = user.display_avatar)
        join_position = [m for m in sorted(interaction.guild.members, key = lambda u: u.joined_at)].index(user) + 1
        embed.set_footer(text = f"Member #{join_position}\U000030fbID: {user.id}", icon_url = user.avatar if user.display_avatar != user.avatar else discord.Embed.Empty)

        embed.add_field(name = "Joined Discord:", value = f"<t:{round(user.created_at.timestamp())}:D>\n(<t:{round(user.created_at.timestamp())}:R>)\n\u200b")
        embed.add_field(name = "Joined Server:", value = f"<t:{round(user.joined_at.timestamp())}:D>\n(<t:{round(user.joined_at.timestamp())}:R>)\n\u200b")

        roles, extra = "", 0

        for role in sorted(user.roles, reverse = True):
            if role.id != interaction.guild.id:
                if len(roles) < 900:
                    roles += f"{role.mention} "
                    continue
                extra += 1
        
        roles = f"{roles}{f' and {extra} other roles . . .' if extra != 0 else ''}" if roles else "This user has no roles"
        embed.add_field(name = "User's Roles:", value = f"{roles}\n\u200b", inline = False)

        # Badges here
        embed = UserBadges(interaction, self.bot, user, embed)

        embed.add_field(name = "Servers:", value = f"{len([guild.id for guild in self.bot.guilds if guild.get_member(user.id)])} shared")

        await interaction.response.send_message(embed = embed)


    @commands.command(name = "avatar", brief = "Get User Avatar", aliases = ['av'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        """ Get a user's avatar """
        user = user or ctx.author
        colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour
        embed = discord.Embed(title = f"Avatar for {user}", colour = colour, timestamp = ctx.message.created_at)
        embed.set_footer(text = f"{ctx.guild}", icon_url = f"{ctx.guild.icon}")

        avatar = user.display_avatar.with_static_format('png')
        jpgav = user.display_avatar.with_static_format('jpg')
        webpav = user.display_avatar.with_static_format('webp')

        embed.set_image(url = avatar)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{avatar}", label = ".png"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{jpgav}", label = ".jpg"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{webpav}", label = ".webp"))

        await ctx.send(embed = embed, view = view)

    @commands.command(name = "serverinfo", brief = "Get Server Info", aliases = ['si'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def serverinfo(self, ctx: commands.Context):
        """ Get some useful stats about this server """
        embed = discord.Embed(colour = self.bot.colour, title = f"{ctx.guild}", description = f"Server was created on <t:{round(ctx.guild.created_at.timestamp())}:D>\nServer ID: `{ctx.guild.id}`\nOwner: {ctx.guild.owner.mention} (`{ctx.guild.owner.id}`)\nVerif Level: {verif[str(ctx.guild.verification_level)]}")
        embed.set_thumbnail(url = f"{ctx.guild.icon}")

        text_channels = f"{self.bot.get_em('text')} **{len(ctx.guild.text_channels)}** Text Channel{'s' if len(ctx.guild.text_channels) != 1 else ''}\n" if len(ctx.guild.text_channels) > 0 else ""
        voice_channels = f"{self.bot.get_em('voice')} **{len(ctx.guild.voice_channels)}** Voice Channels{'s' if len(ctx.guild.voice_channels) != 1 else ''}\n" if len(ctx.guild.voice_channels) > 0 else ""
        stage_channels = f"{self.bot.get_em('stage')} **{len(ctx.guild.stage_channels)}** Stage Channels{'s' if len(ctx.guild.stage_channels) != 1 else ''}" if len(ctx.guild.stage_channels) > 0 else ""

        embed.add_field(name = "Channels", value = f"{text_channels}{voice_channels}{stage_channels}", inline = False)
        embed.add_field(name = "Misc", value = f"**{len([member for member in ctx.guild.members if member.bot])}** Bots\n**{len([member for member in ctx.guild.members if not member.bot])}** Humans\n**{len(ctx.guild.roles)}** Roles")
        embed.add_field(name = "Prefixes", value = "`" + "`\n`".join([f'@{self.bot.user.name}', *((prefix if prefix else '\u200b') for index, prefix in enumerate(await self.bot.getprefix(self.bot, ctx.message)) if index > 1) ]) + "`")

        await ctx.send(embed = embed)
    
    @commands.command(cooldown_after_parsing = True)
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
        `--opt <option>`
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

        content = f"{ctx.author.mention} asks:\n{content}" if not yesno else content

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

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.group(name = "todo", brief = "Todo list related commands", invoke_without_command = True)
    async def todo(self, ctx: commands.Context):
        """ View your todo list """
        try:
            todo = self.todo_cache[ctx.author.id]
        except KeyError:
            todo = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
            self.todo_cache[ctx.author.id] = todo

        if not todo:
            return await ctx.send(f"Your todo list is empty. You can add tasks to your todo by running `{ctx.clean_prefix}{ctx.invoked_with} add <task_here>`")
        elif not todo['data']:
            return await ctx.send(f"Your todo list is empty. You can add tasks to your todo by running `{ctx.clean_prefix}{ctx.invoked_with} add <task_here>`")
        
        stuff = todo['data']
        neat_todo = [f"**[{index+1})]({stuff[task_id]['messagelink']})** {stuff[task_id]['stuff']}" for index, task_id in enumerate(stuff)]
        embeds = []

        while neat_todo:
            embed = discord.Embed(title = f"**{ctx.author.display_name}**'s To Do List", description = "\n".join(neat_todo[:10]), color = self.bot.colour)
            neat_todo = neat_todo[10:]
            embeds.append(embed)
        
        view = TestPagination(embeds = embeds, bot = self.bot, user = ctx.author)
        view.message = await ctx.reply(embed = embeds[0], view = view, mention_author = False)
    
    @commands.cooldown(1, 5, commands.BucketType.user)
    @todo.command(name = "add", brief = "Add todo task")
    async def todo_add(self, ctx: commands.Context, *, task: str):
        """ Add a todo task """
        if len(task) > 150:
            return await ctx.reply('Give me a task with less than 150 charecters')

        try:
            todo = self.todo_cache[ctx.author.id]
        except KeyError:
            todo = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
        if todo is None:
            todo = await self.bot.db.fetchrow(f'INSERT INTO todo(userid, lastupdated, data) VALUES($1, $2, $3) ON CONFLICT (userid) DO UPDATE SET lastupdated = $2 RETURNING *', ctx.author.id, int(datetime.now().timestamp()), {})
        
        self.todo_cache[ctx.author.id] = todo # Update Todo Cache

        if len(todo['data']) >= 100:
            return await ctx.reply('I was unable to add this task as Todo lists are currently limited to a maximum of `100` tasks.')
        
        todo['data'][ctx.message.id] = {'messagelink': f'{ctx.message.jump_url}', 'stuff': f'{task}'}
        self.todo_cache[ctx.author.id] = todo

        await self.bot.db.execute(f'UPDATE todo SET lastupdated = $2, data = $3 WHERE userid = $1', ctx.author.id, int(datetime.now().timestamp()), todo['data'])
        await ctx.reply('Your todo list has been updated!')

    @commands.cooldown(1, 5, commands.BucketType.user)
    @todo.command(name = "remove", brief = "Remove todo task")
    async def todo_remove(self, ctx: commands.Context, id: int):
        """ Remove a task from your todo list """
        try:
            todo = self.todo_cache[ctx.author.id]
        except KeyError:
            todo = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
        
        if id > len(todo['data']) or id <= 0:
            return await ctx.reply(f"You don't have a task with ID:`{id}`")
        
        for index, task_id in enumerate(todo['data']):
            if index + 1 == id:
                deleted = todo['data'][task_id]
                del todo['data'][task_id]
                self.todo_cache[ctx.author.id] = todo
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label = "Source", emoji = "\U0001f517", style = discord.ButtonStyle.link, url = f'{deleted["messagelink"]}'))
                await self.bot.db.execute(f'UPDATE todo SET lastupdated = $2, data = $3 WHERE userid = $1', ctx.author.id, int(datetime.now().timestamp()), todo['data'])
                return await ctx.reply(f'I have removed this task from your todo list:\n  (**{id}**) {deleted["stuff"]}', view = view)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @todo.command(name = "edit", brief = "Remove todo task", aliases = ['update'])
    async def todo_edit(self, ctx: commands.Context, id: int, *, task: str):
        """ Edit a task in your todo list """
        try:
            todo = self.todo_cache[ctx.author.id]
        except KeyError:
            todo = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
        
        if id > len(todo['data']) or id <= 0:
            return await ctx.reply(f"You don't have a task with ID:`{id}`")
        
        for index, task_id in enumerate(todo['data']):
            if index + 1 == id:
                todo['data'][task_id]['stuff'] = task
                await self.bot.db.execute(f'UPDATE todo SET lastupdated = $2, data = $3 WHERE userid = $1', ctx.author.id, int(datetime.now().timestamp()), todo['data'])
                return await ctx.reply(f'Task `{id}` updated!')
    
    @todo.command(name = "clear", brief = "Clear todo")
    async def todo_clear(self, ctx: commands.Context):
        """ Clear your todo list completely """
        try:
            todo = self.todo_cache[ctx.author.id]
        except KeyError:
            todo = await self.bot.db.fetchrow('SELECT * FROM todo WHERE userid = $1', ctx.author.id)
        
        if not todo:
            return await ctx.send(f"There is nothing to clear in your todo list. You can add tasks to your todo by running `{ctx.clean_prefix}{ctx.invoked_with} add <task_here>`")
        elif not todo['data']:
            return await ctx.send(f"There is nothing to clear in your todo list. You can add tasks to your todo by running `{ctx.clean_prefix}{ctx.invoked_with} add <task_here>`")
        
        view = ConfirmClear(user = ctx.author)
        view.message = await ctx.reply(f'This will clear all your todo tasks (`{len(todo["data"])}`). Are you absolutely sure you want to clear your entire list {self.bot.get_em("concern")}?', view = view)
        await view.wait()

        if view.value:
            todo['data'].clear()
            await self.bot.db.execute(f'UPDATE todo SET lastupdated = $2, data = $3 WHERE userid = $1', ctx.author.id, int(datetime.now().timestamp()), todo['data'])
    
    @commands.is_owner()
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.group(name = "tag", brief = "Invoke a tag", invoke_without_command = True)
    async def tag(self, ctx: commands.Context, *, name: str):
        query = "SELECT content FROM tags WHERE (serverid = $1 and (name = $2 OR '$2' = ANY (aliases::varchar[])))"
        content = await self.bot.db.fetchval(query, ctx.guild.id, name)

        if content is None:
            return await ctx.reply("Tag not found!", mention_author = False)
        
        if msg := ctx.message.reference:
            await msg.resolved.reply(f'{content}')
        
        else:
            await ctx.send(f'{content}')
    
    @commands.is_owner()
    @tag.command(name = "add", brief = "Add a Tag")
    async def add_tag(self, ctx: commands.Context, name: str, *, content: str):
        query = "INSERT INTO "