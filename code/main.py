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
import argparse
import sys

#add parsers
parser = argparse.ArgumentParser()
parser.add_argument("--d","--devmode", help = "Enable Devmode on start",action = 'count',default = False)
flags = parser.parse_args()

coglist = WorkingCogs
logger.remove()
logpath = pathway + "/code/Core/horus.log"
logger.add(logpath,level="DEBUG",format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
logger.info("Logged into Horus succesfully")

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=self.noprefix,  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle, description="Horus is a private bot made for fun and is also called as Whorus <:YouWantItToMoveButItWont:873921001023500328>", case_insensitive=True)
        self.persview = False
        self.owner_ids = frozenset(BotOwners)
        self.launch_time = datetime.datetime.utcnow()
        self.launch_ts = time.time()
        self.colour = discord.Colour(0x9c9cff)
        self.cogslist = WorkingCogs
        self.latesterrors = []
        self.emojislist = botemojis
        self.devmode = True if flags.d else False
        self.prefixstate = False
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
    
    async def close(self):
        # do stuff
        await super().close()
    
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
        print(f'\nLogged in as {self.user} (ID: {self.user.id})')
        total_members = list(bot.get_all_members())
        total_channels = sum(1 for x in bot.get_all_channels())
        print(f'Guilds: {len(bot.guilds)}')
        print(f'Large Guilds: {sum(g.large for g in bot.guilds)}')
        print(f'Chunked Guilds: {sum(g.chunked for g in bot.guilds)}')
        print(f'Members: {len(total_members)}')
        print(f'Channels: {total_channels}')
        print(f'Message Cache Size: {len(bot.cached_messages)}\n')
        await asyncio.sleep(10)
        if not bot.devmode:
            await bot.change_presence(status=discord.Status.idle, activity = discord.Game(name="h!help | Watching over Woodlands"))
        else:
            await bot.change_presence(status=discord.Status.invisible, activity = discord.Game(name="Lurk"))
        bot.launch_time = datetime.datetime.utcnow()
        bot.launch_ts = time.time()
        if not self.persview:
            self.add_view(PersistentView())
            self.persview = True
        self.persistent_views_added = True

bot = Bot()

async def run():
    print("\nAttempting to connect to postgresql server")
    credentials = {"user": dbuser, "database": dbdb, "host": dbhost}
    closesys = True
    for i in range(5):
        try:
            bot.db = await asyncpg.create_pool(**credentials)
            print("Connection Successful")
            closesys = False
            break
        except:
            print("Error! I was unable to connect to server, Retrying in 5 seconds\n")
            await asyncio.sleep(5)
    if closesys:
        print("Error! All attempts to connect to server have failed, closing program!\n")
        sys.exit(1)

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

@bot.command(name="load", aliases = ['l','reload','rl','r'], help = "Load Cogs onto the bot", brief = "Load Cogs")
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

# Bot checks
@bot.check
async def owner_only(ctx: commands.Context) -> bool:
  """ Owner only commands globally. """
  if not bot.devmode:
      return True
  return ctx.author.id == 760823877034573864

#Global Cooldown
#_cd = commands.CooldownMapping.from_cooldown(1.0, 2.0, commands.BucketType.member)

#@bot.check_once
#async def cooldown_check(ctx):
    #if not ctx.guild:
        #return True
    #bucket = _cd.get_bucket(ctx.message)
    #retry_after = bucket.update_rate_limit()
    #if retry_after:
        #raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.member)
    #return True

# Persistent View
class PersistentButtons(discord.ui.Button):
    def __init__(self, x: int, y: int, role, emoji):
        super().__init__(style=discord.ButtonStyle.secondary, label=f'{role.name}', row=x, custom_id=f'per:{role.name}', emoji=f'{emoji}')
        self.rlist = {"Edgy":810018752639795220,"Cherry":810018754582151199,"Pearl":810018758009421834,"Bubblegum":810018760869543936,"Aqua":810018764467732480,"Sunset":810018767555526677,"Sky":810018771385319514,"Sid's Role":810090688838107157,"Random Colour":813387935394562108}
        self.x = x
        self.y = y
        self.role = role
    
    async def callback(self, interaction: discord.Interaction):
        role = self.role
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role,reason=f"Button roles")
            await interaction.response.send_message(f'I have removed the {role.mention} role from you', ephemeral=True)
        else:
            await interaction.user.add_roles(role,reason=f"Button roles")
            await interaction.response.send_message(f'I have added the {role.mention} role to you', ephemeral=True)

class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        rlist = {"00":810018752639795220,"01":810018754582151199,"02":810018758009421834,"03":810018760869543936,"10":810018764467732480,"11":810018767555526677,"12":810018771385319514,"13":813387935394562108}
        remoji = {"00":"\U000026ab","01":"\U0001f534","02":"\U000026aa","03":"<:pink_circle:886511143433166879>","10":"<:green:853998821663047710>","11":"\U0001f7e0","12":"\U0001f535","13":"<:rainbow_circle:886456317978484776>"}
        for x in range(2):
            for y in range(4):
                role = rlist[f'{x}{y}']
                emoji = remoji[f'{x}{y}']
                guild = bot.get_guild(809632911690039307)
                role = guild.get_role(role)
                self.add_item(PersistentButtons(x, y, role, emoji))

@bot.command(cooldown_after_parsing=True, aliases = ['broles','br'], brief = 'Button Colour roles', help = "Use Buttons to get colour roles")
@commands.check(woodlands_only)
@commands.is_owner()
async def buttonroles(ctx: commands.Context):
    view = PersistentView()
    embed = discord.Embed(title = "Colour Roles", colour = discord.Colour(0xFCAD69),description = "\U000026ab <@&810018752639795220>\n\U0001f534 <@&810018754582151199>\n\U000026aa <@&810018758009421834>\n<:pink_circle:886511143433166879> <@&810018760869543936>\n<:green:853998821663047710> <@&810018764467732480>\n\U0001f7e0 <@&810018767555526677>\n\U0001f535 <@&810018771385319514>\n<:rainbow_circle:886456317978484776> <@&813387935394562108>\n\nButton roles are an experimental feature to substitue reaction roles but they only work when <@858335663571992618> is online, so to get colour roles you can use the buttons when it is online and the reactions in <#809650375589625867> when it isn't")
    await ctx.send(embed = embed, view=view)

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