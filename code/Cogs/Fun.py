import discord
from discord.ext import commands
import random
import asyncio
from Utils.Useful import *

class PPfight(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label= "Big", style=discord.ButtonStyle.blurple)
    async def bigpp(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            self.value = "Big"
            print()

    @discord.ui.button(label= "Small", style=discord.ButtonStyle.blurple)
    async def smallpp(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            self.value = "Small"
            print()

class Fun(commands.Cog, name = "Fun"):
    """ Fun commands for everyone to use """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot 

    @commands.command(name = "coolservers", aliases = ['servers','cs'], help = "View a list of cool servers owned by some members of Woodlands", brief = "Cool Server Lists")
    @commands.guild_only()
    @commands.check(woodlands_only)
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


    @commands.command(name = "gtn", aliases = ['guess','guessthenumber'], help = "Play a fun game of guess the correct number", brief = "Guess the Number")
    @commands.guild_only()
    async def gtn(self, ctx: commands.Context):

        class Guess(discord.ui.View):
            def __init__(self):
                super().__init__(timeout = 10)
                self.value = None
                self.choices = random.sample(range(1, 100), 9)
                self.correct = random.choice(self.choices)
                self.guess = 3
                for index, number in enumerate(self.choices):
                    self.add_item(self.Button(index = index, number = number))
            
            class Button(discord.ui.Button):
                def __init__(self, index: int, number: int):
                    self.index = index
                    super().__init__(label = f"{number}", style=discord.ButtonStyle.gray, row = index//3)

                async def callback(self, interaction: discord.Interaction):
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(content="This is not your guessing game. Run `h!gtn` if you wanna play", ephemeral=True)
                    if self.view.choices[self.index] == self.view.correct:
                        msg = "You choose the correct number <a:ChickenClap:847462608042197012> !"
                        self.style = discord.ButtonStyle.green
                    else:
                        self.view.guess -= 1
                        msg = f"`{self.label}` is not the correct number. Try again, you have `{self.view.guess}` guess{'es' if self.view.guess != 1 else ''} left" if self.view.guess else f"`{self.label}` is not the correct number either! The correct number was `{self.view.correct}`\nImagine not being able to choose the right even with 3 guesses lmao <a:kekexplode:824150147230466060>"
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
                await self.message.reply(f"You took too long to respond smh {botemojis('idrk')}\nThe correct number was `{self.correct}`")
                await self.message.edit(view = self)

        view = Guess()
        view.message = await ctx.reply('Guess the Number!', view = view)

    @commands.command(name = "tb", aliases = ['button','buttons','testbuttons'], help = "View Different Buttons that can be made", brief = "Test Some Buttons")
    @commands.guild_only()
    async def testbuttons(self, ctx: commands.Context):
        class somebutton(discord.ui.View):

            def __init__(self):
                super().__init__()
                self.value = None

            @discord.ui.button(label= "Green Button", style=discord.ButtonStyle.green, emoji = "<a:prickler:819942044838920233>")
            async def button1(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    await interaction.response.send_message(content="You pressed the green button <a:prickler:819942044838920233>", ephemeral=True)
                else:
                    await interaction.response.send_message(content="This is not your button to press", ephemeral=True)

            @discord.ui.button(label= "Red Button", style=discord.ButtonStyle.red, emoji = "<:CozyBlanket:847491897622134795>")
            async def button2(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    await interaction.response.send_message(content="You pressed the red button <:CozyBlanket:847491897622134795>", ephemeral=True)
                else:
                    await interaction.response.send_message(content="This is not your button to press", ephemeral=True)

            @discord.ui.button(label= "Grey Button", style=discord.ButtonStyle.grey, emoji = "<:Shinobu:847464133003575306>")
            async def button3(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    await interaction.response.send_message(content="You pressed the grey button <:Shinobu:847464133003575306>", ephemeral=True)
                else:
                    await interaction.response.send_message(content="This is not your button to press", ephemeral=True)
        
        view=somebutton()
        view.add_item(discord.ui.Button(label= "Link Button", style=discord.ButtonStyle.link, url="https://www.youtube.com/watch?v=QtBDL8EiNZo", emoji = "<:Popcorn:847491974004998145>"))
        message = await ctx.reply('A sample of all the buttons.', view=view)
        await asyncio.sleep(69)
        for item in view.children:
            item.disabled = True
        await message.edit("A sample of all the buttons. This message is no longer active", view = view)

    @commands.command(name="rps",brief="Play Rps")
    async def rps(self, ctx, opponent: discord.Member):
        if opponent.bot:
            await ctx.send(f"You can't play with bots nab, they'll never respond {botemojis('yikes')}")
            return
        if ctx.author.id == opponent.id:
            await ctx.send(f"You can't play against yourself {botemojis('yikes')}")
            await ctx.send("https://tenor.com/view/we-dont-do-that-here-black-panther-tchalla-bruce-gif-16558003")
            return
        class View(discord.ui.View):
            def __init__(self, *args, **kwargs):
                self.ctx_answer = None
                self.opponent_answer = None
                super().__init__(*args, **kwargs)

            async def button_pressed(self, button, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id  and interaction.user.id != opponent.id:
                    return

                if interaction.user.id == ctx.author.id:
                    if not self.ctx_answer:
                        self.msg.content += f'\n**{ctx.author}** has chosen'
                        self.ctx_answer = button.label
                        await self.msg.edit(self.msg.content)
                    else:
                        await interaction.response.send_message(f"You've already chosen, it's too late to change it now {botemojis('kermitslap')}", ephemeral=True)
                elif interaction.user.id == opponent.id:
                    if not self.opponent_answer:
                        self.msg.content += f'\n**{opponent}** has chosen'
                        self.opponent_answer = button.label
                        await self.msg.edit(self.msg.content)
                    else:
                        await interaction.response.send_message(f"You've already chosen, it's too late to change it now {botemojis('kermitslap')}", ephemeral=True)

                if self.ctx_answer and self.opponent_answer:
                    if self.ctx_answer == self.opponent_answer:
                        output = "Its a Draw, smh stop picking the same thing"
                    elif {"Rock":"Scissors","Paper":"Rock","Scissors":"Paper"}[self.ctx_answer] == self.opponent_answer:
                        output = f"**{ctx.author}** has won {botemojis('kekwiggle')}"
                    else:
                        output = f"**{opponent}** has won {botemojis('kekwiggle')}"
                    await self.msg.edit(f"{ctx.author.mention} vs {opponent.mention}\n**{ctx.author}** chose {self.ctx_answer}\n**{opponent}** chose {self.opponent_answer}\n{output}")
                    for item in self.children:
                        item.disabled = True
                    await self.msg.edit(view=self)
                    self.stop()
            async def on_timeout(self):
                await ctx.send("You took too long to respond")
                for item in self.children:
                    item.disabled = True
                await self.msg.edit(view=self)
                self.stop()

            @discord.ui.button(style=discord.ButtonStyle.primary, label="Rock", emoji = "\U0001faa8")
            async def rock(self, button, interaction):
                await self.button_pressed(button, interaction)

            @discord.ui.button(style=discord.ButtonStyle.primary, label="Paper", emoji = "\U0001f4f0")
            async def paper(self, button, interaction):
                await self.button_pressed(button, interaction)

            @discord.ui.button(style=discord.ButtonStyle.primary, label="Scissors", emoji = "\U00002702")
            async def scissors(self, button, interaction):
                await self.button_pressed(button, interaction)
        view = View(timeout=30)
        view.msg = await ctx.send(content=f"{ctx.author.mention} vs {opponent.mention}", view = view)
        await view.wait()

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))