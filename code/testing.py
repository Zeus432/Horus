from discord import invite, member
from discord.ext import commands
import traceback 
from contextlib import redirect_stdout 
import io
import textwrap
import random
import discord


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('h!'))

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

bot = Bot()

@bot.command()
async def ping(ctx):
    await ctx.author.trigger_typing() 
    await ctx.reply(f"Pong {round(bot.latency*1000)}ms")


        

@bot.command()
async def gtn(ctx: commands.Context):
    numlist = random.sample(range(1, 100), 4)
    correct = random.choice(numlist)
    print(numlist, correct)

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

@bot.command(pass_context=True, hidden=True, name='eval')
@commands.is_owner()
async def _eval(ctx, *, body: str):
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

    """Evaluates a code"""
    _last_result = None
    env = {
            'bot': bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': _last_result
    }
    env.update(globals())

    body = cleanup_code(body)
    stdout = io.StringIO()

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

    func = env['func']
    try:
        with redirect_stdout(stdout):
            ret = await func() 
    except Exception as e:
        value = stdout.getvalue()
        await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        try:
            await ctx.message.add_reaction('\u2705')
        except:
            pass

        if ret is None:
            if value:
                await ctx.send(f'```py\n{value}\n```')
        else:
            _last_result = ret
            await ctx.send(f'```py\n{value}{ret}\n```')

@bot.command()
async def coolservers(ctx: commands.Context):
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



bot.run('ODU4MzM1NjYzNTcxOTkyNjE4.YNcpYQ.0JI0p1KWY1zrDsjbYhmgBMkMrNw')
