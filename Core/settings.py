import os

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

INITIAL_EXTENSIONS = [
    'Cogs.Admin',
    'Cogs.BotStuff',
    'Cogs.ButtonRoles',
    'Cogs.Fun',
    'Cogs.Dev',
    'Cogs.ImageApi',
    'Cogs.Moderation',
    'Cogs.Utility',
    'jishaku',
    'Core.Blacklists',
    'Core.ErrorHandler',
    'Core.Help',
    'Core.Listeners'
]

OWNER_IDS = frozenset({760823877034573864, 401717120918093846})

BOTMODS = []