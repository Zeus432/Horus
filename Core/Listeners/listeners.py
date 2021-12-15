import discord
from discord.ext import commands

from Core.settings import BOTMODS
from Core.Utils.useful import guildanalytics

class Listeners(commands.Cog):
    """ Listeners for bot commands, guild joins and stuff """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
   # @commands.Cog.listener()
   # async def on_command_completion(self, ctx):
   #    Add command logging soon ...

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        embed = guildanalytics(bot = self.bot, guild = guild, type = 1)
        await self.bot.get_channel(874212184828297297).send(embed = embed)
        # First send join embed then check if blacklisted

        try:
            blacklist = self.bot.blacklists[guild.id]
        except KeyError:
            blacklist = await self.bot.db.fetchval("SELECT blacklists FROM guilddata WHERE guildid = $1", guild.id)
            if blacklist is None:
                blacklist = await self.bot.db.fetchval('INSERT INTO guilddata(guildid, blacklists) VALUES($1, $2) ON CONFLICT (guildid) DO UPDATE SET blacklists = $2 RETURNING blacklists', guild.id, {'prevbl': 0, 'blacklisted': False})

            self.bot.blacklists[guild.id] = blacklist # Update Blacklist cache
        
        if blacklist["blacklisted"]:
            await guild.leave()
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        try:
            embed = guildanalytics(bot = self.bot, guild = guild, type = 3 if self.bot.blacklists[guild.id]["blacklisted"] else 2)
        except:
            embed = guildanalytics(bot = self.bot, type = 2, guild = guild)
        
        await self.bot.get_channel(874212184828297297).send(embed = embed)