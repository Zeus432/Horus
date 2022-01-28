from bot import Horus
import disnake as discord
from disnake.ext import commands

import asyncio
import time

from .views import RolesView
from .woodlands import PersistentView
from .converters import EmojiConverter

class ButtonRoles(commands.Cog):
    """ Button Roles """
    def __init__(self, bot: Horus):
        self.bot = bot
        self._using_br = []
        self.bot.loop.create_task(self.initialize_button_roles())

        for command in self.walk_commands():
            command.cooldown_after_parsing = True
            
            if not command._buckets._cooldown:
                command._buckets = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)
    
    async def cog_before_invoke(self, ctx: commands.Context):
        if ctx.guild.id in self._using_br:
            raise commands.MaxConcurrencyReached(1, commands.BucketType.guild)
        else:
            self._using_br.append(ctx.guild.id)
    
    async def cog_after_invoke(self, ctx: commands.Context):
        self._using_br.remove(ctx.guild.id)

    async def initialize_button_roles(self):
        await self.bot.wait_until_ready()

        if self.bot._added_views is True:
            return
        
        self.bot.add_view(PersistentView(bot = self.bot), message_id = 886522591421034556)

        query = "SELECT * FROM buttonroles"
        allitems = await self.bot.db.fetch(query)

        for item in allitems:
            try:
                channel = await self.bot.fetch_channel(item["channelid"])
                message = await channel.fetch_message(item["messageid"])
            
            except:
                query = "DELETE FROM buttonroles WHERE guildid = $1 AND messageid = $2"
                await self.bot.db.execute(query, item["guildid"], item["messageid"])

            else:
                view = RolesView(bot = self.bot, guild = item["guildid"], role_emoji = item["role_emoji"], **item["config"])
                view.message = message

                self.bot.add_view(view, message_id = message.id)
        
        self.bot._added_views = True
    
    async def cog_check(self, ctx: commands.Context) -> bool:
        user = ctx.guild.get_member(ctx.author.id)
        return user.guild_permissions.administrator or await self.bot.is_owner(ctx.author)

    
    # Button Roles Group and Subcommands
    
    @commands.group(name = "buttonroles", aliases = ['br'], invoke_without_command = True, brief = "Button Roles")
    async def buttonroles(self, ctx: commands.Context):
        """ 
        Button Roles can now be used to let users take roles that they want.
        """
        await ctx.send_help(ctx.command)

    @commands.bot_has_permissions(add_reactions = True)
    @commands.cooldown(2, 60, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @buttonroles.command(name = "make", brief = "Make Button Roles")
    async def buttonroles_make(self, ctx: commands.Context, message: discord.Message = None):
        """
        An interactive command to make button roles!
        """
        query = "SELECT * FROM buttonroles WHERE guildid = $1"
        prev = await self.bot.db.fetch(query, ctx.guild.id)

        if message and [view for view in prev if view["messageid"] == message.id]:
            return await ctx.reply(content = f"This message already has a button roles menu. First delete it using `{ctx.clean_prefix}buttonroles delete` before trying again!")

        if len(prev) >= 10:
            return await ctx.reply(content = f'Currently Guilds are limited to a maximum of 10 button roles!\nYou can free up some space by deleting unnecessary button roles using `{ctx.clean_prefix}buttonroles delete`')

        if message is None:
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            
            await ctx.reply("Enter the channel to send the message in!")

            try:
                msg = await self.bot.wait_for(event = 'message', check = check, timeout = 60)
            except asyncio.TimeoutError:
                return await ctx.send(f"You took too long to respond!")
            
            try:
                channel = await commands.TextChannelConverter().convert(ctx, msg.content)
            except commands.ChannelNotFound:
                return await ctx.send(f"I could not find this channel!")

            await ctx.reply("Enter the message to send along with the button roles!")

            try:
                msg = await self.bot.wait_for(event = 'message', check = check, timeout = 60)
            except asyncio.TimeoutError:
                return await ctx.send(f"Can't send them a blank message dumbass {self.bot.get_em('kermitslap')}")
        
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            
            button_message = msg.content

        
        else:
            if message.guild != ctx.guild:
                return await ctx.send_help(ctx.command)

            if message.author.id != self.bot.user.id:
                return await ctx.send(f'I can add to buttons to messages sent by {self.bot.user.mention} only!')
        
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and (m.content.count(";") == 1 or m.content.lower() in ["done", "cancel"])
        
        await ctx.reply(f"Enter the emoji and role pairs in `emoji;role` format. I will react with {self.bot.get_em('tick')} if you've entered properly.\nEnter `done` when your done entering roles and `cancel` to stop.")
        role_emoji = {}
        start = time.perf_counter()

        while len(role_emoji) < 25:
            if time.perf_counter() - start > 900:
                return await ctx.reply(f'This session has timed out, You can start over by running `{ctx.clean_prefix}{ctx.command}` again!')

            try:
                msg = await self.bot.wait_for(event = 'message', check = check, timeout = 60)
            except asyncio.TimeoutError:
                return await ctx.send(f"You took too long to respond!")
            
            if msg.content.lower() == "cancel":
                return await ctx.send("Cancelled.")
            
            elif msg.content.lower() == "done":
                if len(role_emoji) >= 1:
                    break

                await ctx.send('You need to give me atleast one emoji role pair before entering `done`!')
                continue
        
            emoji, role = msg.content.split(';')

            try:
                emoji = await EmojiConverter().convert(ctx, emoji.strip())
                role = await commands.RoleConverter().convert(ctx, role.strip())
            except commands.EmojiNotFound or commands.RoleNotFound:
                await ctx.send(f"Incorrect Input! Please enter the emoji and role pair in `emoji;role` format.")
          
            else:
                if emoji in role_emoji.keys():
                    await ctx.send('This emoji was already used for another role!')

                elif role in role_emoji.values():
                    await ctx.send('This role was previously input!')

                elif role.managed or role.is_default() or role.is_bot_managed():
                    await ctx.send('This role is an integration and cannot be managed by me!')

                else:
                    role_emoji[f"{emoji}"] = [role.name, role.id]
                    await msg.add_reaction(self.bot.get_em('tick'))

        view = RolesView(bot = self.bot, guild = ctx.guild.id, role_emoji = role_emoji)

        if message is None:
            message = await channel.send(content = f"{button_message}", view = view)
            view.message = message

            if channel.id != ctx.channel.id:
                link = discord.ui.View()
                link.add_item(discord.ui.Button(style = discord.ButtonStyle.link, label = "Message Link", emoji = "\U0001f517", url = message.jump_url))
                await ctx.send("I've sent the message with the button roles menu successfully!", view = link)
        
        else:
            try:
                view.message = message
                await message.edit(view = view)

            except:
                return await ctx.reply('I was unable to edit the given message, maybe it was deleted?')
            
            else:
                link = discord.ui.View()
                link.add_item(discord.ui.Button(style = discord.ButtonStyle.link, label = "Message Link", emoji = "\U0001f517", url = message.jump_url))
                await ctx.send("I've added a button roles menu to the message successfully!", view = link)
        
        message = view.message

        query = "INSERT INTO buttonroles(guildid, messageid, channelid, role_emoji) VALUES($1, $2, $3, $4) ON CONFLICT (messageid) DO  NOTHING"
        await self.bot.db.execute(query, message.guild.id, message.id, message.channel.id, role_emoji)

        await ctx.try_add_reaction(self.bot.get_em('tick'))


    @commands.max_concurrency(1, commands.BucketType.guild)
    @buttonroles.command(name = "delete", brief = "Delete Button Roles")
    async def buttonroles_delete(self, ctx: commands.Context, message: discord.Message):
        """
        You can delete old, unnecessary button roles menus by using this command.
        Use message links incease message id doesn't work!
        """
        query = "SELECT * FROM buttonroles WHERE guildid = $1 AND messageid = $2"
        item = await self.bot.db.fetchval(query, message.guild.id, message.id)

        if not item:
            return await ctx.send(content = f'I could not find a buttonroles menu with message ID: `{message.id}`')

        query = "DELETE FROM buttonroles WHERE guildid = $1 AND messageid = $2"
        await self.bot.db.execute(query, message.guild.id, message.id)

        for item in self.bot.persistent_views:
            if isinstance(item, RolesView) and item.message.id == message.id:
                await item.stop_button()

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, label = "Message Link", emoji = "\U0001f517", url = message.jump_url))

        await ctx.send('I have removed the button roles menu from that message!', view = view)

    @buttonroles.command(name = "list", brief = "List Server Button Roles")
    async def buttonroles_list(self, ctx: commands.Context):
        """ Get a list of all current server button roles """
        prev = [view for view in self.bot.persistent_views if isinstance(view, RolesView)]

        if not prev:
            return await ctx.send('This server does not have any button roles!')
        
        embed = discord.Embed(title = "Server Button Roles List", description = "\n".join([f"**{index+1})** [{view.message.id}]({view.message.jump_url})" for index, view in enumerate(prev)]), colour = self.bot.colour)
        embed.set_footer(text = ctx.guild.name, icon_url = ctx.guild._icon or discord.Embed.Empty)
        await ctx.send(embed = embed)
    
    @commands.cooldown(5, 300, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @buttonroles.command(name = "refresh", brief = "Refresh button menus")
    async def buttonroles_refresh(self, ctx: commands.Context, message: discord.Message = None):
        """
        Can be used to refresh your server's button roles incase 
        any of them are out of sync or erroring.

        This command can only be used once per guild 
        and 5 times every 5 minutes so don't use this
        unless necessary
        """

        if message is not None:
            if message.guild != ctx.guild:
                return await ctx.send_help(ctx.command)

            if message.author.id != self.bot.user.id:
                return await ctx.send(f'This message does not contain a buttons menu!')
            
            query = "SELECT * FROM buttonroles WHERE guildid = $1 AND messageid = $2"
            allitems = await self.bot.db.fetch(query, ctx.guild.id, message.id)

            if allitems is []:
                return await ctx.send(f'I could not find a buttonroles menu with message ID: `{message.id}`')
        
        else:
            query = "SELECT * FROM buttonroles WHERE guildid = $1"
            allitems = await self.bot.db.fetch(query, ctx.guild.id)

            if allitems is []:
                return await ctx.send('This server does not have any button roles!')

        start = time.perf_counter()
        notif = await ctx.send(f'Refreshing {self.bot.get_em("loading")}')

        for item in allitems:
            for view in self.bot.persistent_views:
                if isinstance(view, RolesView) and view.message.id == item["messageid"]:

                    newview = RolesView(bot = self.bot, guild = item["guildid"], role_emoji = item["role_emoji"], **item["config"])
                    newview.message = view.message

                    try:
                        await view.refresh_view(view = newview) # remove view from persistent views
            
                    except:
                        query = "DELETE FROM buttonroles WHERE guildid = $1 AND messageid = $2"
                        await self.bot.db.execute(query, item["guildid"], item["messageid"])
        
        end = time.perf_counter()

        await notif.edit(content = f'Finished refreshing **{len(allitems)}** view{"s" if len(allitems) != 1 else ""} in `{round(end - start, 2)}s`')

    @buttonroles.command(name = "block", brief = "Block a role from Button role")
    async def buttonroles_block(self, ctx: commands.Context, role: discord.Role, message: discord.Message):
        """ 
        Block a certain role from using a Button Role Menu
        """
        if message.guild != ctx.guild:
            return await ctx.send_help(ctx.command)

        if message.author.id != self.bot.user.id:
            return await ctx.send(f'I could not find a buttonroles menu with message ID: `{message.id}`')
        
        query = "SELECT * FROM buttonroles WHERE guildid = $1 AND messageid = $2"
        item = await self.bot.db.fetchrow(query, message.guild.id, message.id)

        if not item:
            return await ctx.send(content = f'I could not find a buttonroles menu with message ID: `{message.id}`')
        
        if not item["config"].get("blacklists"):
            item["config"]["blacklists"] = []
        
        if role.id in item["config"]["blacklists"]:
            return await ctx.send(content = "This role is already blacklisted from this button roles!")
        
        item["config"]["blacklists"].append(role.id)
        query = "UPDATE buttonroles SET config = $1 WHERE guildid = $2 AND messageid = $3"
        await self.bot.db.execute(query, item["config"], message.guild.id, message.id)

        for view in self.bot.persistent_views:
            if isinstance(view, RolesView) and view.message.id == message.id:
                view.update_config(blacklists = item["config"]["blacklists"])
                break

        await ctx.send(f'I have blocked {role.mention} from using this button roles.', allowed_mentions = discord.AllowedMentions(roles = False))
    
    @buttonroles.command(name = "unblock", brief = "Unblock a blacklisted role")
    async def buttonroles_unblock(self, ctx: commands.Context, role: discord.Role, message: discord.Message):
        """ 
        Unblock a role previously blacklisted from using a Button Role Menu
        """
        if message.guild != ctx.guild:
            return await ctx.send_help(ctx.command)

        if message.author.id != self.bot.user.id:
            return await ctx.send(f'I could not find a buttonroles menu with message ID: `{message.id}`')
        
        query = "SELECT * FROM buttonroles WHERE guildid = $1 AND messageid = $2"
        item = await self.bot.db.fetchrow(query, message.guild.id, message.id)

        if not item:
            return await ctx.send(f'I could not find a buttonroles menu with message ID: `{message.id}`')
        
        if not item["config"].get("blacklists"):
            return await ctx.send('This role was not previously blacklisted!')
        
        if role.id not in item["config"]["blacklists"]:
            return await ctx.send('This role was not previously blacklisted!')

        item["config"]["blacklists"].remove(role.id)
        query = "UPDATE buttonroles SET config = $1 WHERE guildid = $2 AND messageid = $3"
        await self.bot.db.execute(query, item["config"], message.guild.id, message.id)

        for view in self.bot.persistent_views:
            print(view, isinstance(view, RolesView))
            if isinstance(view, RolesView) and view.message.id == message.id:
                view.update_config(blacklists = item["config"]["blacklists"])
                break

        await ctx.send(f'I have unblocked {role.mention} from using the button roles menu.', allowed_mentions = discord.AllowedMentions(roles = False))