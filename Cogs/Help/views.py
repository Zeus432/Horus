import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from typing import Dict, List

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

        await interaction.response.send_message("This is not yours to interact with!", ephemeral = True)
        return False

    @discord.ui.button(label = "Delete", emoji = emojis("trash"), style = discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self) -> None:
        await self.message.edit(view = None)

class HelpView(discord.ui.View):
    def __init__(self, bot: Horus, ctx: HorusCtx, stuff: List[dict], pages: Dict[str, list] = None, timeout: float = 120) -> None:
        super().__init__(timeout = timeout)
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx

        self.stuff = stuff
        self.total_pages = len(stuff)
        self.current_page = 1

        for item in self.children:
            if isinstance(item, discord.ui.Select) or not item.label:
                continue

            if self.total_pages <= self.current_page:
                if "\U000025ba" in item.label:
                    item.disabled = True

            if self.current_page <= 1:
                if "\U000025c4" in item.label:
                    item.disabled = True

        if pages is not None:
            self.add_item(HelpSelect(bot, ctx, pages))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False

    async def edit_buttons(self, interaction: discord.Interaction):
        for item in self.children:
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

class HelpSelect(discord.ui.Select['HelpView']):
    def __init__(self, bot: Horus, ctx: HorusCtx, pages: Dict[str, list] = None):
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.pages = pages

        options = [discord.SelectOption(label = option, description = stuff[1][0]['embeds'][0].description, emoji = getattr(stuff[0], "emote", bot.memoji)) for option, stuff in pages.items()]
        super().__init__(placeholder = "Choose a Category", options = options, row = 0)

    async def callback(self, interaction: discord.Interaction):
        for option in self.options:
            option.default = True if self.values[0] == option.label else False

        self.view.stuff = self.pages[self.values[0]][1]
        self.view.total_pages = len(self.view.stuff)
        self.view.current_page = 1

        for item in self.view.children:
            if isinstance(item, discord.ui.Select) or not item.label:
                continue

            if "\U000025ba" in item.label:
                item.disabled = True if self.view.total_pages <= self.view.current_page else False

            if "\U000025c4" in item.label:
                item.disabled = True if self.view.current_page <= 1 else False

        await interaction.response.edit_message(view = self.view, **self.view.stuff[0])