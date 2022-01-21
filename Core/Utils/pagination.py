import disnake as discord
from disnake.ext import commands

import asyncio

class TestPagination(discord.ui.View):
    def __init__(self, embeds: list, bot: commands.Bot, user: discord.User | discord.Member, current_page:int = 1):
        super().__init__(timeout = None)
        self.user = user
        self.bot = bot
        self.message: discord.Message
        self.embeds = embeds
        self.total_pages = len(embeds)
        self.current_page = current_page

        for item in self.children:
            if self.current_page == self.total_pages:
                if '►' in item.label:
                    item.disabled = True

            if self.current_page == 1:
                if '◄' in item.label:
                    item.disabled = True
            
            if '1/1' in item.label:
                item.label = f"{self.current_page}/{self.total_pages}"
                item.disabled = False if self.total_pages > 1 else True

    async def edit_buttons(self, interaction: discord.Interaction):
        for item in self.children:
            if '►' in item.label:
                item.disabled = True if self.current_page >= self.total_pages else False

            if '◄' in item.label:
                item.disabled = True if self.current_page <= 1 else False

        embed = self.embeds[self.current_page - 1]
        await interaction.message.edit(embed = embed, view = self)

    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True
        return await interaction.response.send_message('This is not your button to click!', ephemeral = True)

    @discord.ui.button(label = "◄◄")
    async def leftarrow2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "◄")
    async def leftarrow1(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page -= 1
        await self.edit_buttons(interaction)
    
    @discord.ui.button(label = "1/1", style = discord.ButtonStyle.blurple)
    async def go_to_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        reply_message = await self.message.reply(content = f'Enter the page you wish to go to: `1` - `{self.total_pages}`')

        def check(message : discord.Message) -> bool: 
            return message.author.id == self.user.id
        
        try:
            message = await self.bot.wait_for('message', timeout = 30, check = check)
        except asyncio.TimeoutError:
            return await reply_message.reply(content = 'You took too long to respond!')
        
        try:
            page = int(message.content)
        except ValueError:
            return await message.reply(content = 'That is not a page number!', mention_author = False)
        
        if page > self.total_pages or page < 1:
            return await message.reply(content = f'You can only enter a page number between `1` and `{self.total_pages}`!', mention_author = False)
        
        self.current_page = page
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "►")
    async def rightarrow1(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page += 1
        await self.edit_buttons(interaction)

    @discord.ui.button(label = "►►")
    async def rightarrow2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = self.total_pages
        await self.edit_buttons(interaction)