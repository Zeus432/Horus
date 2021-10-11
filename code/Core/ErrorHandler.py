from discord.ext import commands
from typing import Any
from Utils.Useful import *
from Utils.Menus import senderror as senderr, ErrorsPagination

class CommandErrorHandler(commands.Cog, name = "ErrorHandler"):
    """ Global Handler and Management for Errors"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""
        if hasattr(ctx.command, 'on_error'):
            return
        senderror = None
        cmd = self.bot.get_command(ctx.invoked_with)

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, commands.NoPrivateMessage, commands.errors.ExpectedClosingQuoteError)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.reply(f'This command is disabled.')

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.CheckFailure):
            if self.bot.devmode and ctx.author.id != 760823877034573864:
                return
            if ctx.command.qualified_name != 'coolservers':
                if ctx.command.qualified_name == 'whoasked':
                    return
                elif ctx.cog.qualified_name == "Owner":
                    return await ctx.reply(f"These are Bot Owner only commands and I don't see you on the list {self.bot.emojislist('idrk')}", mention_author = False)
                await ctx.reply(f"Missing Permissions!")
            else:
                await ctx.reply(f'This command is not available currently', delete_after = 10)
        
        elif isinstance(error, commands.GuildNotFound):
            await ctx.send(f'Could not find guild: {error.argument}')

        elif isinstance(error, commands.BadArgument):
            return await ctx.send_help(ctx.command)
        
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.reply(f'Woah Woah chill with the spam boi, Try again in {round(error.retry_after, 2)} seconds')
        
        elif isinstance(error, commands.MissingPermissions):
            if isinstance(ctx.channel, discord.TextChannel) and ctx.channel.permissions_for(ctx.channel.guild.me).send_messages:
                senderror = True
            else: pass

        else:
            senderror = True
        if senderror == True:
            await senderr(bot=self.bot,ctx=ctx,error=error)
    
    @commands.group(invoke_without_command = True, brief = "View Bot Errors")
    @commands.is_owner()
    async def errors(self, ctx, start:int = 1):
        """ View the latest bot errors that happened since the bot started up without having to visit the Error Logs every time """
        errors = self.bot.latesterrors[::-1]
        msg = await ctx.reply(f"Looking for Errors {self.bot.emojislist('loading')}",mention_author = False)
        if len(errors) == 0:
            await msg.edit("No errors found to view!")
            return
        start = start if len(errors) >= start else 1
        view = errors[start - 1]['view']
        embed = errors[start - 1]['embed'].copy()
        embed.title = f"Error #{start}"
        channel = self.bot.get_channel(873252901726863441)
        messages = await channel.history(limit=1).flatten()
        lastmsg = messages[0].jump_url
        view = ErrorsPagination(start = start, pages = errors, oldview = view, lastmsg = lastmsg)
        view.user,view.bot = ctx.author,self.bot
        view.message = msg
        await msg.edit(content=f"```py\n{errors[0]['error']}```",embed=embed,view=view)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))