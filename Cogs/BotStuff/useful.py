from discord.ext import commands

import matplotlib.figure
import io
import os

def total_stuff(root: str) -> int:
    lines, files = 0, 0
    fl = [file for file in os.listdir(f'{root}')]
    for file in os.listdir(f'{root}'):
        if os.path.isdir(f"{root}/{file}"):
            result = total_stuff(root = f"{root}/{file}")
            files += result[0]
            lines += result[1]
        else:
            if file.endswith('.py'):
                with open(f"{root}/{file}") as r:
                    lines += len(r.readlines())
                    files += 1

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