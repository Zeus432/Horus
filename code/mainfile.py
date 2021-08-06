import asyncio
import discord
from discord.ext import commands
import logging
from settings import *

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('h!'),  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await asyncio.sleep(10)
        await bot.change_presence(status=discord.Status.do_not_disturb, activity = discord.Game(name="h!help | Watching over Woodlands"))

bot = Bot()

@bot.command(name="load", aliases = ['l'], help = "Load Cogs onto the bot", brief = "Load Cogs")
@commands.is_owner()
async def load(ctx, cog_name):
    try:
        bot.load_extension(f"Cogs.{cog_name}")
        await ctx.send(f"Loaded `{cog_name}`")
    except commands.ExtensionAlreadyLoaded:
        bot.unload_extension(f"Cogs.{cog_name}")
        bot.load_extension(f"Cogs.{cog_name}")
        await ctx.send(f"Reloaded `{cog_name}`")
    except commands.ExtensionNotFound:
        await ctx.send(f"Cog `{cog_name}` not found")
@load.error
async def load_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.reply("Missing Permissions! Only the Bot Owner can run this")
        await ctx.message.add_reaction("<:doubtit:782677480267579412>")
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Specify Something to Load Smh")

@bot.command(name="unload", aliases = ['ul'], help = "Unload Cogs loaded Cogs", brief = "Unload Cogs")
@commands.is_owner()
async def unload(ctx, cog_name):
    try:
        bot.unload_extension(f"Cogs.{cog_name}")
        await ctx.send(f"Unloaded `{cog_name}`")
    except commands.ExtensionNotFound:
        await ctx.send(f"Cog `{cog_name}` not found")
    except commands.ExtensionNotLoaded:
        await ctx.send("Cog is already unloaded")

@unload.error
async def unload_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.reply("Missing Permissions! Only the Bot Owner can run this")
        await ctx.message.add_reaction("<:doubtit:782677480267579412>")
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Specify Something to Unload Smh")

@bot.command(name="shutdown", aliases = ['stop','gotosleepwhorus'], help = "Shutdown the bot in a peaceful way, rather than just closing the window", brief = "Shutdown")
@commands.is_owner()
async def shutdown(ctx):
    message = await ctx.reply("Shutting down")
    await asyncio.sleep(0.5)
    await message.edit("Shutting down .")
    await asyncio.sleep(0.5)
    await message.edit("Shutting down . .")
    await asyncio.sleep(0.5)
    await message.edit("Shutting down . . .")
    await asyncio.sleep(0.5)
    await message.edit("Goodbye <a:Frogsleb:849663487080792085>")
    await ctx.message.add_reaction("<a:tick:873113604080144394>")
    await bot.close()

@shutdown.error
async def unload_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.reply("Missing Permissions! Only the Bot Owner can run this")
        await ctx.message.add_reaction("<:doubtit:782677480267579412>")

#load Cogs on turning on
coglist = ['Fun', 'Utility']
for i in coglist:
    bot.load_extension(f"Cogs.{i}")

print(f"Loaded Cogs - {coglist}")
bot.help_command = commands.DefaultHelpCommand(command_attrs=dict(hidden=True))

bot.run(TOKEN)
