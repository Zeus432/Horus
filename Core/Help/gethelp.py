import discord
from discord.ext import commands

from .menus import HelpView

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
    
    def get_ending_note(self):
        return f'Use {self.context.clean_prefix}{self.invoked_with} [command] for more info on a command.'

    def get_command_signature(self, command):
        return f'{command.qualified_name} {command.signature}'
    
    # Get Help
    
    async def get_bot_help(self, mapping) -> discord.Embed:
        get_em = self.context.bot.get_em
        cog_emojis = {'Admin': get_em('owner'), 'BotStuff' : '\U0001f6e0', 'Fun': get_em('games'), 'Dev': get_em('dev'), 'Sniper' : get_em('lurk'), 'Utility': get_em('utils')}
        embed = discord.Embed(title = 'Horus Help Menu', colour = self.colour)
        embed.set_thumbnail(url = self.context.bot.user.avatar)

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort = True)
            if cog is not None and filtered:
                if cog.qualified_name != 'CustomHelp':
                    embed.add_field(name = f"{cog_emojis[cog.qualified_name]} {cog.qualified_name}", value = f"\n`{self.context.clean_prefix}{self.invoked_with} {cog.qualified_name}`\n" + (cog.description or "...") + "\n\u200b", inline = True)
        
        with open('Core/Help/botnews.txt') as fl:
            content = fl.read()
            if content:
                embed.add_field(name = f"{self.context.bot.get_em('news')} Horus Updates", value = f"{content}", inline = False)
        embed.set_footer(icon_url = self.context.bot.user.avatar, text = self.get_ending_note())
        return embed
    
    async def get_cog_help(self, cog: commands.Cog) -> discord.Embed:
        embed = discord.Embed(title = f'{cog.qualified_name} Help', colour = self.colour, description = f'{cog.description or "No Information"}')
        filtered = await self.filter_commands(cog.get_commands(), sort = True)

        for command in filtered:
            embed.add_field(name = command.qualified_name, value = command.short_doc or 'No documentation', inline = False)
        
        embed.set_footer(text = self.get_ending_note())
        return embed
    
    # Send Help to after getting it using a Select Menu
    
    async def send_bot_help(self, mapping):
        embed = await self.get_bot_help(mapping)
        embeds_list = {'Main Menu': embed}

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort = True)
            if cog is not None and filtered:
                if cog.qualified_name != 'CustomHelp':
                    embeds_list[cog.qualified_name] = await self.get_cog_help(cog)
        
        view = HelpView(user = self.context.author, embeds = embeds_list, original = 'Main Menu', get_em = self.context.bot.get_em, old_self = self, mapping = mapping)
        view.message = await self.context.reply(embed = embed, view = view)
    
    async def send_cog_help(self, cog: commands.Cog):
        if not ((filtered := await self.filter_commands(cog.get_commands(), sort = True)) and cog):
            return
        
        mapping = self.get_bot_mapping()
        embed = await self.get_cog_help(cog)
        embeds_list = {'Main Menu': await self.get_bot_help(mapping)}

        for another_cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort = True)
            if another_cog is not None and filtered:
                if another_cog.qualified_name != 'CustomHelp':
                    embeds_list[another_cog.qualified_name] = await self.get_cog_help(another_cog)
        
        view = HelpView(user = self.context.author, embeds = embeds_list, original = f'{cog.qualified_name}', get_em = self.context.bot.get_em, old_self = self, mapping = mapping)
        view.message = await self.context.reply(embed = embed, view = view)
    
    async def send_group_help(self, group: commands.Group):
        try: await group.can_run(self.context)
        except: return

        embed = discord.Embed(colour = self.colour, title = f"{group.cog_name} Help", description = f"```yaml\nSyntax: {self.context.clean_prefix}{self.get_command_signature(group)}```\n{group.help or 'No documentation'}\n\u200ba")
        embed.set_footer(text = self.get_ending_note(), icon_url = self.context.bot.user.avatar)

        if aliases := '`, `'.join(c for c in group.aliases):
            embed.add_field(name = "Aliases:", value = f"`{aliases}`", inline = False)
        
        filtered = await self.filter_commands(group.commands, sort = True)
        for command in filtered:
            embed.add_field(name = f"> {command.qualified_name}", value = f"> " + (command.short_doc or 'No documentation'), inline = False)

        await self.context.reply(embed = embed)
    
    async def send_command_help(self, command: commands.Command):
        try: await command.can_run(self.context)
        except: return
        embed = discord.Embed(colour = self.colour, title = f"{command.cog_name} Help", description = f"```yaml\nSyntax: {self.context.clean_prefix}{self.get_command_signature(command)}```\n{command.help or 'No documentation'}")
        embed.set_footer(text = self.get_ending_note(), icon_url = self.context.bot.user.avatar)

        if aliases := '`, `'.join(c for c in command.aliases):
            embed.add_field(name = "Aliases:", value = f"`{aliases}`", inline = False)

        await self.context.reply(embed = embed)
    
    async def send_error_message(self, error):
        return await super().send_error_message(error)