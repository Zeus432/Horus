from disnake.ext import commands

import matplotlib.figure
import pathlib
import io
import os

def total_stuff(root: str) -> int:
    lines, files = 0, 0
    fl = [file for file in os.listdir(f'{root}')]
    for file in os.listdir(f'{root}'):
        if "env" in f"{file}":
            continue # skip if its the env

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

def linecount(path: str = './') -> dict:
    p = pathlib.Path(f'{path}')
    cm = cr = fn = cl = ls = fc = 0
    for f in p.rglob('*.py'):
        if str(f).startswith("horus-env"):
            continue
        fc += 1
        with f.open() as of:
            for l in of.readlines():
                l = l.strip()
                if l.startswith('class'):
                    cl += 1
                if l.startswith('def'):
                    fn += 1
                if l.startswith('async def'):
                    cr += 1
                if '#' in l:
                    cm += 1
                ls += 1
    return {"file": f"{fc}", "line": f"{ls:,}", "class": f"{cl}", "function": f"{fn}", "coroutine": f"{cr}", "comment": f"{cm:,}"}