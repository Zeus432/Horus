import discord
from discord.ext import commands

class ModeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        argument = argument.lower()
        if argument in ["easy", "hard", "medium"]:
            return argument
        raise commands.MissingRequiredArgument