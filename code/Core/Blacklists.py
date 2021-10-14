import discord
from discord.ext import commands

import asyncio
import datetime

from Utils.Useful import *
from Utils.Menus import *

class Blacklists(commands.Cog, name = "Blacklists"):
    """ Blacklist people and don't unblacklist them?  """

    def __init__(self, bot):
        self.bot = bot
        self._mc = commands.MaxConcurrency(1, per=commands.BucketType.user, wait = False)
        self.blchannel = self.bot.get_channel(898259956745252864)
    
    @BotModOnly()
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command(name = "blacklist", aliases = ["bl"], brief = "Blacklist user", help = "Blacklist a user from using the bot permanantly <a:amiruspandawalkaway:741544957067919370>\nThat is until someone unblacklists them")
    async def blacklist(self, ctx, user: discord.User, *, reason: str = None):
        try:
            data = self.bot.blacklists[user.id]
            if not data:
                raise KeyError
        except KeyError:
            data = await self.bot.db.fetchval('SELECT blacklists FROM userdata WHERE userid = $1', user.id)
            if not data:
                blacklists = {'prevbl': {}, 'blacklisted': False}
                data = await self.bot.db.fetchval('INSERT INTO userdata(userid, blacklists) VALUES($1, $2) ON CONFLICT (userid) DO UPDATE SET blacklists = $2 RETURNING blacklists', user.id, blacklists)
                self.bot.blacklists[user.id] = data
        if data["blacklisted"]:
            self.bot.blacklists[user.id] = data
            return await ctx.reply('This user is already blacklisted!', mention_author = False)
        if user.id in BotMods or await ctx.bot.is_owner(user):
            return await ctx.reply("This user is whitelisted!")
        if not reason:
            message = await ctx.reply('Enter a reason for blacklist!')
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            try:
                reason = await self.bot.wait_for(event='message', check=check, timeout=30)
                reason = reason.content
            except asyncio.TimeoutError:
                return await message.reply("Response Timed Out!")
    
        view = ConfirmBl(ctx.author, f'{user.mention} was blacklisted\n**Reason:** {reason}', "Alright not gonna Blacklist this one *yet*")
        view.message = await ctx.reply(f"Are you sure you want to blacklist {user.mention}?", view = view, allowed_mentions = discord.AllowedMentions.none())

        await view.wait()
        if not view.value:
            return
        timestamp = int(datetime.datetime.now().timestamp())
        data["blacklisted"] = {"reason": f"{reason}", "mod": ctx.author.id, "timestamp": timestamp}
        self.bot.blacklists[user.id] = data
        await self.bot.db.execute('INSERT INTO userdata(userid, blacklists) VALUES($1, $2) ON CONFLICT (userid) DO UPDATE SET blacklists = $2',user.id, data)
        embed = discord.Embed(description = f"**User:** {user} (`{user.id}`)\n**Reason:** {reason}\n\nUser was blacklisted <t:{timestamp}> (<t:{timestamp}:R>)", colour = self.bot.colour)
        embed.set_author(name = "User Blacklisted", icon_url = user.avatar or user.default_avatar)
        embed.set_footer(text = f"By: {ctx.author} ({ctx.author.id})", icon_url = ctx.author.avatar or ctx.author.default_avatar)
        await self.blchannel.send(embed = embed)

    
    @BotModOnly()
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command(name = "unblacklist", aliases = ["unbl"], brief = "Unblacklist user", help = "Unblacklist a previously blacklisted user <:worryfrog:898211511858790430>")
    async def unblacklist(self, ctx, user: discord.User, *, reason: str = None):
        try:
            data = self.bot.blacklists[user.id]
        except KeyError:
            data = await self.bot.db.fetchval('SELECT blacklists FROM userdata WHERE userid = $1', user.id)
            if not data:
                blacklists = {'prevbl': {}, 'blacklisted': False}
                data = await self.bot.db.fetchval('INSERT INTO userdata(userid, blacklists) VALUES($1, $2) ON CONFLICT (userid) DO UPDATE SET blacklists = $2 RETURNING blacklists', user.id, blacklists)
                self.bot.blacklists[user.id] = data
        if not data["blacklisted"]:
            self.bot.blacklists[user.id] = data
            return await ctx.reply('This is not a previously blacklisted user!', mention_author = False)
        if not reason:
            message = await ctx.reply('Enter a reason for blacklist!')
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            try:
                reason = await self.bot.wait_for(event='message', check=check, timeout=300)
                reason = reason.content
            except asyncio.TimeoutError:
                return await message.reply("Response Timed Out!")

        await ctx.reply(f'{user.mention} was unblacklisted\n**Reason:** {reason}', allowed_mentions = discord.AllowedMentions.none())
        timestamp = int(datetime.datetime.now().timestamp())
        data["prevbl"][len(data["prevbl"])+ 1] = {"ban":{"reason":data["blacklisted"]["reason"], "mod": data["blacklisted"]["mod"],"timestamp":data["blacklisted"]["timestamp"]},"unban":{"reason": f"{reason}", "mod": ctx.author.id, "timestamp": timestamp}}
        data["blacklisted"] = False
        self.bot.blacklists[ctx.author.id] = data
        await self.bot.db.execute('UPDATE userdata SET blacklists = $2 WHERE userid = $1',user.id, data)
        embed = discord.Embed(description = f"**User:** {user} (`{user.id}`)\n**Reason:** {reason}\n\nUser was unblacklisted <t:{timestamp}> (<t:{timestamp}:R>)", colour = self.bot.colour)
        embed.set_author(name = "User Unblacklisted", icon_url = user.avatar or user.default_avatar)
        embed.set_footer(text = f"By: {ctx.author} ({ctx.author.id})", icon_url = ctx.author.avatar or ctx.author.default_avatar)
        await self.blchannel.send(embed = embed)

def setup(bot):
    bot.add_cog(Blacklists(bot))