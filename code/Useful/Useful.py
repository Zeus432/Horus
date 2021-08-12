from discord.ext import commands
from typing import Union, Tuple, Optional
import discord
import datetime
import traceback
import sys
import pathlib

class BaseEmbed(discord.Embed):
    """Main purpose is to get the usual setup of Embed for a command or an error embed"""
    def __init__(self, color: Union[discord.Color, int] = 0xffcccb, timestamp: datetime.datetime = None,
                 fields: Tuple[Tuple[str, str]] = (), field_inline: Optional[bool] = False, **kwargs):
        super().__init__(color=color, timestamp=timestamp or discord.utils.utcnow(), **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def default(cls, ctx: commands.Context,color: Union[discord.Color, int] = discord.Color.red(), **kwargs) -> "BaseEmbed":
        instance = cls(color=color,**kwargs)
        instance.set_footer(text=f"User: {ctx.author}", icon_url=ctx.author.avatar)
        return instance

    @classmethod
    def to_error(cls, title: Optional[str] = "Error",
                 color: Union[discord.Color, int] = discord.Color.red(), **kwargs) -> "BaseEmbed":
        return cls(title=title, color=color, **kwargs)

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
    listemoji =  {"menu":"<:HelpMenu:873859534651809832>","error":"<:Error:874511415086551080>","cogs":"<:Cogs:873861289343090718>","tick":"<:tickyes:873865975441813534>","boost":"<a:BoostBadge:873866459451904010>","pray":"<:angelpray:873863602023596082>","study":"<:Study:873863650471981107>","dev":"<a:DevBadge:873866720530534420>","trash":"<:TrashCan:873917151961026601>","kermitslap":"<a:kermitslap:873919390117158922>","tokitosip":"<a:TokitoSip:875425433980645416>"}
    try:
        return listemoji[emoji]
    except:
        return "<:Error:873859732044136469>"

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