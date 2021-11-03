from discord.ext import commands

from dateutil.relativedelta import relativedelta
from datetime import datetime
import os

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