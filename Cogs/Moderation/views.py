import disnake
from disnake.ext import commands

from datetime import datetime
import datetime as dt

from Core.Utils.useful import display_time

class ConfirmElection(disnake.ui.View):
    def __init__(self, user: int, timeout: float = 30):
        super().__init__(timeout = timeout)
        self.user = user
        self.value = None
    
    async def disableall(self, style: disnake.ButtonStyle):
        for item in self.children:
            item.style = disnake.ButtonStyle.gray if item.style != style else style
            item.disabled = True
        await self.message.edit(view = self)
        self.stop()
    
    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        if interaction.user.id == self.user.id or self.value is None:
            await interaction.response.defer()
            return True
        return await interaction.response.defer()
    
    @disnake.ui.button(label = "Start Election", style = disnake.ButtonStyle.blurple)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.value = True
        await self.message.delete()
        self.stop()

    @disnake.ui.button(label = "Cancel", style = disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        self.value = False
        await self.disableall(button.style)
    
    async def on_timeout(self):
        await self.disableall(disnake.ButtonStyle.red)

class ConfirmEnd(disnake.ui.View):
    def __init__(self, election_view: disnake.ui.View):
        super().__init__(timeout = 30)
        self.election_view = election_view
    
    @disnake.ui.button(label = "Confirm", style = disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.disable(button.style, interaction)
        await self.election_view.end_election()
    
    @disnake.ui.button(label = "Cancel", style = disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.disable(button.style, interaction)
    
    async def disable(self, style: disnake.ButtonStyle, interaction: disnake.Interaction):
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.gray if item.style != style else style
        await interaction.response.edit_message(view = self)

class ElectionVote(disnake.ui.View):
    def __init__(self, bot: commands.Bot, user: int, candidates: list, voters: dict, endtime: int):
        super().__init__(timeout = None)
        self.endtime = endtime
        self.bot = bot
        self.user = user
        self.candidates = candidates
        self.voters = voters
        self.guild = bot.get_guild(876697980449718272)
        self.message: disnake.Message
        self.original_content: str

        def key(interaction: disnake.Interaction):
            return interaction.user

        self._cd = commands.CooldownMapping.from_cooldown(2, 10.0, key)

        for index, can in enumerate(candidates):
            self.add_item(self.ElectionButton(bot = bot, num = index + 1))
        
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        retry_after = self._cd.update_rate_limit(interaction)
        if retry_after:
            return await interaction.response.send_message(content = f"You're clicking too fast! Try again in `{round(retry_after, 1)}s`", ephemeral = True)
        
        return True
    
    class ElectionButton(disnake.ui.Button["ElectionVote"]):
        def __init__(self, bot: commands.Bot, num: int):
            super().__init__(style = disnake.ButtonStyle.gray, emoji = bot.get_em(num), custom_id = f"button:{num}")
            self.num = num
        
        async def callback(self, interaction: disnake.Interaction):
            await interaction.response.defer()
            who = self.view.candidates[self.num - 1]
            found = False

            for name, values in self.view.voters.items():
                if interaction.author.id in values:
                    self.view.voters[f"{name}"].remove(interaction.author.id)
                    found = True
        
                    if f"{name}" == f"{who}":
                        await interaction.followup.send(f"You have removed your vote from <@!{who}>", allowed_mentions = disnake.AllowedMentions.none(), ephemeral = True)
                        break
                    
                    else:
                        self.view.voters[f"{who}"].append(interaction.author.id)
                        await interaction.followup.send(f"You have changed your vote from <@!{name}> to <@!{who}>", allowed_mentions = disnake.AllowedMentions.none(), ephemeral = True)
                        break

            if found is False:
                self.view.voters[f"{who}"].append(interaction.author.id)
                await interaction.followup.send(f"You've succesfully voted for <@!{who}>", allowed_mentions = disnake.AllowedMentions.none(), ephemeral = True)
            
            query = "UPDATE election SET voters = $2 WHERE messageid = $1"
            await self.view.bot.db.execute(query, self.view.message.id, self.view.voters)

            count = f"`{sum([len(item) for item in self.view.voters.values()])}/{len([member for member in self.view.guild.members if not member.bot])}` users have voted"
            await self.view.message.edit(content = f"{self.view.original_content} - {count}")
    
    @disnake.ui.button(label = "Remaining Voters", style = disnake.ButtonStyle.blurple, row = 2, custom_id = "Remain:this")
    async def remain(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.author.id != self.user:
            return await interaction.response.send_message("Only the creator of this election can use this button.", ephemeral = True)
        
        rem_voters = [user for user in self.guild.members if not user.bot and not [True for value in self.voters.values() if user.id in value]]
        content = f"Voters Left: `{len(rem_voters)}`\n" + "\n".join([f"**{index + 1}.** {voter.mention}" for index, voter in enumerate(rem_voters)])

        await interaction.response.send_message(content = content, allowed_mentions = disnake.AllowedMentions.none(), ephemeral = True)
    
    @disnake.ui.button(label = "End Election", style = disnake.ButtonStyle.red, row = 3, custom_id = "End:this")
    async def end(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.author.id != self.user:
            return await interaction.response.send_message("Only the creator of this election can use this button.", ephemeral = True)

        view = ConfirmEnd(election_view = self)
        count = f"`{sum([len(item) for item in self.voters.values()])}/{len([member for member in self.guild.members if not member.bot])}`"
        await interaction.response.send_message(content = f'Are you sure you want to end the election right now?\nElection still has {display_time(int(self.endtime - datetime.now().timestamp()))} left to end and {count} users have voted!', view = view, ephemeral = True)
    
    async def end_election(self):
        query = "SELECT disabled FROM election WHERE messageid = $1"
        disabled = await self.bot.db.fetchval(query, self.message.id)

        if disabled:
            return

        try:
            user = await self.bot.fetch_user(self.user)
            await user.send(content = f"**Results:**\n" + "\n".join([f"<@!{user}> - {len(item)} vote{'s' if len(item) != 1 else ''}" for user, item in self.voters.items()]))
        except:
            return await self.message.reply(f'<@!{self.user}> you need to open dms to end the poll')

        self.bot.get_cog("Moderation").eview = None

        for item in self.children:
            item.disabled = True

        await self.message.edit(view = self)

        query = "UPDATE election SET disabled = $2 WHERE messageid = $1"
        await self.bot.db.execute(query, self.message.id, True)
        self.stop()