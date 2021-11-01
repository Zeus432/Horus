import discord
from discord.ext import commands

from dateutil.relativedelta import relativedelta
import asyncio
import datetime
import json

def load_json(file: str) -> dict:
    with open(file, encoding = 'utf-8') as newfile:
        return json.load(newfile)


def write_json(file: str, contents: dict) -> None:
    with open(file, 'w') as newfile:
        json.dump(contents, newfile, ensure_ascii = True, indent = 4)

def get_uptime(bot: commands.Bot) -> str:
    delta_uptime = relativedelta(datetime.datetime.now(), bot.launch_time)
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

class CheckAsync(commands.Converter):
    async def isAsync(self, ctx: commands.Context, argument):
        if asyncio.iscoroutinefunction(self):
            return self
        raise commands.BadArgument("Argument is meant to be a coroutine function!")

async def try_add_reaction(message: discord.Message, emoji: str):
    try:
        await message.add_reaction(emoji)
    except:
        pass