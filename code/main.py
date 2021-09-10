import asyncio
import discord
from discord.ext import commands
import time
import datetime
from loguru import logger
import asyncpg
from Utils.Useful import *
from Core.settings import *
from Utils.Menus import *

coglist = WorkingCogs
logger.remove()
pathway = pathway + "/Horus/code/Core/horus.log"
logger.add(pathway,level="DEBUG",format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
logger.info("Logged into Horus succesfully")

async def run():
    credentials = {"user": dbuser, "database": dbdb, "host": dbhost}
    db = await asyncpg.create_pool(**credentials)
    bot.db = db

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=self.noprefix,  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle, description="Horus is a private bot made for fun and is also called as Whorus <:YouWantItToMoveButItWont:873921001023500328>")
    
    async def noprefix(self, bot, message):
        prefix_return = ["h!","H!"]
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
bot.cogslist = WorkingCogs
bot.emojislist = botemojis
bot.case_insensitive = True
bot.usingsend = []
bot.usingsendchk = {876703407551938580:True,876703436048044092:True,876703447083253770:True,True:True}

#Load Dropdown Menu
class Load(discord.ui.Select):
    def __init__(self, coglist, ctx):
        self.ctx = ctx
        def loadcheck(cog):
            if cog in bot.extensions:
                return 'Loaded'
            return 'Unloaded'
        length = len(coglist)
        lemoji = {'Cogs':botemojis('cogs'),'Core':botemojis('core'),'jishaku':botemojis('staff')}
        ldesc = {'Cogs':'Cog','Core':'Core Module','jishaku':'Extenision'}
        options = []
        for i in coglist:
            options.append(discord.SelectOption(label=i.split('.')[-1], description=f"{ldesc[i.split('.')[0]]}: {loadcheck(i)}",emoji=f"{lemoji[i.split('.')[0]]}"))
        super().__init__(placeholder='Choose Cogs to Load', min_values=1, max_values=length, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return
        async with self.ctx.typing():
            unload = rload = fload = ""
            for cog in self.values:
                cog = [c for c in bot.cogslist if cog in c][0]
                try:
                    bot.load_extension(cog)
                    unload += f", `{cog}`"
                except commands.ExtensionAlreadyLoaded:
                    bot.unload_extension(cog)
                    bot.load_extension(cog)
                    rload += f", `{cog}`"
                except commands.ExtensionNotFound:
                    fload += f", `{cog}`"
            message = ""
            message += '\U0001f4e5 **Loaded:**\n'+f"{unload[1:]}\n\n" if unload else ""
            message += "\U0001f501 **Reloaded:**\n"+f"{rload[1:]}\n\n" if rload else ""
            message += f"{botemojis('error')} **Failed to Load:**\n"+f"{fload[1:]}\n\n" if fload else ""
            await interaction.response.send_message(message)

@bot.command(name="load", aliases = ['l','reload','rl'], help = "Load Cogs onto the bot", brief = "Load Cogs")
@commands.is_owner()
async def load(ctx, cog = None):
    load = rload = fload = ""
    coglist = bot.cogslist

    if cog == None:
        view = discord.ui.View()
        while len(coglist) > 20:
            coglist = coglist[20:]
            view.add_item(Load(coglist=coglist[:20],ctx=ctx))
        if coglist:
            view.add_item(Load(coglist=coglist,ctx=ctx))
        message = await ctx.reply(f"Load Cogs",view=view)
        await view.wait()
        for item in view.children:
            item.disabled = True
        await message.edit(view=view)
        return

    cog = "" if cog.lower() == "all" else cog
    coglist = [c for c in bot.cogslist if cog.lower() in c.lower()]
    if coglist:
        for x in coglist:
            try:
                bot.load_extension(x)
                load += f", `{x}`"
            except commands.ExtensionAlreadyLoaded:
                bot.unload_extension(x)
                bot.load_extension(x)
                rload += f", `{x}`"
            except commands.ExtensionNotFound:
                fload += f", `{x}`"
        message = ""
        message += '\U0001f4e5 **Loaded:**\n'+f"{load[1:]}\n\n" if load else ""
        message += "\U0001f501 **Reloaded:**\n"+f"{rload[1:]}\n\n" if rload else ""
        message += f"{botemojis('error')} **Failed to Load:**\n"+f"{fload[1:]}\n\n" if fload else ""
        await ctx.send(message)

@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("Only the Bot Owner can load Modules", delete_after = 5)
    else:
        await senderror(bot,ctx,error)


#Unload Dropdown Menu
class Unload(discord.ui.Select):
    def __init__(self, coglist, ctx):
        self.ctx = ctx
        def loadcheck(cog):
            if cog in bot.extensions:
                return 'Loaded'
            return 'Unloaded'
        length = len(coglist)
        lemoji = {'Cogs':botemojis('cogs'),'Core':botemojis('core'),'jishaku':botemojis('staff')}
        ldesc = {'Cogs':'Cog','Core':'Core Module','jishaku':'Extenision'}
        options = []
        for i in coglist:
            options.append(discord.SelectOption(label=i.split('.')[-1], description=f"{ldesc[i.split('.')[0]]}: {loadcheck(i)}",emoji=f"{lemoji[i.split('.')[0]]}"))
        super().__init__(placeholder='Choose Cogs to Unload', min_values=1, max_values=length, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return
        async with self.ctx.typing():
            unload = aload = fload = ""
            for cog in self.values:
                cog = [c for c in bot.cogslist if cog in c][0]
                try:
                    bot.unload_extension(cog)
                    unload += f", `{cog}`"
                except commands.ExtensionNotFound:
                    fload += f", `{cog}`"
                except commands.ExtensionNotLoaded:
                    aload += f", `{cog}`"
            message = ""
            message += '\U0001f4e4 **Unloaded:**\n'+f"{unload[1:]}\n\n" if unload else ""
            message += f"{botemojis('cross')} **Already Unloaded:**\n"+f"{aload[1:]}\n\n" if aload else ""
            message += f"{botemojis('error')} **Failed to Unload:**\n"+f"{fload[1:]}\n\n" if fload else ""
            await interaction.response.send_message(message)

@bot.command(name="unload", aliases = ['ul'], help = "Unload loaded Cogs", brief = "Unload Cogs")
@commands.is_owner()
async def unload(ctx, cog = None):
    unload = aload = fload = ""
    coglist = bot.cogslist

    if cog == None:
        view = discord.ui.View()
        while len(coglist) > 20:
            coglist = coglist[20:]
            view.add_item(Unload(coglist=coglist[:20],ctx=ctx))
        if coglist:
            view.add_item(Unload(coglist=coglist,ctx=ctx))
        message = await ctx.reply(f"Unload Cogs",view=view)
        await view.wait()
        for item in view.children:
            item.disabled = True
        await message.edit(view=view)
        return

    cog = "" if cog.lower() == "all" else cog
    coglist = [c for c in coglist if cog.lower() in c.lower()]
    if coglist:
        for x in coglist:
            try:
                bot.unload_extension(x)
                unload += f", `{x}`"
            except commands.ExtensionNotFound:
                fload += f", `{x}`"
            except commands.ExtensionNotLoaded:
                aload += f", `{x}`"
        message = ""
        message += '\U0001f4e4 **Unloaded:**\n'+f"{unload[1:]}\n\n" if unload else ""
        message += f"{botemojis('cross')} **Already Unloaded:**\n"+f"{aload[1:]}\n\n" if aload else ""
        message += f"{botemojis('error')} **Failed to Load:**\n"+f"{fload[1:]}\n\n" if fload else ""
        await ctx.send(message)

@unload.error
async def unload_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("Only the Bot Owner can unload Modules", delete_after = 5)
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

@bot.event
async def on_message(message: discord.Message):
    channel = bot.get_channel(880294858600894494)
    if message.guild is None and not message.author.bot:
        final = message.content
        view = discord.ui.View()
        if len(message.content) > 1900:
            fl = await mystbin(data = message.content)
            final = f"Message too long to Display"
            view.add_item(discord.ui.Button(label="MystBin", style=discord.ButtonStyle.link, url=f"{fl}"))
        await channel.send(f"\u200b\n**{message.author}** (`{message.author.id}`) [<t:{round(message.created_at.timestamp())}:T>]\n{final}",view=view,files=[await attachment.to_file() for attachment in message.attachments])
    await bot.process_commands(message)

#load Cogs on turning on
error = "Error with loading cogs:"
for i in coglist:
    try:
        bot.load_extension(f"{i}")
        logger.debug(f"Loaded Cog {i}") 
    except:
        error += f" {i},"
        logger.error(f"Failed to load Cog {i}") 
        pass

if error == "Error with loading cogs:":
    error = "No errors while Loading Cogs,"

print(f"Attempted to Load Cogs - {coglist}\n\n{error[:-1]}")

bot.loop.run_until_complete(run())
bot.run(TOKEN)