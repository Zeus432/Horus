import disnake as discord
from bot import Horus
from disnake.ext import commands

from loguru import logger

from .useful import send_error

class ErrorHandler(commands.Cog, name = "ErrorHandler"):
    """ Global Error Handling """

    def __init__(self, bot: Horus):
        self.bot = bot
        logger.info("Error Handler Logged in")
        self.logger = logger

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """The event triggered when an error is raised while invoking a command."""
        if hasattr(ctx.command, 'on_error'):
            return
        senderror = None
        command = self.bot.get_command(ctx.invoked_with)

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, commands.NoPrivateMessage, commands.ExpectedClosingQuoteError, commands.NotOwner)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            return await ctx.reply(f'This command is disabled.')

        elif isinstance(error, commands.MissingRequiredArgument):
            #return await ctx.send_help(ctx.command)
            ending = f'Use {ctx.clean_prefix}help [command] for more info on a command.'
            syntax = f"Syntax: {ctx.clean_prefix}{ctx.command.qualified_name} {ctx.command.signature}"

            embed = discord.Embed(colour = self.bot.colour, title = f"{ctx.command.cog_name} Help" if ctx.command.cog_name else "Horus Help", description = f"```yaml\n{syntax}```\n{ctx.command.help or 'No documentation'}")
            embed.set_footer(text = ending, icon_url = "https://cdn.discordapp.com/avatars/858335663571992618/358132def732d61ce9ed7dbfb8f9a6c1.png?size=1024")

            if aliases := '`, `'.join(c for c in ctx.command.aliases):
                embed.add_field(name = "Aliases:", value = f"`{aliases}`", inline = False)
            
            if isinstance(ctx.command, commands.Group):
                #filtered = await self.filter_commands(ctx.command.commands, sort = True)

                for command in ctx.command.commands:
                    try: await command.can_run(ctx)
                    except: pass
                    else:
                        embed.add_field(name = f"> {command.qualified_name}", value = f"> " + (command.short_doc or 'No documentation'), inline = False)
            
            param = f"{error.param}".split(':')[0]
            space = len(syntax.split(f'<{param}>')[0])

            content = f"```yaml\n{syntax}\n{(space + 1)*' '}{'^'*len(param)}\n{error.args[0]}```"
            
            await ctx.reply(content = content, embed = embed, mention_author = False)

        elif isinstance(error, commands.CheckFailure):
            if "The check functions for" in f"{error}":
                return

            return await ctx.reply(f"{error}", mention_author = False)

        elif isinstance(error, commands.GuildNotFound):
            return await ctx.send(f'Could not find guild: `{error.argument}`')

        elif isinstance(error, (commands.BadArgument, commands.BadUnionArgument)):
            return await ctx.send_help(ctx.command)
        
        elif isinstance(error, commands.errors.CommandOnCooldown):
            if self.bot._bypass_cooldowns and ctx.author.id in self.bot.owner_ids:
                ctx.command.reset_cooldown(ctx)
                new_ctx = await self.bot.get_context(ctx.message)
                await self.bot.invoke(new_ctx)
                return

            return await ctx.reply(f'Whoa chill with the spam boi, Try again in {round(error.retry_after, 2)} seconds')
        
        elif isinstance(error, commands.MissingPermissions):
            if isinstance(ctx.channel, discord.TextChannel) and ctx.channel.permissions_for(ctx.channel.guild.me).send_messages:
                senderror = True
            else: pass
        else:
            senderror = True

        if senderror:
            await send_error(bot = self.bot, ctx = ctx, error = error)
    
    @commands.Cog.listener()
    async def on_message_command_error(self, interaction: discord.MessageCommandInteraction, error):
        command = interaction.application_command
        senderror = None
    
        if hasattr(command, 'on_error'):
            return

        cog = command.cog

        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
    
        error = getattr(error, 'original', error)

        if isinstance(error, commands.NotOwner):
            return await interaction.response.send_message(content = "This is an owner only command and you're not one!", ephemeral = True)

        if isinstance(error, commands.DisabledCommand):
            return await interaction.response.send_message(f'This command is disabled.', ephemeral = True)

        elif isinstance(error, commands.CheckFailure):
            return await interaction.response.send_message(f"{error}", ephemeral = True)

        elif isinstance(error, commands.GuildNotFound):
            return await interaction.response.send_message(f'Could not find guild: `{error.argument}`', ephemeral = True)
        
        elif isinstance(error, commands.errors.CommandOnCooldown):
            if self.bot._bypass_cooldowns and interaction.author.id in self.bot.owner_ids:
                command.reset_cooldown(interaction)
                await self.bot.process_application_commands(interaction)
                return

            return await interaction.response.send_message(f'Whoa chill with the spam boi, Try again in {round(error.retry_after, 2)} seconds', ephemeral = True)
        
        elif isinstance(error, commands.MissingPermissions):
            if isinstance(interaction.channel, discord.TextChannel) and interaction.channel.permissions_for(interaction.guild.me).send_messages:
                senderror = True
            else: pass
        else:
            senderror = True

        if senderror:
            await send_error(bot = self.bot, ctx = interaction, error = error)