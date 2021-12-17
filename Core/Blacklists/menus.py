import discord
from discord.ext import commands

class ConfirmBl(discord.ui.View):
    def __init__(self, what: str, action: str, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.what = what
        self.action = action
    
    async def disableall(self, style: discord.ButtonStyle):
        for item in self.children:
            item.style = discord.ButtonStyle.gray if item.style != style else style
            item.disabled = True
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id
    
    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.message.edit(f'`{self.what}` has been {self.action}!')
        self.value = True
        self.stop()
        await self.disableall(button.style)
    
    @discord.ui.button(label = "Cancel", style = discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.message.edit(f"Cancelled {self.action}ing `{self.what}`")
        self.stop()
        await self.disableall(button.style)
    
    async def on_timeout(self):
        await self.message.edit("You took too long to respond!")
        await self.disableall(discord.ButtonStyle.red)