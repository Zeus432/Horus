import discord
from bot import Horus
from discord.ext import commands

class InfoButtons(discord.ui.View):
    """ View for Bot Info command """
    def __init__(self, ctx: commands.Context, bot: Horus):
        super().__init__(timeout = 300)
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.add_item(discord.ui.Button(label = "Horus Support", style = discord.ButtonStyle.link, url = f"https://discord.gg/8BQMHAbJWk"))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            return await interaction.response.send_message("Not your button to interact with!", ephemeral = True)
        return True

    @discord.ui.button(label = "Request Bot Invite", style = discord.ButtonStyle.blurple)
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("Not your button to interact with!", ephemeral = True)
        await interaction.response.defer()
        embed = discord.Embed(description = f"Bot isn't fully set up yet {self.bot.get_em('hadtodoittoem')}", colour = self.bot.colour)
        embed.set_image(url = "https://c.tenor.com/Z6gmDPeM6dgAAAAC/dance-moves.gif")
        await self.ctx.reply(embed = embed)
            
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view = self)