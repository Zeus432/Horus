import disnake as discord
from bot import Horus
from disnake.ext import commands

from .pagination import HelpView, DeleteButton

class NewHelp(commands.HelpCommand):
    """ Custom Help Handling """
    def __init__(self):
        super().__init__(
            command_attrs = {
                'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member),
                'help': 'Shows help about the bot, a command, or a category'
            }
        )
        self.colour = discord.Colour(0x9c9cff)
        self.footer = "https://cdn.discordapp.com/avatars/858335663571992618/358132def732d61ce9ed7dbfb8f9a6c1.png?size=1024"

        def cog_emojis(bot, cog):
            get_em = bot.get_em
            dct = {'Admin': get_em('owner'), 'BotStuff' : '\U0001f6e0', 'Fun': get_em('games'), 'Dev': get_em('dev'), 'Image Api': '\U0001f5bc\U0000fe0f', 'Moderation' : get_em('mod'), 'Sniper' : get_em('lurk'), 'Utility': get_em('utils'), 'Blacklists': '\U00002692', 'Main Menu': get_em('core')}
            try:
                return dct[cog]
            except:
                return get_em('error')

        self.cog_emojis = cog_emojis
        self.syntax_help = f"""**Important Things to Know**
```yaml
• <argument>         - Argument is required
• [argument]         - Argument is optional
• [argument=default] - Argument is optional and has a default value
• [argument...]      - Argument is optional and can take multiple entries.
• <argument...>      - Argument is required and can take multiple entries.
• [X|Y|Z]            - Argument can be either X, Y or Z```
__**Note:**__ Do not literally type out the `<>`, `[]`, `|`!

Use `[$prefix$]help <command | category>` to get help for any command"""

        with open('Core/Help/botnews.md') as fl:
            self.bot_news = fl.read()

    
    def get_ending_note(self):
        return f'Use {self.context.clean_prefix}{self.invoked_with} [command] for more info on a command.'

    def get_command_signature(self, command):
        return f'{command.qualified_name} {command.signature}'
    
    # Get Help
    
    async def get_bot_help(self, mapping) -> list[dict]:
        embed = discord.Embed(title = 'Horus Help Menu', colour = self.colour)
        embed.set_thumbnail(url = self.footer)

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort = True)
            if cog is not None and filtered:
                if cog.qualified_name != 'CustomHelp':
                    embed.add_field(name = f"{self.cog_emojis(self.context.bot, cog.qualified_name)} {cog.qualified_name}", value = f"\n`{self.context.clean_prefix}{self.invoked_with} {cog.qualified_name}`\n" + (cog.description or "...") + "\n\u200b", inline = True)
        
        if self.bot_news:
            embed.add_field(name = f"{self.context.bot.get_em('news')} Horus Updates", value = f"{self.bot_news.replace('[prefix]', f'{self.context.clean_prefix}')}", inline = False)
        embed.set_footer(icon_url = self.footer, text = self.get_ending_note())

        return [{'embeds': [embed]}, {'content': self.syntax_help.replace('[$prefix$]', f"{self.context.clean_prefix}")}]
    
    async def get_cog_help(self, cog: commands.Cog) -> list[dict]:
        filtered = await self.filter_commands(cog.get_commands(), sort = True)
        embeds = []
        pages = (len(filtered) // 8) + 1
        current_page = 1

        while filtered:
            embed = discord.Embed(title = f'{cog.qualified_name} Help', colour = self.colour, description = f'{cog.description or "No Information"}')
            embed.set_footer(text = (f"Page {current_page} of {pages} - "  if pages > 1 else "") + self.get_ending_note())
    
            for index, command in enumerate(filtered[:8]):
                embed.add_field(name = command.qualified_name, value = command.short_doc or 'No documentation', inline = False)

            embeds.append({'embeds': [embed]})
            filtered = filtered[8:]
            current_page += 1

        return embeds
    
    # Send Help to after getting it using a Select Menu
    
    async def send_bot_help(self, mapping):
        stuff_list = await self.get_bot_help(mapping)
        embeds_list = {'Main Menu': stuff_list}

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort = True)
            if cog is not None and filtered:
                if cog.qualified_name != 'CustomHelp':
                    embeds_list[cog.qualified_name] = await self.get_cog_help(cog)

        view = HelpView(stuff_dict = embeds_list, user = self.context.author, old_self = self, mapping = mapping, bot = self.context.bot, original = 'Main Menu', cog_emojis = self.cog_emojis)
        view.message = await self.context.reply(view = view, mention_author = False, **stuff_list[0])
    
    async def send_cog_help(self, cog: commands.Cog):
        if not ((filtered := await self.filter_commands(cog.get_commands(), sort = True)) and cog):
            return
        
        mapping = self.get_bot_mapping()
        embeds_list = {'Main Menu': await self.get_bot_help(mapping)}

        for another_cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort = True)
            if another_cog is not None and filtered:
                if another_cog.qualified_name != 'CustomHelp':
                    embeds_list[another_cog.qualified_name] = await self.get_cog_help(another_cog)
        
        view = HelpView(stuff_dict = embeds_list, user = self.context.author, old_self = self, mapping = mapping, bot = self.context.bot, original = f'{cog.qualified_name}', cog_emojis = self.cog_emojis)
        view.message = await self.context.reply(view = view, mention_author = False, **embeds_list[f'{cog.qualified_name}'][0])
    
    async def send_group_help(self, group: commands.Group):
        try: await group.can_run(self.context)
        except: return # Return if user can't run this group commands

        embed = discord.Embed(colour = self.colour, title = f"{group.cog_name} Help" if group.cog_name else "Horus Help", description = f"```yaml\nSyntax: {self.context.clean_prefix}{self.get_command_signature(group)}```\n{group.help or 'No documentation'}\n\u200b")
        embed.set_footer(text = self.get_ending_note(), icon_url = self.footer)

        if aliases := '`, `'.join(c for c in group.aliases):
            embed.add_field(name = "Aliases:", value = f"`{aliases}`", inline = False)
        
        filtered = await self.filter_commands(group.commands, sort = True)
        for command in filtered:
            embed.add_field(name = f"> {command.qualified_name}", value = f"> " + (command.short_doc or 'No documentation'), inline = False)

        view = DeleteButton(user = self.context.author)
        await self.context.reply(embed = embed, view = view, mention_author = False)
    
    async def send_command_help(self, command: commands.Command):
        try: await command.can_run(self.context)
        except: return # Return if user can't run this command
        embed = discord.Embed(colour = self.colour, title = f"{command.cog_name} Help" if command.cog_name else "Horus Help", description = f"```yaml\nSyntax: {self.context.clean_prefix}{self.get_command_signature(command)}```\n{command.help or 'No documentation'}")
        embed.set_footer(text = self.get_ending_note(), icon_url = self.footer)

        if aliases := '`, `'.join(c for c in command.aliases):
            embed.add_field(name = "Aliases:", value = f"`{aliases}`", inline = False)
        
        view = DeleteButton(user = self.context.author)
        await self.context.reply(embed = embed, view = view, mention_author = False)
    
    async def send_error_message(self, error):
        return await super().send_error_message(error)