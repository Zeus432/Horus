from bot import Horus
import disnake as discord
from disnake.ext import commands

class ButtonRoles(commands.Cog):
    """ Button Roles """

    def __init__(self, bot: Horus):
        self.bot = bot
    
    async def cog_check(self, ctx: commands.Context):
        result = await self.bot.is_owner(ctx.author)
        if result:
            return True
        raise commands.NotOwner()