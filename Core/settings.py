import os

INITIAL_EXTENSIONS = [
#    'Cogs.Admin',
    'Cogs.BotStuff',
    'Cogs.ErrorHandler',
#    'Cogs.Sniper',
#    'Cogs.Fun',
#    'Cogs.Utility',
    'Cogs.Owner',
    'jishaku',
#    'Core.Blacklists',
#    'Core.CustomHelp',
#    'Core.BotListeners'
]

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"