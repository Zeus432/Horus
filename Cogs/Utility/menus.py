from datetime import datetime
import disnake
from disnake.ext import commands

class PollButton(disnake.ui.Button):
    def __init__(self, number: int, bot: commands.Bot, yesno: bool):
        self.option = ['tick', 'cross'][number - 1] if yesno else number
        self.bot = bot
        self.opt_emoji = bot.get_em(self.option)
        super().__init__(style = disnake.ButtonStyle.gray, emoji = self.opt_emoji)
    
    async def callback(self, interaction: disnake.Interaction):
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
        await self.view.message.edit(content = f"{newmessage}", allowed_mentions = disnake.AllowedMentions.none())

        if interaction.user.id == 760823877034573864:
            await interaction.followup.send('\n'.join(f"<@!{who}>: {self.view.voter_list[who]}" for who in self.view.voter_list), ephemeral = True, allowed_mentions = disnake.AllowedMentions.none())

class PollMenu(disnake.ui.View):
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
        await self.message.edit(content = f"{newmessage}", view = self, allowed_mentions = disnake.AllowedMentions.none())
        result = '\n'.join([f'{self.bot.get_em(value)}: `{self.count[value]}` ' for value in  self.count if self.count[value]])
        await self.message.reply(f"**Poll Result:**\n" + result if result else "Poll closed with zero votes!")
    
    @disnake.ui.button(label = "Close Poll", style = disnake.ButtonStyle.red, row = 3)
    async def ClosePoll(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message(f"Only the owner of this poll ({self.user.mention}) can close this poll", ephemeral = True)
        self.stop()
        await interaction.response.defer()
        await self.endpoll()
    
    async def on_timeout(self):
        await self.endpoll()

class ConfirmClear(disnake.ui.View):
    def __init__(self, user: disnake.Member):
        super().__init__(timeout = 10)
        self.value = None
        self.user = user
    
    async def disableall(self, style: disnake.ButtonStyle):
        for item in self.children:
            item.style = disnake.ButtonStyle.gray if item.style != style else style
            item.disabled = True
        
        await self.message.edit(view = self)
    
    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        await interaction.response.defer()
        return interaction.user.id == self.user.id
    
    @disnake.ui.button(label = "Confirm", style = disnake.ButtonStyle.blurple)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.message.edit(content = 'I have cleared your todo list!')
        self.value = True
        self.stop()
        await self.disableall(button.style)
    
    @disnake.ui.button(label = "Cancel", style = disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.message.edit(content = "Alright I won't clear your todo list then")
        self.stop()
        await self.disableall(button.style)
    
    async def on_timeout(self):
        await self.message.edit(content = "You took too long to respond!")
        await self.disableall(disnake.ButtonStyle.red)