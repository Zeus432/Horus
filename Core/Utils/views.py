import discord
from .useful import CheckAsync

class Confirm(discord.ui.View):
    def __init__(self, onconfirm: CheckAsync, oncancel: CheckAsync, ontimeout: CheckAsync, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.onconfirm = onconfirm
        self.oncancel = oncancel
        self.ontimeout = ontimeout
    
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.onconfirm(self, button, interaction)
    
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.oncancel(self, button, interaction)
    
    async def on_timeout(self):
        await self.ontimeout(self)