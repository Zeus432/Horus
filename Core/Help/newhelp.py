import discord
from discord.ext import commands

class NewHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs = {
                'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member),
                'help': 'Shows help about the bot, a command, or a category'
            }
        )
        self.colour = discord.Colour(0x9c9cff)
    
    async def send_bot_help(self, mapping):
        return await super().send_bot_help(mapping)
    
    async def send_cog_help(self, cog):
        return await super().send_cog_help(cog)
    
    async def send_group_help(self, group):
        return await super().send_group_help(group)
    
    async def send_command_help(self, command):
        return await super().send_command_help(command)
    
    async def send_error_message(self, error):
        return await super().send_error_message(error)