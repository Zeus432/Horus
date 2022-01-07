import disnake as discord
from disnake.ext import commands

class HelpSelect(discord.ui.Select['HelpView']):
    def __init__(self, embeds: dict[discord.Embed], original: str, cog_emojis, bot):
        self.embeds = embeds
        options = [discord.SelectOption(label = option, description = embeds[option].description or discord.Embed.Empty, default = True if option == original else False, emoji = cog_emojis(bot, option)) for option in embeds]
        super().__init__(placeholder = "Choose a Category", min_values = 1, max_values = 1, options = options)

    async def callback(self, interaction: discord.Interaction):
        for option in self.options:
            option.default = True if self.values[0] == option.label else False

        return await interaction.response.edit_message(embed = self.embeds[self.values[0]], view = self.view)
    
class HelpView(discord.ui.View):
    def __init__(self, user: discord.Member, embeds: dict[discord.Embed], old_self, mapping, original: str, cog_emojis, bot: commands.Bot, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.user = user
        self.old_self = old_self
        self.cog_emojis = cog_emojis
        self.bot = bot
        self.mapping = mapping
        self.add_item(HelpSelect(embeds = embeds, original = original, cog_emojis = cog_emojis, bot = bot))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user.id:
            return True

        #return await interaction.response.send_message('Not your help menu to interact with!', ephemeral = True)
        self.old_self.context.author = interaction.user
        embed = await self.old_self.get_bot_help(self.mapping)

        embeds_list = {'Main Menu': embed}

        for cog, commands in self.mapping.items():
            filtered = await self.old_self.filter_commands(commands, sort = True)
            if cog is not None and filtered:
                if cog.qualified_name != 'CustomHelp':
                    embeds_list[cog.qualified_name] = await self.old_self.get_cog_help(cog)
        
        view = HelpView(user = interaction.user, embeds = embeds_list, original = 'Main Menu', cog_emojis = self.cog_emojis, old_self = self.old_self, bot = self.bot, mapping = self.mapping)
        view.message = await interaction.response.send_message(f"{interaction.user.mention} here is your help menu!", embed = embed, view = view, ephemeral = True)

    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try: await self.message.edit(view = self)
        except: pass