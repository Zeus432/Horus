import discord
from discord.ext import commands
import time


bot = commands.Bot(command_prefix="h!")

@bot.event
async def on_ready():
  print ("Bot is online!")

@bot.command()
async def ping(ctx):
    t_1 = time.perf_counter()
    await ctx.author.trigger_typing()  # tell Discord that the bot is "typing", which is a very simple request
    t_2 = time.perf_counter()
    time_delta = round((t_2-t_1)*1000)  # calculate the time needed to trigger typing
    await ctx.reply(f"Pong. {time_delta}ms")

@bot.command(brief="Send a message with a button!") # Create a command inside a cog
async def button(ctx):
    view = discord.ui.View() # Establish an instance of the discord.ui.View class
    style = discord.ButtonStyle.grey  # The button will be gray in color
    item = discord.ui.Button(style=style, label="This is the button", url="https://www.youtube.com/watch?v=Uj1ykZWtPYI&list=PLzJ2D8f51wW-H40q3dMB0evI7iJ0dmRdT&index=3")  # Create an item to pass into the view class.
    view.add_item(item=item)  # Add that item into the view class
    item = discord.ui.Button(style=discord.ButtonStyle.green , label ="Another Button Woo" )
    view.add_item(item=item)
    await ctx.send("This message has buttons!", view=view)  # Send your message with a button.

bot.run("ODU4MzM1NjYzNTcxOTkyNjE4.YNcpYQ.0JI0p1KWY1zrDsjbYhmgBMkMrNw")
