import disnake as discord
from disnake.ext import commands

class RolesButton(discord.ui.Button):
    def __init__(self, emoji: str, role: int):
        super().__init__(emoji = f"{emoji}", style = discord.ButtonStyle.gray, custom_id = f'per:{role}')

        self.role = role
    
    async def callback(self, interaction: discord.Interaction):
        try:
            role = interaction.guild.get_role(self.role)
        except commands.RoleNotFound:
            return await interaction.response.send_message(content = "This role doesn't seem to exist in this server anymore!", ephemeral = True)
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role, reason = "Button Roles")
            return await interaction.response.send_message(content = f"I have removed the {role.mention} role from you!", ephemeral = True)

        await interaction.user.add_roles(role, reason = "Button Roles")
        return await interaction.response.send_message(content = f"I have added the {role.mention} role from you!", ephemeral = True)

class RolesView(discord.ui.View):
    def __init__(self, bot: commands.Bot, guild: int, role_emoji: dict, blacklists: list = []):
        super().__init__(timeout = None)
        self.role_emoji = role_emoji
        self.blacklists = blacklists

        try:
            bot.get_guild(guild)
        except commands.GuildNotFound:
            return

        for emoji, role in role_emoji.items():
            self.add_item(RolesButton(emoji = emoji, role = role))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not [role.id for role in self.blacklists if role.id in interaction.user.roles]:
            return True
        await interaction.response.defer()