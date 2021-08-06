import asyncio
import discord
from discord.ext import commands

from discord.ext.commands.errors import DisabledCommand


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('h!'),  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await asyncio.sleep(10)
        await bot.change_presence(status=discord.Status.do_not_disturb, activity = discord.Game(name="h!help | Watching over Woodlands"))

bot = Bot()

@bot.command(name="load")
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
        await ctx.send("Missing Permissions! Only Bot Owner can run this")

@bot.command(name="unload")
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
        await ctx.send("Missing Permissions! Only Bot Owner can run this")

#load Cogs on turning on
coglist = ['Fun', 'Utility']
for i in coglist:
    bot.load_extension(f"Cogs.{i}")

print(f"Loaded Cogs - {coglist}")
bot.help_command = commands.DefaultHelpCommand(command_attrs=dict(hidden=True))

bot.run('ODU4MzM1NjYzNTcxOTkyNjE4.YNcpYQ.0JI0p1KWY1zrDsjbYhmgBMkMrNw')
