import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from typing import List

from Core.Utils.functions import emojis


class DeleteButton(discord.ui.View):
    """ A view for deleting the msg """
    def __init__(self, ctx: HorusCtx, timeout: float = 30) -> None:
        super().__init__(timeout = timeout)
        self.user = ctx.author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False

    @discord.ui.button(label = "Delete", emoji = emojis("trash"), style = discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self) -> None:
        await self.message.edit(view = None)

class HelpView(discord.ui.View):
    def __init__(self, bot: Horus, ctx: HorusCtx, stuff: List[dict], select: bool = True, timeout: float = 120) -> None:
        super().__init__(timeout = timeout)
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx

        self.stuff = stuff
        self.total_pages = len(stuff)
        self.current_page = 1

        for index, item in enumerate(self.children):
            if isinstance(item, discord.ui.Select) or not item.label:
                continue

            if self.total_pages <= self.current_page:
                if "\U000025ba" in item.label:
                    item.disabled = True

            if self.current_page <= 1:
                if "\U000025c4" in item.label:
                    item.disabled = True

        if select is True:
            0 # do stuff

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False

    async def edit_buttons(self, interaction: discord.Interaction):
        for index, item in enumerate(self.children):
            if isinstance(item, discord.ui.Select) or not item.label:
                continue

            if "\U000025ba" in item.label:
                item.disabled = True if self.total_pages <= self.current_page else False

            if "\U000025c4" in item.label:
                item.disabled = True if self.current_page <= 1 else False

        await interaction.response.edit_message(**self.stuff[self.current_page - 1], view = self)

    @discord.ui.button(label = "\U000025c4\U000025c4", row = 1)
    async def leftarrow2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "\U000025c4", row = 1)
    async def leftarrow1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "\U000025ba", row = 1)
    async def rightarrow1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "\U000025ba\U000025ba", row = 1)
    async def rightarrow2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = self.total_pages
        await self.edit_buttons(interaction)

    @discord.ui.button(emoji = emojis("trash"), style = discord.ButtonStyle.red, row = 1)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

        await self.message.edit(view = self)