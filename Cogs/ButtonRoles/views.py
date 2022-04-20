import disnake
from disnake.ext import commands

import traceback

class RolesButton(disnake.ui.Button["RolesView"]):
    def __init__(self, emoji: str, role: list, use_role_name: bool = False):
        self.role = role[1]
        super().__init__(emoji = f"{emoji}", label = f"{role[0]}" if use_role_name else None, style = disnake.ButtonStyle.gray, custom_id = f'per:{role}')
  
    async def callback(self, interaction: disnake.Interaction):
        role = interaction.guild.get_role(self.role)
        
        if role is None:
            roles = [role for role in (await interaction.guild.fetch_roles()) if role.id == self.role]
            if not roles:
                return await interaction.response.send_message(content = "This role doesn't seem to exist in this server anymore!", ephemeral = True)
            
            else:
                role = roles[0]
        
        if interaction.me.guild_permissions.manage_roles == False:
            return await interaction.response.send_message("I'm missing the `Manage Roles` permission!", ephemeral = True)

        if interaction.me.top_role <= role:
            return await interaction.response.send_message("I was unable to manage this role as it is above mine!", ephemeral = True)
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role, reason = "Button Roles")
            return await interaction.response.send_message(content = f"I have removed the {role.mention} role from you!", ephemeral = True)

        await interaction.user.add_roles(role, reason = "Button Roles")
        return await interaction.response.send_message(content = f"I have added the {role.mention} role to you!", ephemeral = True)

class RolesView(disnake.ui.View):
    def __init__(self, bot: commands.Bot, guild: int, role_emoji: dict, blacklists: list = [], use_role_name: bool = False):
        super().__init__(timeout = None)
        self.bot = bot
        self.role_emoji = role_emoji
        self.blacklists = blacklists
        self.use_role_name = use_role_name

        try:
            self.guild = bot.get_guild(guild)
        except commands.GuildNotFound:
            return

        for emoji, role in role_emoji.items():
            self.add_item(RolesButton(emoji = emoji, role = role, use_role_name = use_role_name))
    
    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        if [role.id for role in interaction.user.roles if role.id in self.blacklists]:
            return await interaction.response.send_message("You're not allowed to use this button roles", ephemeral = True)

        return True
    
    async def on_error(self, error: Exception, button: disnake.ui.Button, interaction: disnake.Interaction):
        traceback_error = traceback.format_exception(type(error), error, error.__traceback__)

        split_error, final_error = "", []
        
        for line in traceback_error:
            if len(split_error + line) < 1900:
                split_error += f"\n{line}"

            else:
                final_error.append(split_error)
                split_error = ""

        final_error.append(split_error)

        await self.bot._notif_webhook.send(f'{self.bot.zeus.mention} Button roles view at [{self.message.id}]({self.message.jump_url}) has errored!\n```py\n{final_error[0]}```')

        for e in final_error[1:]:
            await self.bot._notif_webhook.send(f'```py\n{e}```')
    
    async def stop_button(self) -> None:
        await self.message.edit(view = None)
        self.stop()

    async def refresh_view(self, view: disnake.ui.View = None):
        await self.message.edit(view = view or self)
    
    def update_config(self, blacklists: list = None, role_emoji: dict = None, use_role_name: bool = None):
        if blacklists is not None:
            self.blacklists = blacklists
        
        if role_emoji is not None:
            self.role_emoji = role_emoji
        
        if use_role_name is not None:
            self.use_role_name = use_role_name

# Views for the Button Roles Config
class ConfigView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout = 300)

        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.link, label = "Message Link", emoji = "\U0001f517", url = "stuff here"))

    @disnake.ui.button(label = "Role Pairs", style = disnake.ButtonStyle.blurple)
    async def role_pair(self, button: disnake.Button, interaction: disnake.Interaction):
        pass

    @disnake.ui.button(label = "Blacklists", style = disnake.ButtonStyle.blurple)
    async def blacklists(self, button: disnake.Button, interaction: disnake.Interaction):
        pass