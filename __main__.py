from Core.bot import Horus
from loguru import logger
import vacefron
import asyncio
import aiohttp
import pathlib

from Core.Utils.functions import load_toml


CONFIG = load_toml('Core/config.toml')
rootdir = pathlib.Path(__file__).parent.resolve()

logger.remove() # Loggers help keep your console from being flooded with Errors, you can instead send them to a file which you can check later
logger.add(f'{rootdir}/Core/Horus.log', level = "DEBUG", format = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

bot = Horus(CONFIG)

async def startup():
    async with bot, aiohttp.ClientSession() as session:
        bot.session = session
        bot.vac_api = vacefron.Client(session = bot.session)

        await bot.start(CONFIG['TOKEN'], reconnect = True)


if __name__ == "__main__":
    asyncio.run(startup())
