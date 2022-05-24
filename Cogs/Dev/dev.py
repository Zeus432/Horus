import discord
from Core.bot import Horus, HorusCtx
from discord.ext import commands

from contextlib import redirect_stdout
from datetime import datetime
import traceback
import textwrap
import io

from Core.Utils.functions import write_toml
from .functions import get_reply, cleanup_code, restart_program
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
