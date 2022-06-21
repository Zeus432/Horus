import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from Core.Utils.functions import emojis, write_toml

class ListenerView(discord.ui.View):
    def __init__(self, bot: Horus, ctx: HorusCtx, config: dict, timeout: float = 90.0) -> None:
        super().__init__(timeout = timeout)
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.config = config.copy()
        self.add_item(ListenerSelect(bot, ctx, self.config))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            return True
        
        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False
    
    async def end(self):
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(title = f"{self.bot.user.name} Listener Config", colour = self.bot.colour)
        embed.description = "```yaml\n" + "\n".join([f"{var} : {val}" for var, val in self.ctx.cog._config.items()]) + "```"
        await self.message.edit(embed = embed, view = self)
    
    @discord.ui.button(label = "Confirm Changes", style = discord.ButtonStyle.green, row = 1)
    async def change(self, interaction: discord.Interaction, button: discord.ui.Button):
        changelog = [f"{var} : {val} => {True if val is False else False}" for var, val in self.ctx.cog._config.items() if self.config[var] is not val]

        if not changelog:
            return await interaction.response.send_message("There are no changes to make.", ephemeral = True)

        await interaction.response.send_message("Made the following changes to Listener config: ```yaml\n" + "\n".join(changelog) + "```", ephemeral = True)
        write_toml("Cogs/Listeners/config.toml", self.config)
        self.ctx.cog._config = self.config

        await self.end()
        self.stop()
    
    @discord.ui.button(emoji = emojis("trash"), style = discord.ButtonStyle.blurple, row = 1)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()
    
    async def on_timeout(self):
        await self.end()


class ListenerSelect(discord.ui.Select):
    def __init__(self, bot: Horus, ctx: HorusCtx, config: dict) -> None:
        super().__init__(placeholder = "Select option to toggle", options = [discord.SelectOption(label = f"{var}", description = f"Set to : {val}") for var, val in config.items()])
        self.config = config
        self.ctx = ctx
        self.bot = bot
    
    async def callback(self, interaction: discord.Interaction):
        self.config[self.values[0]] = True if self.config[self.values[0]] == False else False
        embed = discord.Embed(title = f"{self.bot.user.name} Listener Config", colour = self.bot.colour)
        embed.description = "```yaml\n" + "\n".join([f"{var} : {val}" for var, val in self.config.items()]) + "```"

        await interaction.response.edit_message(embed = embed)