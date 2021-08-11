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

    @commands.command(pass_context=True, name='eval', aliases = ['e'])
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
            view=HelpButtons(60)
            if ret is None:
                if value:
                    msg =await ctx.send(f'```py\n{value}\n```', view=view)
                    try:
                        await asyncio.wait_for(view.wait(), timeout=30)
                    except asyncio.TimeoutError:
                        try:
                            await msg.edit(view=None)
                        except:
                            pass
            else:
                self._last_result = ret
                msg = await ctx.send(f'```py\n{value}{ret}\n```', view=view)
                try:
                    await asyncio.wait_for(view.wait(), timeout=30)
                except asyncio.TimeoutError:
                    try:
                        await msg.edit(view=None)
                    except:
                        pass
    @_eval.error
    async def _eval_error(self, ctx, error, test = None):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send(f"Give me something to eval bitch, this isn't just for you to flex your eval perms {botemojis('kermitslap')}")
        else:
            print(error)
    
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
    
    @commands.command(aliases = ["wa","whoevenaskedbro"], brief = "when people say random shit no one asked for")
    async def whoasked(self, ctx, what: Union[discord.Member, discord.Message, str] = "None"):
        """Who even asked bro"""
        msgid = None
        if type(what) == discord.message.Message:
            msgid = what.id
        elif type(what) == discord.member.Member:
            messages = await ctx.channel.history(limit=20).flatten()
            for m in messages:
                if m.author.id == what.id:
                    msgid = m.id
                    break
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label= "◄◄", style=discord.ButtonStyle.grey))
        view.add_item(discord.ui.Button(label= "▐▐", style=discord.ButtonStyle.grey))
        view.add_item(discord.ui.Button(label= "►►", style=discord.ButtonStyle.grey))
        button = discord.ui.Button(emoji= "\U0001f50a", style=discord.ButtonStyle.grey)
        async def callback(interaction):
            if button.emoji.name == "\U0001f50a":
                button2.label = "◉━━━━━"
                button.emoji = "\U0001f507"
            else:
                button2.label = "━━━━━◉"
                button.emoji = "\U0001f50a"
            await interaction.response.edit_message(view=view)
        button.callback = callback
        view.add_item(button)
        button2 = discord.ui.Button(label= "━━━━━◉", style=discord.ButtonStyle.grey)
        view.add_item(button2)
        try:
            channel = ctx.channel
            replyto = await channel.fetch_message(msgid)
            msg = await replyto.reply('Now playing: \nWho Asked (Feat. Nobody Did)\n⬤────────────────', view=view)
        except:
            msg = await ctx.send('Now playing: \nWho Asked (Feat. Nobody Did)\n⬤────────────────', view=view)
        for x in range(1,5):
            await asyncio.sleep(1)
            try:
                await msg.edit("Now playing: \nWho Asked (Feat. Nobody Did)\n"+"────"*x + "⬤" + "────"*(4-x))
            except:
                pass
        for item in view.children:
            if item.label == "▐▐":
                item.label = "▶"
                try:
                    await msg.edit(view = view)
                except:
                    pass
                break
        await asyncio.sleep(60)
        for item in view.children:
            item.disabled = True
        try:
            await msg.edit(view = view)
        except:
            pass

    @commands.command(aliases = ['di'])
    async def disable(self, ctx, command):
        """Disable a command."""

        command = self.bot.get_command(command)
        if command == None:
            return await ctx.send("Could not find command")
        if not command.enabled:
            return await ctx.send("This command is already disabled.")
        command.enabled = False
        await ctx.send(f"Disabled {command.name} command.")

    @commands.command(aliases = ['en'])
    async def enable(self, ctx, command):
        """Enable a command."""

        command = self.bot.get_command(command)
        if command == None:
            return await ctx.send("Could not find command")
        if command.enabled:
            return await ctx.send("This command is already enabled.")
        command.enabled = True
        await ctx.send(f"Enabled {command.name} command.")

    @commands.command()
    async def getguilds(self, ctx):
        async with ctx.typing():
            msg = await ctx.reply("Fetching Guilds", mention_author = False)
            guilds = ", ".join([g.name + f" ({g.id})" for g in self.bot.guilds])
            await msg.delete()
            await ctx.send(f"```glsl\n{guilds}```")

    @commands.group(invoke_without_command=True)
    async def foo(self, ctx):
        await ctx.send("1")

    @foo.group(invoke_without_group = True)
    async def sub(self, ctx):
        await ctx.send("2")
    @sub.command()
    async def meee(self, ctx):
        await ctx.send("3")      

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction(botemojis('error'))
        elif isinstance(error, commands.MissingRequiredArgument):
            pass
        else:
            await ctx.reply(error)  

def setup(bot):
    bot.add_cog(Owner(bot))