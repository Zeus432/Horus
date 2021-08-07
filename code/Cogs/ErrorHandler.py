from discord.ext import commands
from typing import Any
from Utils.Useful import BaseEmbed, print_exception

class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""
        async def send_del(*args: Any, **kwargs: Any) -> None:
            if embed := kwargs.get("embed"):
                command = self.bot.get_command('ping')
                command_sig = f"{ctx.clean_prefix}{command.qualified_name} {command.signature}"
                text = f"If you think this is an error. Report via {command_sig}"
                embed.set_footer(icon_url=self.bot.user.avatar, text=text)
            await ctx.reply(*args, delete_after=60, **kwargs)
        if hasattr(ctx.command, 'on_error'):
            return

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

        elif isinstance(error, commands.NoPrivateMessage):
            pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'ui':
                await ctx.send('I could not find that member. Please try again.')
            else:
                senderror = True

        else:
            senderror = True
        if senderror == True:
            await send_del(embed=BaseEmbed.to_error(description=f"{error}"))
            traceback_error = print_exception(f'Ignoring exception in command {ctx.command}:', error)
            error_message = "__**Command Errored!**__\n\n" \
                            f"**Command:** {ctx.message.content}\n" \
                            f"**Message ID:** `{ctx.message.id}`\n" \
                            f"**Author:** {ctx.author.mention} (`{ctx.author.id}`)\n" \
                            f"**Guild:** **{ctx.guild}** (`{ctx.guild.id}`)\n" \
                            f"**Channel:** {ctx.channel.mention} (`{ctx.channel.id}`)\n" \
                            f"**Jump:** [`Jump to Error`]({ctx.message.jump_url})"
            channel = self.bot.get_channel(873252901726863441)
            self.bot.error_channel = channel
            await self.bot.error_channel.send(embed=BaseEmbed.default(ctx, description=error_message))
            await self.bot.error_channel.send(f"```py\n{traceback_error}```")

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
