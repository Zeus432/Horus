import re
import disnake as discord
from disnake.ext import commands

from dateutil.relativedelta import relativedelta
from datetime import datetime
from loguru import logger
import vacefron
import aiohttp
import asyncio
import asyncpg
import json
import time

from Core.Utils.useful import load_json, write_json
from Core.settings import INITIAL_EXTENSIONS, OWNER_IDS

class HorusCtx(commands.Context):
    async def try_add_reaction(self, *args, **kwargs):
        try:
            await self.message.add_reaction(*args, **kwargs)
        except: pass


class Horus(commands.Bot):
    def __init__(self, CONFIG: dict,  *args, **kwargs):
        super().__init__(command_prefix = self.getprefix,  intents = discord.Intents.all(), activity = discord.Game(name = "Waking Up"), status = discord.Status.online, case_insensitive = True, sync_commands_on_cog_unload = True, sync_permissions = True, description = CONFIG['description'], **kwargs)
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
        self._config = CONFIG
        self.colour = discord.Colour(0x9c9cff)
        self._noprefix = False
        self._added_views = False
        self._bypass_cooldowns = False
        self.owner_ids = OWNER_IDS
        self.prefix_cache = {}
        self.blacklists = []
        self.server_blacklists = {}
        self.dev_mode = False
        self.if_ready = False

        # Load Initial Extensions
        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'\nFailed to load extension {extension}\n{type(e).__name__}: {e}')
        
        # Edit restart message if exists
        restart = self._config["restart"]
        if restart:
            self.loop.create_task(self.restartcheck(**restart))
    
    async def getprefix(self, bot: commands.Bot, message: discord.Message):
        # Check for prefix in cache, if not then get from db and build cache
        prefix = self._config['prefix'] # Default prefix
        devprefix = []

        if message.guild:
            try:
                prefix = self.prefix_cache[message.guild.id]
            except KeyError:
                prefix = await self.db.fetchval('SELECT prefix FROM guilddata WHERE guildid = $1', message.guild.id)

            if not prefix:
                prefix = await self.db.fetchval(f'INSERT INTO guilddata(guildid, prefix) VALUES($1, $2) ON CONFLICT (guildid) UPDATE SET prefix = $2 RETURNING prefix', message.guild.id, self._config['prefix'])

            self.prefix_cache[message.guild.id] = prefix # Update Cache

        if await self.is_owner(message.author):
            if "h!" not in prefix:
                devprefix.append("h!")
            if self._noprefix == True:
                devprefix.append("")

        return commands.when_mentioned_or(*prefix, *devprefix)(bot, message) # Return Prefix
    
    async def restartcheck(self, **kwargs):
        await self.wait_until_ready()
        self._config['restart'] = {}
        self._config = self._config
        write_json(f'Core/config.json', self._config)

        message = kwargs.pop("message")
        invoke = kwargs.pop("invoke")
        start = kwargs.pop("start")
        end = datetime.utcnow().timestamp()

        try:
            msg = self.get_channel(message[0]).get_partial_message(message[1])
        except: pass
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

        # Build Blacklisted Guild & User Cache
        bl_guilds = [guild['guildid'] for guild in await self.db.fetch("SELECT guildid FROM guilddata WHERE blacklists->'blacklisted' @> 'true'") if guild]
        await asyncio.sleep(3) # Wait a while before next db request
        bl_users = [user['userid'] for user in await self.db.fetch("SELECT userid FROM userdata WHERE blacklists->'blacklisted' @> 'true'") if user]
        self.blacklists.extend([*bl_guilds, *bl_users])

        await asyncio.sleep(10)
        if not self.dev_mode:
            await self.change_presence(status = discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.watching, name = f"for @{self.user.name} help"))

        logger.info(f"{self.user} is Online!")
        self.if_ready = True

        self._notif_webhook = await self.fetch_webhook(self._config["webhook"])
        await self._notif_webhook.send(
            f'{self.user.mention} is now online!\n'
            f'```py\nGuilds: {len(self.guilds)}\n'
            f'Large Guilds: {sum(g.large for g in self.guilds)}\n'
            f'Chunked Guilds: {sum(g.chunked for g in self.guilds)}\n'
            f'Members: {len(list(self.get_all_members()))}\n'
            f'Channels: {len([1 for x in self.get_all_channels()])}```'
        )
    
    async def start(self, *args, **kwargs):
        self.session = aiohttp.ClientSession()
        self.vac_api = vacefron.Client(session = self.session)
        await super().start(*args, **kwargs)
    
    async def close(self):
        await self.vac_api.close()
        await self.session.close()

        await self._notif_webhook.send(
            f'{self.user.mention} is now going offline!\n'
            f'```prolog\nGuilds: {len(self.guilds)}\n'
            f'Large Guilds: {sum(g.large for g in self.guilds)}\n'
            f'Chunked Guilds: {sum(g.chunked for g in self.guilds)}\n'
            f'Members: {len(list(self.get_all_members()))}\n'
            f'Channels: {len([1 for x in self.get_all_channels()])}```'
        )

        await super().close()
    
    def run(self):
        super().run(self._config['TOKEN'], reconnect = True)
    
    def starter(self):
        try:
            print("\nConnecting to database ...")
            start = time.perf_counter()
            async def init_connection(conn):
                await conn.set_type_codec(
                        'jsonb',
                        encoder = json.dumps,
                        decoder = json.loads,
                        schema = 'pg_catalog'
                    )
            pg_pool = self.loop.run_until_complete(
                asyncpg.create_pool(
                    init = init_connection, **self._config["db"]
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

            # To Initialise Databases

            # guilddata_table = """ CREATE TABLE IF NOT EXISTS guilddata (
            # guildid BIGINT UNIQUE PRIMARY KEY,
            # prefix VARCHAR[] DEFAULT '{"h!"}',
            # blacklists jsonb DEFAULT '{"prevbl": 0, "blacklisted": false}',
            # server_bls jsonb DEFAULT '{}'
            # ); """

            # userdata_table = """ CREATE TABLE IF NOT EXISTS userdata (
            # userid BIGINT UNIQUE PRIMARY KEY,
            # blacklists jsonb DEFAULT '{"prevbl": 0, "blacklisted": false}'
            # ); """

            # todo_table =  """ CREATE TABLE IF NOT EXISTS todo (
            # userid BIGINT UNIQUE PRIMARY KEY,
            # lastupdated BIGINT NOT NULL,
            # data jsonb DEFAULT '{}'
            # ); """

            # tags_table = """ CREATE TABLE IF NOT EXISTS tags (
            # name VARCHAR NOT NULL,
            # serverid BIGINT NOT NULL,
            # content TEXT NOT NULL,
            # usage BIGINT DEFAULT 0,
            # info jsonb DEFAULT '{"owner":null, "created_at": null}',
            # aliases VARCHAR[] DEFAULT '{}'
            # ); """
            
            # buttonroles_table = """ CREATE TABLE IF NOT EXISTS buttonroles (
            # guildid BIGINT NOT NULL,
            # messageid BIGINT PRIMARY KEY,
            # channelid BIGINT NOT NULL,
            # role_emoji jsonb DEFAULT '{}',
            # config jsonb DEFAULT '{}'
            # ); """

    def get_em(self, emoji: str | int) -> str:
        numdict = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten'}
        if emoji in numdict:
            emoji = numdict[emoji]

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
    
    async def get_context(self, message: discord.Message, *, cls = HorusCtx):
        return await super().get_context(message, cls = cls)

    async def on_message(self, message: discord.Message):
        if self.http.token in message.content:
            view = discord.ui.View(timeout = 50)
            view.add_item(discord.ui.Button(label = "Message Link", url = f"{message.jump_url}", emoji = "\U0001f517"))
            await self._notif_webhook.send(content = f"{self.zeus.mention} Token has been leaked, please regenerate it as soon as posssible!!", view = view)

        if not (message.guild and self.if_ready):
            return # Don't process commands if commands are in dms or if bot isn't ready yet
        
        try:
            user = message.guild.get_member(message.author.id)
            if not user:
                return
        except: return

        if self.dev_mode and message.author.id not in self.owner_ids:
            return # Only Developers can run commands in dev mode

        if not (message.channel.permissions_for(message.guild.me).send_messages and message.channel.permissions_for(message.guild.me).embed_links):
            return # return if bot doesn't have send messages and embed links permissions
        
        if (message.author.id in self.blacklists or message.guild.id in self.blacklists) and message.author.id not in self.owner_ids:
            return # Don't process commands if server or user is blacklisted. But also make sure I don't fricking lock myself out of my own bot
        
        # Now check for server specific blacklists
        try:
            blacklist = self.server_blacklists[message.guild.id]
        except KeyError:
            blacklist = await self.db.fetchval("SELECT server_bls FROM guilddata WHERE guildid = $1", message.guild.id)
            if blacklist is None:
                blacklist = await self.db.fetchval('INSERT INTO guilddata(guildid) VALUES($1) ON CONFLICT (guildid) DO NOTHING RETURNING server_bls', message.guild.id)
            self.server_blacklists[message.guild.id] = blacklist
        
        for item in ['user', 'channel', 'role']:
            if item not in blacklist:
                blacklist[item] = []

        if (message.author.id in blacklist['user'] or message.channel.id in blacklist['channel']) and message.author.id not in self.owner_ids:
            return # Return if user or channel is blocked in that server

        user_roles = user.roles
        if user_roles:
            if [role.id for role in user_roles if role.id in blacklist['role']] != [] and message.author.id not in self.owner_ids:
                return # Return if role is blocked in that server

        await self.process_commands(message)
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not (after.channel.permissions_for(after.guild.me).send_messages and after.channel.permissions_for(after.guild.me).embed_links):
            return

        if after.author.id in self.owner_ids:
            await self.process_commands(after)
