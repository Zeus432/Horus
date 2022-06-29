import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

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
    
    async def on_timeout(self) -> None:
        await self.message.edit(view = None)