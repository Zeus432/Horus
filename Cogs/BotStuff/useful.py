from discord.ext import commands

import matplotlib
import io
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

async def pie_gen(ctx: commands.Context):
    prc = round(sum(m.bot for m in ctx.guild.members) / len(ctx.guild.members) * 100, 3)

    labels = ["Bots", "Non-Bots"]
    sizes = [prc, 100 - prc]
    colors = ["lightcoral", "lightskyblue"]

    fig = matplotlib.figure.Figure(figsize=(5, 5))
    ax = fig.add_subplot()
    patches, _ = ax.pie(sizes, colors=colors, startangle=90)
    ax.legend(patches, labels)

    fp = io.BytesIO()
    fig.savefig(fp)
    fp.seek(0)

    return [fp, prc]