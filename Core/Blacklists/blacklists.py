import discord
from discord.ext import commands

from typing import Union

from Core.settings import BOTMODS
from .menus import ConfirmBl

class Blacklists(commands.Cog):
    """ Blacklist people """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._mc = commands.MaxConcurrency(1, per = commands.BucketType.user, wait = False)

        for command in self.walk_commands():
            command._max_concurrency = self._mc # Set Concurrency to all the commands
    
    def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.author.id in BOTMODS or ctx.author.id in self.bot.owner_ids
    
    @commands.command(name = "blacklist", aliases = ['bl'], brief = "Blacklist a Server / User")
    async def blacklist(self, ctx: commands.Context, what: Union[discord.Guild, discord.User]):
        """ Blacklist a Server / User """
        what_type = "guild" if isinstance(what, discord.Guild) else "user"
        if what.id in self.bot.blacklists:
            return await ctx.reply(f'This {what_type} is already blacklisted!')

        view = ConfirmBl(what = f"{what}", action = "blacklist", user = ctx.author)
        view.message = await ctx.reply(f"Are you sure you want to blacklist: `{what}`?", view = view)
        await view.wait()

        if view.value is True:
            if what.id in self.bot.blacklists:
                return
            self.bot.blacklists.append(what.id)
            query = f'SELECT blacklists FROM {what_type}data WHERE {what_type}id = $1'
            what_data = await self.bot.db.fetchval(query, what.id)

            if what_data is None:
                default_bl = {'prevbl': 0, 'blacklisted': True}
                query = f'INSERT INTO {what_type}data({what_type}id, blacklists) VALUES($1, $2) ON CONFLICT ({what_type}id) DO UPDATE SET blacklists = $2 RETURNING blacklists'
                what_data = await self.bot.db.fetchval(query, what.id, default_bl)
            
            else:
                what_data['blacklisted'] = True
                query = f'UPDATE {what_type}data SET blacklists = $2 WHERE {what_type}id = $1'
                await self.bot.db.execute(query, what.id, what_data)
    
    @commands.command(name = "unblacklist", aliases = ['unbl'], brief = "Unblacklist a Server / User")
    async def unblacklist(self, ctx: commands.Context, what: Union[discord.Guild, discord.User]):
        """ Unblacklist a Server / User """
        what_type = "guild" if isinstance(what, discord.Guild) else "user"
        if what.id not in self.bot.blacklists:
            return await ctx.reply(f'This {what_type} is not blacklisted!')
        
        view = ConfirmBl(what = f"{what}", action = "unblacklist", user = ctx.author)
        view.message = await ctx.reply(f"Are you sure you want to unblacklist: `{what}`?", view = view)
        await view.wait()
        
        if view.value is True:
            if what.id not in self.bot.blacklists:
                return
            self.bot.blacklists.remove(what.id)
            query = f'SELECT blacklists FROM {what_type}data WHERE {what_type}id = $1'
            what_data = await self.bot.db.fetchval(query, what.id)

            if what_data is None:
                default_bl = {'prevbl': 1, 'blacklisted': False}
                query = f'INSERT INTO {what_type}data({what_type}id, blacklists) VALUES($1, $2) ON CONFLICT ({what_type}id) DO UPDATE SET blacklists = $2 RETURNING blacklists'
                what_data = await self.bot.db.fetchval(query, what.id, default_bl)

            else:
                what_data['prevbl'] += 1
                what_data['blacklisted'] = False
                query = f'UPDATE {what_type}data SET blacklists = $2 WHERE {what_type}id = $1'
                await self.bot.db.execute(query, what.id, what_data)
