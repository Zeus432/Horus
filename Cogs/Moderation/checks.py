import disnake as discord
from discord.ext import commands

class Hierarchy(commands.CheckFailure):
    pass

class CheckHierarchy1(commands.Converter):
    async def convert(self, ctx: commands.Context, user: discord.Member) -> discord.Member:
        user = await commands.MemberConverter().convert(ctx, user)

        if ctx.author == user:
            raise Hierarchy(f'Nope can\'t let you do that. Self Harm is bad {ctx.bot.get_em("pensive")}')

        elif user == ctx.guild.owner:
            raise Hierarchy('I cannot do that to the server owner.')

        elif ctx.me.top_role <= user.top_role:
            raise Hierarchy('I am not high enough in the role hierarchy to do that.')
        
        elif ctx.author.top_role <= user.top_role and ctx.guild.owner != ctx.author:
            raise Hierarchy('You are not high enough in the role hierarchy to do that.')

        return user

class CheckHierarchy2(commands.Converter):
    async def convert(self, ctx: commands.Context, user: discord.Member) -> discord.Member:
        user = await commands.MemberConverter().convert(ctx, user)

        if user == ctx.guild.owner:
            raise Hierarchy('I cannot do that to the server owner.')

        elif ctx.me.top_role <= user.top_role:
            raise Hierarchy('I am not high enough in the role hierarchy to do that.')
        
        elif ctx.author.top_role <= user.top_role and ctx.guild.owner != ctx.author:
            raise Hierarchy('You are not high enough in the role hierarchy to do that.')

        return user

class RoleHierarchy(commands.Converter):
    async def convert(self, ctx: commands.Context, role: discord.Role) -> discord.Role:
        role = await commands.RoleConverter().convert(ctx, role)

        if ctx.me.top_role <= role:
            raise Hierarchy('I am not high enough in the role hierarchy to do that.')
        
        elif ctx.author.top_role <= role and ctx.guild.owner != ctx.author:
            raise Hierarchy('You are not high enough in the role hierarchy to do that.')
        
        elif not role.is_assignable():
            raise commands.CheckFailure('This role cannot be managed by me.')

        return role