import discord
import traceback
import sys
import pathlib
import json
import datetime
from dateutil.relativedelta import relativedelta
import aiohttp

def print_exception(text: str, error: Exception, *, _print: bool = False) -> str:
        """Prints the exception with proper traceback."""
        if _print:
            print(text, file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        etype = type(error)
        trace = error.__traceback__
        lines = traceback.format_exception(etype, error, trace)
        return "".join(lines)

def botemojis(emoji = None):
    with open("/Users/siddharthm/Desktop/Horus/Assets/emojis.json","r") as emojis:
        listemoji = json.loads(emojis.read())
    try:
        return listemoji[emoji]
    except:
        return listemoji['error']

class HelpButtons(discord.ui.View):
    def __init__(self, timeout:int, **kwargs):
        super().__init__(timeout=timeout, **kwargs)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji = botemojis("trash"))
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()

def fileanalytics():
    p = pathlib.Path('./')
    cm = cr = fn = cl = ls = fc = 0
    for f in p.rglob('*.py'):
        if str(f).startswith("venv"):
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
    return [fc,ls,cl,fn,cr,cm,f"file: {fc}\nline: {ls:,}\nclass: {cl}\nfunction: {fn}\ncoroutine: {cr}\ncomment: {cm:,}"]
    #returns in order 1. Files, 2. Lines, 3. Classes, 4.Functions, 5.Coroutines, 6.Comments, 7.The whole thing together

def woodlands_only(ctx):
    hidecmd = True if ctx.guild.id in [809632911690039307,844164205418512424] else False
    return hidecmd

class plural:
    def __init__(self, value):
        self.value = value
    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'

class TabularData:
    def __init__(self):
        self._widths = []
        self._columns = []
        self._rows = []

    def set_columns(self, columns):
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row):
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 2
            if width > self._widths[index]:
                self._widths[index] = width

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def render(self):
        """Renders a table in rST format.
        Example:
        +-------+-----+
        | Name  | Age |
        +-------+-----+
        | Alice | 24  |
        |  Bob  | 19  |
        +-------+-----+
        """

        sep = '+'.join('-' * w for w in self._widths)
        sep = f'+{sep}+'

        to_draw = [sep]

        def get_entry(d):
            elem = '|'.join(f'{e:^{self._widths[i]}}' for i, e in enumerate(d))
            return f'|{elem}|'

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return '\n'.join(to_draw)

def get_uptime(bot):
        delta_uptime = relativedelta(datetime.datetime.utcnow(), bot.launch_time)
        days, hours, minutes, seconds = delta_uptime.days, delta_uptime.hours, delta_uptime.minutes, delta_uptime.seconds

        uptimes = {x[0]: x[1] for x in [('days, ' if days != 1 else 'day, ', days), ('hours, ' if hours != 1 else 'hour, ', hours),
                                        ('minutes' if minutes != 1 else 'minute', minutes), ('seconds' if seconds != 1 else 'second', seconds)] if x[1]}

        last = " ".join(value for index, value in enumerate(uptimes.keys()) if index == len(uptimes)-1)
        uptime_string = "".join(
            f"{v} {k}" if k != last else f" and {v} {k}" if len(uptimes) != 1 else f"{v} {k}"
            for k, v in uptimes.items()
        )
        return uptime_string

async def mystbin(data):
      data = bytes(data, 'utf-8')
      async with aiohttp.ClientSession() as cs:
        async with cs.post('https://mystb.in/documents', data = data) as r:
          res = await r.json()
          key = res["key"]
          return f"https://mystb.in/{key}"