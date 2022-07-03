import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from Core.Utils.functions import load_toml, GuildEmbed
from .views import ListenerView


class Listeners(commands.Cog):
    """ Listener for bot events """

    def __init__(self, bot: Horus):
        self.bot = bot
        self.emote = bot.get_em('listeners')
        self._config = load_toml("Cogs/Listeners/config.toml")

    async def cog_check(self, ctx: HorusCtx):
        if await self.bot.is_owner(ctx.author):
            return True
        raise commands.NotOwner()

    @commands.command(name = "setlistener", brief = "Set Listener settings")
    async def setlistener(self, ctx: HorusCtx):
        embed = discord.Embed(title = f"{self.bot.user.name} Listener Config", colour = self.bot.colour)
        embed.description = "```yaml\n" + "\n".join([f"{var} : {val}" for var, val in self._config.items()]) + "```"
        await ctx.send(embed = embed, view = ListenerView(self.bot, ctx, self._config))


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if self._config.get('guild-join-leave') is not True:
            return

        webhook = await self.bot.fetch_webhook(self.bot._config.get('guildlog'))
        await webhook.send(embed = await GuildEmbed.join(self.bot, guild))

        if await self.bot.redis.lpos("blacklist", guild.id) is not None:
            await guild.leave() # Leave guild if previously blacklisted

        if await self.bot.db.fetchval("SELECT * FROM guilddata WHERE guildid = $1", guild.id) is None:
            await self.bot.db.execute("INSERT INTO guilddata(guildid, blacklists) VALUES($1, $2) ON CONFLICT (guildid) DO UPDATE SET blacklists = $2", guild.id, {'prevbl': 0, 'blacklisted': False})

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if self._config.get('guild-join-leave') is not True:
            return

        webhook = await self.bot.fetch_webhook(self.bot._config.get('guildlog'))
        await webhook.send(embed = GuildEmbed.leave(self.bot, guild, blacklist = True if await self.bot.redis.lpos("blacklist", guild.id) is not None else False))

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: HorusCtx):
        if self._config.get('command-logs') is not True:
            return

        # Do stuff here later