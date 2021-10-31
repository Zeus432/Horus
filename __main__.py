import discord
from discord.ext import commands

from datetime import datetime
import logging
import aiohttp
import pathlib
import asyncio
import asyncpg
import json
import time


from Core.utils import load_json, write_json
from Core.settings import INITIAL_EXTENSIONS

CONFIG = load_json('Core/config.json')
TOKEN = CONFIG['TOKEN']

rootdir = pathlib.Path(__file__).parent.resolve()

# Loggers help keep your console from being flooded with Errors, you can instead send them to a file which you can check later
logger = logging.getLogger('HorusLog')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename = f'{rootdir}/Core/Horus.log', encoding = 'utf-8', mode = 'a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Horus(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix = commands.when_mentioned_or(*CONFIG['prefix']),  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle, case_insensitive = True, **kwargs)
        self.description = CONFIG['description']
        self.config = CONFIG
        self.colour = discord.Colour(0x2F3136)

        # Load Initial Extensions
        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}\n{type(e).__name__}: {e}')
        
        # Edit restart message if exists
        restart = CONFIG["restart"]
        if restart:
            start = restart[0]
            end = datetime.utcnow().timestamp()
            restart.append(round((end - start) * 10, 2))
            self.restart = restart
            self.loop.create_task(self.restartcheck())
    
    async def restartcheck(self):
        await self.wait_until_ready()
        CONFIG['restart'] = []
        self.config = CONFIG
        write_json('Core/config.json', CONFIG)
        try:
            msg = self.get_channel(self.restart[1][0]).get_partial_message(self.restart[1][1])
        except:
            return
        await msg.edit(content = f"Restarted **{self.user.name}** in `{self.restart[2]}`s")
    
    async def on_ready(self):
        print(f'\nLogged in as {self.user} (ID: {self.user.id})')
        print(f'Guilds: {len(self.guilds)}')
        print(f'Large Guilds: {sum(g.large for g in self.guilds)}')
        print(f'Chunked Guilds: {sum(g.chunked for g in self.guilds)}')
        print(f'Members: {len(list(self.get_all_members()))}')
        print(f'Channels: {len([1 for x in self.get_all_channels()])}')
        print(f'Message Cache Size: {len(self.cached_messages)}\n')
        await asyncio.sleep(10)
        await self.change_presence(status = discord.Status.idle, activity = discord.Activity(type=discord.ActivityType.watching, name = f"for @{self.user.name} help"))
        logger.info(f"{self.user} is Online!")
    
    async def start(self, *args, **kwargs):
        self.session = aiohttp.ClientSession()
        await super().start(*args, **kwargs)
    
    async def close(self):
        await self.session.close()
        await super().close()
    
    def run(self):
        super().run(TOKEN, reconnect = True)
    
    def starter(self):
        try:
            print("Connecting to database ...")
            start = time.perf_counter()
            async def init_connection(conn):
                await conn.set_type_codec(
                        'jsonb',
                        encoder=json.dumps,
                        decoder=json.loads,
                        schema='pg_catalog'
                    )
            pg_pool = self.loop.run_until_complete(
                asyncpg.create_pool(
                    init = init_connection, **self.config["db"]
                )
            )
            self.db = pg_pool

        except Exception as e:
            print("Could not connect to database:", e)
        
        else:
            self.launch_time = datetime.now()
            self.launch_ts = self.launch_time.timestamp()
            print(f"Connected to database ({round((time.perf_counter() - start) * 10, 2)}s)")
            self.run()

if __name__ == "__main__":
    horus = Horus()
    horus.starter()