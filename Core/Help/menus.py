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
    def __init__(self, user: discord.Member, embeds: dict[discord.Embed], old_self, mapping, original: str, cog_emojis, prefix: str, bot: commands.Bot, timeout: float = 180, dont_delete : bool= False):
        super().__init__(timeout = timeout)
        self.user = user
        self.old_self = old_self
        self.cog_emojis = cog_emojis
        self.prefix = prefix
        self.bot = bot
        self.mapping = mapping
        self.message = None
        self.dont_delete = dont_delete
        self.add_item(HelpSelect(embeds = embeds, original = original, cog_emojis = cog_emojis, bot = bot))
        link = discord.ui.Button(style = discord.ButtonStyle.link, label = "Support Server", emoji = "<:hsupport:893556630820618251>", row = 1, url = "https://discord.gg/8BQMHAbJWk")
        self.add_item(link)
        self.children.pop(self.children.index(link))

        for index, item in enumerate(self.children):
            try:
                if item.label == "Syntax Help":
                    self.children.insert(index + 1, link)
            
                if item.label == "Delete":
                    if self.dont_delete is True:
                        self.children.pop(index)
            except: pass
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.message is None:
            self.message = interaction.message

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
        
        view = HelpView(user = interaction.user, embeds = embeds_list, original = 'Main Menu', cog_emojis = self.cog_emojis, old_self = self.old_self, bot = self.bot, prefix = f"{self.prefix}", mapping = self.mapping, dont_delete = True)
        view.message = await interaction.response.send_message(f"{interaction.user.mention} here is your help menu!", embed = embed, view = view, ephemeral = True)
    
    @discord.ui.button(label = "Syntax Help", emoji = "<:HelpMenu:873859534651809832>", style = discord.ButtonStyle.grey, row = 1)
    async def syntax_help(self, button: discord.ui.Button, interaction: discord.Interaction):

        msg = f"""**Important Things to Know**
```yaml
• <argument>         - Argument is required
• [argument]         - Argument is optional
• [argument=default] - Argument is optional and has a default value
• [argument...]      - Argument is optional and can take multiple entries.
• <argument...>      - Argument is required and can take multiple entries.
• [X|Y|Z]            - Argument can be either X, Y or Z```
__**Note:**__ Do not literally type out the `<>`, `[]`, `|`!

Use `{self.prefix}help <command | category>` to get help for any command"""
        view = SyntaxHelp(old_view = self, old_content = interaction.message.content, old_embed = interaction.message.embeds[0], dont_delete = self.dont_delete)

        view.message = await interaction.response.edit_message(content = msg, embed = None, view = view)

    @discord.ui.button(label = "Delete", emoji = "<:TrashCan:873917151961026601>", style = discord.ButtonStyle.red, row = 1)
    async def support_link(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.message.delete()
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try: 
            await self.message.edit(view = self)
        except: 
            await self.clear_items()

class SyntaxHelp(discord.ui.View):
    def __init__(self, old_view: discord.ui.View, old_content: str, old_embed = discord.Embed, dont_delete: bool = False):
        super().__init__(timeout = 60)
        self.old_view = old_view
        self.old_content = old_content
        self.dont_delete = dont_delete
        self.old_embed = old_embed
        self.message = None

        for index, item in enumerate(self.children):
            if item.label == "Delete":
                if self.dont_delete is True:
                    self.children.pop(index)

    
    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if self.message is None:
            self.message = interaction.message

        if interaction.user.id == self.old_view.user.id:
            return True

        return await interaction.response.send_message('Not your button to interact with!', ephemeral = True)
    
    @discord.ui.button(label = "Go Back", style = discord.ButtonStyle.blurple)
    async def go_back(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content = self.old_content, embed = self.old_embed, view = self.old_view)
    
    @discord.ui.button(label = "Delete", emoji = "<:TrashCan:873917151961026601>", style = discord.ButtonStyle.red)
    async def support_link(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.message.delete()
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try: 
            await self.message.edit(view = self)
        except: 
            pass

class DeleteButton(discord.ui.View):
    def __init__(self, user: discord.Member | discord.User):
        super().__init__(timeout = 180)
        self.user = user
    
    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if interaction.user.id == self.user.id:
            return True
        
        return await interaction.response.send_message('Not your button to interact with!', ephemeral = True)
    
    @discord.ui.button(label = "Delete", emoji = "<:TrashCan:873917151961026601>", style = discord.ButtonStyle.red)
    async def support_link(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.message.delete()