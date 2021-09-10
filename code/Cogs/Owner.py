from discord.ext import commands
import discord
import asyncio
from discord.ext.commands import Greedy
from Utils.Useful import *
from Core.settings import *
from Utils.Menus import *
from typing import Union
import io
from contextlib import redirect_stdout
import textwrap
import sys
import os

class Owner(commands.Cog):
    """ Overall bot management (or just for abooz) commands """

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
        if ctx.command.qualified_name != 'whoasked':
            return await self.bot.is_owner(ctx.author)
        else:
            if await self.bot.is_owner(ctx.author) == True or ctx.author.id in sweg:
                return True
            else:
                return False

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot.http.token': "",
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'faketoken': "||MjM4Uc3Nz **Token Deez Nuts** Bad joke? Nvm then <:YouWantItToMoveButItWont:873921001023500328> .wNNTIxzQgV4||",
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body.replace('bot.http.token','faketoken'))
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
    
    @commands.command(aliases = ["wa","whoevenaskedbro"], brief = "when people say random shit no one asked for", hidden = True)
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
        if ctx.message.reference != None:
            msgid = ctx.message.reference.message_id
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label= "◄◄", style=discord.ButtonStyle.grey))
        view.add_item(discord.ui.Button(label= "▐▐", style=discord.ButtonStyle.grey))
        view.add_item(discord.ui.Button(label= "►►", style=discord.ButtonStyle.grey))
        buttontime = discord.ui.Button(label= "0:00 / 3:56", style=discord.ButtonStyle.grey)
        view.add_item(buttontime)
        button = discord.ui.Button(label= "━━━━━◉", emoji="\U0001f50a", style=discord.ButtonStyle.grey)
        async def callback(interaction):
            if button.emoji.name == "\U0001f50a":
                button.label = "◉━━━━━"
                button.emoji = "\U0001f507"
            else:
                button.label = "━━━━━◉"
                button.emoji = "\U0001f50a"
            await interaction.response.edit_message(view=view)
        button.callback = callback
        view.add_item(button)
        try:
            channel = ctx.channel
            replyto = await channel.fetch_message(msgid)
            msg = await replyto.reply('Now playing: \nWho Asked (Feat. Nobody Did)\n⬤────────────────', view=view)
        except:
            msg = await ctx.send('Now playing: \nWho Asked (Feat. Nobody Did)\n⬤────────────────', view=view)
        timelim = ['0:00', '1:19', '1:55', '2:37', '3:56']
        for x in range(1,5):
            await asyncio.sleep(1)
            try:
                buttontime.label = f"{timelim[x]} / 3:56"
                await msg.edit("Now playing: \nWho Asked (Feat. Nobody Did)\n"+"────"*x + "⬤" + "────"*(4-x), view=view)            
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
    async def sql(self, ctx, *, query: str):
        """Run some SQL."""
        # the imports are here because I imagine some people would want to use
        # this cog as a base for their other cog, and since this one is kinda
        # odd and unnecessary for most people, I will make it easy to remove
        # for those people.

        import time

        query = self.cleanup_code(query)

        is_multistatement = query.count(';') > 1
        if is_multistatement:
            # fetch does not support multiple statements
            strategy = self.bot.db.execute
        else:
            strategy = self.bot.db.fetch

        try:
            start = time.perf_counter()
            results = await strategy(query)
            dt = (time.perf_counter() - start) * 1000.0
        except Exception:
            return await ctx.send(f'```py\n{traceback.format_exc()}\n```')

        rows = len(results)
        if is_multistatement or rows == 0:
            return await ctx.send(f'`{dt:.2f}ms: {results}`')

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()

        fmt = f'```\n{render}\n```\n*Returned {plural(rows):row} in {dt:.2f}ms*'
        if len(fmt) > 2000:
            fp = io.BytesIO(fmt.encode('utf-8'))
            await ctx.send('Too many results...', file=discord.File(fp, 'results.txt'))
        else:
            await ctx.send(fmt)


    @commands.command()
    async def guilds(self, ctx):
        async with ctx.typing():
            msg = await ctx.reply("Fetching Guilds", mention_author = False)
            guilds = ", ".join([g.name + f" ({g.id})" for g in self.bot.guilds])
            await msg.delete()
            await ctx.send(f"```glsl\n{guilds}```")
    
    @commands.command()
    async def getguild(self, ctx, guild: discord.Guild):
        async with ctx.typing():
            emb = guildanalytics(bot = self.bot, join=None, guild = guild)
            view = GuildButtons(guild=guild,ctx=ctx,bot=self.bot,user=ctx.author)
            view.message = await ctx.reply(embed = emb,view = view)

    @commands.command()
    async def noprefix(self, ctx):
        try:
            if self.bot.prefixstate == False:
                self.bot.prefixstate = True
                state = f"enabled for bot owners {botemojis('tokitosip')}"
            else:
                self.bot.prefixstate = False
                state = "disabled, use default prefixes now <a:hmmnope:810188098464907334>"
        except:
            self.bot.prefixstate = True
            state = f"enabled for bot owners {botemojis('tokitosip')}"
        await ctx.reply(f"No prefix has been {state}")
    
    @commands.command()
    async def dm(self, ctx, member: Greedy[discord.User], *, message: str = None):
        reply,error = ctx,[]
        if not member:
            return await ctx.send_help(ctx.command)
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        if not message:
            await ctx.reply("Enter the message you want to send")
            try:
                message = await self.bot.wait_for(event='message', check=check, timeout=60)
                message = message.content
            except asyncio.TimeoutError:
                await ctx.reply(f"Can't send them a blank message dumbass {botemojis('kermitslap')}")
                return
        dmlist = '\n'.join([f"**{i}** (`{i.id}`)" for i in member])
        view = discord.ui.View(timeout=5)
        button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
        button.confirmed = True
        async def callback(interaction):
            if interaction.user.id != ctx.author.id:
                return
            emb.description = emb.description + "\n\n**Process Canceled by User**"
            emb.color = discord.Colour.red()
            await button.msg.edit(embed=emb)
            button.confirmed = False
            view.stop()
        button.callback = callback
        view.add_item(button)
        emb = discord.Embed(title="Attempting to dm the following users",description=dmlist,colour=self.bot.colour)
        confirm = button.msg = await reply.reply(embed = emb,view=view)
        await view.wait()
        await confirm.edit(view=None)
        if button.confirmed:
            for user in member:
                try:
                    await user.send(f"**You have a message from a Bot Dev - {ctx.author.name}**:\n{message}")
                except:
                    error.append(user)
            emb.description += "\n\n**Dmed All Users Successfully**" if not error else ""
            if error:
                emb.add_field(name="\n\nI was unable to dm the following users:",value="\n".join([f"{botemojis('parrow')} **{who}**" for who in error]))
            await confirm.edit(embed=emb)

    @commands.command()
    async def restart(self, ctx):
        def restart_program():
            python = sys.executable
            os.execl(python, python, * sys.argv)
        message = await ctx.send(f"Horus is Restarting {botemojis('loading')}")
        try:
            restart_program()
        except:
            await ctx.message.add_reaction(botemojis('warning'))
            await message.edit('Error I was unable to restart')

    @commands.group(invoke_without_command=True)
    async def foo(self, ctx):
        await ctx.send("1")

    @foo.group(invoke_without_group = True)
    async def sub(self, ctx):
        await ctx.send("2")
    @sub.command()
    async def meee(self, ctx):
        await ctx.send("3")      

#errorhandler

def setup(bot):
    bot.add_cog(Owner(bot))