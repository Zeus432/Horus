import os

INITIAL_EXTENSIONS = [
#    'Cogs.Admin',
    'Cogs.BotStuff',
    'Cogs.ErrorHandler',
    'Cogs.Fun',
    'Cogs.Owner',
    'Cogs.Sniper',
#    'Cogs.Utility',
    'jishaku',
#    'Core.Blacklists',
#    'Core.CustomHelp',
#    'Core.BotListeners'
]

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"