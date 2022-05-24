import discord
from Core.bot import Horus, HorusCtx
from discord.ext import commands

from contextlib import redirect_stdout
from datetime import datetime
import traceback
import textwrap
import time
import io

from Core.Utils.functions import write_toml
from .functions import get_reply, cleanup_code, restart_program, plural, TabularData
from .views import ConfirmShutdown


class Dev(commands.Cog):
    """ Bot Management """

    def __init__(self, bot: Horus):
        self.bot = bot
        self._last_result = None

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
        `discord` - disnake.py library
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
            await ctx.try_add_reaction("<:TickYes:904315692311011360>")

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
    
    @commands.command(name = "shutdown", aliases = ['die','sd','stop'], help = "Shutdown the Bot", brief = "Shutdown")
    async def shutdown(self, ctx: HorusCtx):
        # Define some confirm buttons functions
        view = ConfirmShutdown(self.bot, ctx, 60)
        view.message = await ctx.reply("Are you sure you want to shutdown?", view = view)
    
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