import disnake
from bot import Horus
from disnake.ext import commands

from datetime import datetime
import datetime as dt
import json
from io import BytesIO

from Core.Utils.useful import TimeConverter, display_time
from .checks import CheckHierarchy1, CheckHierarchy2, RoleHierarchy, election_check
from .views import ConfirmElection, ElectionVote

class Moderation(commands.Cog):
    """ Moderation Commands """ 
    def __init__(self, bot: Horus):
        self.bot = bot
        self.eview = None
        self.bot.loop.create_task(self.initialize())
    
    async def initialize(self):
        await self.bot.wait_until_ready()

        if self.bot._added_election is True:
            return

        query = "SELECT * FROM election WHERE disabled = $1"
        item = await self.bot.db.fetchrow(query, False)

        if not item:
            return

        channel = await self.bot.fetch_channel(item["channelid"])
        message = await channel.fetch_message(item["messageid"])
        view = ElectionVote(bot = self.bot, user = item["authorid"], candidates = item["candidates"], voters = item["voters"], endtime = item["endtime"])
        view.message = message

        view.original_content = message.content.split('-')[0]

        self.bot.add_view(view, message_id = item["messageid"])

        self.eview = view
        self.bot._added_election = True

        await disnake.utils.sleep_until(when = datetime.fromtimestamp(item["endtime"]))
        await view.end_election()


    @commands.group(name = "role", invoke_without_command = True, brief = "Manage User roles")
    @commands.bot_has_guild_permissions(manage_roles = True)
    @commands.has_guild_permissions(manage_roles = True)
    async def role(self, ctx: commands.Context, user: disnake.Member, role: RoleHierarchy):
        """ Add or Remove a role from a user """
        if role in user.roles:
            await user.remove_roles(role, reason = f"Requested by {ctx.author}")
            return await ctx.send(f'Removed {role} from {user.mention}', allowed_mentions = disnake.AllowedMentions(users = False))
        
        await user.add_roles(role, reason = f"Requested by {ctx.author}")
        return await ctx.send(f'Added {role} to {user.mention}', allowed_mentions = disnake.AllowedMentions(users = False))
    
    @role.command(name = "add", invoke_without_command = True, brief = "Add Roles to a User")
    @commands.bot_has_guild_permissions(manage_roles = True)
    @commands.has_guild_permissions(manage_roles = True)
    async def role_add(self, ctx: commands.Context, user: disnake.Member, role: RoleHierarchy):
        """ Add a role to a user """
        if role in user.roles:
            await ctx.reply('This user already has this role!')
        
        await user.add_roles(role, reason = f"Requested by {ctx.author}")
        await ctx.send(f'Added {role} to {user.mention}', allowed_mentions = disnake.AllowedMentions(users = False))
    
    @role.command(name = "remove", invoke_without_command = True, brief = "Remove Roles from a User")
    @commands.bot_has_guild_permissions(manage_roles = True)
    @commands.has_guild_permissions(manage_roles = True)
    async def role_add(self, ctx: commands.Context, user: disnake.Member, role: RoleHierarchy):
        """ Remove a role from a user """
        if role not in user.roles:
            await ctx.reply('This user doesn\'t have this role!')
        
        await user.remove_roles(role, reason = f"Requested by {ctx.author}")
        await ctx.send(f'Removed {role} from {user.mention}', allowed_mentions = disnake.AllowedMentions(users = False))

    
    @commands.group(name = "timeout", invoke_without_command = True, brief = "Timeout a user")
    @commands.bot_has_guild_permissions(moderate_members = True)
    @commands.has_guild_permissions(moderate_members = True)
    async def timeout(self, ctx: commands.Context, user: CheckHierarchy1, duration: TimeConverter):
        """ Time out a user """
        await user.edit(timeout = duration)
        await ctx.send(f'{user.mention} has been timed out until <t:{int(datetime.now().timestamp() + duration)}>!', allowed_mentions = disnake.AllowedMentions(users = False))
    
    @timeout.command(name = "clear", brief = "Clear user's timeout")
    @commands.bot_has_guild_permissions(moderate_members = True)
    @commands.has_guild_permissions(moderate_members = True)
    async def timeout_clear(self, ctx: commands.Context, user: CheckHierarchy2):
        """ Clear a user's time out if they are timed out! """
        if not user.current_timeout:
            return await ctx.send(f'This is user is not timed out currently!')
        await user.edit(timeout = None)
        await ctx.send(f'{user.mention} is no longer timed out!', allowed_mentions = disnake.AllowedMentions(users = False))
    
    @timeout.command(name = "view", brief = "View user's timeout")
    @commands.bot_has_guild_permissions(moderate_members = True)
    @commands.has_guild_permissions(moderate_members = True)
    async def timeout_view(self, ctx: commands.Context, user: disnake.Member):
        """ View the time left for a user's time if they have any"""
        await ctx.send(f"{user.mention} is timed out until <t:{int(user.current_timeout.timestamp())}>!" if user.current_timeout else "This is user is not timed out currently!", allowed_mentions = disnake.AllowedMentions(users = False))

    @commands.message_command(name = "Raw Embed Data", default_permission = True)
    @commands.has_permissions(manage_messages = True)
    async def embed_data(self, interaction: disnake.MessageCommandInteraction, message: disnake.Message):
        if not message.embeds:
            return await interaction.response.send_message(content = f"This message has no embeds to view!", ephemeral = True)

        embed_files = [disnake.File(BytesIO(json.dumps(embed.to_dict(), indent = 2).encode('utf-8')), filename = f'embed-{index + 1}.json') for index, embed in enumerate(message.embeds)]

        await interaction.response.send_message(content = f"Here is the raw embed data in json", files = embed_files, ephemeral = True)
    
    @election_check()
    @commands.group(name = "election", brief = "View Election", invoke_without_command = True)
    async def election(self, ctx: commands.Context):
        if not self.eview:
            if ctx.author.guild_permissions.administrator:
                await ctx.send(content = f'No elections are ongoing currently. Run `{ctx.clean_prefix}election start` to start one')
            return

        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(style = disnake.ButtonStyle.link, emoji = "\U0001f517", label = "Message Link", url = self.eview.message.jump_url))

        await ctx.reply(f"Election ends in {display_time(int(self.eview.endtime - datetime.now().timestamp()))}\nClick the button below to go to the voting message", view = view)
    
    @election_check()
    @commands.has_guild_permissions(administrator = True)
    @election.command(name = "start", brief = "Start Election", invoke_without_command = True)
    async def election_start(self, ctx: commands.Context, duration: TimeConverter, candidates: commands.Greedy[disnake.Member]):
        if self.eview:
            return await ctx.send(content = "There is an election ongoing currently. Wait until it ends before starting one again!")

        clean_can = []
        [clean_can.append(i) for i in candidates if i not in clean_can]

        if len(clean_can) <= 1:
            return await ctx.send('Atleast 2 different candidates venum da gopal')
        
        if len(clean_can) > 10:
            return await ctx.send('Adei maximum 10 candidates dhan')
        
        if duration > 604800:
            return await ctx.send('Duration of election can\'t be longer than one week!')
        
        embed = disnake.Embed(color = self.bot.colour, description = "Check if the details for the election is correct!")
        embed.add_field(name = "Duration", value = f"Election will end in {display_time(seconds = duration)} (<t:{int(datetime.now().timestamp() + duration)}>)")
        embed.add_field(name = "Candidates", value = '\n'.join([user.mention for user in clean_can]), inline = False)

        view = ConfirmElection(user = ctx.author)
        view.message = await ctx.send(embed = embed, view = view)
        await view.wait()

        if not view.value:
            return

        candidates = [user.id for user in clean_can]
        voters = {f"{user.id}": [] for user in clean_can}
        endtime = int(datetime.now().timestamp() + duration)

        view = ElectionVote(bot = self.bot, user = ctx.author.id, candidates = candidates, voters = voters, endtime = endtime)
        view.message = await ctx.send(content = "Yaaru nambu server oda adutha owner\n\n" + "\n\n".join([f'{self.bot.get_em(index + 1)} {user.mention}' for index, user in enumerate(clean_can)]) + f"\n\nEnd on <t:{int(datetime.now().timestamp() + duration)}>", view = view, allowed_mentions = disnake.AllowedMentions.none())
        view.original_content = view.message.content

        self.eview = view

        query = "INSERT INTO election(messageid, channelid, authorid, candidates, voters, endtime) VALUES($1, $2, $3, $4, $5, $6) ON CONFLICT (messageid) DO  NOTHING"
        await self.bot.db.execute(query, view.message.id, ctx.channel.id, ctx.author.id, candidates, voters, endtime)

        await disnake.utils.sleep_until(when = datetime.fromtimestamp(endtime))
        await view.end_election()