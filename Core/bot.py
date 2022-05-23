import discord
from discord.ext import commands

import wavelink, wavelink.ext.spotify as spotify
from dateutil.relativedelta import relativedelta
from datetime import datetime
import redis.asyncio as redis
from loguru import logger
import asyncpg
import json

from Core.Utils.functions import load_json
from .settings import INITIAL_EXTENSIONS


class HorusCtx(commands.Context):
    async def try_add_reaction(self, *args, **kwargs) -> None:
        """Tries to add a reaction, ignores the error if it can't """
        try:
            await self.message.add_reaction(*args, **kwargs)
        except: pass

class Horus(commands.Bot):
    def __init__(self, CONFIG: dict, *args, **kwargs) -> None:
        super().__init__(command_prefix = commands.when_mentioned_or("h!"), intents = discord.Intents.all(), activity = discord.Game(name = "Waking Up"), status = discord.Status.online, case_insensitive = True, description = CONFIG['description'])
        self.colour = discord.Colour(0x9C9CFF)
        self._config = CONFIG
        self._launch = None

    async def on_ready(self) -> None:
        print(f'\nLogged in as {self.user} (ID: {self.user.id})')
        print(f'Guilds: {len(self.guilds)}')
        print(f'Large Guilds: {sum(g.large for g in self.guilds)}')
        print(f'Chunked Guilds: {sum(g.chunked for g in self.guilds)}')
        print(f'Members: {len(list(self.get_all_members()))}')
        print(f'Channels: {len([1 for x in self.get_all_channels()])}')
        print(f'Message Cache Size: {len(self.cached_messages)}\n')

        self._launch = datetime.now()
        
        logger.info(f"{self.user}: All systems Online!")
        await self.change_presence(status = discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.watching, name = f"for @{self.user.name} help"))

    async def setup_hook(self) -> None:
        try: # Try Connecting to Postgres
            async def init_connection(conn):
                await conn.set_type_codec(
                        'jsonb',
                        encoder = json.dumps,
                        decoder = json.loads,
                        schema = 'pg_catalog'
                    )

            self.db = await asyncpg.create_pool(self._config["postgresuri"], init = init_connection)
            print('Connected to Postgresql!')

            #with open("schema.sql", encoding='utf-8') as f:
            #    schema = f.read()
            #    await self.db.execute(schema) # To add the tables to database if they don't exist
    
        except Exception as e:
            print(f"Unable to connect to Postgresql...\n{e}")
            return await self.close()
        

        try: # Try connecting to Redis
            self.redis = await redis.from_url(self._config["redisuri"], decode_responses = True)
            print('Connected to Redis!')
        
        except Exception as e:
            print(f"Unable to connect to Redis...\n{e}")
            return await self.close()
        

        try: # Try connecting to Lavalink
            self.node = await wavelink.NodePool.create_node(
                bot = self,
                spotify_client = spotify.SpotifyClient(**self._config["spotify"]),
                **self._config["lavalink"]
            )
            print('Connected to Lavalink!')
        
        except Exception as e:
            print(f"Unable to connect to Lavalink...\n{e}")
            return await self.close()
        
        # Now Load extensions
        for ext in INITIAL_EXTENSIONS:
            await self.load_extension(ext)
        await self.load_extension('jishaku')
        logger.info(f"Loaded: {', '.join(INITIAL_EXTENSIONS)}, jishaku")
    
    async def close(self):
        await self.vac_api.close()
        await self.session.close()

        await super().close()

    async def get_context(self, message: discord.Message, *, cls = HorusCtx) -> HorusCtx:
        return await super().get_context(message, cls = cls)
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None: # Process commands when owner edits a message
        if not (after.channel.permissions_for(after.guild.me).send_messages and after.channel.permissions_for(after.guild.me).embed_links):
            return

        if self.is_owner(after.author):
            await self.process_commands(after)
    
    def get_em(self, emoji: str | int) -> str:
        if isinstance(emoji, int):
            return self.get_emoji(emoji)

        emojis = load_json(f'Core/Assets/emojis.json')
        try:
            return emojis[emoji]
        except:
            return emojis["error"]
    
    def get_uptime(self) -> str:
        """ Get Bot Uptime in a neatly converted string """
        delta_uptime = relativedelta(datetime.now(), self._launch)
        days, hours, minutes, seconds = delta_uptime.days, delta_uptime.hours, delta_uptime.minutes, delta_uptime.seconds

        uptimes = {x[0]: x[1] for x in [('day', days), ('hour', hours), ('minute', minutes), ('second', seconds)] if x[1]}
        l = len(uptimes) 

        last = " ".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes) - 1)

        uptime_string = ", ".join(
            f"{uptimes[value]} {value}{'s' if uptimes[value] > 1 else ''}" for index, value in enumerate(uptimes.keys()) if index != l-1
        )
        uptime_string += f" and {uptimes[last]}" if l > 1 else f"{uptimes[last]}"
        uptime_string += f" {last}{'s' if uptimes[last] > 1 else ''}"

        return uptime_string