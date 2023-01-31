import discord

import json
import aiohttp
import asyncio
import asyncpg
import logging
import vacefron
import contextlib
from logging.handlers import RotatingFileHandler

from Core.bot import Horus
from Core.Utils.functions import load_toml


CONFIG = load_toml("Core/config.toml")


@contextlib.contextmanager
def setup_logging():
    """
    Logging method from RoboDanny (https://github.com/Rapptz/RoboDanny)

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    https://github.com/Rapptz/RoboDanny/blob/514566b39f556866161b54959ccd49904828d71c/launcher.py#L167-L192

    Rapptz/RoboDanny
    """
    log = logging.getLogger()
    try:
        discord.utils.setup_logging()

        # Logs below level logging.WARNING does not get displayed on stdout
        logging.getLogger().handlers[0].setLevel(logging.WARNING)

        # __enter__
        max_bytes = 32 * 1024 * 1024  # 32 MiB
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)

        handler = RotatingFileHandler(
            filename="Core/horus.log",
            encoding="utf-8",
            mode="a",
            maxBytes=max_bytes,
            backupCount=5,
        )
        fmt = logging.Formatter(
            "{asctime} | {levelname:<8} | [{name}] : {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{",
        )

        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield

    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


async def create_pool() -> asyncpg.Pool:
    async def init_connection(conn):
        await conn.set_type_codec(
            "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
        )

    return await asyncpg.create_pool(CONFIG.get("postgresuri"), init=init_connection)


async def startup():
    try:
        db = await create_pool()
    except Exception as e:
        logging.exception("Could not set up PostgreSQL!", exc_info=e)
        return
    else:
        logging.info("Connection to PostgreSQL successful!")

    async with Horus(CONFIG) as bot, aiohttp.ClientSession() as session:
        bot.db = db
        bot.session = session
        bot.vac_api = vacefron.Client(session=bot.session)

        await bot.start(CONFIG["TOKEN"], reconnect=True)


if __name__ == "__main__":
    try:
        import uvloop
    except ImportError:
        logging.info("UV loop could not be imported! Using default Event Loop Policy")
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    try:
        with setup_logging():
            logging.info(" ")
            logging.info("-" * 25 + " Starting a new bot loop " + "-" * 25)
            asyncio.run(startup())

    except KeyboardInterrupt:
        pass
