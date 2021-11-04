import discord
from discord.ext import commands

from .useful import UserBadges

class Utility(commands.Cog):
    """ Utility Commands that contain general information """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.todo_cache = {}
    
    @commands.command(name = "userinfo", aliases = ['ui'], brief = "Get User Info", ignore_extra = True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def userinfo(self, ctx: commands.Context, user: discord.Member = None):
        """ Get information about a user """
        user = user or ctx.author
        embed = discord.Embed(title = f"{user.display_name}\U000030fb{user}", colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour)
        embed.timestamp = ctx.message.created_at
        embed.set_thumbnail(url = user.display_avatar)
        join_position = [m for m in sorted(ctx.guild.members, key = lambda u: u.joined_at)].index(ctx.author) + 1
        embed.set_footer(text = f"Member #{join_position}\U000030fbID: {user.id}", icon_url = user.avatar if user.display_avatar != user.avatar else discord.Embed.Empty)

        embed.add_field(name = "Joined Discord:", value = f"<t:{round(user.created_at.timestamp())}:D>\n(<t:{round(user.created_at.timestamp())}:R>)\n\u200b")
        embed.add_field(name = "Joined Server:", value = f"<t:{round(user.joined_at.timestamp())}:D>\n(<t:{round(user.joined_at.timestamp())}:R>)\n\u200b")

        roles, extra = "", 0

        for role in sorted(user.roles, reverse = True):
            if role.id != ctx.guild.id:
                if len(roles) < 900:
                    roles += f"{role.mention} "
                    continue
                extra += 1
        
        roles = f"{roles}{f' and {extra} other roles . . .' if extra != 0 else ''}" if roles else "This user has no roles"
        embed.add_field(name = "User's Roles:", value = f"{roles}", inline = False)

        # Badges here
        embed = UserBadges(ctx, self.bot, user, embed)

        embed.add_field(name = "Servers:", value = f"{len([guild.id for guild in self.bot.guilds if guild.get_member(user.id)])} shared")

        await ctx.send(embed = embed)

    @commands.command(name = "avatar", brief = "Get User Avatar", aliases = ['av'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        """ Get a user's avatar """
        user = user or ctx.author
        colour = user.colour if user.colour != discord.Colour(000000) else self.bot.colour
        embed = discord.Embed(title = f"Avatar for {user}", colour = colour, timestamp = ctx.message.created_at)
        embed.set_footer(text = f"{ctx.guild}", icon_url = ctx.guild.icon)

        avatar = user.display_avatar.with_static_format('png')
        jpgav = user.display_avatar.with_static_format('jpg')
        webpav = user.display_avatar.with_static_format('webp')

        embed.set_image(url = avatar)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{avatar}", label = ".png"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{jpgav}", label = ".jpg"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{webpav}", label = ".webp"))

        await ctx.send(embed = embed, view = view)