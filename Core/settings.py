import os


os.environ['JISHAKU_NO_UNDERSCORE'] = "True"
os.environ['JISHAKU_HIDE'] = "True"
os.environ['JISHAKU_NO_DM_TRACEBACK'] = "True"

INITIAL_EXTENSIONS = [
    'Cogs.Admin',
    'Cogs.BotStuff',
    'Cogs.Dev',
    'Cogs.Listeners',
    'Cogs.Utility'
]