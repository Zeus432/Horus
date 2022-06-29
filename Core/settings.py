import os


os.environ['JISHAKU_NO_UNDERSCORE'] = "True"
os.environ['JISHAKU_HIDE'] = "True"
os.environ['JISHAKU_NO_DM_TRACEBACK'] = "True"

bot_colour = 0x9c9cff # enter bot colour

INITIAL_EXTENSIONS = [
    'Cogs.Admin',
    'Cogs.BotStuff',
    'Cogs.Dev',
    'Cogs.ErrorHandler',
    'Cogs.Help',
    'Cogs.Listeners',
    'Cogs.Utility'
]