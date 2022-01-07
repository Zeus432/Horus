import disnake as discord
from bot import Horus
from disnake.ext import commands

from typing import Union

from Core.Blacklists.menus import ConfirmBl
from .useful import BlType

class Admin(commands.Cog):
    """ Server Management """
    def __init__(self, bot: Horus):
        self.bot = bot
    
    async def cog_check(self, ctx: commands.Context) -> bool:
        user = ctx.guild.get_member(ctx.author.id)
        return user.guild_permissions.administrator

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
    
    @commands.is_owner()
    @server.command(name = "blacklist", aliases = ['bl'], brief = "Blacklist a Channel / User")
    async def serverblacklist(self, ctx: commands.Context, what: Union[discord.TextChannel, discord.Role, discord.User]):
        """ Blacklist a Channel, Role or User from using the bot in your server """
        what_type = "channel" if isinstance(what, discord.TextChannel) else "role" if isinstance(what, discord.Role) else "user"

        try:
            blacklist = self.bot.server_blacklists[ctx.guild.id]
        except KeyError:
            blacklist = await self.bot.db.fetchval("SELECT server_bls FROM guilddata WHERE guildid = $1", ctx.guild.id)
            self.bot.server_blacklists[ctx.guild.id] = [] if blacklist is None else blacklist

        if what.id in blacklist:
            return await ctx.reply(f'This {what_type} is already server blacklisted!')
        
        if what.id == ctx.guild.id:
            await ctx.send_help(ctx.command)

        view = ConfirmBl(what = f"{what}", action = "server blacklist", user = ctx.author)
        view.message = await ctx.reply(f"Are you sure you want to server blacklist: `{what}`?", view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False))
        await view.wait()

        if view.value is True:
            if what.id in blacklist:
                return

            blacklist.append(what.id)
            self.bot.server_blacklists[ctx.guild.id] = blacklist

            if not blacklist:
                await self.bot.db.execute('INSERT INTO guilddata(guildid, server_bls) VALUES($1, $2) ON CONFLICT (guildid) DO NOTHING RETURNING server_bls', ctx.guild.id, blacklist)
            
            else:
                query = f'UPDATE guilddata SET server_bls = $2 WHERE guildid = $1'
                await self.bot.db.execute(query, ctx.guild.id, blacklist)
    
    @commands.is_owner()
    @server.command(name = "unblacklist", aliases = ['unbl'], brief = "Unblacklist a Channel / User")
    async def unserverblacklist(self, ctx: commands.Context, what: Union[discord.TextChannel, discord.Role, discord.User]):
        """ Unblacklist a Channel, Role or User from using the bot in your server """
        what_type = "channel" if isinstance(what, discord.TextChannel) else "role" if isinstance(what, discord.Role) else "user"

        try:
            blacklist = self.bot.server_blacklists[ctx.guild.id]
        except KeyError:
            blacklist = await self.bot.db.fetchval("SELECT server_bls FROM guilddata WHERE guildid = $1", ctx.guild.id)
            self.bot.server_blacklists[ctx.guild.id] = [] if blacklist is None else blacklist

        if what.id not in blacklist:
            return await ctx.reply(f'This {what_type} is not server blacklisted!')
        
        if what.id == ctx.guild.id:
            await ctx.send_help(ctx.command)
        
        view = ConfirmBl(what = f"{what}", action = "server unblacklist", user = ctx.author)
        view.message = await ctx.reply(f"Are you sure you want to server unblacklist: `{what}`?", view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False))
        await view.wait()
        
        if view.value is True:
            if what.id not in blacklist:
                return

            if not blacklist:
                self.bot.server_blacklists[ctx.guild.id] = await self.bot.db.execute('INSERT INTO guilddata(guildid, server_bls) VALUES($1, $2) ON CONFLICT (guildid) UPDATE SET server_bls = $2 RETURNING server_bls', ctx.guild.id, blacklist)
            
            else:
                blacklist.remove(what.id)
                self.bot.server_blacklists[ctx.guild.id] = blacklist
                query = f'UPDATE guilddata SET server_bls = $2 WHERE guildid = $1'
                await self.bot.db.execute(query, ctx.guild.id, blacklist)
    
    @commands.is_owner()
    @server.command(name = "showblacklists", aliases = ["showbls"], brief = "Show a list of blacklisted users, channels and roles")
    async def showblacklists(self, ctx: commands.Context, category: BlType = None):
        """
        You can filter your bl list by specifying a category:
        `-` user
        `-` role
        `-` channel
        """
        bltype = category if category else "all"