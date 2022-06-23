import discord
from Core.bot import HorusCtx
from discord.ext import commands

import sys
import os


def get_reply(ctx: HorusCtx) -> discord.Message | discord.DeletedReferencedMessage | None:
    """ Returns the reference to message of given ctx or None """
    if ctx.message.reference:
        return ctx.message.reference.resolved
    return None

def cleanup_code(content: str) -> str:
    """Automatically removes code blocks from the code."""
    if content.startswith("```") and content.endswith("```"):
        num = 6 if content.startswith("```py\n") else (4 if content.startswith("```\n") else 3)
        return content[num:-3]
    else: return content

def restart_program() -> None:
    """ Restart the program """
    python = sys.executable
    os.execl(python, python, * sys.argv)

class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"

class TabularData:
    """ Tabularize given data properly """
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
        """
        Renders a table in rST format.
        Example:
        +-------+-----+
        | Name  | Age |
        +-------+-----+
        | Alice | 24  |
        |  Bob  | 19  |
        +-------+-----+
        """

        sep = "+".join("-" * w for w in self._widths)
        sep = f"+{sep}+"

        to_draw = [sep]

        def get_entry(d):
            elem = "|".join(f"{e:^{self._widths[i]}}" for i, e in enumerate(d))
            return f"|{elem}|"

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return "\n".join(to_draw)