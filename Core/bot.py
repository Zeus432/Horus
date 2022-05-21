import discord
from discord.ext import commands

import wavelink, wavelink.ext.spotify as spotify
from .settings import INITIAL_EXTENSIONS
import redis.asyncio as redis
import asyncpg
import json


class HorusCtx(commands.Context):
    async def try_add_reaction(self, *args, **kwargs):
        try:
            await self.message.add_reaction(*args, **kwargs)
        except: pass

class Horus(commands.Bot):
    def __init__(self, CONFIG: dict, *args, **kwargs) -> None:
        super().__init__(command_prefix = commands.when_mentioned_or("h!"), intents = discord.Intents.all(), activity = discord.Game(name = "Waking Up"), status = discord.Status.online, case_insensitive = True, description = CONFIG['description'])
        self._config = CONFIG
        self.colour = discord.Colour(0x9C9CFF)

    async def on_ready(self):
        print(f'\nLogged in as {self.user} (ID: {self.user.id})')
        print(f'Guilds: {len(self.guilds)}')
        print(f'Large Guilds: {sum(g.large for g in self.guilds)}')
        print(f'Chunked Guilds: {sum(g.chunked for g in self.guilds)}')
        print(f'Members: {len(list(self.get_all_members()))}')
        print(f'Channels: {len([1 for x in self.get_all_channels()])}')
        print(f'Message Cache Size: {len(self.cached_messages)}\n')

        await self.change_presence(status = discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.watching, name = f"for @{self.user.name} help"))
    
    async def setup_hook(self):
        await self.connector()

        for ext in INITIAL_EXTENSIONS:
            await self.load_extension(ext)
        await self.load_extension('jishaku')
  
    async def connector(self):
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
    
        except Exception as e:
            print(f"Unable to connect to Postgresql...\n{e}")
        

        try: # Try connecting to Redis
            self.redis = await redis.from_url(self._config["redisuri"], decode_responses = True)
            print('Connected to Redis!')
        
        except Exception as e:
            print(f"Unable to connect to Redis...\n{e}")
            return
        

        try: # Try connecting to Lavalink
            self.node = await wavelink.NodePool.create_node(
                bot = self,
                spotify_client = spotify.SpotifyClient(**self._config["spotify"]),
                **self._config["lavalink"]
            )
            print('Connected to Lavalink!')
        
        except Exception as e:
            print(f"Unable to connect to Lavalink...\n{e}")
            return
    
    async def get_context(self, message: discord.Message, *, cls = HorusCtx):
        return await super().get_context(message, cls = cls)
