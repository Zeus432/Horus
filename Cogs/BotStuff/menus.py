import disnake as discord
from bot import Horus
from disnake.ext import commands

import humanize
import psutil
import os

from Core.Utils.useful import get_commits
from .useful import linecount

class InfoButtons(discord.ui.View):
    """ View for Bot Info command """
    def __init__(self, ctx: commands.Context, bot: Horus):
        super().__init__(timeout = 300)
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.add_item(discord.ui.Button(label = "Invite Horus", style = discord.ButtonStyle.link, url = f"{self.bot._config['invite']['normal']}"))
        self.add_item(discord.ui.Button(label = "Horus Support", style = discord.ButtonStyle.link, url = f"https://discord.gg/8BQMHAbJWk"))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            return await interaction.response.send_message("Not your button to interact with!", ephemeral = True)
        return True
    
    @discord.ui.button(label = "Bot Stats", style = discord.ButtonStyle.blurple)
    async def stats(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(colour = self.bot.colour)
        
        embed.add_field(name = "Statistics", value = f"```yaml\nUsers:    {len([g.id for g in self.bot.users])}\nServers:  {len([g.id for g in self.bot.guilds])}\nChannels: {sum([len([chan.id for chan in guild.channels]) for guild in self.bot.guilds])}\nCommands: {len(list(self.bot.walk_commands()))}```")
        embed.add_field(name = "System", value = f"```yaml\nSystem OS:{' '*6}macOS\nCPU Usage:{' '*6}{round(psutil.getloadavg()[2]/os.cpu_count()*100, 2)}%\nRAM Usage:{' '*6}{round(psutil.virtual_memory()[2], 2)}%\nMemory Usage:   {humanize.naturalsize(psutil.Process().memory_full_info().uss)}```")

        await interaction.response.send_message(embed = embed, ephemeral = True)
    
    @discord.ui.button(label = "Latest Commits", style = discord.ButtonStyle.blurple)
    async def commits(self, button: discord.ui.Button, interaction: discord.Interaction):
        commits, commit_list = get_commits(), []

        for num in range(10):
            short_hash = commits[num]['hash'][0:7]
            commit_list.append(f'[`{short_hash}`](https://github.com/Zeus432/Horus/commit/{commits[num]["hash"]}) - {commits[num]["title"]}')
        
        embed = discord.Embed(title = "Latest Commits", description = "\n".join(commit_list), colour = self.bot.colour)
        await interaction.response.send_message(embed = embed, ephemeral = True)
            
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True if item.style != discord.ButtonStyle.link else False 
        await self.message.edit(view = self)