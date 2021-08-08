from discord.ext import commands
import discord
import traceback
import textwrap
from contextlib import redirect_stdout
import io
import asyncio

from Useful.Useful import *
# to expose to the eval command


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            num = 3
            if content.startswith('```\n'):
                num = 4
            elif content.startswith('```py\n'):
                num = 6
            return content[num:-3]
        else: return content

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author) 

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command(pass_context=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates code"""

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

        body = self.cleanup_code(body)
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
                await ctx.message.add_reaction(botemojis('tick'))
            except:
                pass
            view=HelpButtons()
            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```', view=view)
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```', view=view)
    @_eval.error
    async def _eval_error(self, ctx, error, test = None):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("I need something to eval bitch")
        else:
            await ctx.send(f"```py\n{error}```")
    
    @commands.command(name="shutdown", aliases = ['stop','gotosleepwhorus'], help = "Shutdown the bot in a peaceful way, rather than just closing the window", brief = "Shutdown ")
    async def shutdown(self, ctx):
        """Put Horus to sleep <a:Frogsleb:849663487080792085> """
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
            await ctx.message.add_reaction(botemojis('tick'))
        except:
            pass
        await self.bot.close()
    
    @commands.command()
    async def disable(self, ctx, command):
        """Disable a command."""

        command = self.bot.get_command(command)
        if command == None:
            return await ctx.send("Could not find command")
        if not command.enabled:
            return await ctx.send("This command is already disabled.")
        command.enabled = False
        await ctx.send(f"Disabled {command.name} command.")

    @commands.command()
    async def enable(self, ctx, command):
        """Enable a command."""

        command = self.bot.get_command(command)
        if command == None:
            return await ctx.send("Could not find command")
        if command.enabled:
            return await ctx.send("This command is already enabled.")
        command.enabled = True
        await ctx.send(f"Enabled {command.name} command.")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("Missing Permissions! Only the Bot Owner can run this")
            await ctx.message.add_reaction(botemojis('boost'))
        else:
            await ctx.reply(error)           

def setup(bot):
    bot.add_cog(Owner(bot))
