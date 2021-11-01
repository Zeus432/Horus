import discord
from discord.ext import commands

import asyncio

from Core.Utils.useful import try_add_reaction

def cleanup_code(content) -> str:
    """Automatically removes code blocks from the code."""
    if content.startswith('```') and content.endswith('```'):
        num = 6 if content.startswith('```py\n') else (4 if content.startswith('```\n') else 3)
        return content[num:-3]
    else: return content
    
def get_syntax_error(error) -> str:
    if error.text is None:
        return f'```py\n{error.__class__.__name__}: {error}\n```'
    return f'```py\n{error.text}{"^":>{error.offset}}\n{error.__class__.__name__}: {error}```'

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

class ConfirmLeave(discord.ui.View):
    def __init__(self, ctx: commands.Context, guild: discord.Guild, bot: commands.Bot, timeout: float = 180.0) -> bool:
        super().__init__(timeout = timeout)
        self.ctx = ctx
        self.guild = guild
        self.bot = bot
        self.value = None
    
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
                return
        for item in self.children:
            item.disabled = True
        button.style = discord.ButtonStyle.green
        try:
            await self.guild.leave()
        except:
            button.style = discord.ButtonStyle.red
            await interaction.message.edit(embed = discord.Embed(description = f"I was unable to leave **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})**!", color = discord.Colour.red()), view = self)
            await try_add_reaction(self.ctx.message, self.bot.get_em('tick'))
        else:
            self.value = True
            await interaction.message.edit(embed = discord.Embed(description = f"I have left **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})**, sucks for them {self.bot.get_em('shinobubully')}", color = discord.Colour.green()), view = self)
            await try_add_reaction(self.ctx.message, self.bot.get_em('tick'))
        self.stop()

    @discord.ui.button(label='Cancel', style = discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item == button else discord.ButtonStyle.gray
        self.value = False
        await interaction.message.edit(embed = discord.Embed(description = f"Guess I'm not leaving **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})** today", colour = discord.Colour.red()), view = self)
        self.stop()
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item.label == "Cancel" else discord.ButtonStyle.gray
        self.value = False
        await self.message.edit(embed = discord.Embed(description = f"You took too long to respond!", colour = discord.Colour.red()), view = self)

class WhoAsked(discord.ui.View):
    def __init__(self, *, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.playing = False
    
    async def playmusic(self):
        self.playing = True
        timeline = ['0:00', '1:19', '1:55', '2:37', '3:56']

        for item in self.children:
            if item.custom_id == "time":
                button = item
            if item.custom_id == "play":
                playpause = item

        playpause.label = "▐▐"
        for x in range(5):
            await asyncio.sleep(1)
            try:
                button.label = f"{timeline[x]} / 3:56"
                await self.message.edit("Now playing: \nWho Asked (Feat. Nobody Did)\n"+"────"*x + "⬤" + "────"*(4-x), view = self)
            except: pass
        
        playpause.label = "▶"
        self.playing = False
        await self.message.edit(view = self)

    @discord.ui.button(label = "◄◄", style = discord.ButtonStyle.gray, custom_id = 'prevtrack')
    async def prevtrack(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label = "▶", style = discord.ButtonStyle.gray, custom_id = 'play')
    async def play(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.playing:
            return
        await interaction.response.defer()
        await self.playmusic()

    @discord.ui.button(label = "►►", style = discord.ButtonStyle.gray, custom_id = 'nextrack')
    async def nexttrack(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label = "0:00 / 3:56", style = discord.ButtonStyle.gray, custom_id = 'time')
    async def time(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label= "━━━━━◉", emoji = "\U0001f50a", style = discord.ButtonStyle.gray, custom_id = 'sound')
    async def sound(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.label = "◉━━━━━" if button.label == "━━━━━◉" else "━━━━━◉"
        button.emoji = "\U0001f507" if button.label != "━━━━━◉" else "\U0001f50a"
        await self.message.edit(view = self)