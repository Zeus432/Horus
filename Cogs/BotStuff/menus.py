import disnake
from bot import Horus
from disnake.ext import commands

class InfoButtons(disnake.ui.View):
    """ View for Bot Info command """
    def __init__(self, ctx: commands.Context, bot: Horus):
        super().__init__(timeout = 300)
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.add_item(disnake.ui.Button(label = "Horus Support", style = disnake.ButtonStyle.link, url = f"https://disnake.gg/8BQMHAbJWk"))
    
    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        if interaction.user != self.user:
            return await interaction.response.send_message("Not your button to interact with!", ephemeral = True)
        return True

    @disnake.ui.button(label = "Request Bot Invite", style = disnake.ButtonStyle.blurple)
    async def callback(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("Not your button to interact with!", ephemeral = True)
        embed = disnake.Embed(description = f"Bot isn't fully set up yet {self.bot.get_em('hadtodoittoem')}", colour = self.bot.colour)
        embed.set_image(url = "https://c.tenor.com/Z6gmDPeM6dgAAAAC/dance-moves.gif")
        await self.ctx.reply(embed = embed)
            
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view = self)