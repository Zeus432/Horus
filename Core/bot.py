import discord
from discord.ext import commands

from typing import Any, List, Optional, Union, Sequence
import wavelink, wavelink.ext.spotify as spotify
from dateutil.relativedelta import relativedelta
from datetime import datetime
import redis.asyncio as redis
from loguru import logger
import asyncpg
import json

from Core.Utils.functions import write_toml, emojis
from .settings import INITIAL_EXTENSIONS, bot_colour


class HorusCtx(commands.Context):
    async def try_add_reaction(self, emoji: str) -> None:
        """Tries to add a reaction, ignores the error if it can't """
        try:
            await self.message.add_reaction(emoji)
        except: pass
    
    async def tick(self, ignore_errors: bool = False) -> None:
        """ Easy way to react with tick emoji """
        if ignore_errors is True:
            await self.try_add_reaction(self.bot.get_em('tick'))
        else:
            await self.message.add_reaction(self.bot.get_em('tick'))
    
    async def cross(self, ignore_errors: bool = False) -> None:
        """ Easy way to react with cross emoji """
        if ignore_errors is True:
            await self.try_add_reaction(self.bot.get_em('cross'))
        else:
            await self.message.add_reaction(self.bot.get_em('cross'))

    async def send(self, content: Optional[str] = None, *, tts: bool = False, embed: Optional[discord.Embed] = None, embeds: Optional[Sequence[discord.Embed]] = None, file: Optional[discord.File] = None, files: Optional[Sequence[discord.File]] = None, stickers: Optional[Sequence[Union[discord.GuildSticker, discord.StickerItem]]] = None, delete_after: Optional[float] = None, nonce: Optional[Union[str, int]] = None, allowed_mentions: Optional[discord.AllowedMentions] = None, reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]] = None, mention_author: Optional[bool] = None, view: Optional[discord.ui.View] = None, suppress_embeds: bool = False, ephemeral: bool = False) -> discord.Message:
        obj = await super().send(content, tts = tts, embed = embed, embeds = embeds, file = file, files = files, stickers = stickers, delete_after = delete_after, nonce = nonce, allowed_mentions = allowed_mentions, reference = reference, mention_author = mention_author, view = view, suppress_embeds = suppress_embeds, ephemeral = ephemeral)
        if view is not None:
            view.message = obj
        return obj
    
    async def reply(self, content: Optional[str] = None, **kwargs: Any) -> discord.Message:
        obj = await super().reply(content, **kwargs)
        if "view" in kwargs.keys():
            kwargs['view'].message = obj
        return obj

class Horus(commands.Bot):
    def __init__(self, CONFIG: dict, *args, **kwargs) -> None:
        super().__init__(command_prefix = self.getprefix, intents = discord.Intents.all(), activity = discord.Game(name = "Waking Up"), status = discord.Status.online, case_insensitive = True, description = CONFIG['description'])
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
        self.owner_ids = frozenset(CONFIG['Owners']) # I like freezing my bot owner ids you can remove this frozenset if you want to
        self.colour = discord.Colour(bot_colour)
        self.memoji = self.get_em('me')
        self._config = CONFIG
        self._launch = None
        self._devmode = None
        self._webhook = None
        self._noprefix = None
        self._bypasscd = None
    
    async def getprefix(self, bot: commands.Bot, message: discord.Message) -> List[str]:
        # Check for prefix in cache, if not then get from db and build cache
        default = await self.redis.hget("prefix", "default")
        prefix = [default]

        if message.guild:
            if pre := await self.redis.hget("prefix", message.guild.id):
                prefix = [pre]
            
            else:
                if pre := await self.db.fetchval("SELECT prefix FROM guilddata WHERE guildid = $1", message.guild.id):
                    prefix = pre
                
                else:
                    prefix = await self.db.fetchval(f"INSERT INTO guilddata(guildid, prefix) VALUES($1, $2) ON CONFLICT (guildid) UPDATE SET prefix = $2 RETURNING prefix", message.guild.id, default)

                await self.redis.hset("prefix", message.guild.id, prefix[0]) # Update cache to have new value

        if message.author.id in self.owner_ids:
            if default not in prefix:
                prefix.append(default)

            if self._noprefix:
                prefix.append("")
        
        return commands.when_mentioned_or(*prefix)(bot, message) # Return Prefix

    async def on_ready(self) -> None:
        print(f"\nLogged in as {self.user} (ID: {self.user.id})")
        print(f"Guilds: {len(self.guilds)}")
        print(f"Large Guilds: {sum(g.large for g in self.guilds)}")
        print(f"Chunked Guilds: {sum(g.chunked for g in self.guilds)}")
        print(f"Members: {len(list(self.get_all_members()))}")
        print(f"Channels: {len([1 for x in self.get_all_channels()])}")
        print(f"Message Cache Size: {len(self.cached_messages)}\n")

        self._launch = datetime.now()
        self._webhook = await self.fetch_webhook(self._config.get('webhook'))

        await self.redis.hmset("prefix", {'default': self._config.get('prefix')}) # make redis prefix cache
        
        logger.info(f"{self.user}: All systems Online!")
        await self._webhook.send(
            f"{self.user.mention} is now online! <t:{round(datetime.now().timestamp())}>\n"
            f"```py\nGuilds: {len(self.guilds)}\n"
            f"Large Guilds: {sum(g.large for g in self.guilds)}\n"
            f"Chunked Guilds: {sum(g.chunked for g in self.guilds)}\n"
            f"Members: {len(list(self.get_all_members()))}\n"
            f"Channels: {len([1 for x in self.get_all_channels()])}```"
        )

        await self.change_presence(status = discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.watching, name = f"for @{self.user.name} help"))

    async def setup_hook(self) -> None:
        try: # Try Connecting to Postgres
            async def init_connection(conn):
                await conn.set_type_codec(
                        "jsonb",
                        encoder = json.dumps,
                        decoder = json.loads,
                        schema = "pg_catalog"
                    )

            self.db = await asyncpg.create_pool(self._config.get('postgresuri'), init = init_connection)
            print("Connected to Postgresql!")

            #with open("schema.sql", encoding="utf-8") as f:
            #    schema = f.read()
            #    await self.db.execute(schema) # To add the tables to database if they don't exist
    
        except Exception as e:
            print(f"Unable to connect to Postgresql...\n{e}")
            return await self.close()
        

        try: # Try connecting to Redis
            self.redis = await redis.from_url(self._config.get('redisuri'), decode_responses = True)
            print("Connected to Redis!")
        
        except Exception as e:
            print(f"Unable to connect to Redis...\n{e}")
            return await self.close()
        
        # Comment out lavalink until i actually start using it

        # try: # Try connecting to Lavalink
        #     self.node = await wavelink.NodePool.create_node(
        #         bot = self,
        #         spotify_client = spotify.SpotifyClient(**self._config.get('spotify')),
        #         **self._config.get('lavalink')
        #     )
        #     print("Connected to Lavalink!")
        
        # except Exception as e:
        #     print(f"Unable to connect to Lavalink...\n{e}")
        #     return await self.close()

        if restart := self._config.get('restart'): # Check if bot just started or if it was restarted
            self.loop.create_task(self.restartchk(**restart))
            self._config['restart'] = {}
            write_toml(f"Core/config.toml", self._config)

   
        # Now Load extensions
        for ext in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(f"\nFailed to load extension: {ext}\n{type(e).__name__}: {e}")
        await self.load_extension("jishaku")
        logger.info(f"Loaded: " + ", ".join(INITIAL_EXTENSIONS) + ", jishaku")
    
    async def close(self):
        await self.vac_api.close()
        await self.session.close()
        await self.redis.shutdown()

        if self._webhook:
            await self._webhook.send(
                f"{self.user.mention} is now going offline! <t:{round(datetime.now().timestamp())}>\n"
                f"```prolog\nGuilds: {len(self.guilds)}\n"
                f"Large Guilds: {sum(g.large for g in self.guilds)}\n"
                f"Chunked Guilds: {sum(g.chunked for g in self.guilds)}\n"
                f"Members: {len(list(self.get_all_members()))}\n"
                f"Channels: {len([1 for x in self.get_all_channels()])}```"
            )

        await super().close()

    async def get_context(self, message: discord.Message, *, cls = HorusCtx) -> HorusCtx:
        return await super().get_context(message, cls = cls)
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None: # Process commands when owner edits a message
        if not (after.channel.permissions_for(after.guild.me).send_messages and after.channel.permissions_for(after.guild.me).embed_links):
            return

        if after.author.id in self.owner_ids:
            await self.process_commands(after)
    
    def get_em(self, emoji: str | int) -> str:
        if isinstance(emoji, int):
            return self.get_emoji(emoji)

        return emojis(emoji)
    
    def get_uptime(self) -> str:
        """ Get Bot Uptime in a neatly converted string """
        delta_uptime = relativedelta(datetime.now(), self._launch)
        days, hours, minutes, seconds = delta_uptime.days, delta_uptime.hours, delta_uptime.minutes, delta_uptime.seconds

        uptimes = {x[0]: x[1] for x in [("day", days), ("hour", hours), ("minute", minutes), ("second", seconds)] if x[1]}
        l = len(uptimes) 

        last = " ".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes) - 1)

        uptime_string = ", ".join(
            f"{uptimes[value]} {value}{'s' if uptimes[value] > 1 else ''}" for index, value in enumerate(uptimes.keys()) if index != l-1
        )
        uptime_string += f" and {uptimes[last]}" if l > 1 else f"{uptimes[last]}"
        uptime_string += f" {last}{'s' if uptimes[last] > 1 else ''}"

        return uptime_string
    
    async def restartchk(self, message: List[int], invoke: List[int], start: int) -> None:
        """ Do stuff if bot has been restarted """
        await self.wait_until_ready()
        end = datetime.utcnow().timestamp()

        try:
            msg = self.get_channel(message[0]).get_partial_message(message[1])
            await msg.edit(content = f"Restarted **{self.user.name}** in `{round(end - start, 2)}s`")
        except: pass

        try:
            react = self.get_channel(invoke[0]).get_partial_message(invoke[1])
            await react.add_reaction(self.get_em('tick'))
        except: pass
    
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return # Return if command is in dms

        if self._devmode and message.author.id not in self.owner_ids:
            return # Only Developers can run commands in dev mode

        await self.process_commands(message)