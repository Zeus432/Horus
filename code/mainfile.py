import asyncio
import discord
from discord.ext import commands
#/usr/local/bin/python3 /Users/siddharthm/Desktop/mine/Horus/main.py

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('h!'),  intents = discord.Intents.all(), activity = discord.Game(name="Waking Up"), status=discord.Status.idle)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await asyncio.sleep(10)
        await bot.change_presence(status=discord.Status.do_not_disturb, activity = discord.Game(name="h!help | Watching over Woodlands"))
        bot.launch_time = datetime.datetime.utcnow()
        bot.launch_ts = time.time()

bot = Bot()
bot.owner_ids = BotOwners
bot.launch_time = datetime.datetime.utcnow()
bot.launch_ts = time.time()

@bot.command(name="load", aliases = ['l'], help = "Load Cogs onto the bot", brief = "Load Cogs")
@commands.is_owner()
async def load(ctx, cog_name = None):
    coglist = WorkingCogs
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
                cogdetails = {'ErrorHandler':{'emoji':'<:Error:873642469114384456>','msg':'Load up the Global Error Handler'},'CustomHelp':{'emoji':'<a:DES_Loading2:864035219971506226>','msg':'Load the Custom Help Menu for the Bot'}}
                def getemoji(cog):
                    try:
                        return cogdetails[cog]
                    except:
                        return {'emoji':'<:cogsred:873220470416236544>','msg':f'Load Cog: {cog}'}
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

@commands.is_owner()
async def unload(ctx, cog_name = None):
    coglist = WorkingCogs
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
                cogdetails = {'ErrorHandler':{'emoji':'<:Error:873642469114384456>','msg':'Unload Global Error Handler'},'CustomHelp':{'emoji':'<a:DES_Loading2:864035219971506226>','msg':'Unload the Custom Help Menu and use the default'}}
                def getemoji(cog):
                    try:
                        return cogdetails[cog]
                    except:
                        return {'emoji':'<:cogsred:873220470416236544>','msg':f'Unload Cog: {cog}'}
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

#load Cogs on turning on
error = "Error with loading cogs:"
for i in coglist:
    try:
        bot.load_extension(f"Cogs.{i}")
    except:
        error += f" {i},"
        pass
if error == "Error with loading cogs:":
    error = "No errors while Loading Cogs,"

print(f"Attempted to Load Cogs - {coglist}\n\n{error[:-1]}")

bot.run(TOKEN)
