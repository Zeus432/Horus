from discord.ext import commands
import discord
from Utils.Useful import HelpButtons
import asyncio

class HelpMenu(discord.ui.Select):
    def __init__(self, bot, getself, user,options=None):
        self.bot = bot
        self.getself = getself
        self.user = user

        super().__init__(placeholder="Help Menu Dropdown",min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        try:
            cog = self.bot.get_cog(self.values[0])
            embed = await self.getself.send_cog_help(cog, ifreturn = True)
        except:
            embed = await self.getself.send_bot_help(mapping = self.getself.get_bot_mapping(), ifreturn = True)
            embed = embed[0]
        if interaction.user.id == self.user.id:
            await interaction.response.edit_message(embed=embed)
            return

        #ephermal help for new user
        newview = discord.ui.View()
        newself = self.getself
        newself.context.author = self.bot.get_user(interaction.user.id)
        val = await newself.send_bot_help(mapping = newself.get_bot_mapping(), ifreturn = True, changeuser = interaction.user.id)
        embed,newview = val[0],val[1]
        await interaction.response.send_message(embed=embed,view=newview, ephemeral=True)
        

class NewHelp(commands.HelpCommand):
    colour = discord.Colour(0x9c9cff)

    def em(self, emoji):
        lst = {"Admin": "mod","Fun": "games","Utility": "staff","Owner": "dev","ErrorHandler":"error"}
        try:
            emoji = lst[emoji]
        except: pass
        return self.context.bot.emojislist(emoji)


    def get_ending_note(self):
        return f'Use {self.context.clean_prefix}{self.invoked_with} [command] for more info on a command.'

    def get_command_signature(self, command):
        return f'{command.qualified_name} {command.signature}'

    async def send_bot_help(self, mapping, ifreturn = False, changeuser = None):
        embed = discord.Embed(title='Horus Help Menu', colour=self.colour)
        embed.set_thumbnail(url=self.context.bot.get_user(858335663571992618).avatar)
        if changeuser:
            self.context.author = self.context.guild.get_member(changeuser)
        description = "Whorus is a private bot made for fun, has simple moderation, fun commands. If the commands break a lot while using it's probably just me testing new commands, fixing stuff or just breaking shit\n\u200b"
        if description:
            embed.description = description

        options = [discord.SelectOption(label=f'Bot Help',description=f"View the main help page", emoji=self.em('core'))]
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                if cog is None:
                    continue
                if cog.qualified_name == 'CustomHelp':
                    continue
                name,desc = cog.qualified_name, f"{cog.description}" if cog.description else ""
                options.append(discord.SelectOption(label=f'{name}',description=f"{desc}", emoji=self.em(name)))
                name = f"{self.em(f'{name}')} {name}"
                value = f'{cog.description}' if cog and cog.description else "..."
                value += "\n\u200b"
                 
                embed.add_field(name=name, value=value, inline=True)
            
        embed.set_footer(text=self.get_ending_note())
        view=discord.ui.View(timeout=None)
        view.add_item(HelpMenu(bot=self.context.bot, options=options, getself = self, user = self.context.author))
        if not ifreturn:
            await self.context.reply(view = view, embed = embed, mention_author = False)
        else:
            return [embed,view]

    async def send_cog_help(self, cog, ifreturn = False):
        mapping = self.get_bot_mapping()
        embed = discord.Embed(title=f'{cog.qualified_name} Commands', colour=self.colour)
        if cog.description:
            embed.description = cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=command.qualified_name, value= command.short_doc or 'No documentation provided', inline=False)
        
        options = [discord.SelectOption(label=f'Bot Help',description=f"View the main help page",emoji=self.em('core'))]
        for cogs, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                if cogs is None:
                    continue
                if cogs.qualified_name == 'CustomHelp':
                    continue
                name,desc = cogs.qualified_name, f"{cogs.description}" if cogs.description else ""
                options.append(discord.SelectOption(label=f'{name}',description=f"{desc}", emoji=self.em(name)))
        
        embed.set_footer(text=self.get_ending_note())
        view=discord.ui.View(timeout=None)
        view.add_item(HelpMenu(bot=self.context.bot, options=options, getself = self, user = self.context.author))
        if not ifreturn:
            await self.context.reply(view = view, embed = embed, mention_author = False)
        else:
            return embed

    async def send_group_help(self, group):
        #self.nodms()
        embed = discord.Embed(colour=self.colour, description=group.help or 'No documentation provided')
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
        embed = discord.Embed(colour=self.colour, description=f"```yaml\nSyntax: {self.context.clean_prefix}{self.get_command_signature(command)}```\n")
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

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        help_command = NewHelp()
        help_command.cog = self
        bot.help_command = help_command

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

def setup(bot):
    bot.add_cog(CustomHelp(bot))