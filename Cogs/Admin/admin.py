from bot import Horus
import disnake
from disnake.ext import commands

from typing import Union

from Core.Blacklists.menus import ConfirmBl
from Core.Utils.pagination import Pagination
from .useful import BlType

class Admin(commands.Cog):
    """ Server Management """
    def __init__(self, bot: Horus):
        self.bot = bot

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



    # Server Group and Sub Commands
    
    @commands.group(name = "server", brief = "Server Blacklist and Management Commands", invoke_without_command = True)
    async def server(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @server.command(name = "blacklist", aliases = ['bl'], brief = "Blacklist a Channel, User or Role")
    async def serverblacklist(self, ctx: commands.Context, what: Union[disnake.TextChannel, disnake.Role, disnake.Member]):
        """ Blacklist a Channel, Role or User from using the bot in your server """
        what_type = "channel" if isinstance(what, disnake.TextChannel) else "role" if isinstance(what, disnake.Role) else "user"

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
        view.message = await ctx.reply(f"Are you sure you want to server blacklist: `{what}`?", view = view, allowed_mentions = disnake.AllowedMentions(roles = False, users = False))
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
    async def unserverblacklist(self, ctx: commands.Context, what: Union[disnake.TextChannel, disnake.Role, disnake.User, int]):
        """ Unblacklist a Channel, Role or User from using the bot in your server """
        what_type = "channel" if isinstance(what, disnake.TextChannel) else "role" if isinstance(what, disnake.Role) else "user"

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
        view.message = await ctx.reply(f"Are you sure you want to server unblacklist: `{what}`?", view = view, allowed_mentions = disnake.AllowedMentions(roles = False, users = False))
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
            embed = disnake.Embed(description = "\n".join([f'**{(page*20) + index + 1})** {start}{item}> (`{item}`)' for index, item in enumerate(items[:20])]), colour = self.bot.colour)
            embed.set_author(name = f"Server Blacklisted {category.capitalize()}s", icon_url = f"{ctx.guild.icon}")
            embed.set_footer(text = f"Page {page + 1}/{total}")

            embeds.append(embed)
            items = items[20:]
            page += 1
        
        view = Pagination(embeds =  embeds, user = ctx.author, bot = self.bot)

        view.message = await ctx.reply(embed = embeds[0], view = view, mention_author = False)
        await view.wait()

    @server.command(name = "checkblacklist", aliases = ["checkbl"], brief = "Check if an user, channel or role")
    async def checkblacklist(self, ctx: commands.Context, what: Union[disnake.TextChannel, disnake.Role, disnake.User, int]):
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