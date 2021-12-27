import disnake
from disnake.ext import commands

class HelpSelect(disnake.ui.Select['HelpView']):
    def __init__(self, embeds: dict[disnake.Embed], original: str, get_em):
        self.embeds = embeds
        cog_emojis = {'Main Menu': get_em('core'), 'Admin': get_em('owner'), 'BotStuff' : '\U0001f6e0', 'Fun': get_em('games'), 'Dev': get_em('dev'), 'Sniper' : get_em('lurk'), 'Utility': get_em('utils'), 'Blacklists': '\U00002692'}
        options = [disnake.SelectOption(label = option, description = embeds[option].description or disnake.Embed.Empty, default = True if option == original else False, emoji = cog_emojis[option]) for option in embeds]
        super().__init__(placeholder = "Choose a Category", min_values = 1, max_values = 1, options = options)

    async def callback(self, interaction: disnake.Interaction):
        for option in self.options:
            option.default = True if self.values[0] == option.label else False

        return await interaction.response.edit_message(embed = self.embeds[self.values[0]], view = self.view)
    
class HelpView(disnake.ui.View):
    def __init__(self, user: disnake.Member, embeds: dict[disnake.Embed], old_self, mapping, original: str, get_em, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.user = user
        self.old_self = old_self
        self.mapping = mapping
        self.add_item(HelpSelect(embeds = embeds, original = original, get_em = get_em))
    
    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
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
        
        view = HelpView(user = interaction.user, embeds = embeds_list, original = 'Main Menu', get_em = self.old_self.context.bot.get_em, old_self = self.old_self, mapping = self.mapping)
        view.message = await interaction.response.send_message(f"{interaction.user.mention} here is your help menu!", embed = embed, view = view, ephemeral = True)

    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try: await self.message.edit(view = self)
        except: pass