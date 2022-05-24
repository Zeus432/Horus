import discord
from Core.bot import Horus, HorusCtx
from discord.ext import commands


class ConfirmShutdown(discord.ui.View):
    """ A view for confirming shutdown """
    def __init__(self, bot: Horus, ctx: HorusCtx, timeout: float = 30.0, **kwargs) -> None:
        super().__init__(timeout = timeout)
        self.kwargs = kwargs
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
    
    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True
        
        await interaction.response.send_message('This is not your button to click!', ephemeral = True)
        return False
    
    @discord.ui.button(label = 'Confirm', style = discord.ButtonStyle.green)
    async def confirm(self,  interaction: discord.Interaction, button: discord.ui.Button):
        await self.message.edit(content = "https://tenor.com/view/nick-fury-mother-damn-it-gone-bye-bye-gif-16387502", view = None)
        await self.ctx.try_add_reaction("<:TickYes:904315692311011360>")
        self.stop()
        await self.bot.close()
    
    @discord.ui.button(label = 'Cancel', style = discord.ButtonStyle.grey)
    async def cancel(self,  interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item.label == button.label else discord.ButtonStyle.gray 
        self.stop()
        await self.message.edit(content = "Cancelled Shutdown...", view = self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item.label == "Cancel" else discord.ButtonStyle.gray 
        await self.message.edit(content = "Decide faster next time", view = self)