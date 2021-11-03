import discord
from discord.ext import commands

from dateutil.relativedelta import relativedelta
from datetime import datetime
from loguru import logger
import aiohttp
import pathlib
import asyncio
import asyncpg
import json
import time

from Core.Utils.useful import load_json, write_json
from Core.settings import INITIAL_EXTENSIONS

CONFIG = load_json('Core/config.json')
TOKEN = CONFIG['TOKEN']

rootdir = pathlib.Path(__file__).parent.resolve()

# Loggers help keep your console from being flooded with Errors, you can instead send them to a file which you can check later
logger.remove()
logger.add(f'{rootdir}/Core/Horus.log', level="DEBUG", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

class Horus(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix = self.getprefix,  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle, case_insensitive = True, **kwargs)
        self.description = CONFIG['description']
        self.config = CONFIG
        self.colour = discord.Colour(0x9c9cff)
        self.noprefix = False

        # Load Initial Extensions
        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'\nFailed to load extension {extension}\n{type(e).__name__}: {e}')
        
        # Edit restart message if exists
        restart = CONFIG["restart"]
        if restart:
            self.loop.create_task(self.restartcheck(**restart))
    
    async def getprefix(self, bot: commands.Bot, message: discord.Message):
        # Check for prefix in cache, if not then get from db and build cache
        prefix = CONFIG['prefix'] # Default prefix
        devprefix = []

        if await self.is_owner(message.author):
            if "h!" not in prefix:
                devprefix.append("h!")
            if self.noprefix == True:
                devprefix.append("")
        return commands.when_mentioned_or(*prefix,*devprefix)(bot, message) # Return Prefix
    
    async def restartcheck(self, **kwargs):
        await self.wait_until_ready()
        CONFIG['restart'] = {}
        self.config = CONFIG
        write_json(f'Core/config.json', CONFIG)

        message = kwargs.pop("message")
        invoke = kwargs.pop("invoke")
        start = kwargs.pop("start")
        end = datetime.utcnow().timestamp()

        try:
            msg = self.get_channel(message[0]).get_partial_message(message[1])
        except:
            pass
        else:
            await msg.edit(content = f"Restarted **{self.user.name}** in `{round(end - start, 2)}s`")

        react = self.get_channel(invoke[0]).get_partial_message(invoke[1])
        await react.add_reaction(self.get_em('tick'))
    
    async def on_ready(self):
        self.zeus = self.get_user(760823877034573864)
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
            print("\nConnecting to database ...")
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
            print("Could not connect to database:\n", e)
            logger.opt(exception = e).error("I was unable to connect to database:\n")
        
        else:
            logger.info("Connected to database")
            self.launch_time = datetime.now()
            self.launch_ts = self.launch_time.timestamp()
            print(f"Connected to database ({round((time.perf_counter() - start) * 10, 2)}s)\n")
            self.run()

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
        delta_uptime = relativedelta(datetime.now(), self.launch_time)
        days, hours, minutes, seconds = delta_uptime.days, delta_uptime.hours, delta_uptime.minutes, delta_uptime.seconds

        uptimes = {x[0]: x[1] for x in [('day', days), ('hour', hours), ('minute', minutes), ('second', seconds)] if x[1]}
        l = len(uptimes) 

        last = " ".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes)-1)

        uptime_string = ", ".join(
            f"{uptimes[value]} {value}{'s' if uptimes[value] > 1 else ''}" for index, value in enumerate(uptimes.keys()) if index != l-1
        )
        uptime_string += f" and {uptimes[last]}" if l > 1 else f"{uptimes[last]}"
        uptime_string += f" {last}{'s' if uptimes[last] > 1 else ''}"
        
        return uptime_string

if __name__ == "__main__":
    horus = Horus()
    horus.starter()