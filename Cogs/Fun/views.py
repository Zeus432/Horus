import disnake as discord
from bot import Horus
from disnake.ext import commands

import asyncio
import random
import time

from Core.Utils.useful import get_em

class Guess(discord.ui.View):
    """ View for Guess the number """
    def __init__(self, bot: Horus, ctx: commands.Context):
        super().__init__(timeout = 100)
        self.value = None
        self.choices = random.sample(range(1, 100), 8)
        self.choices = [*self.choices, 69]
        random.shuffle(self.choices)
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
                return await interaction.response.send_message(content = f"This is not your guessing game. Run `{self.view.ctx.clean_prefix}{self.view.ctx.invoked_with}` if you wanna play", ephemeral = True)

            if self.view.choices[self.index] == self.view.correct:
                msg = f"You choose the correct number {get_em('pog')}!"
                self.style = discord.ButtonStyle.green
            else:
                self.view.guess -= 1
                msg = f"`{self.label}` is not the correct number. Try again, you have `{self.view.guess}` guess{'es' if self.view.guess != 1 else ''} left" if self.view.guess else f"`{self.label}` is not the correct number either! The correct number was `{self.view.correct}`\nImagine not being able to choose the right even with 3 guesses lmao {get_em('kekexplode')}"
                self.style, self.disabled = discord.ButtonStyle.red, True

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
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id  and interaction.user.id != self.opponent.id:
            return await interaction.response.send_message(f"This isn't your game to play! Run `{self.ctx.clean_prefix}{self.ctx.invoked_with}` if you wanna play", ephemeral = True)
        return True

    async def button_pressed(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            if not self.user_answer:
                self.user_answer = button.label
                self.message.content += f'\n**{self.ctx.author.name}** has chosen'
                await self.message.edit(content = self.message.content)
                await interaction.response.send_message(f"You have chosen **{button.label}**!", ephemeral = True)
            else:
                await interaction.response.send_message(f"You've already chosen `{self.user_answer}`, It's too late to change it now {get_em('kermitslap')}", ephemeral = True)
        
        elif interaction.user.id == self.opponent.id:
            if not self.opponent_answer:
                self.opponent_answer = button.label
                self.message.content += f'\n**{self.opponent.name}** has chosen'
                await self.message.edit(content = self.message.content)
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
            await self.message.edit(content = self.message.content, view = self)
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
        await self.message.edit(content = self.message.content, view = self)
        self.stop()
    
class MatchView(discord.ui.View):
    def __init__(self, mode: str, user: discord.Member, total: int):
        super().__init__(timeout = 30 + total * 2)
        self.user = user
        self.matches = 0
        self.pressed = 0
        self.total = total
        self.mode = mode
        self.timer_start = time.perf_counter()
        self.last_used_button = None
        def key(interaction: discord.Interaction):
            return interaction.user
        self._cd = commands.CooldownMapping.from_cooldown(2, 2.0, key)

        emojis = random.sample(
            ['<:AphosHoardingCats:877268478493597696>','<:CheckList:879961726865522688>','<a:DevBadge:873866720530534420>','<a:BoostBadge:873866459451904010>','<:MuichiroLurking:921111418206572584>','<:Rules:879780637417041970>','<a:TokitoSip:875425433980645416>','<:Utils:877796922876919808>','<:angelpray:873863602023596082>','<:YouWantItToMoveButItWont:873921001023500328>','<:Yikes:877267180662714428>','<:games:873863717585059970>','<:hadtodoittoem:874263602897502208>','<a:inspect:886257382575988766>','<a:kekwiggle:879997954444890142>','<:mylife:880692470021763102>','<a:FloatingBoost:920999518990893097>','<a:idrk:897066077043965972>','<:PensiveApple:890044889281228841>','<:hsupport:893556630820618251>'],
            k = int(total/2)
        )
        emojis.extend(emojis)
        random.shuffle(emojis)

        for num in range(0, total):
            self.add_item(self.MatchButton(payload = emojis[num]))
    
    class MatchButton(discord.ui.Button):
        def __init__(self, payload: str):
            super().__init__(style = discord.ButtonStyle.gray, emoji = "<:BlankSpace:929004286078226492>")
            self.payload = payload

        async def callback(self, interaction: discord.MessageInteraction):
            await interaction.response.defer()

            self.view.pressed += 1

            self.emoji = self.payload
            self.disabled = True

            if self.view.last_used_button is None:
                self.view.last_used_button = self
            
            else:
                if self.view.last_used_button.payload == self.payload:
                    self.view.last_used_button.style = discord.ButtonStyle.green
                    self.style = discord.ButtonStyle.green

                    await self.view.message.edit(view = self.view)
                    await asyncio.sleep(0.5)

                    self.view.last_used_button.style = discord.ButtonStyle.blurple
                    self.style = discord.ButtonStyle.blurple

                    self.view.matches += 1

                else:
                    self.view.last_used_button.style = discord.ButtonStyle.red
                    self.style = discord.ButtonStyle.red

                    await self.view.message.edit(view = self.view)
                    await asyncio.sleep(0.5)

                    self.view.last_used_button.emoji = "<:BlankSpace:929004286078226492>"
                    self.view.last_used_button.style = discord.ButtonStyle.gray
                    self.view.last_used_button.disabled = False

                    self.emoji = "<:BlankSpace:929004286078226492>"
                    self.style = discord.ButtonStyle.gray
                    self.disabled = False

                self.view.last_used_button = None

            await self.view.message.edit(view = self.view)

            if self.view.matches * 2 >= self.view.total:
                self.view.stop()
                accuracy = self.view.total/self.view.pressed * 100
                timer = (time.perf_counter() - self.view.timer_start)
                await self.view.message.edit(content = f"Finished this `{self.view.mode}` puzzle in `{round(timer, 2)}s` with about `{round(accuracy, 2)}%` accuracy!")

    async def interaction_check(self, interaction: discord.MessageInteraction):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(content = "Not your button to click!", ephemeral = True)

        retry_after = self._cd.update_rate_limit(interaction)
        if retry_after:
            return await interaction.response.send_message(content = f"You're clicking too fast! Try again in `{round(retry_after, 1)}s`", ephemeral = True)

        return True
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(content = "You took too long to finish this puzzle, Better luck next time!", view = self)