from loguru import logger
import pathlib

from bot import Horus

from Core.Utils.useful import load_json

CONFIG = load_json('Core/config.json')
TOKEN = CONFIG['TOKEN']

rootdir = pathlib.Path(__file__).parent.resolve()

# Loggers help keep your console from being flooded with Errors, you can instead send them to a file which you can check later
logger.remove()
logger.add(f'{rootdir}/Core/Horus.log', level = "DEBUG", format = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

if __name__ == "__main__":
    horus = Horus(CONFIG)
    horus.starter()