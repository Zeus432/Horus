from tkinter.messagebox import NO
from bot import Horus
import disnake as discord
from disnake.ext import commands

import asyncio
import time

from .views import RolesView

class ButtonRoles(commands.Cog):
    """ Button Roles """

    def __init__(self, bot: Horus):
        self.bot = bot
        self.bot.loop.create_task(self.initialize())
    
    async def initialize(self):
        await self.bot.wait_until_ready()

        query = "SELECT * FROM buttonroles"
        allitems = await self.bot.db.fetch(query)

        for item in allitems:
            try:
                channel = await self.bot.fetch_channel(item["channelid"])
                await channel.fetch_message(item["messageid"])
            
            except:
                query = "DELETE FROM buttonroles WHERE guildid = $1 AND messageid = $2"
                await self.bot.db.execute(query, item["guildid"], item["messageid"])

            else:
                view = RolesView(bot = self.bot, guild = item["guildid"], role_emoji = item["role_emoji"], blacklists = item["blacklists"])
                self.bot.add_view(view, message_id = item["messageid"])

    async def cog_check(self, ctx: commands.Context):
        result = await self.bot.is_owner(ctx.author)
        if result:
            return True
        raise commands.NotOwner()

    @commands.group(name = "buttonroles", aliases = ['br'], invoke_without_command = True)
    async def buttonroles(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)
    
    @buttonroles.command(name = "make")
    @commands.bot_has_permissions(add_reactions = True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def buttonroles_make(self, ctx: commands.Context, message: discord.Message = None):
        query = "SELECT * FROM buttonroles WHERE guildid = $1"
        prev = await self.bot.db.fetch(query, ctx.guild.id)

        if len(prev) > 9:
            return await ctx.reply(f'Currently Guilds are limited to a maximum of 10 button roles!\nYou can free up some space by deleting unnecessary button roles using `{ctx.clean_prefix}buttonroles delete`')

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
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and (m.content.count(";") == 1 or m.content.lower() == "done")
        
        await ctx.reply(f"Enter the emoji and role pairs in `emoji;role` format.\nI will react with {self.bot.get_em('tick')} if you've entered properly.\nEnter `done` when your done entering roles.")
        role_emoji = {}
        start = time.perf_counter()

        while len(role_emoji) < 25:
            if time.perf_counter() - start > 900:
                return await ctx.reply(f'This session has timed out, You can start over by running `{ctx.clean_prefix}{ctx.command}` again!')

            try:
                msg = await self.bot.wait_for(event = 'message', check = check, timeout = 60)
            except asyncio.TimeoutError:
                return await ctx.send(f"You took too long to respond!")
            
            if msg.content.lower() == "done":
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
        
        else:
            try:
                view.message = message
                await message.edit(view = view)
            except:
                return await ctx.reply('I was unable to edit the given message, maybe it was deleted?')
        
        message = view.message
        self.bot.add_view(view, message_id = message.id)

        query = "INSERT INTO buttonroles(guildid, messageid, channelid, role_emoji) VALUES($1, $2, $3, $4) ON CONFLICT (messageid) DO NOTHING"
        await self.bot.db.execute(query, message.guild.id, message.id, message.channel.id, role_emoji)

        await ctx.try_add_reaction(self.bot.get_em('tick'))

    @buttonroles.command(name = "delete")
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def buttonroles_delete(self, ctx: commands.Context, message: discord.Message):
        query = "SELECT * FROM buttonroles WHERE guildid = $1 AND messageid = $2"
        item = await self.bot.db.fetchval(query, message.guild.id, message.id)

        if not item:
            return await ctx.send(content = f'I could not find a buttonroles menu with message ID: `{message.id}`')
        
        try:
            msg = await message.channel.fetch_message(message.id)
            await msg.edit(view = None)
        except:
            pass

        query = "DELETE FROM buttonroles WHERE guildid = $1 AND messageid = $2"
        await self.bot.db.execute(query, message.guild.id, message.id)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, label = "Message Link", emoji = "\U0001f517", url = message.jump_url))

        await ctx.send('I have removed the button roles menu from that message!', view = view)