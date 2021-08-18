from discord import colour
from discord.ext import commands
from typing import Any
from Useful.Useful import *

class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""
        async def send_del(*args: Any, **kwargs: Any) -> None:
            if embed := kwargs.get("embed"):
                text = f"Spamming errored commands will result in a blacklist"
                embed.set_footer(icon_url=self.bot.user.avatar, text=text)
            await ctx.reply(*args, **kwargs)
        if hasattr(ctx.command, 'on_error'):
            return
        senderror = None

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.reply(f'This command is disabled.')

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.NoPrivateMessage):
            pass

        elif isinstance(error, commands.CheckFailure):
            if ctx.command.qualified_name != 'coolservers':
                await ctx.reply("Missing Permissions!")
            else:
                await ctx.reply(f'This command is not available here', delete_after = 10)

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'userinfo':
                await ctx.send(error)
            else:
                senderror = True
        else:
            senderror = True
        if senderror == True:
            if await self.bot.is_owner(ctx.message.author):
                await ctx.message.add_reaction(botemojis('error'))
                await ctx.reply("This command has errored, check your Error Logs to see what happened")
            else:
                await send_del(embed=BaseEmbed.to_error("**Command Error!**",description=f"This error has been forwarded to the bot developer and will be fixed soon. Do not spam errored commands, doing so will get you blacklisted. If this isn't fixed feel free to dm me <@760823877034573864>\n\n**Error:**```py\n{error}```"), delete_after = 20)
            traceback_error = print_exception(f'Ignoring exception in command {ctx.command}:', error)
            embed = BaseEmbed.default(ctx, title = "**Command Error!**")
            embed.add_field(name="Command Used:", value=f"`{ctx.message.content}`", inline=False)
            embed.add_field(name="Author:", value=f"{ctx.author.mention}\n (`{ctx.author.id}`)")
            if ctx.guild:
                embed.add_field(name="Channel:", value=f"{ctx.channel.mention}\n (`{ctx.channel.id}`)")
                embed.add_field(name="Guild:", value=f"**{ctx.guild}**\n (`{ctx.guild.id}`)")
            else:
                embed.add_field(name="Dm Channel:", value=f"<#{ctx.channel.id}>\n (`{ctx.channel.id}`)")
            embed.add_field(name="Message ID:", value=f"`{ctx.message.id}`")
            embed.add_field(name="Jump to Error", value=f"[**Message Link \U0001f517**]({ctx.message.jump_url})")
            channel = self.bot.get_channel(873252901726863441)
            self.bot.error_channel = channel
            await self.bot.error_channel.send(embed=embed)
            await self.bot.error_channel.send(f"```py\n{traceback_error}```")

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))