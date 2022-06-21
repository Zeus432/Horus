import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from contextlib import redirect_stdout
from datetime import datetime
import traceback
import textwrap
import time
import io

from Core.Utils.functions import GuildEmbed, write_toml
from Core.settings import INITIAL_EXTENSIONS
from .functions import get_reply, cleanup_code, restart_program, plural, TabularData
from .views import ConfirmShutdown, ChangeStatus, GuildView, ConfirmLeave


class Dev(commands.Cog):
    """ Bot Management """

    def __init__(self, bot: Horus):
        self.bot = bot
        self._last_result = None
        self._last_cog = None

    async def cog_check(self, ctx: HorusCtx):
        if await self.bot.is_owner(ctx.author):
            return True
        raise commands.NotOwner()
    
    @commands.command(name = 'eval', aliases = ['e'], brief = "Evaluate Code")
    async def _eval(self, ctx: HorusCtx, *, body: str):
        """ 
        **Execute asynchronous code.**
        This command wraps code into the body of an async function and then
        calls and awaits it. The bot will respond with anything printed to
        stdout, as well as the return value of the function.

        The code can be within a codeblock, inline code or neither, as long
        as they are not mixed and they are formatted correctly.

        **Environment Variables:**
        `ctx` - command invocation context
        `bot` - bot object
        `channel` - the current channel object
        `author` - command author's member object
        `message` - the command's message object
        `_` - The result of the last dev command.
        """

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'reply': get_reply(ctx),
            '_': self._last_result
        }

        env.update(globals())

        body = cleanup_code(content = body)
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
            await ctx.tick(ignore_errors = True)

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
    
    @_eval.error
    async def _eval_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Give me something I can't eval empty space.")
        else:
            print(error)

    @commands.command(name = "restart", brief = "Restart Bot")
    async def restart(self, ctx: HorusCtx):
        """ Easier way to restart the bot without having to stop it and then manually start it again """
        print("\nRestarting Bot . . .\n")
        message = await ctx.send(f"**{self.bot.user.name}** is Restarting")
        await ctx.try_add_reaction("\U000023f0")

        try:
            self.bot._config['restart'] = {
                "start": datetime.utcnow().timestamp(),
                "message": [message.channel.id, message.id],
                "invoke": [ctx.message.channel.id, ctx.message.id]
            }
            write_toml('Core/config.toml', self.bot._config)
            restart_program()
        except:
            await message.add_reaction(self.bot.get_em('cross'))
    
    @commands.command(name = "shutdown", aliases = ['die','sd','stop', 'https://tenor.com/view/thanos-gamora-infinity-war-soul-stone-sacrifice-gif-14289940'], help = "Shutdown the Bot", brief = "Shutdown")
    async def shutdown(self, ctx: HorusCtx):
        # Define some confirm buttons functions
        await ctx.reply("Are you sure you want to shutdown?", view = ConfirmShutdown(self.bot, ctx, 60))
    
    @commands.command(name = "enable", aliases = ['en'], brief = "Enable Command")
    async def enable(self, ctx: HorusCtx, command: str):
        """Enable a command."""
        cmd = self.bot.get_command(command)
        if command == None:
            return await ctx.send("Could not find command")
        if command.enabled:
            return await ctx.send("This command is already enabled.")

        command.enabled = True
        await ctx.send(f"Enabled {command.name} command.")

    @commands.command(name = "disable", aliases = ['di'], brief = "Disable Command")
    async def disable(self, ctx: HorusCtx, command: str):
        """Disable a command."""
        command = self.bot.get_command(command)
        if command == None:
            return await ctx.send("Could not find command")
        if not command.enabled:
            return await ctx.send("This command is already disabled.")

        command.enabled = False
        await ctx.send(f"Disabled {command.name} command.")
    
    @commands.command(name = "sql", brief = "Run some Sql")
    async def sql(self, ctx: HorusCtx, *, query: str):
        """
        Run some SQL and get properly formatted result.
        """
        query = cleanup_code(query)

        is_multistatement = query.count(';') > 1
        if is_multistatement:
            # fetch does not support multiple statements
            execute = self.bot.db.execute
        else:
            execute = self.bot.db.fetch

        try:
            start = time.perf_counter()
            results = await execute(query)
            exectime = (time.perf_counter() - start) * 1000.0
        except Exception:
            return await ctx.send(f'```py\n{traceback.format_exc()}\n```')

        rows = len(results)
        if is_multistatement or rows == 0:
            return await ctx.send(f'`{exectime:.2f}ms: {results}`')

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()

        endresult = f'```\n{render}\n```\n*Returned {plural(rows):row} in {exectime:.2f}ms*'
        if len(endresult) > 2000:
            file = io.BytesIO(endresult.encode('utf-8'))
            await ctx.send('Too many results...', file = discord.File(file, 'results.txt'))
        else:
            await ctx.send(endresult)
    
    @commands.command(name = "devmode", brief = "Enter Devmode")
    async def devmode(self, ctx: HorusCtx):
        """ Start Developer mode to test major commands without others interfering """
        if self.bot._devmode:
            self.bot._devmode = False
            await self.bot.change_presence(status = discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.watching, name = f"for @{self.bot.user.name} help"))
            return await ctx.reply('Developer Mode has been disabled!')
        
        self.bot._devmode = True
        await self.bot.change_presence(status = discord.Status.invisible)
        return await ctx.reply('Developer Mode has been enabled!')
    
    @commands.command(name = "noprefix", brief = "Toggle Noprefix")
    async def noprefix(self, ctx: HorusCtx):
        """ Enable/Disable Noprefix for Bot Owners """
        self.bot._noprefix = False if self.bot._noprefix else True
        state = f"disabled, use default prefixes now {self.bot.get_em('hadtodoittoem')}" if not self.bot._noprefix else f"enabled for bot owners {self.bot.get_em('tokitosip')}"
        await ctx.reply(f"No prefix has been {state}")
    
    @commands.command(name = "status", brief = "Change Bot Status")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def status(self, ctx: HorusCtx):
        embed = discord.Embed(colour = self.bot.colour)
        embed.add_field(name = "Status:", value = f"{self.bot.get_em(ctx.guild.me.status.name)} {ctx.guild.me.status.name.capitalize()}", inline = False)
        if (act := ctx.guild.me.activity) is not None:
            embed.add_field(name = "Activity:", value = f"```{act.type.name.capitalize()} {act.name}```", inline = False)

        await ctx.send(embed = embed, view = ChangeStatus(self.bot, ctx))
    
    @commands.command(name = "load", aliases = ['l'], brief = "Load Cogs")
    async def load(self, ctx: HorusCtx, cog: str = None):
        """ Loads/Reloads the Cog(s) given. If no cog is mentioned it reloads the last loaded cog """
        if cog is None and (cog := self._last_cog) is None:
            return await ctx.reply("You need to provide a cog to load!")
        
        for c in INITIAL_EXTENSIONS:
            if cog.lower() in c.lower():
                cog = c
                break
        
        try:
            await self.bot.load_extension(cog)
        except commands.ExtensionAlreadyLoaded:
            try:
                await self.bot.unload_extension(cog)
                await self.bot.load_extension(cog)
            except Exception as error:
                await ctx.send(f"I was unable to reload `{cog}`\n```py\n{''.join(traceback.format_exception(type(error), error, error.__traceback__, 1))}```")
            
            else:
                await ctx.send(f"\U0001f501 Reloaded Module `{cog}`")
                self._last_cog = cog
        
        except Exception as error:
            await ctx.send(f"I was unable to load `{cog}`\n```py\n{''.join(traceback.format_exception(type(error), error, error.__traceback__, 1))}```")
        else:
            await ctx.send(f"\U0001f4e5 Loaded Module `{cog}`")
            self._last_cog = cog
    
    @commands.command(name = "unload", aliases = ['ul'], brief = "Unload Cogs")
    async def unload(self, ctx: HorusCtx, cog: str = None):
        """ Unloads the Cog(s) given. If no cog is mentioned it unloads the last loaded cog """
        if cog is None and (cog := self._last_cog) is None:
            return await ctx.reply("You need to provide a cog to unload!")
        
        for c in INITIAL_EXTENSIONS:
            if cog.lower() in c.lower():
                cog = c
                break
        
        try:
            await self.bot.unload_extension(cog)
        except Exception as error:
            await ctx.send(f"I was unable to unload `{cog}`\n```py\n{''.join(traceback.format_exception(type(error), error, error.__traceback__, 1))}```")
        else:
            await ctx.send(f"\U0001f4e4 Unloaded Module `{cog}`")
            self._last_cog = cog

    @commands.command(name = "guildlist", brief = "Guilds List")
    async def guildlist(self, ctx: HorusCtx):
        """ Get a list of all Guilds Horus is in """
        async with ctx.typing():
            msg = await ctx.reply("Fetching Guilds", mention_author = False)
            guilds = "\n".join([f"{index + 1}) {guild.name} ({guild.id})" for index, guild in enumerate(sorted(self.bot.guilds, key = lambda u: u.me.joined_at))])
        
        try:
            await msg.delete()
        except:
            await msg.edit(content = f"```glsl\n{guilds}```")
        else:
            await ctx.send(content = f"```glsl\n{guilds}```")
    
    @commands.command(name = "leave", brief = "Leave Guild")
    async def leave(self, ctx: HorusCtx, guild: discord.Guild = None):
        guild = ctx.guild if not guild else guild
        embed = discord.Embed(description = f"Are you sure you want to leave **[{guild}]({guild.icon})**?", colour = discord.Colour(0x2F3136))

        await ctx.reply(embed = embed, view = ConfirmLeave(self.bot, ctx))

    @commands.command(name = "getguild", aliases = ["gg"], brief = "Get Guild Info")
    async def getguild(self, ctx: HorusCtx, guild: discord.Guild = None):
        """ Get all information and staistics about the specified guild """
        guild = ctx.guild if not guild else guild

        await ctx.send(embed = GuildEmbed.default(self.bot, guild), view = GuildView(self.bot, ctx))