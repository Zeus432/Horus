import discord
from .useful import CheckAsync

class Confirm(discord.ui.View):
    """ Global Confirm View can be used by inputting functions """
    def __init__(self, onconfirm: CheckAsync, oncancel: CheckAsync, ontimeout: CheckAsync, user, timeout: float = 180.0, **kwargs):
        super().__init__(timeout=timeout)
        self.onconfirm = onconfirm
        self.oncancel = oncancel
        self.ontimeout = ontimeout
        self.kwargs = kwargs
        self.user = user
    
    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if self.user.id == interaction.user.id:
            return True
        return await interaction.response.send_message('This is not your button to click!', ephemeral = True)
    
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.onconfirm(self, button, interaction)
    
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.oncancel(self, button, interaction)
    
    async def on_timeout(self):
        await self.ontimeout(self)