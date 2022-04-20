import disnake
from disnake.ext import commands

class Hierarchy(commands.CheckFailure):
    pass

class CheckHierarchy1(commands.Converter):
    async def convert(self, ctx: commands.Context, user: disnake.Member) -> disnake.Member:
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
    async def convert(self, ctx: commands.Context, user: disnake.Member) -> disnake.Member:
        user = await commands.MemberConverter().convert(ctx, user)

        if user == ctx.guild.owner:
            raise Hierarchy('I cannot do that to the server owner.')

        elif ctx.me.top_role <= user.top_role:
            raise Hierarchy('I am not high enough in the role hierarchy to do that.')
        
        elif ctx.author.top_role <= user.top_role and ctx.guild.owner != ctx.author:
            raise Hierarchy('You are not high enough in the role hierarchy to do that.')

        return user

class RoleHierarchy(commands.Converter):
    async def convert(self, ctx: commands.Context, role: disnake.Role) -> disnake.Role:
        role = await commands.RoleConverter().convert(ctx, role)

        if ctx.me.top_role <= role:
            raise Hierarchy('I am not high enough in the role hierarchy to do that.')
        
        elif ctx.author.top_role <= role and ctx.guild.owner != ctx.author:
            raise Hierarchy('You are not high enough in the role hierarchy to do that.')
        
        elif not role.is_assignable():
            raise commands.CheckFailure('This role cannot be managed by me.')

        return role

def election_check():
    def predicate(ctx):
        if ctx.guild.id in [876697980449718272, 920553103147802644] or ctx.author.id == 807866303788220458:
            return True
        raise commands.NotOwner()
        # a function that takes ctx as it's only arg, that returns a truethy or falsey value, or raises an exception
    return commands.check(predicate)