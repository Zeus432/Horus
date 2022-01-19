import disnake as discord
from disnake.ext import commands

class TestPagination(discord.ui.View):
    def __init__(self, embeds: list, user, current_page:int = 1):
        super().__init__(timeout = None)
        self.user = user
        self.embeds = embeds
        self.total_pages = len(embeds)
        self.current_page = current_page

        for item in self.children:
            if self.current_page == self.total_pages:
                if '►' in item.label:
                    item.disabled = True

            if self.current_page == 1:
                if '◄' in item.label:
                    item.disabled = True

    async def edit_buttons(self, interaction: discord.Interaction):
        for item in self.children:
            if '►' in item.label:
                item.disabled = True if self.current_page >= self.total_pages else False

            if '◄' in item.label:
                item.disabled = True if self.current_page <= 1 else False

        embed = self.embeds[self.current_page - 1]
        await interaction.message.edit(embed = embed, view = self)

    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True
        return await interaction.response.send_message('This is not your button to click!', ephemeral = True)

    @discord.ui.button(label = "◄◄")
    async def leftarrow2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "◄")
    async def leftarrow1(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page -= 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "►")
    async def rightarrow1(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page += 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "►►")
    async def rightarrow2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = self.total_pages
        await self.edit_buttons(interaction)