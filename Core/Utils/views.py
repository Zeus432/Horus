import disnake
from .useful import CheckAsync

class Confirm(disnake.ui.View):
    """ Global Confirm View can be used by inputting functions """
    def __init__(self, onconfirm: CheckAsync, oncancel: CheckAsync, ontimeout: CheckAsync, timeout: float = 180.0, **kwargs):
        super().__init__(timeout=timeout)
        self.onconfirm = onconfirm
        self.oncancel = oncancel
        self.ontimeout = ontimeout
        self.kwargs = kwargs
    
    @disnake.ui.button(label='Confirm', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.onconfirm(self, button, interaction)
    
    @disnake.ui.button(label='Cancel', style=disnake.ButtonStyle.grey)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.oncancel(self, button, interaction)
    
    async def on_timeout(self):
        await self.ontimeout(self)