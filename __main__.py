from Core.bot import Horus
import asyncio
import aiohttp

from Core.Utils.functions import load_toml

CONFIG = load_toml('Core/config.toml')

bot = Horus(CONFIG)

async def startup():
    async with bot, aiohttp.ClientSession() as session:
        bot.session = session

        await bot.start(CONFIG["TOKEN"], reconnect = True)


if __name__ == "__main__":
    asyncio.run(startup())
