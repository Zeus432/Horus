from Useful.Useful import botemojis
import asyncio
import discord
from discord.ext import commands
import time
import datetime
from loguru import logger
import asyncpg
from Useful.Useful import *
from Useful.settings import *
from Useful.Menus import *

coglist = WorkingCogs
logger.remove()
logger.add("/Users/siddharthm/Desktop/Horus/horus.log",level="DEBUG",format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
logger.info("Logged into Horus succesfully")

#/usr/local/bin/python3 /Users/siddharthm/Desktop/mine/Horus/main.py

async def run():
    credentials = {"user": dbuser, "database": dbdb, "host": dbhost}
    db = await asyncpg.create_pool(**credentials)
    bot.db = db

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=self.noprefix,  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle)
    
    async def noprefix(self, bot, message):
        prefix_return = ["h!"]
        if await bot.is_owner(message.author):
            try:
                if bot.prefixstate == True:
                    prefix_return.append("")
            except:
                pass
        return prefix_return
    
    async def on_ready(self):
        print(f'\n\nLogged in as {self.user} (ID: {self.user.id})')
        total_members = list(bot.get_all_members())
        total_channels = sum(1 for x in bot.get_all_channels())
        print(f'Guilds: {len(bot.guilds)}')
        print(f'Large Guilds: {sum(g.large for g in bot.guilds)}')
        print(f'Chunked Guilds: {sum(g.chunked for g in bot.guilds)}')
        print(f'Members: {len(total_members)}')
        print(f'Channels: {total_channels}')
        print(f'Message Cache Size: {len(bot.cached_messages)}\n')
        await asyncio.sleep(10)
        await bot.change_presence(status=discord.Status.idle, activity = discord.Game(name="h!help | Watching over Woodlands"))
        bot.launch_time = datetime.datetime.utcnow()
        bot.launch_ts = time.time()

bot = Bot()
bot.owner_ids = frozenset(BotOwners)
bot.launch_time = datetime.datetime.utcnow()
bot.launch_ts = time.time()
bot.colour = discord.Colour(0x9c9cff)

def cogstate(cog_name):
    if cog_name == 'jishaku':
        return "Jishaku Cog"
    elif bot.get_cog(cog_name) == None:
        return "State: Unloaded"
    else:
        return "State: Loaded"

@bot.command(name="load", aliases = ['l'], help = "Load Cogs onto the bot", brief = "Load Cogs")
@commands.is_owner()
async def load(ctx, cog_name = None):
    coglist = WorkingCogs
    if cog_name != None:
        try:
            if cog_name == 'jishaku':
                bot.load_extension(cog_name)
            bot.load_extension(f"Cogs.{cog_name}")
            await ctx.send(f"Loaded `{cog_name}`")
        except commands.ExtensionAlreadyLoaded:
            if cog_name == 'jishaku':
                bot.unload_extension(cog_name)
                bot.load_extension(cog_name)
            else:
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
                cogdetails = {'ErrorHandler':{'emoji':botemojis("error"),'msg':'Load Global Error Handler'},'CustomHelp':{'emoji':botemojis("menu"),'msg':'Load Custom Help Menu'}}
                def getemoji(cog):
                    try:
                        return cogdetails[cog]
                    except:
                        return {'emoji':botemojis("cogs"),'msg':cogstate(cog_name=cog)}
                for i in coglist:
                    options.append(discord.SelectOption(label=i, description=getemoji(i)['msg'], emoji=getemoji(i)['emoji']))
                super().__init__(placeholder='Choose Cogs to Load', min_values=1, max_values=length, options=options)

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    async with ctx.typing():
                        Loaded = ""
                        Reloaded = ""
                        for cog in self.values:
                            try:
                                if cog == 'jishaku':
                                    bot.load_extension(cog)
                                else:
                                    bot.load_extension(f"Cogs.{cog}")
                                Loaded += f", `{cog}`"
                                for opt in view.children:
                                    for item in opt.options:
                                        print(item.value)
                                        if item.value == cog:
                                            item.description = "State: Loaded"
                                            await msg.edit(view = view)
                                            break
                                        
                            except commands.ExtensionAlreadyLoaded:
                                if cog == 'jishaku':
                                    bot.unload_extension(cog)
                                    bot.load_extension(cog)
                                else:
                                    bot.unload_extension(f"Cogs.{cog}")
                                    bot.load_extension(f"Cogs.{cog}")
                                Reloaded += f", `{cog}`"
                        if Loaded != "":
                            Loaded = f"**Loaded Cogs:**\n{Loaded[2:]}\n\n"
                        if Reloaded != "":
                            Reloaded = f"**Reloaded Cogs:**\n{Reloaded[2:]}"
                        await interaction.response.send_message(f'{Loaded}{Reloaded}', ephemeral=False)
                else:
                    await interaction.response.send_message("This select isn't for you to use", ephemeral=True)

        class DropdownView(discord.ui.View):
            def __init__(self):
                super().__init__()

                # Adds the dropdown to our view object.
                self.add_item(Dropdown())

        view = DropdownView()
        msg = await ctx.send('Select to Load Cogs', view=view)
        await asyncio.sleep(30)
        for item in view.children:
            item.disabled = True
        await msg.edit("Select to Load Cogs. This message is no longer active", view = view)

@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("Only the Bot Owner can run this command!", delete_after = 5)
    else:
        await senderror(bot,ctx,error)

@bot.command(name="unload", aliases = ['ul'], help = "Unload loaded Cogs", brief = "Unload Cogs")
@commands.is_owner()
async def unload(ctx, cog_name = None):
    coglist = WorkingCogs
    if cog_name != None:
        try:
            if cog_name == 'jishaku':
                bot.unload_extension(cog_name)
            else:
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
                cogdetails = {'ErrorHandler':{'emoji':botemojis("error"),'msg':'Unload Global Error Handler'},'CustomHelp':{'emoji':botemojis("menu"),'msg':'Unload  Custom Help Menu and use the default one'}}
                def getemoji(cog):
                    try:
                        return cogdetails[cog]
                    except:
                        return {'emoji':botemojis("cogs"),'msg':cogstate(cog_name=cog)}
                for i in coglist:
                    options.append(discord.SelectOption(label=i, description=getemoji(i)['msg'], emoji=getemoji(i)['emoji']))
                super().__init__(placeholder='Choose Cogs to Unload', min_values=1, max_values=length, options=options)

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    async with ctx.typing():
                        Unloaded = ""
                        Failed = ""
                        for cog in self.values:
                            try:
                                if cog == 'jishaku':
                                    bot.unload_extension(cog)
                                else:
                                    bot.unload_extension(f"Cogs.{cog}")
                                Unloaded += f", `{cog}`"
                                for opt in view.children:
                                    for item in opt.options:
                                        print(item.value)
                                        if item.value == cog:
                                            item.description = "State: Unloaded"
                                            await msg.edit(view = view)
                                            break
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
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("Only the Bot Owner can run this command!", delete_after = 5)
    else:
        await senderror(bot,ctx,error)


#guild listeners
@bot.event
async def on_guild_join(guild):
    channel = bot.get_channel(874212184828297297)
    bot.log_channel = channel
    embed = guildanalytics(bot = bot, join=True, guild = guild)
    await bot.log_channel.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    embed = guildanalytics(bot = bot, join=False, guild = guild)
    channel = bot.get_channel(874212184828297297)
    bot.log_channel = channel
    await bot.log_channel.send(embed=embed)

#load Cogs on turning on
error = "Error with loading cogs:"
for i in coglist:
    try:
        if i == 'jishaku':
            bot.load_extension(i)
            logger.debug(f"Loaded Cog {i}") 
            continue
        bot.load_extension(f"Cogs.{i}")
        logger.debug(f"Loaded Cog {i}") 
    except:
        error += f" {i},"
        logger.debug(f"Error, failed to load Cog {i}") 
        pass

if error == "Error with loading cogs:":
    error = "No errors while Loading Cogs,"

print(f"Attempted to Load Cogs - {coglist}\n\n{error[:-1]}")

bot.loop.run_until_complete(run())
bot.run(TOKEN)