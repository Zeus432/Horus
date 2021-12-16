import discord
from discord.ext import commands

class HelpSelect(discord.ui.Select):
    def __init__(self, embeds: dict[discord.Embed], original: str):
        self.embeds = embeds
        options = [discord.SelectOption(label = option, description = option, default = True if option == original else False) for option in embeds]
        super().__init__(placeholder = "Choose a Category", min_values = 1, max_values = 1, options = options)

    async def callback(self, interaction: discord.Interaction):
        for option in self.options:
            option.default = True if self.values[0] == option.label else False

        return await self.view.message.edit(embed = self.embeds[self.values[0]], view = self.view)
    
class HelpView(discord.ui.View):
    def __init__(self, user: discord.Member, embeds: dict[discord.Embed], original: str, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.add_item(HelpSelect(embeds = embeds, original = original))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view = self)