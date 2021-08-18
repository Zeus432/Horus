from discord.ext import commands
import discord
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
    def nodms(self):
        if not self.context.guild:
            raise commands.NoPrivateMessage
        

    def get_ending_note(self):
        return 'Use {0}{1} [command] for more info on a command.'.format(self.context.clean_prefix, self.invoked_with)

    def get_command_signature(self, command):
        return '{0.qualified_name} {0.signature}'.format(command)

    async def send_bot_help(self, mapping):
        self.nodms()
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
        self.nodms()
        embed = discord.Embed(title='{0.qualified_name} Commands'.format(cog), colour=self.COLOUR)
        if cog.description:
            embed.description = cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=command.qualified_name, value= command.short_doc or 'No documentation provided', inline=False)

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
        self.nodms()
        embed = discord.Embed(colour=self.COLOUR, description=group.help or 'No documentation provided')
        embed.set_author(name="Horus Help Menu")
        aliases = '`, `'.join(c for c in group.aliases)
        if aliases != '':
            embed.add_field(name="**Aliases:**", value=f"`{aliases}`", inline=False)

        filtered = await self.filter_commands(group.commands, sort=True)
        for command in filtered:
            embed.add_field(name=self.get_command_signature(command), value=command.short_doc or 'No info', inline=False)

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

    async def send_command_help(self, command):
        embed = discord.Embed(colour=self.COLOUR, description=f"```yaml\nSyntax: {self.context.clean_prefix}{self.get_command_signature(command)}```\n")
        embed.add_field(name="Description:", value= command.help or 'No documentation provided')
        embed.set_author(name="Horus Help Menu")
        aliases = '`, `'.join(c for c in command.aliases)
        if aliases != '':
            embed.add_field(name="Aliases:", value=f"`{aliases}`", inline=False)

        if isinstance(command, commands.Group):
            filtered = await self.filter_commands(command, sort=True)
            embed.description=command.help or 'No documentation provided'
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