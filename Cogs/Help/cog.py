import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from typing import Mapping, Optional, List
from math import ceil

from .views import DeleteButton


class Help(commands.Cog):
    """ Custom Help Handling """
    def __init__(self, bot: Horus):
        self.bot = bot
        self._original_help_command = bot.help_command

        help_command = CustomHelp()
        help_command.cog = self
        bot.help_command = help_command

    def additional(self, ctx: HorusCtx) -> List[dict]:
        syntax_help = "**Important Things to Know**\n" \
        "```yaml\n" \
        "• <argument>         - Argument is required\n" \
        "• [argument]         - Argument is optional\n" \
        "• [argument=default] - Argument is optional and has a default value\n" \
        "• [argument...]      - Argument is optional and can take multiple entries.\n" \
        "• <argument...>      - Argument is required and can take multiple entries.\n" \
        "• [X|Y|Z]            - Argument can be either X, Y or Z```\n" \
        "__**Note:**__ Do not literally type out the `<>`, `[]`, `|`!\n" \
        f"Use `{ctx.clean_prefix}help <command | category>` to get help for any command"

        return [{"content": syntax_help}]

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


class CustomHelp(commands.HelpCommand):
    """ Custom Help Handling """
    def __init__(self):
        super().__init__(command_attrs = {
            "aliases": ['h'],
            "help": "Get help for a specific command or cog",
            "hidden": True
        })

        self.context: HorusCtx

        with open("Cogs/Help/botnews.md") as fl:
            self.bot_news = fl.read()

    def ending_note(self) -> str:
        """ Get ending note for embeds """
        return f"Use {self.context.clean_prefix}{self.invoked_with} [command] for more info on a command."

    def command_signature(self, command: commands.Command) -> str:
        """ Get proper command signature """
        return f"{command.qualified_name} {command.signature}"

    def icon(self, ctx: HorusCtx) -> str:
        """ returns the bot's avatar url """
        return ctx.bot.user.display_avatar.url

    # Seperately define functions to return embeds in a list

    async def get_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]) -> list[dict]:
        embed = discord.Embed(title = "Horus Help Menu", colour = self.context.bot.colour)
        embed.set_thumbnail(url = self.icon(self.context))

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort = True)

            if cog is not None and cog != self.cog and filtered:
                embed.add_field(name = f"{getattr(cog, 'emote', self.context.bot.memoji)} {cog.qualified_name}", value = f"\n`{self.context.clean_prefix}{self.invoked_with} {cog.qualified_name}`\n" + (cog.description or "...") + "\n\u200b", inline = True)

        if self.bot_news:
            embed.add_field(name = f"{self.context.bot.get_em('news')} {self.context.bot.user.name} Updates", value = self.bot_news.replace("[prefix]", f"{self.context.clean_prefix}"), inline = False)
        embed.set_footer(icon_url = self.icon(self.context), text = self.ending_note())

        syntax_help = "**Important Things to Know**\n" \
        "```yaml\n" \
        "• <argument>         - Argument is required\n" \
        "• [argument]         - Argument is optional\n" \
        "• [argument=default] - Argument is optional and has a default value\n" \
        "• [argument...]      - Argument is optional and can take multiple entries.\n" \
        "• <argument...>      - Argument is required and can take multiple entries.\n" \
        "• [X|Y|Z]            - Argument can be either X, Y or Z```\n" \
        "__**Note:**__ Do not literally type out the `<>`, `[]`, `|`!\n" \
        f"Use `{self.context.clean_prefix}help <command | category>` to get help for any command"

        return [{"embeds": [embed]}, {"content": syntax_help}]

    async def get_cog_help(self, cog: commands.Cog) -> List[dict]:
        filtered = await self.filter_commands(cog.get_commands(), sort = True)
        pages = ceil(len(filtered) / 8)
        coghelp = []

        for index, command in enumerate(filtered):
            if index % 8 == 0:
                embed = discord.Embed(title = f"{cog.qualified_name} Help", colour = self.context.bot.colour, description = cog.description or "Couldn't get any info about this cog")
                embed.set_footer(text = (f"Page {(index // 8) + 1} of {pages} - "  if pages > 1 else "") + self.ending_note())

            embed.add_field(name = command.qualified_name, value = command.short_doc or "Couldn't get any info about this command", inline = False)

            if index % 8 == 7 or index + 1 == len(filtered):
                coghelp.append({"embeds": [embed]})

        if additional := getattr(cog, "additional", None):
            coghelp.extend(additional(self.context))

        return coghelp

    # The actual send help functions

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]):
        bothelp = await self.get_bot_help(mapping)

        for msg in bothelp:
            await self.context.reply(**msg, mention_author = False)

    async def send_cog_help(self, cog: commands.Cog):
        coghelp = await self.get_cog_help(cog)

        for msg in coghelp:
            await self.context.reply(**msg, mention_author = False)

    async def send_group_help(self, group: commands.Group):
        try: await group.can_run(self.context)
        except: return # Return if user can't run this group commands

        embed = discord.Embed(colour = self.context.bot.colour, title = f"{group.cog_name or self.context.bot} Help", description = f"```yaml\nSyntax: {self.context.clean_prefix}{self.command_signature(group)}```\n>>> " + (group.help or "Couldn't get any info about this group"))
        embed.set_footer(text = self.ending_note(), icon_url = self.icon(self.context))

        if aliases := "`, `".join(alias for alias in group.aliases):
            embed.add_field(name = "Aliases:", value = f"`{aliases}`", inline = False)

        if cd := group._buckets._cooldown:
            cdtype = group._buckets._type
            embed.add_field(name = "Cooldown", value = f"Can be used {cd.rate} time" + "s" if cd.rate != 1 else "" + f" every {round(cd.per)} seconds " + "by" if cdtype.name == "user" else "in" + f" a {cdtype.name}", inline = False)

        if concur := group._max_concurrency:
            embed.add_field(name = "Concurrency", value = f"Can be used {concur.number} time" + "s" if concur.number != 1 else "" + " consecutively " + "by" if concur.per.name == "user" else "in" + f" a {concur.per.name}", inline = False)

        filtered = await self.filter_commands(group.commands, sort = True)
        pages = ceil(len(filtered) / 6)
        print(len(filtered), pages)
        grouphelp = []

        for index, command in enumerate(filtered):
            if index % 6 == 0:
                embed.set_footer(text = (f"Page {(index // 6) + 1} of {pages} - "  if pages > 1 else "") + self.ending_note(), icon_url = self.icon(self.context))

            embed.add_field(name = f"> {command.qualified_name}", value = f"> " + (command.short_doc or "Couldn't get any info about this command"), inline = False)

            if index % 6 == 5 or index + 1 == len(filtered):
                grouphelp.append({"embeds": [embed]})

                embed = discord.Embed(title = f"{group.cog_name or self.context.bot} Help", colour = self.context.bot.colour)

        for msg in grouphelp:
            await self.context.reply(**msg, view = DeleteButton(self.context), mention_author = False)

    async def send_command_help(self, command: commands.Command):
        try: await command.can_run(self.context)
        except: return # Return if user can't run this command

        embed = discord.Embed(colour = self.context.bot.colour, title = f"{command.cog_name} Help" if command.cog_name else f"{self.context.bot} Help", description = f"```yaml\nSyntax: {self.context.clean_prefix}{self.command_signature(command)}```\n>>> " + (command.help or "Couldn't get any info about this command"))
        embed.set_footer(text = self.ending_note(), icon_url = self.icon(self.context))

        if aliases := "`, `".join(alias for alias in command.aliases):
            embed.add_field(name = "Aliases:", value = f"`{aliases}`", inline = False)

        if cd := command._buckets._cooldown:
            cdtype = command._buckets._type
            embed.add_field(name = "Cooldown", value = f"Can be used {cd.rate} time" + "s" if cd.rate != 1 else "" + f" every {round(cd.per)} seconds " + "by" if cdtype.name == "user" else "in" + f" a {cdtype.name}", inline = False)

        if concur := command._max_concurrency:
            embed.add_field(name = "Concurrency", value = f"Can be used {concur.number} time" + "s" if concur.number != 1 else "" + " consecutively " + "by" if concur.per.name == "user" else "in" + f" a {concur.per.name}", inline = False)

        await self.context.reply(embed = embed, view = DeleteButton(self.context), mention_author = False)