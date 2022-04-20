import disnake
from disnake.ext import commands

import asyncio

class Pagination(disnake.ui.View):
    def __init__(self, embeds: list, bot: commands.Bot, user: disnake.User | disnake.Member, current_page:int = 1, timeout: int = 180):
        super().__init__(timeout = timeout)
        self.user = user
        self.bot = bot
        self.message: disnake.Message
        self._yet_to_respond = False
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

    async def edit_buttons(self, interaction: disnake.Interaction):
        for item in self.children:
            if '►' in item.label:
                item.disabled = True if self.current_page >= self.total_pages else False

            if '◄' in item.label:
                item.disabled = True if self.current_page <= 1 else False
            
            if '/' in item.label:
                item.label = f"{self.current_page}/{self.total_pages}"

        embed = self.embeds[self.current_page - 1]
        await interaction.message.edit(embed = embed, view = self)

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True
        return await interaction.response.send_message('This is not your button to click!', ephemeral = True)

    @disnake.ui.button(label = "◄◄")
    async def leftarrow2(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.current_page = 1
        await self.edit_buttons(interaction)

    @disnake.ui.button(label = "◄")
    async def leftarrow1(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.current_page -= 1
        await self.edit_buttons(interaction)
    
    @disnake.ui.button(label = "1/1", style = disnake.ButtonStyle.blurple)
    async def go_to_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if self._yet_to_respond is True:
            return await interaction.followup.send('This button can only be used one at time!', ephemeral = False)

        self._yet_to_respond = True
        reply_message = await self.message.reply(content = f'Enter the page you wish to go to: `1` - `{self.total_pages}`')

        def check(message : disnake.Message) -> bool: 
            return message.author.id == self.user.id
        
        try:
            message = await self.bot.wait_for('message', timeout = 30, check = check)
        except asyncio.TimeoutError:
            self._yet_to_respond = False
            return await reply_message.reply(content = 'You took too long to respond!')
        
        try:
            page = int(message.content)
        except ValueError:
            await message.reply(content = 'That is not a page number!', mention_author = False)
        
        else:
            if page > self.total_pages or page < 1:
                await message.reply(content = f'You can only enter a page number between `1` and `{self.total_pages}`!', mention_author = False)
            
            elif self.current_page == page:
                await message.reply(content = f'You\'re already on page `{page}!`', mention_author = False)
            
            else:
                self.current_page = page
                await self.edit_buttons(interaction)

        self._yet_to_respond = False

    @disnake.ui.button(label = "►")
    async def rightarrow1(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.current_page += 1
        await self.edit_buttons(interaction)

    @disnake.ui.button(label = "►►")
    async def rightarrow2(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.current_page = self.total_pages
        await self.edit_buttons(interaction)
    
    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        
        await self.message.edit(view = self)