import discord
from discord.ext import commands

from typing import List

from Core.Utils.useful import TimeConverter

def UserBadges(ctx: commands.Context, bot: commands.Bot, user: discord.Member, embed: discord.Embed) -> discord.Embed:
    """ Adds member badges to the userinfo embed, if user has any """
    badges = []

    if user.id in bot.owner_ids:
        badges.append(f"{bot.get_em('dev')} **[Bot Owner]({user.display_avatar})**")
    if user == ctx.guild.owner:
        badges.append(f"{bot.get_em('owner')} **[Server Owner]({user.display_avatar})**")
    if ctx.guild.premium_tier:
        if [role.id for role in user.roles if role.id == ctx.guild.premium_subscriber_role.id]:
            badges.append(f"{bot.get_em('boost')} **[Server Booster](https://cdn.discordapp.com/emojis/782210035329138698.gif?v=1)**")
    if user.bot:
        badges = [f"{bot.get_em('cogs')} **[Bots Supreme]({user.avatar})**"]
    if user.id == bot.user.id:
        badges = [f"{bot.get_em('horus')} **[Oh Look It's a Me]({user.avatar})**"]
    
    if badges:
        embed.add_field(name = "Badges:", value = "\n".join(badges))

    return embed

class PollFlags(commands.FlagConverter, prefix = '--', delimiter = ' ', case_insensitive = True):
    question: str = commands.flag(name = 'question', aliases = ["q","ques"])
    time: TimeConverter = 600.0
    yesno: bool = False
    opt: List[str]  = commands.flag(name = 'option', aliases = ["opt"], default = [])
    webhook: bool = False