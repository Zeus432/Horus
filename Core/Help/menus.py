import discord
from discord.ext import commands

class HelpSelect(discord.ui.Select):
    def __init__(self, embeds: dict[discord.Embed], original: str, get_em):
        self.embeds = embeds
        cog_emojis = {'Main Menu': get_em('core'), 'Admin': get_em('owner'), 'BotStuff' : '\U0001f6e0', 'Fun': get_em('games'), 'Dev': get_em('dev'), 'Sniper' : get_em('lurk'), 'Utility': get_em('utils')}
        options = [discord.SelectOption(label = option, description = embeds[option].description or discord.Embed.Empty, default = True if option == original else False, emoji = cog_emojis[option]) for option in embeds]
        super().__init__(placeholder = "Choose a Category", min_values = 1, max_values = 1, options = options)

    async def callback(self, interaction: discord.Interaction):
        for option in self.options:
            option.default = True if self.values[0] == option.label else False

        return await self.view.message.edit(embed = self.embeds[self.values[0]], view = self.view)
    
class HelpView(discord.ui.View):
    def __init__(self, user: discord.Member, embeds: dict[discord.Embed], original: str, get_em, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.user = user
        self.add_item(HelpSelect(embeds = embeds, original = original, get_em = get_em))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view = self)