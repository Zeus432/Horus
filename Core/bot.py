import discord
from discord.ext import commands

import wavelink, wavelink.ext.spotify as spotify
from dateutil.relativedelta import relativedelta
from datetime import datetime
import redis.asyncio as redis
from loguru import logger
from typing import List
import asyncpg
import json

from Core.Utils.functions import load_json, write_toml
from .settings import INITIAL_EXTENSIONS


class HorusCtx(commands.Context):
    async def try_add_reaction(self, *args, **kwargs) -> None:
        """Tries to add a reaction, ignores the error if it can't """
        try:
            await self.message.add_reaction(*args, **kwargs)
        except: pass

class Horus(commands.Bot):
    def __init__(self, CONFIG: dict, *args, **kwargs) -> None:
        super().__init__(command_prefix = self.getprefix, intents = discord.Intents.all(), activity = discord.Game(name = "Waking Up"), status = discord.Status.online, case_insensitive = True, description = CONFIG['description'])
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
        self.owner_ids = frozenset(CONFIG['Owners']) # I like freezing my bot owner ids you can remove this frozenset if you want to
        self.colour = discord.Colour(0x9C9CFF)
        self._config = CONFIG
        self._launch = None
        self._devmode = None
        self._webhook = None
        self._noprefix = None
    
    async def getprefix(self, bot: commands.Bot, message: discord.Message) -> List[str]:
        # Check for prefix in cache, if not then get from db and build cache
        default = await self.redis.hget("prefix", "default")
        prefix = [default]

        if message.guild:
            if pre := await self.redis.hget("prefix", message.guild.id):
                prefix = [pre]
            
            else:
                if pre := await self.db.fetchval('SELECT prefix FROM guilddata WHERE guildid = $1', message.guild.id):
                    prefix = pre
                
                else:
                    prefix = await self.db.fetchval(f'INSERT INTO guilddata(guildid, prefix) VALUES($1, $2) ON CONFLICT (guildid) UPDATE SET prefix = $2 RETURNING prefix', message.guild.id, default)

                await self.redis.hset("prefix", message.guild.id, prefix[0]) # Update cache to have new value

        if message.author.id in self.owner_ids:
            if default not in prefix:
                prefix.append(default)

            if self._noprefix:
                prefix.append("")
        
        return commands.when_mentioned_or(*prefix)(bot, message) # Return Prefix

    async def on_ready(self) -> None:
        print(f'\nLogged in as {self.user} (ID: {self.user.id})')
        print(f'Guilds: {len(self.guilds)}')
        print(f'Large Guilds: {sum(g.large for g in self.guilds)}')
        print(f'Chunked Guilds: {sum(g.chunked for g in self.guilds)}')
        print(f'Members: {len(list(self.get_all_members()))}')
        print(f'Channels: {len([1 for x in self.get_all_channels()])}')
        print(f'Message Cache Size: {len(self.cached_messages)}\n')

        self._launch = datetime.now()
        self._webhook = await self.fetch_webhook(self._config['webhook'])

        await self.redis.hmset("prefix", {"default": self._config['prefix']}) # make redis prefix cache
        
        logger.info(f"{self.user}: All systems Online!")
        await self._webhook.send(
            f'{self.user.mention} is now online! <t:{round(datetime.now().timestamp())}>\n'
            f'```py\nGuilds: {len(self.guilds)}\n'
            f'Large Guilds: {sum(g.large for g in self.guilds)}\n'
            f'Chunked Guilds: {sum(g.chunked for g in self.guilds)}\n'
            f'Members: {len(list(self.get_all_members()))}\n'
            f'Channels: {len([1 for x in self.get_all_channels()])}```'
        )

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

            self.db = await asyncpg.create_pool(self._config['postgresuri'], init = init_connection)
            print('Connected to Postgresql!')

            #with open("schema.sql", encoding='utf-8') as f:
            #    schema = f.read()
            #    await self.db.execute(schema) # To add the tables to database if they don't exist
    
        except Exception as e:
            print(f"Unable to connect to Postgresql...\n{e}")
            return await self.close()
        

        try: # Try connecting to Redis
            self.redis = await redis.from_url(self._config['redisuri'], decode_responses = True)
            print('Connected to Redis!')
        
        except Exception as e:
            print(f"Unable to connect to Redis...\n{e}")
            return await self.close()
        

        try: # Try connecting to Lavalink
            self.node = await wavelink.NodePool.create_node(
                bot = self,
                spotify_client = spotify.SpotifyClient(**self._config['spotify']),
                **self._config['lavalink']
            )
            print('Connected to Lavalink!')
        
        except Exception as e:
            print(f"Unable to connect to Lavalink...\n{e}")
            return await self.close()

        if restart := self._config['restart']: # Check if bot just started or if it was restarted
            self.loop.create_task(self.restartchk(**restart))
            self._config['restart'] = {}
            write_toml(f'Core/config.toml', self._config)

   
        # Now Load extensions
        for ext in INITIAL_EXTENSIONS:
            await self.load_extension(ext)
        await self.load_extension('jishaku')
        logger.info(f"Loaded: {', '.join(INITIAL_EXTENSIONS)}, jishaku")
    
    async def close(self):
        await self.vac_api.close()
        await self.session.close()

        if self._webhook:
            await self._webhook.send(
                f'{self.user.mention} is now going offline! <t:{round(datetime.now().timestamp())}>\n'
                f'```prolog\nGuilds: {len(self.guilds)}\n'
                f'Large Guilds: {sum(g.large for g in self.guilds)}\n'
                f'Chunked Guilds: {sum(g.chunked for g in self.guilds)}\n'
                f'Members: {len(list(self.get_all_members()))}\n'
                f'Channels: {len([1 for x in self.get_all_channels()])}```'
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

        emojis = load_json(f'Core/Assets/emojis.json')
        try:
            return emojis[emoji]
        except:
            return emojis['error']
    
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
        if self.dev_mode and message.author.id not in self.owner_ids:
            return # Only Developers can run commands in dev mode
        
        await self.process_commands(message)