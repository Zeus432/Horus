import disnake as discord
from disnake.ext import commands

class RolesButton(discord.ui.Button["RolesView"]):
    def __init__(self, emoji: str, role: int, use_role_name: bool = False):
        self.role = role[1]
        super().__init__(emoji = f"{emoji}", label = f"{role[0]}" if use_role_name else None, style = discord.ButtonStyle.gray, custom_id = f'per:{role}')
  
    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role)
        
        if role is None:
            roles = [role for role in (await interaction.guild.fetch_roles()) if role.id == self.role]
            if roles is []:
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

class RolesView(discord.ui.View):
    def __init__(self, bot: commands.Bot, guild: int, role_emoji: dict, blacklists: list = [], whitelists: list = [], use_role_name: bool = False):
        super().__init__(timeout = None)
        self.role_emoji = role_emoji
        self.blacklists = blacklists
        self.whitelists = whitelists
        self.use_role_name = use_role_name

        try:
            self.guild = bot.get_guild(guild)
        except commands.GuildNotFound:
            return

        for emoji, role in role_emoji.items():
            self.add_item(RolesButton(emoji = emoji, role = role, use_role_name = use_role_name))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not [role.id for role in interaction.user.roles if role.id in self.blacklists] and not self.whitelists and [role.id for role in interaction.user.roles if role.id in self.whitelists]:
            return True
        await interaction.response.defer()
    
    async def stop_button(self) -> None:
        await self.message.edit(view = None)
        self.stop()

    async def refresh_view(self, view: discord.ui.View = None):
        await self.message.edit(view = view or self)
    
    def update_config(self, blacklists: list = None, role_emoji: dict = None, use_role_name: bool = None):
        if blacklists is not None:
            self.blacklists = blacklists
        
        if role_emoji is not None:
            self.role_emoji = role_emoji
        
        if use_role_name is not None:
            self.use_role_name = use_role_name