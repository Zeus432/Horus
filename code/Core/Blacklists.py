import discord
from discord.ext import commands

import asyncio
import datetime

from Utils.Useful import *
from Core.settings import *
from Utils.Menus import *

class Blacklists(commands.Cog, name = "Blacklists"):
    """ Blacklist people and don't unblacklist them?  """

    def __init__(self, bot):
        self.bot = bot
        self._mc = commands.MaxConcurrency(1, per=commands.BucketType.user, wait = False)
    
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
                blacklists = {'prevbl': 0, 'blacklisted': False}
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
        await self.bot.get_channel(898259956745252864).send(embed = embed)
        try:
            await user.send(f"You were blacklisted from the bot  by a Bot Moderator: {ctx.author.mention}\nIf this is a mistake you can appeal your ban in the support server: https://discord.gg/8BQMHAbJWk")
        except:
            await view.message.edit(f"{user.mention} was blacklisted\n**Reason:** {reason}\n\nI was unable to dm this user about their blacklist! Maybe you could?", allowed_mentions = discord.AllowedMentions.none())

    
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
            message = await ctx.reply('Enter a reason for unblacklist!')
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            try:
                reason = await self.bot.wait_for(event='message', check=check, timeout=300)
                reason = reason.content
            except asyncio.TimeoutError:
                return await message.reply("Response Timed Out!")

        message = await ctx.reply(f'{user.mention} was unblacklisted\n**Reason:** {reason}', allowed_mentions = discord.AllowedMentions.none())
        timestamp = int(datetime.datetime.now().timestamp())
        data["prevbl"] += 1
        data["blacklisted"] = False
        self.bot.blacklists[user.id] = data
        await self.bot.db.execute('UPDATE userdata SET blacklists = $2 WHERE userid = $1',user.id, data)
        embed = discord.Embed(description = f"**User:** {user} (`{user.id}`)\n**Reason:** {reason}\n\nUser was unblacklisted <t:{timestamp}> (<t:{timestamp}:R>)", colour = self.bot.colour)
        embed.set_author(name = "User Unblacklisted", icon_url = user.avatar or user.default_avatar)
        embed.set_footer(text = f"By: {ctx.author} ({ctx.author.id})", icon_url = ctx.author.avatar or ctx.author.default_avatar)
        await self.bot.get_channel(898259956745252864).send(embed = embed)
        try:
            await user.send(f"You were unblacklisted from the bot by a Bot Moderator: {ctx.author.mention}")
        except:
            await message.edit(f'{user.mention} was unblacklisted\n**Reason:** {reason}\n\nI was unable to dm this user about their unblacklist! Maybe you could?', allowed_mentions = discord.AllowedMentions.none())
        
    @BotModOnly()
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command(name = "serverblacklist", aliases = ["serverbl"], brief = "Blacklist server", help = "Blacklist a server from being able to add the bot and use it <a:amiruspandawalkaway:741544957067919370>\nThat is until someone unblacklists it")
    async def serverblacklist(self, ctx, guild: discord.Guild, *, reason: str = None):
        try:
            data = self.bot.blacklists[guild.id]
        except KeyError:
            data = await self.bot.db.fetchval('SELECT blacklists FROM guilddata WHERE guildid = $1', guild.id)
            if not data:
                blacklists = {'prevbl': 0, 'blacklisted': False}
                data = await self.bot.db.fetchval('INSERT INTO guilddata(guildid, blacklists) VALUES($1, $2) ON CONFLICT (guildid) DO UPDATE SET blacklists = $2 RETURNING blacklists', guild.id, blacklists)
                self.bot.blacklists[guild.id] = data
        if data["blacklisted"]:
            self.bot.blacklists[guild.id] = data
            return await ctx.reply('This server is already blacklisted!', mention_author = False)
        if guild.id in WhiteListedServers:
            return await ctx.reply("This server is whitelisted!")
        if not reason:
            message = await ctx.reply('Enter a reason for blacklist!')
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            try:
                reason = await self.bot.wait_for(event='message', check=check, timeout=30)
                reason = reason.content
            except asyncio.TimeoutError:
                return await message.reply("Response Timed Out!")
    
        view = ConfirmBl(ctx.author, f'**{guild}** was blacklisted\n**Reason:** {reason}', "Alright not gonna Blacklist this server *yet*")
        view.message = await ctx.reply(f"Are you sure you want to blacklist **{ctx.guild}**?\n**Note:** This will also make me leave the server", view = view, allowed_mentions = discord.AllowedMentions.none())
        
        await view.wait()
        if not view.value:
            return
        timestamp = int(datetime.datetime.now().timestamp())
        data["blacklisted"] = {"reason": f"{reason}", "mod": ctx.author.id, "timestamp": timestamp}
        self.bot.blacklists[guild.id] = data
        await self.bot.db.execute('INSERT INTO guilddata(guildid, blacklists) VALUES($1, $2) ON CONFLICT (guildid) DO UPDATE SET blacklists = $2',guild.id, data)
        embed = discord.Embed(description = f"**Server:** {guild} (`{guild.id}`)\n**Reason:** {reason}\n\nServer was blacklisted <t:{timestamp}> (<t:{timestamp}:R>)", colour = self.bot.colour)
        embed.set_author(name = "Server Blacklisted", icon_url = guild.icon or discord.Embed.Empty)
        embed.set_footer(text = f"By: {ctx.author} ({ctx.author.id})", icon_url = ctx.author.avatar or ctx.author.default_avatar)
        await self.bot.get_channel(898259956745252864).send(embed = embed)
        try:
            await guild.owner.send(f"Your server (**{guild}**) was blacklisted from the bot by a Bot Moderator: {ctx.author.mention}\nIf this is a mistake you can appeal your ban in the support server: https://discord.gg/8BQMHAbJWk")
        except:
            await view.message.edit(f"**{guild}** was blacklisted\n**Reason:** {reason}\n\nI was unable to dm the owner ({guild.owner.mention}) about their server's blacklist! Maybe you could?", allowed_mentions = discord.AllowedMentions.none())
        await guild.leave()

    
    @BotModOnly()
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command(name = "unserverblacklist", aliases = ["unserverbl"], brief = "Unblacklist server", help = "Unblacklist a previously blacklisted server")
    async def unserverblacklist(self, ctx, guild: discord.Guild, *, reason: str = None):
        try:
            data = self.bot.blacklists[guild.id]
        except KeyError:
            data = await self.bot.db.fetchval('SELECT blacklists FROM guilddata WHERE guildid = $1', guild.id)
            if not data:
                blacklists = {'prevbl': 0, 'blacklisted': False}
                data = await self.bot.db.fetchval('INSERT INTO guilddata(guildid, blacklists) VALUES($1, $2) ON CONFLICT (guildid) DO UPDATE SET blacklists = $2 RETURNING blacklists', guild.id, blacklists)
                self.bot.blacklists[guild.id] = data
        if not data["blacklisted"]:
            self.bot.blacklists[guild.id] = data
            return await ctx.reply('This is not a previously blacklisted server!', mention_author = False)
        
        if not reason:
            message = await ctx.reply('Enter a reason for blacklist!')
            def check(m: discord.Message):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
            try:
                reason = await self.bot.wait_for(event='message', check=check, timeout=30)
                reason = reason.content
            except asyncio.TimeoutError:
                return await message.reply("Response Timed Out!")

        message = await ctx.reply(f'**{guild}** was unblacklisted\n**Reason:** {reason}', allowed_mentions = discord.AllowedMentions.none())
        timestamp = int(datetime.datetime.now().timestamp())
        data["prevbl"] += 1
        data["blacklisted"] = False
        self.bot.blacklists[guild.id] = data
        await self.bot.db.execute('UPDATE guilddata SET blacklists = $2 WHERE guildid = $1',guild.id, data)
        embed = discord.Embed(description = f"**Server:** {guild} (`{guild.id}`)\n**Reason:** {reason}\n\Server was unblacklisted <t:{timestamp}> (<t:{timestamp}:R>)", colour = self.bot.colour)
        embed.set_author(name = "Server Unblacklisted", icon_url = guild.icon or discord.Embed.Empty)
        embed.set_footer(text = f"By: {ctx.author} ({ctx.author.id})", icon_url = ctx.author.avatar or ctx.author.default_avatar)
        await self.bot.get_channel(898259956745252864).send(embed = embed)

        try:
            await guild.owner.send(f"Your server (**{guild}**) was unblacklisted from the bot by a Bot Moderator: {ctx.author.mention}")
        except:
            await message.edit(f"**{guild}** was unblacklisted\n**Reason:** {reason}\n\nI was unable to dm the owner ({guild.owner.mention}) about their server's unblacklist! Maybe you could?", allowed_mentions = discord.AllowedMentions.none())

def setup(bot):
    bot.add_cog(Blacklists(bot))