import discord
from discord.ext import commands

import aiohttp
import asyncpg
import logging
import vacefron
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter
from typing import Any, Optional, List, Sequence, Union

from .settings import INITIAL_EXTENSIONS, bot_colour
from Core.Utils.functions import emojis


class HorusCtx(commands.Context):
    async def try_add_reaction(self, emoji: str) -> None:
        """Tries to add a reaction, ignores the error if it can't"""
        try:
            await self.message.add_reaction(emoji)
        except:
            pass

    # fmt: off
    # Turning formatting off because I'm merely overriding to make sure the view (if any) is linked to its message by default and formatting this looks very weird

    async def send(self, content: Optional[str] = None, *, tts: bool = False, embed: Optional[discord.Embed] = None, embeds: Optional[Sequence[discord.Embed]] = None, file: Optional[discord.File] = None, files: Optional[Sequence[discord.File]] = None, stickers: Optional[Sequence[Union[discord.GuildSticker, discord.StickerItem]]] = None, delete_after: Optional[float] = None, nonce: Optional[Union[str, int]] = None, allowed_mentions: Optional[discord.AllowedMentions] = None, reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]] = None, mention_author: Optional[bool] = None, view: Optional[discord.ui.View] = None, suppress_embeds: bool = False, ephemeral: bool = False) -> discord.Message:
        message = await super().send(content, tts=tts, embed=embed, embeds=embeds, file=file, files=files, stickers=stickers, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions, reference=reference, mention_author=mention_author, view=view, suppress_embeds=suppress_embeds, ephemeral=ephemeral)
        if view is not None:
            view.message = message
        return message

    async def reply(self, content: Optional[str] = None, **kwargs: Any) -> discord.Message:
        message = await super().reply(content, **kwargs)
        if "view" in kwargs.keys():
            kwargs['view'].message = message
        return message

    # fmt: on


class Horus(commands.Bot):
    def __init__(self, CONFIG: dict, **kwargs) -> None:
        super().__init__(
            command_prefix=self.getprefix,  # shall change later
            intents=discord.Intents.all(),
            activity=discord.Game(name="Waking Up"),
            status=discord.Status.online,
            case_insensitive=True,
            description="Hello there, I'm Horus",
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
            **kwargs,
        )
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
        self.owner_ids = frozenset(CONFIG["Owners"])
        self._config = CONFIG
        self._noprefix = False
        self.prefix_cache = {}
        self.colour = discord.Colour(bot_colour)

        self.db: asyncpg.Pool
        self.vac_api: vacefron.Client
        self.session: aiohttp.ClientSession
        self._app_info: discord.AppInfo

    async def getprefix(self, bot: commands.Bot, message: discord.Message) -> List[str]:
        # Check for prefix in cache, if not then get from db and build cache
        prefix = [self._config["prefix"]]  # Default prefix

        if message.guild:
            prefix = self.prefix_cache.get(message.guild.id)
            if prefix is None:
                prefix = await self.db.fetchval(
                    "SELECT prefix FROM guilddata WHERE guildid = $1", message.guild.id
                )

            if not prefix:
                prefix = await self.db.fetchval(
                    f"INSERT INTO guilddata(guildid, prefix) VALUES($1, $2) ON CONFLICT (guildid) UPDATE SET prefix = $2 RETURNING prefix",
                    message.guild.id,
                    self._config["prefix"],
                )

            self.prefix_cache[message.guild.id] = prefix  # Update Cache

        if await self.is_owner(message.author) and self._noprefix == True:
            prefix.append("")

        return commands.when_mentioned_or(*prefix)(bot, message)  # Return Prefix

    async def on_ready(self) -> None:
        logging.warn(
            f"{self.user} (ID: {self.user.id}) is now ready!"
        )  # Using warn feels kinda hacky but i'll use for now to override level limit for stdout
        logging.info(f"Guilds: {len(self.guilds)}")
        logging.info(f"Large Guilds: {sum(g.large for g in self.guilds)}")
        logging.info(f"Chunked Guilds: {sum(g.chunked for g in self.guilds)}")
        logging.info(f"Members: {len(list(self.get_all_members()))}")
        logging.info(f"Channels: {len([1 for x in self.get_all_channels()])}")
        logging.info(f"Message Cache Size: {len(self.cached_messages)}\n")

        self._app_info = await self.application_info()
        self._launch = datetime.now()

    async def setup_hook(self) -> None:
        loaded = []
        for ext in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(ext)
            except Exception as e:
                logging.exception(f"Failed to load extension: {ext}", exc_info=e)
            else:
                loaded.append(ext)
        logging.info(f"Loaded: " + ", ".join(loaded))

        async def func():
            await self.wait_until_ready()
            await self.wait_until_ready()
            await self.change_presence(
                status=discord.Status.idle,
                activity=discord.Activity(type=discord.ActivityType.watching, name=f"for @{self.user.name} help"),
            )

        self.loop.create_task(func())

    async def close(self):
        await self.vac_api.close()
        await self.session.close()
        await super().close()

    async def get_context(self, message: Union[discord.Interaction, discord.Message], *, cls=HorusCtx) -> HorusCtx:
        return await super().get_context(message, cls=cls)

    async def process_commands(self, message: discord.Message):
        ctx = await self.get_context(message)

        if message.author.bot:
            return

        if ctx.command is None:
            return

        if message.guild is None and ctx.command.extras.get("dm", False) is not True:
            return  # Return if command is in dms

        if message.guild and not (
            message.channel.permissions_for(message.guild.me).send_messages
            and message.channel.permissions_for(message.guild.me).embed_links
        ):  # return if you can send messages or send embeds
            return

        await self.invoke(ctx)

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if after.author.id in self.owner_ids:
            await self.process_commands(after)

    def get_em(self, emoji: str | int) -> str:
        if isinstance(emoji, int):
            return self.get_emoji(emoji)

        return emojis(emoji)

    def get_uptime(self) -> str:
        """Get Bot Uptime in a neatly converted string"""
        delta_uptime = relativedelta(datetime.now(), self._launch)
        days, hours, minutes, seconds = (
            delta_uptime.days,
            delta_uptime.hours,
            delta_uptime.minutes,
            delta_uptime.seconds,
        )

        uptimes = {
            x[0]: x[1] for x in [("day", days), ("hour", hours), ("minute", minutes), ("second", seconds)] if x[1]
        }
        l = len(uptimes)

        last = " ".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes) - 1)

        uptime_string = ", ".join(
            f"{uptimes[value]} {value}{'s' if uptimes[value] > 1 else ''}"
            for index, value in enumerate(uptimes.keys())
            if index != l - 1
        )
        uptime_string += f" and {uptimes[last]}" if l > 1 else f"{uptimes[last]}"
        uptime_string += f" {last}{'s' if uptimes[last] > 1 else ''}"

        return uptime_string

    @discord.utils.cached_property
    async def stats_webhook(self) -> discord.Webhook:
        return await self.fetch_webhook(self._config.get("webhook")["id"])

    @discord.utils.cached_property
    def static_stats_webhook(self) -> discord.Webhook:
        return discord.Webhook.partial(**self._config.get("webhook"), session=self.session)
