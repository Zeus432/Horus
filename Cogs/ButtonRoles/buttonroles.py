from tkinter.messagebox import NO
from bot import Horus
import disnake as discord
from disnake.ext import commands

import asyncio
import time

class ButtonRoles(commands.Cog):
    """ Button Roles """

    def __init__(self, bot: Horus):
        self.bot = bot
    
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
                break
        
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

                elif not (role.managed or role.is_default or role.is_bot_managed()):
                    await ctx.send('This role is an integration and cannot be manage by me!')

                else:
                    role_emoji[emoji] = role.id
                    await msg.add_reaction(self.bot.get_em('tick'))
        
        await ctx.send(f"{role_emoji}")