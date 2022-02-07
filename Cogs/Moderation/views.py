import disnake as discord
from disnake.ext import commands
from numpy import True_

class ConfirmElection(discord.ui.View):
    def __init__(self, user: discord.Member, timeout: float = 30):
        super().__init__(timeout = timeout)
        self.user = user
        self.value = None
    
    async def disableall(self, style: discord.ButtonStyle):
        for item in self.children:
            item.style = discord.ButtonStyle.gray if item.style != style else style
            item.disabled = True
        await self.message.edit(view = self)
        self.stop()
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user.id or self.value is None:
            await interaction.response.defer()
            return True
        return await interaction.response.defer()
    
    @discord.ui.button(label = "Start Election", style = discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        await self.disableall(button.style)

    @discord.ui.button(label = "Cancel", style = discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        await self.disableall(button.style)
    
    async def on_timeout(self):
        await self.disableall(discord.ButtonStyle.red)