import discord
from discord.ext import commands

from Utils.Useful import *

# Poll Buttons for Menu

class PollButton(discord.ui.Button):
    def __init__(self, number:int):
        self.num = number
        self.em = botemojis(str(number+1))
        super().__init__(style=discord.ButtonStyle.gray, emoji=self.em)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.view.lst:
            self.view.count[self.view.lst[interaction.user.id]-1] -= 1
            if self.view.lst[interaction.user.id] == self.num + 1:
                del self.view.lst[interaction.user.id]
                await interaction.response.send_message(f"Your vote for option:{self.em} has been removed", ephemeral = True)
                content = self.view.originalmessage + "\n\n" + "\U000030fb".join([f"{botemojis(i)}: `{self.view.count[i-1]}` " for i in range(1,self.view.num + 1)]) + f"\n\nPoll ends on <t:{self.view.tm}:F> (<t:{self.view.tm}:R>)"
                await self.view.message.edit(content = content, allowed_mentions = discord.AllowedMentions.none())
                return
            await interaction.response.send_message(f"Your vote has been changed from option:{botemojis(str(self.view.lst[interaction.user.id]))} to option:{self.em}", ephemeral = True)
        else:
            await interaction.response.send_message(f"Your vote for option:{self.em} has been counted", ephemeral = True)
        self.view.count[self.num] += 1
        self.view.lst[interaction.user.id] = self.num + 1
        content = self.view.originalmessage + "\n\n" + "\U000030fb".join([f"{botemojis(i)}: `{self.view.count[i-1]}` " for i in range(1,self.view.num + 1)]) + f"\n\nPoll ends on <t:{self.view.tm}:F> (<t:{self.view.tm}:R>)"
        await self.view.message.edit(content = content, allowed_mentions = discord.AllowedMentions.none())

# Delete Interaction Message
class Delete(discord.ui.Button):
    def __init__(self, user):
        self.user = user
        super().__init__(label = "Delete", emoji = f"{botemojis('trash')}", style = discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        if self.user.id != interaction.user.id:
            return
        await interaction.message.delete()