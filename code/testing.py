import asyncio
import discord
from discord.ext import commands
from Useful.settings import *


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
async def button(ctx: commands.Context):

    class somebutton(discord.ui.View):

        def __init__(self):
            super().__init__()
            self.value = None

        @discord.ui.button(label= "Green Button", style=discord.ButtonStyle.green, emoji = "<a:prickler:819942044838920233>")
        async def button1(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user.id == ctx.author.id:
                await interaction.response.send_message(content="You pressed the green button :clap:")
            else:
                await interaction.response.send_message(content="This is not your button to press", ephemeral=True)

        @discord.ui.button(label= "Red Button", style=discord.ButtonStyle.red, emoji = "<:CozyBlanket:847491897622134795>")
        async def button2(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user.id == ctx.author.id:
                await interaction.response.send_message(content="You pressed the red button :clap:")
            else:
                await interaction.response.send_message(content="This is not your button to press", ephemeral=True)

        @discord.ui.button(label= "Grey Button", style=discord.ButtonStyle.grey, emoji = "<:Shinobu:847464133003575306>")
        async def button3(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user.id == ctx.author.id:
                await interaction.response.send_message(content="You pressed the grey button :clap:")
            else:
                await interaction.response.send_message(content="This is not your button to press", ephemeral=True)

    view=somebutton()
    view.add_item(discord.ui.Button(label= "Link Button", style=discord.ButtonStyle.link, url="https://www.youtube.com/watch?v=QtBDL8EiNZo", emoji = "<:Popcorn:847491974004998145>"))
    message = await ctx.reply('A sample of all the buttons.', view=view)
    await asyncio.sleep(69)
    await message.edit("A sample of all the buttons. This message is no longer active")
    for item in view.children:
        item.disabled = True

bot.run(TOKEN)
