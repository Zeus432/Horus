import disnake as discord
from disnake.ext import commands

class PersistentButtons(discord.ui.Button):
    def __init__(self, x: int, y: int, role, emoji):
        super().__init__(style=discord.ButtonStyle.secondary, label=f'{role.name}', row=x, custom_id=f'per:{role.name}', emoji=f'{emoji}')
        self.rlist = {"Edgy":810018752639795220,"Cherry":810018754582151199,"Pearl":810018758009421834,"Bubblegum":810018760869543936,"Aqua":810018764467732480,"Sunset":810018767555526677,"Sky":810018771385319514,"Random Colour":813387935394562108}
        self.x = x
        self.y = y
        self.role = role
    
    async def callback(self, interaction: discord.Interaction):
        roles = await interaction.guild.fetch_roles()
        role = [role for role in (roles) if role.name == self.role]

        if dict(interaction.me.guild_permissions)["manage_roles"] == False:
            return await interaction.response.send_message("I'm missing the `Manage Roles` permission!", ephemeral = True)

        if interaction.me.top_role <= role[0]:
            return await interaction.response.send_message("This role is above me, so I cannot give you this role!", ephemeral = True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role, reason = f"Button roles")
            await interaction.response.send_message(f'I have removed the {role.mention} role from you', ephemeral = True)
        else:
            await interaction.user.add_roles(role, reason = f"Button roles")
            await interaction.response.send_message(f'I have added the {role.mention} role to you', ephemeral = True)

class PersistentView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout = None)
        rlist = {"00":810018752639795220,"01":810018754582151199,"02":810018758009421834,"03":810018760869543936,"10":810018764467732480,"11":810018767555526677,"12":810018771385319514,"13":813387935394562108}
        remoji = {"00":"\U000026ab","01":"\U0001f534","02":"\U000026aa","03":"<:pink_circle:886511143433166879>","10":"<:green:853998821663047710>","11":"\U0001f7e0","12":"\U0001f535","13":f"<:rainbow_circle:886456317978484776> "}
        for x in range(2):
            for y in range(4):
                role = rlist[f'{x}{y}']
                emoji = remoji[f'{x}{y}']
                guild = bot.get_guild(809632911690039307)
                role = guild.get_role(role)
                self.add_item(PersistentButtons(x, y, role, emoji))