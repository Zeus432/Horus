import disnake as discord
from disnake.ext import commands

from .converters import format_help

class HelpSelect(discord.ui.Select['HelpView']):
    def __init__(self, embeds: dict, original: str, cog_emojis, bot):
        self.embeds = embeds
        options = [discord.SelectOption(label = option, description = embeds[option][0]['embeds'][0].description or discord.Embed.Empty, default = True if option == original else False, emoji = cog_emojis(bot, option)) for option in embeds]
        super().__init__(placeholder = "Choose a Category", min_values = 1, max_values = 1, options = options, row = 0)

    async def callback(self, interaction: discord.Interaction):
        for option in self.options:
            option.default = True if self.values[0] == option.label else False

        return await interaction.response.edit_message(embeds = self.embeds[self.values[0]]['embeds'], view = self.view)

class HelpView(discord.ui.View):
    def __init__(self, stuff_dict: dict, user: discord.Member, old_self, mapping, bot: commands.Bot, original: str, cog_emojis, timeout: float = 180, dont_delete : bool = False):
        super().__init__(timeout = None if dont_delete else timeout)
        self.user = user
        self.bot = bot
        self.original = original

        self._old_self = old_self
        self._mapping = mapping
        self._cog_emojis = cog_emojis
        self._dont_delete = dont_delete

        self._stuff_dict = stuff_dict
        self._current_list = format_help(stuff_dict[original])

        self.message = None
        self.total_pages = len(self._current_list)
        self.current_page = 1

        for index, item in enumerate(self.children):
            if isinstance(item, discord.ui.Select):
                continue

            if self.total_pages == self.current_page:
                if '►' in item.label:
                    item.disabled = True

            if self.current_page == 1:
                if '◄' in item.label:
                    item.disabled = True
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user.id:
            return True
        
        # new view for user
        self.old_self.context.author = interaction.user
        stuff_list = await self._old_self.get_bot_help(self._mapping)

        embeds_list = {'Main Menu': stuff_list}

        for cog, commands in self.mapping.items():
            filtered = await self.old_self.filter_commands(commands, sort = True)
            if cog is not None and filtered:
                if cog.qualified_name != 'CustomHelp':
                    embeds_list[cog.qualified_name] = await self.old_self.get_cog_help(cog)

        view = HelpView(stuff_dict = embeds_list, user = interaction.user, old_self = self._old_self, mapping = self._mapping, bot = self.bot, original = 'Main Menu', cog_emojis = self._cog_emojis, dont_delete = True)
        await interaction.response.send_message(f"{interaction.user.mention} here is your help menu!", view = view, ephemeral = True, **stuff_list)
    
    @discord.ui.button(label = "◄◄", row = 1)
    async def leftarrow2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "◄", row = 1)
    async def leftarrow1(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page -= 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "►", row = 1)
    async def rightarrow1(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page += 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "►►", row = 1)
    async def rightarrow2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = self.total_pages
        await self.edit_buttons(interaction)
    
    @discord.ui.button(label = "Delete", emoji = "<:TrashCan:873917151961026601>", style = discord.ButtonStyle.red, row = 1)
    async def support_link(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.message.delete()

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message: 
            await self.message.edit(view = self)