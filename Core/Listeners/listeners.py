import discord
from discord.ext import commands

from Core.settings import BOTMODS

class Listeners(commands.Cog):
    """ Listeners for bot commands, guild joins and stuff """
    def __init__(self, bot: commands.Bot):
        self.bot = bot