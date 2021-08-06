import discord
from discord.ext import commands
import random

class Fun(commands.Cog): 
    def __init__(self, bot: commands.Bot):
        self.bot = bot 

    def helper(self, message: discord.Message): #Notice self!
            return message.content.startswith("hi")

    @commands.command()
    async def gtn(self, ctx: commands.Context):

        class Guess(discord.ui.View):
            numlist = random.sample(range(1, 100), 4)
            correct = random.choice(numlist)
            print(numlist, correct)

            def __init__(self):
                super().__init__()
                self.value = None

            @discord.ui.button(label= numlist[0], style=discord.ButtonStyle.grey)
            async def choice1(self, button: discord.ui.Button, interaction: discord.Interaction, numlist = numlist, correct = correct):
                if interaction.user.id == ctx.author.id:
                    if numlist[0] == correct:
                        msg = "You choose the correct number <a:ChickenClap:847462608042197012>!"
                        button.style = discord.ButtonStyle.green
                    else:
                        msg = f"Imagine not being able to choose the right answer out of only 4 options <a:kekexplode:824150147230466060>, the correct number was {correct}"
                        button.style = discord.ButtonStyle.red
                    for item in self.children:
                        if item.label == correct:
                            item.style = discord.ButtonStyle.green
                        item.disabled = True
                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(content=msg, ephemeral=False)
                    self.stop()
                else:
                    await interaction.response.send_message(content="This is not your guessing game. Start one for yourself nab", ephemeral=True)

            @discord.ui.button(label= numlist[1], style=discord.ButtonStyle.grey)
            async def choice2(self, button: discord.ui.Button, interaction: discord.Interaction, numlist = numlist, correct = correct):
                if interaction.user.id == ctx.author.id:
                    if numlist[1] == correct:
                        msg = "You choose the correct number <a:ChickenClap:847462608042197012>!"
                        button.style = discord.ButtonStyle.green
                    else:
                        msg = f"Imagine not being able to choose the right answer out of only 4 options <a:kekexplode:824150147230466060>, the correct number was {correct}"
                        button.style = discord.ButtonStyle.red
                    for item in self.children:
                        if item.label == correct:
                            item.style = discord.ButtonStyle.green
                        item.disabled = True
                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(content=msg, ephemeral=False)
                    self.stop()
                else:
                    await interaction.response.send_message(content="This is not your guessing game. Start one for yourself nab", ephemeral=True)

            @discord.ui.button(label= numlist[2], style=discord.ButtonStyle.grey)
            async def choice3(self, button: discord.ui.Button, interaction: discord.Interaction, numlist = numlist, correct = correct):
                if interaction.user.id == ctx.author.id:
                    if numlist[2] == correct:
                        msg = "You choose the correct number <a:ChickenClap:847462608042197012>!"
                        button.style = discord.ButtonStyle.green
                    else:
                        msg = f"Imagine not being able to choose the right answer out of only 4 options <a:kekexplode:824150147230466060>, the correct number was {correct}"
                        button.style = discord.ButtonStyle.red
                    for item in self.children:
                        if item.label == correct:
                            item.style = discord.ButtonStyle.green
                        item.disabled = True
                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(content=msg, ephemeral=False)
                    self.stop()
                else:
                    await interaction.response.send_message(content="This is not your guessing game. Start one for yourself nab", ephemeral=True)

            @discord.ui.button(label=numlist[3], style=discord.ButtonStyle.grey)
            async def choice4(self, button: discord.ui.Button, interaction: discord.Interaction, numlist = numlist, correct = correct):
                if interaction.user.id == ctx.author.id:
                    if numlist[3] == correct:
                        msg = "You choose the correct number <a:ChickenClap:847462608042197012>!"
                        button.style = discord.ButtonStyle.green
                    else:
                        msg = f"Imagine not being able to choose the right answer out of only 4 options <a:kekexplode:824150147230466060>, the correct number was {correct}"
                        button.style = discord.ButtonStyle.red
                    for item in self.children:
                        if item.label == correct:
                            item.style = discord.ButtonStyle.green
                        item.disabled = True
                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(content=msg, ephemeral=False)
                    self.stop()
                else:
                    await interaction.response.send_message(content="This is not your guessing game. Start one for yourself nab", ephemeral=True)

        view=Guess()
        await ctx.reply('Guess the Number!', view=view)

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
