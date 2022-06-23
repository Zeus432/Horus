import discord
from discord.ext import commands
from discord import app_commands
from Core.bot import Horus, HorusCtx

import re
import traceback

from .functions import send_error


class ErrorHandler(commands.Cog):
    """ Global Error Handling """

    def __init__(self, bot: Horus):
        self.bot = bot
        self.emote = bot.get_em('errorhandler')
        self.bot.tree.on_error = self.on_tree_error
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: HorusCtx, error: commands.CommandError):
        if hasattr(ctx.command, "on_error"):
            return # return if command has local error handler

        command = self.bot.get_command(ctx.invoked_with)

        if cog := ctx.cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return # return if cog has local error handler
        
        error = getattr(error, "original", error)
        ignored = (commands.CommandNotFound, commands.NoPrivateMessage, commands.ExpectedClosingQuoteError, commands.NotOwner)

        if isinstance(error, ignored):
            return
        
        if isinstance(error, commands.DisabledCommand):
            return await ctx.reply(f"This command is disabled.", mention_author = False)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            syntax = f"Syntax: {ctx.clean_prefix}{ctx.command.qualified_name} {ctx.command.signature}"
            result = re.findall("[0-9]+", getattr(ctx.cog, "emote", self.bot.memoji))

            embed = discord.Embed(colour = self.bot.colour, description = f"```yaml\n{syntax}```\n" + (f"{ctx.command.help}" or "No documentation"))
            embed.set_author(name = f"{ctx.command.cog_name} Help" if ctx.command.cog_name else f"{self.bot.user.name} Help", icon_url = f"https://cdn.discordapp.com/emojis/{result[0]}.webp?size=240&quality=lossless")
            embed.set_footer(text = f"Use {ctx.clean_prefix}help [command] for more info on a command.")

            if aliases := [c for c in ctx.command.aliases]:
                embed.add_field(name = "Aliases:", value = f"`" + "`, `".join(aliases) + "`", inline = False)
            
            if isinstance(ctx.command, commands.Group):
                filtered = await self.bot.help_command.filter_commands(ctx.command.commands, sort = True)

                for command in filtered:
                    try:
                        await command.can_run(ctx)
                    except:
                        pass
                    else:
                        embed.add_field(name = f"> {command.qualified_name}", value = f"> " + (command.short_doc or "No documentation"), inline = False)
            
            param = f"{error.param}".split(":")[0]
            space = len(syntax.split(f"<{param}>")[0])
            content = f"```yaml\n{syntax}\n" + (space + 1) * " " + "^" * len(param) + f"\n{error.args[0]}```"

            return await ctx.reply(content = content, embed = embed, mention_author = False)
        
        elif isinstance(error, commands.CheckFailure):
            return await ctx.reply(f"{error}", mention_author = False)
        
        elif isinstance(error, commands.GuildNotFound):
            return await ctx.send(f"Could not find guild: `{error.argument}`")
        
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send(f"Could not find user: `{error.argument}`")
        
        elif isinstance(error, (commands.BadArgument, commands.BadUnionArgument)):
            return await ctx.send_help(ctx.command)
        
        elif isinstance(error, commands.CommandOnCooldown):
            if self.bot._bypasscd and ctx.author.id in self.bot.owner_ids:
                ctx.command.reset_cooldown(ctx)
                new_ctx = await self.bot.get_context(ctx.message)

                if ctx.valid:
                    return await self.bot.invoke(new_ctx)

            return await ctx.reply(f"You've hit the command ratelimit, Try again in {round(error.retry_after, 2)} seconds", mention_author = False)
        
        elif isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.reply(f"{error}", mention_author = False)
        
        elif isinstance(error, commands.MissingPermissions):
            if isinstance(ctx.channel, discord.TextChannel) and ctx.channel.permissions_for(ctx.channel.guild.me).send_messages is False:
                return
        
        await send_error(self.bot, ctx, error)

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        await interaction.response.send_message("This slash command has errored, please try again!", ephemeral = True)
        await traceback.print_exception(type(error), error, error.__traceback__)