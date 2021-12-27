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
        
        elif ctx.author.top_role <= user.top_role:
            raise Hierarchy('You are not high enough in the role hierarchy to do that.')

        return user

class CheckHierarchy2(commands.Converter):
    async def convert(self, ctx: commands.Context, user: disnake.Member) -> disnake.Member:
        user = await commands.MemberConverter().convert(ctx, user)

        if ctx.author == user:
            raise Hierarchy(f'You cannot use this command on yourself!')

        elif user == ctx.guild.owner:
            raise Hierarchy('I cannot do that to the server owner.')

        elif ctx.me.top_role <= user.top_role:
            raise Hierarchy('I am not high enough in the role hierarchy to do that.')
        
        elif ctx.author.top_role <= user.top_role:
            raise Hierarchy('You are not high enough in the role hierarchy to do that.')

        return user