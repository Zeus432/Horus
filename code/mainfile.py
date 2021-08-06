import asyncio
import discord
from discord.ext import commands
from loguru import logger
import sys 
from settings import *

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="ERROR")
coglist = ['Fun', 'Utility', 'Admin']


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('h!'),  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await asyncio.sleep(10)
        await bot.change_presence(status=discord.Status.do_not_disturb, activity = discord.Game(name="h!help | Watching over Woodlands"))

bot = Bot()
bot.owner_ids = BotOwners

@bot.command(name="load", aliases = ['l'], help = "Load Cogs onto the bot", brief = "Load Cogs")
@commands.is_owner()
async def load(ctx, cog_name = None):
    if cog_name != None:
        try:
            bot.load_extension(f"Cogs.{cog_name}")
            await ctx.send(f"Loaded `{cog_name}`")
        except commands.ExtensionAlreadyLoaded:
            bot.unload_extension(f"Cogs.{cog_name}")
            bot.load_extension(f"Cogs.{cog_name}")
            await ctx.send(f"Reloaded `{cog_name}`")
        except commands.ExtensionNotFound:
            await ctx.send(f"Cog `{cog_name}` not found")
    else:
        class Dropdown(discord.ui.Select):
            def __init__(self):
                length = len(coglist)
                if length >= 20:
                    length = 20
                options = []
                for i in coglist:
                    options.append(discord.SelectOption(label=i, description=f'Load Cog: {i}', emoji='<:cogsred:873220470416236544>'))
                super().__init__(placeholder='Choose Cogs to Load', min_values=1, max_values=length, options=options)

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    Loaded = ""
                    Reloaded = ""
                    for cog in self.values:
                        try:
                            bot.load_extension(f"Cogs.{cog}")
                            Loaded += f", `{cog}`"
                        except commands.ExtensionAlreadyLoaded:
                            bot.unload_extension(f"Cogs.{cog}")
                            bot.load_extension(f"Cogs.{cog}")
                            Reloaded += f", `{cog}`"
                    if Loaded != "":
                        Loaded = f"**Loaded Cogs:**\n{Loaded[2:]}\n\n"
                    if Reloaded != "":
                        Reloaded = f"**Reloaded Cogs:**\n{Reloaded[2:]}"
                    await interaction.response.send_message(f'{Loaded}{Reloaded}', ephemeral=False)
                else:
                    await interaction.response.send_message("This select menu isn't for you to use, run `h!load` to use this command", ephemeral=True)

        class DropdownView(discord.ui.View):
            def __init__(self):
                super().__init__()

                # Adds the dropdown to our view object.
                self.add_item(Dropdown())

        view = DropdownView()
        msg = await ctx.send('Select Menu to Load Cogs', view=view)
        await asyncio.sleep(30)
        for item in view.children:
            item.disabled = True
        await msg.edit("Select Menu to Load Cogs. This message is no longer active", view = view)

@load.error
async def load_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.reply("Missing Permissions! Only the Bot Owner can run this")
        await ctx.message.add_reaction("<:doubtit:782677480267579412>")
    else:
        await ctx.send(f"```py\n```{error}")

@bot.command(name="unload", aliases = ['ul'], help = "Unload Cogs loaded Cogs", brief = "Unload Cogs")
@commands.is_owner()
async def unload(ctx, cog_name = None):
    if cog_name != None:
        try:
            bot.unload_extension(f"Cogs.{cog_name}")
            await ctx.send(f"Unloaded `{cog_name}`")
        except commands.ExtensionNotFound:
            await ctx.send(f"Cog `{cog_name}` not found")
        except commands.ExtensionNotLoaded:
            await ctx.send("Cog is already unloaded")

    else:
        class Dropdown(discord.ui.Select):
            def __init__(self):
                length = len(coglist)
                if length >= 20:
                    length = 20
                options = []
                for i in coglist:
                    options.append(discord.SelectOption(label=i, description=f'Load Cog: {i}', emoji='<:cogsred:873220470416236544>'))
                super().__init__(placeholder='Choose Cogs to Unload', min_values=1, max_values=length, options=options)

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    Unloaded = ""
                    Failed = ""
                    for cog in self.values:
                        try:
                            bot.unload_extension(f"Cogs.{cog}")
                            Unloaded += f", `{cog}`"
                        except commands.ExtensionNotLoaded:
                            Failed += f", `{cog}`"
                    if Unloaded != "":
                        Unloaded = f"**Unloaded Cogs:**\n{Unloaded[2:]}\n\n"
                    if Failed != "":
                        Failed = f"**Failed to Unload - Already Unloaded:**\n{Failed[2:]}"
                    await interaction.response.send_message(f'{Unloaded}{Failed}', ephemeral=False)
                else:
                    await interaction.response.send_message("This select menu isn't for you to use, run `h!unload` to use this command", ephemeral=True)

        class DropdownView(discord.ui.View):
            def __init__(self):
                super().__init__()

                # Adds the dropdown to our view object.
                self.add_item(Dropdown())

        view = DropdownView()
        msg = await ctx.send('Select Menu to Unload Cogs', view=view)
        await asyncio.sleep(30)
        for item in view.children:
            item.disabled = True
        await msg.edit("Select Menu to Unload Cogs. This message is no longer active", view = view)

@unload.error
async def unload_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.reply("Missing Permissions! Only the Bot Owner can run this")
        await ctx.message.add_reaction("<:doubtit:782677480267579412>")
    else:
        await ctx.send(f"```py\n```{error}")

@bot.command(name="shutdown", aliases = ['stop','gotosleepwhorus'], help = "Shutdown the bot in a peaceful way, rather than just closing the window", brief = "Shutdown")
@commands.is_owner()
async def shutdown(ctx):
    msg = await ctx.reply("Shutting down")
    await asyncio.sleep(0.5)
    await msg.edit("Shutting down .")
    await asyncio.sleep(0.5)
    await msg.edit("Shutting down . .")
    await asyncio.sleep(0.5)
    await msg.edit("Shutting down . . .")
    await asyncio.sleep(0.5)
    await msg.edit("Goodbye <a:Frogsleb:849663487080792085>")
    try:
        await ctx.message.add_reaction("<a:tick:873113604080144394>")
    except:
        pass
    await bot.close()

#load Cogs on turning on
for i in coglist:
    bot.load_extension(f"Cogs.{i}")

print(f"Loaded Cogs - {coglist}")
bot.help_command = commands.DefaultHelpCommand(command_attrs=dict(hidden=True))

bot.run(TOKEN)
