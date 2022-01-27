from tkinter.messagebox import NO
import disnake as discord
from bot import Horus
from disnake.ext import commands

from typing import Union
import asyncio
import time

from Core.Blacklists.menus import ConfirmBl
from Core.Utils.woodlands import PersistentView
from Core.Utils.pagination import Pagination
from .useful import BlType
from .views import RolesView

class Admin(commands.Cog):
    """ Server Management """
    def __init__(self, bot: Horus):
        self.bot = bot
        self._using_br = []
        self.bot.loop.create_task(self.initialize_button_roles())
    
    async def cog_before_invoke(self, ctx: commands.Context):
        if ctx.command.full_parent_name.startswith('buttonroles'):
            if ctx.guild.id in self._using_br:
                raise commands.MaxConcurrencyReached(1, commands.BucketType.guild)
            else:
                self._using_br.append(ctx.guild.id)
    
    async def cog_after_invoke(self, ctx: commands.Context):
        self._using_br.remove(ctx.guild.id)

    async def initialize_button_roles(self):
        await self.bot.wait_until_ready()

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
    
    async def cog_check(self, ctx: commands.Context) -> bool:
        user = ctx.guild.get_member(ctx.author.id)
        return user.guild_permissions.administrator or await self.bot.is_owner(ctx.author)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name = "setprefix", brief = "Set Server prefix")
    async def setprefix(self, ctx: commands.Context, prefix: str):
        """
        Set a custom prefix for your server.
        User requires Administrator permissions in the guild to use this command
        """
        self.bot.prefix_cache[ctx.guild.id] = [f"{prefix}"]
        await self.bot.db.execute('UPDATE guilddata SET prefix = $2 WHERE guildid = $1', ctx.guild.id, self.bot.prefix_cache[ctx.guild.id])
        await ctx.send(f'Prefix changed to: `{prefix}`')
    
    @commands.group(name = "server", brief = "Server Blacklist and Management Commands", invoke_without_command = True)
    async def server(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @server.command(name = "blacklist", aliases = ['bl'], brief = "Blacklist a Channel, User or Role")
    async def serverblacklist(self, ctx: commands.Context, what: Union[discord.TextChannel, discord.Role, discord.Member]):
        """ Blacklist a Channel, Role or User from using the bot in your server """
        what_type = "channel" if isinstance(what, discord.TextChannel) else "role" if isinstance(what, discord.Role) else "user"

        try:
            blacklist = self.bot.server_blacklists[ctx.guild.id]
        except KeyError:
            blacklist = await self.bot.db.fetchval("SELECT server_bls FROM guilddata WHERE guildid = $1", ctx.guild.id)
            self.bot.server_blacklists[ctx.guild.id] = {} if blacklist is None else blacklist
        
        if what_type not in blacklist:
            blacklist[what_type] = []

        if what.id in blacklist[what_type]:
            return await ctx.reply(f'`{what}` is already server blacklisted!')
        
        if what.id == ctx.guild.id:
            await ctx.send_help(ctx.command)

        view = ConfirmBl(what = f"{what}", action = "server blacklist", user = ctx.author)
        view.message = await ctx.reply(f"Are you sure you want to server blacklist: `{what}`?", view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False))
        await view.wait()

        if view.value is True:
            if what.id in blacklist[what_type]:
                return

            blacklist[what_type].append(what.id)
            self.bot.server_blacklists[ctx.guild.id] = blacklist

            if not blacklist:
                await self.bot.db.execute('INSERT INTO guilddata(guildid, server_bls) VALUES($1, $2) ON CONFLICT (guildid) DO NOTHING RETURNING server_bls', ctx.guild.id, blacklist)
            
            else:
                query = f'UPDATE guilddata SET server_bls = $2 WHERE guildid = $1'
                await self.bot.db.execute(query, ctx.guild.id, blacklist)

    @server.command(name = "unblacklist", aliases = ['unbl'], brief = "Unblacklist a Channel, User or Role")
    async def unserverblacklist(self, ctx: commands.Context, what: Union[discord.TextChannel, discord.Role, discord.User, int]):
        """ Unblacklist a Channel, Role or User from using the bot in your server """
        what_type = "channel" if isinstance(what, discord.TextChannel) else "role" if isinstance(what, discord.Role) else "user"

        if not isinstance(what, int):
            what_id = what.id
        else:
            what_id = what

        try:
            blacklist = self.bot.server_blacklists[ctx.guild.id]
        except KeyError:
            blacklist = await self.bot.db.fetchval("SELECT server_bls FROM guilddata WHERE guildid = $1", ctx.guild.id)
            self.bot.server_blacklists[ctx.guild.id] = {} if blacklist else blacklist
        
        if what_type not in blacklist:
            blacklist[what_type] = []

        if what_id not in blacklist[what_type]:
            return await ctx.reply(f'`{what}` is not server blacklisted!')
        
        if what_id == ctx.guild.id:
            await ctx.send_help(ctx.command)
        
        view = ConfirmBl(what = f"{what}", action = "server unblacklist", user = ctx.author)
        view.message = await ctx.reply(f"Are you sure you want to server unblacklist: `{what}`?", view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False))
        await view.wait()
        
        if view.value is True:
            if what_id not in blacklist[what_type]:
                return

            if not blacklist:
                self.bot.server_blacklists[ctx.guild.id] = await self.bot.db.execute('INSERT INTO guilddata(guildid, server_bls) VALUES($1, $2) ON CONFLICT (guildid) UPDATE SET server_bls = $2 RETURNING server_bls', ctx.guild.id, blacklist)
            
            else:
                blacklist[what_type].remove(what_id)
                self.bot.server_blacklists[ctx.guild.id] = blacklist
                query = f'UPDATE guilddata SET server_bls = $2 WHERE guildid = $1'
                await self.bot.db.execute(query, ctx.guild.id, blacklist)

    @server.command(name = "showblacklists", aliases = ["showbls"], brief = "Show a list of blacklisted users, channels and roles")
    async def showblacklists(self, ctx: commands.Context, category: BlType):
        """
        You can filter your bl list by specifying a category:
        `-` user
        `-` role
        `-` channel
        """
        if not category:
            return await ctx.send('Mention a specific type to view!')
        
        query = f"SELECT server_bls -> '{category}' FROM guilddata WHERE guildid = $1"
        items = await self.bot.db.fetchval(query, ctx.guild.id)

        if ctx.guild.id not in self.bot.server_blacklists:
            self.bot.server_blacklists[ctx.guild.id] = {}
        
        self.bot.server_blacklists[ctx.guild.id][category] = items

        if not items:
            return await ctx.send(f'No {category} has been blacklisted in this server!')

        start = "<@!" if category == "user" else "<#" if category == "channel" else "<@&"
        total = (len(items) // 20) + 1
        embeds = []
        page = 0
        
        while items:
            embed = discord.Embed(description = "\n".join([f'**{(page*20) + index + 1})** {start}{item}> (`{item}`)' for index, item in enumerate(items[:20])]), colour = self.bot.colour)
            embed.set_author(name = f"Server Blacklisted {category.capitalize()}s", icon_url = f"{ctx.guild.icon}")
            embed.set_footer(text = f"Page {page + 1}/{total}")

            embeds.append(embed)
            items = items[20:]
            page += 1
        
        view = Pagination(embeds =  embeds, user = ctx.author, bot = self.bot)

        view.message = await ctx.reply(embed = embeds[0], view = view, mention_author = False)
        await view.wait()

    @server.command(name = "checkblacklist", aliases = ["checkbl"], brief = "Check if an user, channel or role")
    async def checkblacklist(self, ctx: commands.Context, what: Union[discord.TextChannel, discord.Role, discord.User, int]):
        """
        Check if a user, channel or role is blacklisted.
        Accepts id too if it is deleted
        """
        if not isinstance(what, int):
            what = what.id

        query = f"SELECT server_bls FROM guilddata WHERE guildid = $1"
        items = await self.bot.db.fetchval(query, ctx.guild.id)

        for type, item in items.values():
            if what in item:
                return await ctx.reply(f'This {item} is server blacklisted!', mention_author = False)
        
        await ctx.send(f'`{what}` doesn\'t seem to be on the server blacklist!', mention_author = False)
    
    @commands.group(name = "buttonroles", aliases = ['br'], invoke_without_command = True, brief = "Button Roles")
    async def buttonroles(self, ctx: commands.Context):
        """ 
        Button Roles can now be used to let users take roles that they want.
        """
        await ctx.send_help(ctx.command)
    
    @buttonroles.command(name = "make", brief = "Make Button Roles")
    @commands.bot_has_permissions(add_reactions = True)
    async def buttonroles_make(self, ctx: commands.Context, message: discord.Message = None):
        """
        An interactive command to make button roles!
        """
        query = "SELECT * FROM buttonroles WHERE guildid = $1"
        prev = await self.bot.db.fetch(query, ctx.guild.id)

        if [view for view in prev if view["messageid"] == message.id]:
            return await ctx.reply(content = f"This message already has a button roles menu. First delete it using `{ctx.clean_prefix}buttonroles delete` before trying again!")

        if len(prev) > 9:
            return await ctx.reply(content = f'Currently Guilds are limited to a maximum of 10 button roles!\nYou can free up some space by deleting unnecessary button roles using `{ctx.clean_prefix}buttonroles delete`')

        if message is None:
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

            await ctx.reply("Enter the message to send along with the button roles!")

            try:
                msg = await self.bot.wait_for(event = 'message', check = check, timeout = 60)
            except asyncio.TimeoutError:
                return await ctx.send(f"Can't send them a blank message dumbass {self.bot.get_em('kermitslap')}")
        
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            
            button_message = msg.content
        
            await ctx.reply("Enter the channel to send the message in!")

            try:
                msg = await self.bot.wait_for(event = 'message', check = check, timeout = 60)
            except asyncio.TimeoutError:
                return await ctx.send(f"You took too long to respond!")
            
            try:
                channel = await commands.TextChannelConverter().convert(ctx, msg.content)
            except commands.ChannelNotFound:
                return await ctx.send(f"I could not find this channel!")
        
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
                emoji = await commands.EmojiConverter().convert(ctx, emoji)
                role = await commands.RoleConverter().convert(ctx, role)
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
                    role_emoji[f"{emoji}"] = role.id
                    await msg.add_reaction(self.bot.get_em('tick'))

        view = RolesView(bot = self.bot, guild = ctx.guild.id, role_emoji = role_emoji)

        if message is None:
            view.message = await channel.send(content = f"{button_message}", view = view)

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
        
        try:
            msg = await message.channel.fetch_message(message.id)
            await msg.edit(view = None)
        except: pass

        query = "DELETE FROM buttonroles WHERE guildid = $1 AND messageid = $2"
        await self.bot.db.execute(query, message.guild.id, message.id)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, label = "Message Link", emoji = "\U0001f517", url = message.jump_url))

        await ctx.send('I have removed the button roles menu from that message!', view = view)
    
    @buttonroles.command(name = "block", brief = "Block a role from Button role")
    @commands.is_owner()
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
        
        item["config"]["blacklists"].append(role.id)
        query = "UPDATE buttonroles SET config = $1 WHERE guildid = $2 AND messageid = $3"
        await self.bot.db.execute(query, item["config"], message.guild.id, message.id)

        await ctx.send(f'I have blocked {role.mention} from using the button roles menu.', allowed_mentions = discord.AllowedMentions(roles = False))
    
    @buttonroles.command(name = "unblock", brief = "Unblock a blacklisted role")
    @commands.is_owner()
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
            return await ctx.send(content = f'I could not find a buttonroles menu with message ID: `{message.id}`')
        
        if not item["config"].get("blacklists"):
            return await ctx.send('This role was not previously blacklisted!')
        
        if role.id not in item["config"]["blacklists"]:
            return await ctx.send('This role was not previously blacklisted!')

        item["config"]["blacklists"].remove(role.id)
        query = "UPDATE buttonroles SET config = $1 WHERE guildid = $2 AND messageid = $3"
        await self.bot.db.execute(query, item["config"], message.guild.id, message.id)

        await ctx.send(f'I have unblocked {role.mention} from using the button roles menu.', allowed_mentions = discord.AllowedMentions(roles = False))
    
    @buttonroles.command(name = "refresh", brief = "Refresh button menus")
    @commands.is_owner()
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def buttonroles_unblock(self, ctx: commands.Context, message: discord.Message = None):
        if message is not None:
            if message.guild != ctx.guild:
                return await ctx.send_help(ctx.command)

            if message.author.id != self.bot.user.id:
                return await ctx.send(f'This message does not contain a buttons menu!')
        
        else:
            query = "SELECT * FROM buttonroles WHERE guildid = $1"
            allitems = await self.bot.db.fetchrow(query, ctx.guild.id)
            
        
        for perview in self.bot.persistent_views:
            if isinstance(perview, RolesView) and perview.message.id == message.id:
                perview.stop() # remove view from persistent views
        
        print(self.bot.persistent_views)
        #self.bot.add_view(view, message_id = message.id)
        print(self.bot.persistent_views)