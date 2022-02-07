import disnake as discord
from bot import Horus
from disnake.ext import commands

from datetime import datetime
import json
from io import BytesIO

from Core.Utils.useful import TimeConverter, display_time
from .checks import CheckHierarchy1, CheckHierarchy2, RoleHierarchy, election_check
from .views import ConfirmElection

class Moderation(commands.Cog):
    """ Moderation Commands """ 
    def __init__(self, bot: Horus):
        self.bot = bot
        self.eview = None
    
    @commands.group(name = "role", invoke_without_command = True, brief = "Manage User roles")
    @commands.bot_has_guild_permissions(manage_roles = True)
    @commands.has_guild_permissions(manage_roles = True)
    async def role(self, ctx: commands.Context, user: discord.Member, role: RoleHierarchy):
        """ Add or Remove a role from a user """
        if role in user.roles:
            await user.remove_roles(role, reason = f"Requested by {ctx.author}")
            return await ctx.send(f'Removed {role} from {user.mention}', allowed_mentions = discord.AllowedMentions(users = False))
        
        await user.add_roles(role, reason = f"Requested by {ctx.author}")
        return await ctx.send(f'Added {role} to {user.mention}', allowed_mentions = discord.AllowedMentions(users = False))
    
    @role.command(name = "add", invoke_without_command = True, brief = "Add Roles to a User")
    @commands.bot_has_guild_permissions(manage_roles = True)
    @commands.has_guild_permissions(manage_roles = True)
    async def role_add(self, ctx: commands.Context, user: discord.Member, role: RoleHierarchy):
        """ Add a role to a user """
        if role in user.roles:
            await ctx.reply('This user already has this role!')
        
        await user.add_roles(role, reason = f"Requested by {ctx.author}")
        await ctx.send(f'Added {role} to {user.mention}', allowed_mentions = discord.AllowedMentions(users = False))
    
    @role.command(name = "remove", invoke_without_command = True, brief = "Remove Roles from a User")
    @commands.bot_has_guild_permissions(manage_roles = True)
    @commands.has_guild_permissions(manage_roles = True)
    async def role_add(self, ctx: commands.Context, user: discord.Member, role: RoleHierarchy):
        """ Remove a role from a user """
        if role not in user.roles:
            await ctx.reply('This user doesn\'t have this role!')
        
        await user.remove_roles(role, reason = f"Requested by {ctx.author}")
        await ctx.send(f'Removed {role} from {user.mention}', allowed_mentions = discord.AllowedMentions(users = False))

    
    @commands.group(name = "timeout", invoke_without_command = True, brief = "Timeout a user")
    @commands.bot_has_guild_permissions(moderate_members = True)
    @commands.has_guild_permissions(moderate_members = True)
    async def timeout(self, ctx: commands.Context, user: CheckHierarchy1, duration: TimeConverter):
        """ Time out a user """
        await user.edit(timeout = duration)
        await ctx.send(f'{user.mention} has been timed out until <t:{int(datetime.now().timestamp() + duration)}>!', allowed_mentions = discord.AllowedMentions(users = False))
    
    @timeout.command(name = "clear", brief = "Clear user's timeout")
    @commands.bot_has_guild_permissions(moderate_members = True)
    @commands.has_guild_permissions(moderate_members = True)
    async def timeout_clear(self, ctx: commands.Context, user: CheckHierarchy2):
        """ Clear a user's time out if they are timed out! """
        if not user.current_timeout:
            return await ctx.send(f'This is user is not timed out currently!')
        await user.edit(timeout = None)
        await ctx.send(f'{user.mention} is no longer timed out!', allowed_mentions = discord.AllowedMentions(users = False))
    
    @timeout.command(name = "view", brief = "View user's timeout")
    @commands.bot_has_guild_permissions(moderate_members = True)
    @commands.has_guild_permissions(moderate_members = True)
    async def timeout_view(self, ctx: commands.Context, user: discord.Member):
        """ View the time left for a user's time if they have any"""
        await ctx.send(f"{user.mention} is timed out until <t:{int(user.current_timeout.timestamp())}>!" if user.current_timeout else "This is user is not timed out currently!", allowed_mentions = discord.AllowedMentions(users = False))

    @commands.message_command(name = "Raw Embed Data", default_permission = True)
    @commands.has_permissions(manage_messages = True)
    async def embed_data(self, interaction: discord.MessageCommandInteraction, message: discord.Message):
        if not message.embeds:
            return await interaction.response.send_message(content = f"This message has no embeds to view!", ephemeral = True)

        embed_files = [discord.File(BytesIO(json.dumps(embed.to_dict(), indent = 2).encode('utf-8')), filename = f'embed-{index + 1}.json') for index, embed in enumerate(message.embeds)]

        await interaction.response.send_message(content = f"Here is the raw embed data in json", files = embed_files, ephemeral = True)
    
    @election_check()
    @commands.group(name = "election", brief = "View Election", invoke_without_command = True)
    async def election(self, ctx: commands.Context):
        if not self.eview:
            if ctx.author.guild_permissions.administrator:
                await ctx.send(content = f'No elections are ongoing currently. Run `{ctx.clean_prefix}election start` to start one')
            return

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, emoji = "\U0001f517", label = "Message Link", url = self.eview.message.jump_url))

        await ctx.reply(f"Election ends in {self.eview.endtime}\nClick the button below to go to the voting message", view = view)
    
    @election_check()
    @commands.has_guild_permissions(administrator = True)
    @election.command(name = "start", brief = "Start Election", invoke_without_command = True)
    async def election_start(self, ctx: commands.Context, duration: TimeConverter, candidates: commands.Greedy[discord.Member]):
        if self.eview:
            return await ctx.send(content = "There is already an election ongoing. Wait until it ends before starting one again!")

        clean_can = []
        [clean_can.append(i) for i in candidates if i not in clean_can]

        if len(clean_can) <= 1:
            return await ctx.send('You need to provide atleast 2 different candidates!')
        
        if duration > 604800:
            return await ctx.send('Duration of election can\'t be longer than one week!')
        
        embed = discord.Embed(color = self.bot.colour, description = "Check if the details for the election is correct!")
        embed.add_field(name = "Duration", value = f"Election will end in {display_time(seconds = duration)} (<t:{int(datetime.now().timestamp() + duration)}>)")
        embed.add_field(name = "Candidates", value = '\n'.join([user.mention for user in clean_can]), inline = False)

        view = ConfirmElection(user = ctx.author)
        view.message = await ctx.send(embed = embed, view = view)
        await view.wait()

        if not view.value:
            return
        
        await ctx.send("Election config done!")