from discord.ext import commands
import discord
from discord.ext.commands.context import Context
from Useful.Useful import HelpButtons
import asyncio

class EmbedHelpCommand(commands.HelpCommand):
    """This is an example of a HelpCommand that utilizes embeds.
    It's pretty basic but it lacks some nuances that people might expect.
    1. It breaks if you have more than 25 cogs or more than 25 subcommands. (Most people don't reach this)
    2. It doesn't DM users. To do this, you have to override `get_destination`. It's simple.
    Other than those two things this is a basic skeleton to get you started. It should
    be simple to modify if you desire some other behaviour.
    
    To use this, pass it to the bot constructor e.g.:
       
    bot = commands.Bot(help_command=EmbedHelpCommand())
    """
    # Set the embed colour here
    COLOUR = discord.Colour(0x9c9cff)

    def get_ending_note(self):
        return 'Use {0}{1} [command] for more info on a command.'.format(self.context.clean_prefix, self.invoked_with)

    def get_command_signature(self, command):
        return '{0.qualified_name} {0.signature}'.format(command)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Bot Commands', colour=self.COLOUR)
        description = self.context.bot.description
        if description:
            embed.description = description

        for cog, commands in mapping.items():
            name = 'Miscellaneous' if cog is None else cog.qualified_name
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                value = '`\n・`'.join(c.name for c in filtered)
                value = f"・`{value}`"
                if cog and cog.description:
                    value = '{0}\n{1}'.format(cog.description, value)
                    
                if name != "CustomEmbed":
                    embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(text=self.get_ending_note())
        view=HelpButtons(30)
        msg = await self.context.reply(view = view,embed=embed, mention_author = False)
        try:
            await asyncio.wait_for(view.wait(), timeout=30)
        except asyncio.TimeoutError:
            try:
                await msg.edit(view=None)
            except:
                pass

    async def send_cog_help(self, cog):
        embed = discord.Embed(title='{0.qualified_name} Commands'.format(cog), colour=self.COLOUR)
        if cog.description:
            embed.description = cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=self.get_command_signature(command), value= command.short_doc or 'No documentation provided', inline=False)

        embed.set_footer(text=self.get_ending_note())
        view=HelpButtons(30)
        msg = await self.context.reply(view = view,embed=embed, mention_author = False)
        try:
            await asyncio.wait_for(view.wait(), timeout=30)
        except asyncio.TimeoutError:
            try:
                await msg.edit(view=None)
            except:
                pass

    async def send_group_help(self, group):
        COLOUR = discord.Colour(0x9c9cff)
        embed = discord.Embed(title=group.qualified_name, colour=self.COLOUR)
        aliases = '`, `'.join(c for c in group.aliases)
        if group.help:
            embed.description = group.help
        if aliases != '':
            embed.add_field(name="**Aliases:**", value=f"`{aliases}`", inline=False)

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(name=self.get_command_signature(command), value=command.short_doc or 'No documentation provided', inline=False)

        embed.set_footer(text=self.get_ending_note())
        view=HelpButtons(30)
        msg = await self.context.reply(view = view,embed=embed, mention_author = False)
        try:
            await asyncio.wait_for(view.wait(), timeout=30)
        except asyncio.TimeoutError:
            try:
                await msg.edit(view=None)
            except:
                pass

    # This makes it so it uses the function above
    # Less work for us to do since they're both similar.
    # If you want to make regular command help look different then override it
    async def send_command_help(self, command):
        embed = discord.Embed(title=command.qualified_name, colour=self.COLOUR)
        aliases = '`, `'.join(c for c in command.aliases)
        if command.help:
            embed.description = command.help
        if aliases != '':
            embed.add_field(name="**Aliases:**", value=f"`{aliases}`", inline=False)

        if isinstance(command, commands.Group):
            filtered = await self.filter_commands(command, sort=True)
            for command in filtered:
                embed.add_field(name=self.get_command_signature(command), value=command.short_doc or 'No documentation provided', inline=False)

        embed.set_footer(text=self.get_ending_note())
        view=HelpButtons(30)
        msg = await self.context.reply(view = view,embed=embed, mention_author = False)
        try:
            await asyncio.wait_for(view.wait(), timeout=30)
        except asyncio.TimeoutError:
            try:
                await msg.edit(view=None)
            except:
                pass

class CustomEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        # Focus here
        # Setting the cog for the help
        help_command = EmbedHelpCommand()
        help_command.cog = self # Instance of YourCog class
        bot.help_command = help_command

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(CustomEmbed(bot))