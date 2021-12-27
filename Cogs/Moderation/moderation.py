import disnake
from bot import Horus
from disnake.ext import commands

from datetime import datetime

from .checks import CheckHierarchy1, CheckHierarchy2
from Core.Utils.useful import TimeConverter, display_time

class Moderation(commands.Cog):
    """ Moderation Commands """ 
    def __init__(self, bot: Horus):
        self.bot = bot
    
    @commands.group(name = "timeout", invoke_without_command = True, brief = "Timeout a user")
    @commands.has_guild_permissions(moderate_members = True)
    async def timeout(self, ctx: commands.Context, user: CheckHierarchy1, duration: TimeConverter):
        """ Time out a user """
        await user.edit(timeout = duration)
        await ctx.send(f'{user.mention} has been timed out until <t:{int(datetime.now().timestamp() + duration)}>!', allowed_mentions = disnake.AllowedMentions(users = False))
    
    @timeout.command(name = "clear", brief = "Clear user's timeout")
    async def timeout_clear(self, ctx: commands.Context, user: CheckHierarchy2):
        """ Clear a user's time out if they are timed out! """
        if not user.current_timeout:
            return await ctx.send(f'This is user is not timed out currently!')
        await user.edit(timeout = None)
        await ctx.send(f'{user.mention} is no longer timed out!', allowed_mentions = disnake.AllowedMentions(users = False))
    
    @timeout.command(name = "view", brief = "View user's timeout")
    async def timeout_view(self, ctx: commands.Context, user: disnake.Member):
        """ View the time left for a user's time if they have any"""
        await ctx.send(f"{user.mention} is timed out until <t:{int(user.current_timeout.timestamp())}>!" if user.current_timeout else "This is user is not timed out currently!", allowed_mentions = disnake.AllowedMentions(users = False))