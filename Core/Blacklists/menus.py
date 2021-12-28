import disnake
from disnake.ext import commands

class ConfirmBl(disnake.ui.View):
    def __init__(self, what: str, action: str, user: disnake.Member, timeout: float = 30):
        super().__init__(timeout = timeout)
        self.user = user
        self.what = what
        self.action = action
        self.value = None
    
    async def disableall(self, style: disnake.ButtonStyle):
        for item in self.children:
            item.style = disnake.ButtonStyle.gray if item.style != style else style
            item.disabled = True
    
    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        if interaction.user.id == self.user.id:
            return True
        return await interaction.response.defer()
    
    @disnake.ui.button(label = "Confirm", style = disnake.ButtonStyle.blurple)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.value = True
        self.stop()
        await self.disableall(button.style)
        await self.message.edit(f'`{self.what}` has been {self.action}ed!', view = self)
    
    @disnake.ui.button(label = "Cancel", style = disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.stop()
        await self.disableall(button.style)
        await self.message.edit(f"Cancelled {self.action}ing `{self.what}`", view = self)
    
    async def on_timeout(self):
        await self.message.edit(content = "You took too long to respond!")
        await self.disableall(disnake.ButtonStyle.red)
        await self.message.edit(content = "You took too long to respond!", view = self)