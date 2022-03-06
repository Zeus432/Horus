import discord
from bot import Horus
from discord.ext import commands

from Core.settings import BOTMODS
from Core.Utils.useful import guildanalytics

class Listeners(commands.Cog):
    """ Bot Listeners """
    def __init__(self, bot: Horus):
        self.bot = bot
    
   # @commands.Cog.listener()
   # async def on_command_completion(self, ctx):
   #    Add command logging soon ...

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        embed = await guildanalytics(bot = self.bot, guild = guild, type = 1)
        await self.bot.get_channel(874212184828297297).send(embed = embed)

        # After sending join embed then check if blacklisted
        if guild.id in self.bot.blacklists:
            return await guild.leave()
        
        check_for_guild = await self.bot.db.fetchval("SELECT * FROM guilddata WHERE guildid = $1", guild.id)

        if check_for_guild is None:
            await self.bot.db.execute("INSERT INTO guilddata(guildid, blacklists) VALUES($1, $2) ON CONFLICT (guildid) DO UPDATE SET blacklists = $2", guild.id, {'prevbl': 0, 'blacklisted': False})
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        embed = await guildanalytics(bot = self.bot, guild = guild, type = 3 if guild.id in self.bot.blacklists else 2)

        await self.bot.get_channel(874212184828297297).send(embed = embed)