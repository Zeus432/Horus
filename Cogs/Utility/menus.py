from datetime import datetime
from typing import List
import discord
from discord.ext import commands
from discord.member import Member

class PollButton(discord.ui.Button):
    def __init__(self, number: int, bot: commands.Bot, yesno: bool):
        self.option = ['tick', 'cross'][number - 1] if yesno else number
        self.bot = bot
        self.opt_emoji = bot.get_em(self.option)
        super().__init__(style = discord.ButtonStyle.gray, emoji = self.opt_emoji)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.view.voter_list:
            self.view.count[self.view.voter_list[interaction.user.id]] -= 1

            if self.view.voter_list[interaction.user.id] == self.option:
                del self.view.voter_list[interaction.user.id]
                await interaction.response.send_message(f"Your vote for {self.opt_emoji} has been removed", ephemeral = True)
            
            else:
                oldvote = self.bot.get_em(self.view.voter_list[interaction.user.id])
                self.view.voter_list[interaction.user.id] = self.option
                self.view.count[self.option] += 1
                await interaction.response.send_message(f"Your vote has been changed {oldvote} from to {self.opt_emoji}", ephemeral = True)
        
        else:
            self.view.voter_list[interaction.user.id] = self.option
            self.view.count[self.option] += 1
            await interaction.response.send_message(f"Your vote for {self.opt_emoji} has been counted", ephemeral = True)
        
        # Now change the visible poll to show new vote rankings
        newmessage = self.view.content + '\n\n' + '\U000030fb'.join([f'{self.bot.get_em(value)}: `{self.view.count[value]}` ' for value in  self.view.count]) + f"\n\nPoll ends on <t:{self.view.endtime}:F> (<t:{self.view.endtime}:R>)"
        await self.view.message.edit(f"{newmessage}", allowed_mentions = discord.AllowedMentions.none())

class PollMenu(discord.ui.View):
    def __init__(self, options: int, content: str, endtime: int, bot: commands.Bot, ctx: commands.Context, timeout: float = 180, yesno: bool = False):
        super().__init__(timeout = timeout)
        self.content = content
        self.bot = bot
        self.ctx = ctx
        self.endtime = endtime
        self.count, self.voter_list = {}, {}

        for num in range(1, options + 1):
            self.count[['tick', 'cross'][num - 1] if yesno else num] = 0
            self.add_item(PollButton(number = num, bot = self.bot, yesno = yesno))
    
    async def endpoll(self):
        for item in self.children:
            item.disabled = True
        newmessage = self.content + '\n\n' + '\U000030fb'.join([f'{self.bot.get_em(value)}: `{self.count[value]}` ' for value in  self.count]) + f"\n\nPoll Closed! (<t:{int(datetime.now().timestamp())}:F>)"
        await self.message.edit(f"{newmessage}", view = self, allowed_mentions = discord.AllowedMentions.none())
        result = '\n'.join([f'{self.bot.get_em(value)}: `{self.count[value]}` ' for value in  self.count if self.count[value]])
        await self.message.reply(f"**Poll Result:**\n" + result if result else "Poll closed with zero votes!")
    
    @discord.ui.button(label = "Close Poll", style = discord.ButtonStyle.red, row = 3)
    async def ClosePoll(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message(f"Only the owner of this poll ({self.user.mention}) can close this poll", ephemeral = True)
        self.stop()
        await self.endpoll()
    
    async def on_timeout(self):
        await self.endpoll()

class ConfirmClear(discord.ui.View):
    def __init__(self, user: discord.Member):
        super().__init__(timeout = 10)
        self.value = None
        self.user = user
    
    async def disableall(self, label: discord.ButtonStyle):
        for item in self.children:
            item.style = discord.ButtonStyle.gray if item.style != label else label
            item.disabled = True
    
    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        await self.message.edit('I have cleared your todo list!')
        self.value = True
        self.stop()
        await self.disableall(button.label)
    
    @discord.ui.button(label = "Cancel", style = discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        await self.message.edit("Alright I won't clear your todo list then")
        self.stop()
        await self.disableall(button.label)
    
    async def on_timeout(self):
        await self.message.edit("Alright I won't clear your todo list then")
        await self.disableall(discord.ButtonStyle.red)