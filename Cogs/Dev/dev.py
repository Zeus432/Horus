import discord
from Core.bot import Horus
from discord.ext import commands

from contextlib import redirect_stdout
import traceback
import textwrap
import io

from .functions import get_reply, cleanup_code


class Dev(commands.Cog):
    """ Bot Management """

    def __init__(self, bot: Horus):
        self.bot = bot
        self._last_result = None

    async def cog_check(self, ctx: commands.Context):
        if await self.bot.is_owner(ctx.author):
            return True
        raise commands.NotOwner()
    
    @commands.command(name = 'eval', brief = "Evaluate Code", aliases = ['e'])
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
            await ctx.try_add_reaction(self.bot.get_em("tick"))

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
