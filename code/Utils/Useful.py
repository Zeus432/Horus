import discord
import traceback
import sys
import pathlib

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
    listemoji =  {"menu":"<:HelpMenu:873859534651809832>","error":"<:warning:879672016704258078>","cogs":"<:Cogs:873861289343090718>","tick":"<:tickyes:873865975441813534>","cross":"<:crossno:879671980691972137>",
                  "boost":"<a:BoostBadge:873866459451904010>","pray":"<:angelpray:873863602023596082>","study":"<:Study:873863650471981107>","dev":"<a:DevBadge:873866720530534420>",
                  "trash":"<:TrashCan:873917151961026601>","kermitslap":"<a:kermitslap:873919390117158922>","tokitosip":"<a:TokitoSip:875425433980645416>",
                  "text":"<:Text:875775212648529950>","voice":"<:Voice:875775169375903745>","stage":"<:Stage:875775175965167708>","replycont":"<:replycont:875990141427146772>","replyend":"<:replyend:875990157554237490>",
                  "parrow":"<:parrowright:872774335675375649>","shinobubully":"<:shinobubully:849249987417997323>","yikes":"<:Yikes:877267180662714428>","pandahug":"<a:pandahug:877267922282749952>",
                  "apos":"<:AphosHoardingCats:877268478493597696>","shadowz":"<a:shadowzcat:877269423025684561>","owner":"<:owner:877271761710878740>","rooburn":"<a:rooburn:873586500518948884>",
                  "judge":"<:judge:877796702633996288>","staff":"<:Staff:877796922876919808>","UNSC":"<:UNSC:877810185954017350> ","UNHRC":"<:UNHRC:877810210650091520>","WHO":"<:WHO:877810579845283870>",
                  "IPC":"<:IPC:877810993621782529>","mod":"<:Moderator:877796954011222047>"
                  }
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