import discord
from discord.ext import commands

import random

from Core.Utils.useful import get_em

class Guess(discord.ui.View):
    """ View for Guess the number """
    def __init__(self, bot:commands.Bot, ctx: commands.Context):
        super().__init__(timeout = 10)
        self.value = None
        self.choices = random.sample(range(1, 100), 9)
        self.correct = random.choice(self.choices)
        self.guess = 3
        self.bot = bot
        self.ctx = ctx
        self.author = ctx.author
        for index, number in enumerate(self.choices):
            self.add_item(self.Button(index = index, number = number, author = self.author))
            
    class Button(discord.ui.Button):
        """ Buttons to loop through to add to the view """
        def __init__(self, index: int, number: int, author: discord.Member):
            self.index = index
            self.author = author
            super().__init__(label = f"{number}", style = discord.ButtonStyle.gray, row = index//3)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                return await interaction.response.send_message(content = f"This is not your guessing game. Run `{self.view.ctx.invoked_with}gtn` if you wanna play", ephemeral = True)

            if self.view.choices[self.index] == self.view.correct:
                msg = f"You choose the correct number {get_em('pog')}!"
                self.style = discord.ButtonStyle.green
            else:
                self.view.guess -= 1
                msg = f"`{self.label}` is not the correct number. Try again, you have `{self.view.guess}` guess{'es' if self.view.guess != 1 else ''} left" if self.view.guess else f"`{self.label}` is not the correct number either! The correct number was `{self.view.correct}`\nImagine not being able to choose the right even with 3 guesses lmao {get_em('kekexplode')}"
                self.style,self.disabled = discord.ButtonStyle.red, True

            if (not self.view.guess) or self.view.choices[self.index] == self.view.correct:
                for item in self.view.children:
                    if item.label == f"{self.view.correct}":
                        item.style = discord.ButtonStyle.green if self.view.choices[self.index] == self.view.correct else discord.ButtonStyle.blurple
                    item.disabled = True
                    self.view.stop()

            await interaction.response.edit_message(view = self.view)
            await interaction.followup.send(content = msg)

    async def on_timeout(self):
        for item in self.children:
            if item.label == f"{self.correct}":
                item.style = discord.ButtonStyle.blurple
            item.disabled = True
        await self.message.reply(f"You took too long to respond smh {get_em('idrk')}\nThe correct number was `{self.correct}`")
        await self.message.edit(view = self)

class RpsView(discord.ui.View):
    def __init__(self, ctx: commands.Context, opponent: discord.Member, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.user_answer = None
        self.opponent_answer = None
        self.ctx = ctx
        self.opponent = opponent

    async def button_pressed(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id  and interaction.user.id != self.opponent.id:
            return interaction.response.send_message(f"This isn't your game to play!", ephemeral = True)
        
        if interaction.user.id == self.ctx.author.id:
            if not self.user_answer:
                self.user_answer = button.label
                self.message.content += f'\n**{self.ctx.author.name}** has chosen'
                await self.message.edit(self.message.content)
                await interaction.response.send_message(f"You have chosen **{button.label}**!", ephemeral = True)
            else:
                await interaction.response.send_message(f"You've already chosen `{self.user_answer}`, It's too late to change it now {get_em('kermitslap')}", ephemeral = True)
        
        elif interaction.user.id == self.opponent.id:
            if not self.opponent_answer:
                self.opponent_answer = button.label
                self.message.content += f'\n**{self.opponent.name}** has chosen'
                await self.message.edit(self.message.content)
                await interaction.response.send_message(f"You have chosen **{button.label}**!", ephemeral = True)
            else:
                await interaction.response.send_message(f"You've already chosen `{self.opponent_answer}`, It's too late to change it now {get_em('kermitslap')}", ephemeral = True)
        
        if self.user_answer and self.opponent_answer:
            if self.user_answer == self.opponent_answer:
                result = "Its a Draw, smh stop picking the same thing"

            elif {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}[self.user_answer] == self.opponent_answer:
                result = f"**{self.ctx.author}** has won {get_em('kekwiggle')}"
            
            else:
                result = f"**{self.opponent.mention}** has won {get_em('kekwiggle')}"

            for item in self.children:
                item.disabled = True
            
            self.message.content = f"{self.ctx.author.mention} vs {self.opponent.mention}\n**{self.ctx.author}** chose {self.user_answer}\n**{self.opponent}** chose {self.opponent_answer}\n\n> {result}"
            await self.message.edit(self.message.content, view = self)
            self.stop()
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label="Rock", emoji = "\U0001faa8")
    async def rock(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Paper", emoji = "\U0001f4f0")
    async def paper(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="Scissors", emoji = "\U00002702")
    async def scissors(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction)

    async def on_timeout(self):
        await self.message.reply("You both took too long to respond")
        for item in self.children:
            item.disabled = True
        self.message : discord.Message
        self.message.content += '\n\n> You took too long to respond'
        await self.message.edit(self.message.content, view = self)
        self.stop()