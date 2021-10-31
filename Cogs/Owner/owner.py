import discord
from discord.ext import commands

from contextlib import redirect_stdout
from datetime import datetime
import traceback
import textwrap
import time
import sys
import io
import os

from .useful import cleanup_code, plural, TabularData
from Core.Utils.useful import write_json
from Core.Utils.views import Confirm

class Owner(commands.Cog):
    """ Overall bot related management stuff, or just for abuse commands """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_result = None
    
    async def cog_check(self, ctx: commands.Context):
        result = await self.bot.is_owner(ctx.author)
        if result:
            return True
        raise commands.NotOwner()
    
    @commands.command(name='eval', brief = "Evaluate Code")
    async def _eval(self, ctx: commands.Context, *, body: str):
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
        `discord` - discord.py library
        `_` - The result of the last dev command.
        """

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
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
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
    
    @_eval.error
    async def _eval_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Give me something to eval dumbass, this isn't just for you to flex your eval perms")
        else:
            print(error)
    
    @commands.command(name="shutdown", aliases = ['die','sd','stop'], help = "Shutdown the Bot", brief = "Shutdown")
    async def shutdown(self, ctx: commands.Context):
        # Define some confirm buttons functions
        async def onconfirm(view: discord.ui.View, button: discord.Button, interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return
            await view.message.edit("https://tenor.com/view/nick-fury-mother-damn-it-gone-bye-bye-gif-16387502", view = None)
            try:
                await ctx.message.add_reaction(self.bot.get_em('tick'))
            except:
                pass
            view.stop()
            await self.bot.close()

        async def oncancel(view: discord.ui.View, button: discord.Button, interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return
            for item in view.children:
                item.disabled = True
                item.style = discord.ButtonStyle.red if item == button else discord.ButtonStyle.gray 
            await view.message.edit("Cancelled Shutdown...",view = view)
            view.stop()

        async def ontimeout(view: discord.ui.View):
            for item in view.children:
                item.disabled = True
                item.style = discord.ButtonStyle.red if item.label == "Cancel" else discord.ButtonStyle.gray 
            await view.message.edit("Cancelled Shutdown...",view = view)

        view = Confirm(onconfirm, oncancel, ontimeout, 60)
        view.message = await ctx.reply("Are you sure you want to shutdown?", view = view)
    
    @commands.command(brief = "Restart Bot")
    async def restart(self, ctx: commands.Context):
        """ Restart the Bot  """
        def restart_program():
            python = sys.executable
            os.execl(python, python, * sys.argv)
        message = await ctx.send(f"**{self.bot.user.name}** is Restarting")
        try:
            await ctx.message.add_reaction("\U000023f0")
        except:
            pass
        try:
            self.bot.config['restart'] = {
                "start": datetime.utcnow().timestamp(),
                "message": [message.channel.id, message.id],
                "invoke": [ctx.message.channel.id, ctx.message.id]
            }
            write_json('Core/config.json', self.bot.config)
            restart_program()
        except:
            await message.add_reaction(self.bot.get_em('cross'))
    
    @commands.command(aliases = ['en'], brief = "Enable Command")
    async def enable(self, ctx: commands.Context, command: str):
        """Enable a command."""
        command = self.bot.get_command(command)
        if command == None:
            return await ctx.send("Could not find command")
        if command.enabled:
            return await ctx.send("This command is already enabled.")
        command.enabled = True
        await ctx.send(f"Enabled {command.name} command.")

    @commands.command(aliases = ['di'], brief = "Disable Command")
    async def disable(self, ctx: commands.Context, command: str):
        """Disable a command."""
        command = self.bot.get_command(command)
        if command == None:
            return await ctx.send("Could not find command")
        if not command.enabled:
            return await ctx.send("This command is already disabled.")
        command.enabled = False
        await ctx.send(f"Disabled {command.name} command.")
    
    @commands.command(name = "sql", brief = "Run some Sql")
    async def sql(self, ctx: commands.Context, *, query: str):
        """
        Run some SQL.
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
            await ctx.send('Too many results...', file=discord.File(file, 'results.txt'))
        else:
            await ctx.send(endresult)
    
    @commands.command(name = "error", aliases = ["err"], brief = "Manual Error")
    async def error(self, ctx: commands.Context, error: commands.CommandError = commands.CommandError):
        """ Manually Invoke an Error """
        raise error