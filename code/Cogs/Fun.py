import discord
from discord.ext import commands
import random

class Fun(commands.Cog): 
    def __init__(self, bot: commands.Bot):
        self.bot = bot 

    @commands.command()
    async def coolservers(self, ctx: commands.Context):
        class Dropdown(discord.ui.Select):
            def __init__(self):

                    # Set the options that will be presented inside the dropdown
                    options = [
                        discord.SelectOption(label='The Woodlands', description='12th Community Server', emoji='<:angelpray:872522672670642246>'),
                        discord.SelectOption(label="The Students' Space", description='12th Study Server', emoji='<:Study:847464342207463494>'),
                        discord.SelectOption(label='Knights of Cinder (KOC)', description='Gaming and Community Based Server', emoji='<:games:873040244637839381>'),
                        discord.SelectOption(label='Pattani Vekum Samudhayam', description='Community Based? Not sure, Relatively New Server', emoji='<:jaipattani:865310852033937468>')
                    ]

                    # The placeholder is what will be shown when no option is chosen
                    # The min and max values indicate we can only pick one of the three options
                    # The options parameter defines the dropdown options. We defined this above
                    super().__init__(placeholder='Choose a server', min_values=1, max_values=1, options=options)
            
            async def callback(self, interaction: discord.Interaction):
                    # Use the interaction object to send a response message containing
                    # the user's favourite colour or choice. The self object refers to the
                    # Select object, and the values attribute gets a list of the user's 
                    # selected options. We only want the first one.
                    if interaction.user.id == ctx.author.id:
                        invites = {"The Woodlands":"M6zzYnHwZc", "The Students' Space":"B6WbTg9juG", "Knights of Cinder (KOC)":"NzpkdAY5CU", "Pattani Vekum Samudhayam":"ecqH6cspac"}
                        await interaction.response.send_message(f'Invite to {self.values[0]}\nhttps://discord.gg/{invites[self.values[0]]} ', ephemeral=True)
                    else:
                        await interaction.response.send_message("This select menu isn't for you to use, run `h!coolservers` to view this command", ephemeral=True)

        class DropdownView(discord.ui.View):
            def __init__(self):
                super().__init__()

                # Adds the dropdown to our view object.
                self.add_item(Dropdown())

        view = DropdownView()
        await ctx.send('Cool Servers List', view=view)

    @commands.command()
    async def gtn(self, ctx: commands.Context):

        class Guess(discord.ui.View):
            numlist = random.sample(range(1, 100), 4)
            correct = random.choice(numlist)

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
