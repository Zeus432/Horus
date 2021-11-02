from discord.ext import commands

from dateutil.relativedelta import relativedelta
from datetime import datetime
import os

def get_uptime(bot: commands.Bot) -> str:
    """ Get Bot Uptime in a neatly converted string """
    delta_uptime = relativedelta(datetime.now(), bot.launch_time)
    days, hours, minutes, seconds = delta_uptime.days, delta_uptime.hours, delta_uptime.minutes, delta_uptime.seconds

    uptimes = {x[0]: x[1] for x in [('day', days), ('hour', hours), ('minute', minutes), ('second', seconds)] if x[1]}
    l = len(uptimes) 

    last = " ".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes)-1)

    uptime_string = ", ".join(
        f"{uptimes[value]} {value}{'s' if uptimes[value] > 1 else ''}" for index, value in enumerate(uptimes.keys()) if index != l-1
    )
    uptime_string += f" and {uptimes[last]}" if l > 1 else f"{uptimes[last]}"
    uptime_string += f" {last}{'s' if uptimes[last] > 1 else ''}"
        
    return uptime_string

def total_stuff(root: str, /) -> int:
    """ Get number of python files and sum of lines in a certain directory"""
    lines = files = 0
    for x in os.listdir(root):
        if os.path.isdir(x):
            result = total_stuff(root + "/" + x)
            files += result[0]
            lines += result[1]
        else:
            if x.endswith((".py")):
                files += 1
                with open(f"{root}/{x}") as r:
                    lines += len(r.readlines())
    return [files, lines]