import discord
from discord.ext import commands

import asyncio

from Core.Utils.useful import get_em

class ConfirmLeave(discord.ui.View):
    """ View to Confirm Leave """
    def __init__(self, ctx: commands.Context, guild: discord.Guild, bot: commands.Bot, timeout: float = 180.0) -> bool:
        super().__init__(timeout = timeout)
        self.ctx = ctx
        self.guild = guild
        self.bot = bot
        self.value = None
    
    @discord.ui.button(label = 'Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
                return
        for item in self.children:
            item.disabled = True
        button.style = discord.ButtonStyle.green
        try:
            await self.guild.leave()
        except:
            button.style = discord.ButtonStyle.red
            await interaction.message.edit(embed = discord.Embed(description = f"I was unable to leave **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})**!", color = discord.Colour.red()), view = self)
        else:
            self.value = True
            await interaction.message.edit(embed = discord.Embed(description = f"I have left **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})**, sucks for them {self.bot.get_em('shinobubully')}", color = discord.Colour.green()), view = self)
        self.stop()

    @discord.ui.button(label = 'Cancel', style = discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item == button else discord.ButtonStyle.gray
        self.value = False
        await interaction.message.edit(embed = discord.Embed(description = f"Guess I'm not leaving **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})** today", colour = discord.Colour.red()), view = self)
        self.stop()
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item.label == "Cancel" else discord.ButtonStyle.gray
        self.value = False
        await self.message.edit(embed = discord.Embed(description = f"You took too long to respond!", colour = discord.Colour.red()), view = self)

class WhoAsked(discord.ui.View):
    """ View for Whoasked """
    def __init__(self, *, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.playing = False
        self.message: discord.Message
    
    async def playmusic(self, wait: bool = True):
        self.playing = True
        timeline = ['0:00', '1:19', '1:55', '2:37', '3:56']

        for item in self.children:
            if item.custom_id == "time":
                button = item
            if item.custom_id == "play":
                playpause = item

        playpause.label = "▐▐"

        for x in range((0 if wait else 1), 5):
            await asyncio.sleep(1)
            try:
                button.label = f"{timeline[x]} / 3:56"
                await self.message.edit("Now playing: \nWho Asked (Feat. Nobody Did)\n" + "────"*x + "⬤" + "────"*(4-x), view = self)
            except: pass
        
        playpause.label = "▶"
        self.playing = False
        await self.message.edit(view = self)

    @discord.ui.button(label = "◄◄", style = discord.ButtonStyle.gray, custom_id = 'prevtrack')
    async def prevtrack(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label = "▶", style = discord.ButtonStyle.gray, custom_id = 'play')
    async def play(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.playing:
            return
        await interaction.response.defer()
        await self.playmusic()

    @discord.ui.button(label = "►►", style = discord.ButtonStyle.gray, custom_id = 'nextrack')
    async def nexttrack(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label = "0:00 / 3:56", style = discord.ButtonStyle.gray, custom_id = 'time')
    async def time(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label= "━━━━━◉", emoji = "\U0001f50a", style = discord.ButtonStyle.gray, custom_id = 'sound')
    async def sound(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.label = "◉━━━━━" if button.label == "━━━━━◉" else "━━━━━◉"
        button.emoji = "\U0001f507" if button.label != "━━━━━◉" else "\U0001f50a"
        await self.message.edit(view = self)
    
    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view = self)

class GuildButtons(discord.ui.View):
    """ View for getguild """
    def __init__(self, ctx: commands.Context, bot: commands.Bot, guild: discord.Guild):
        super().__init__(timeout = 90)
        self.ctx = ctx
        self.bot = bot
        self.guild = guild
        self.user = ctx.author
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(content = f"This is not your button to interact with", ephemeral = True)
        return True

    @discord.ui.button(label = "Join Guild", style = discord.ButtonStyle.green)
    async def joinguild(self, button: discord.ui.Button, interaction: discord.Interaction):
        for chan in self.guild.text_channels:
            try:
                invite = await chan.create_invite(reason = f"Requested by {self.user}", max_age = 7, temporary = True)
                break
            except: 
                return await interaction.response.send_message(f"I was unable to generate an invite to this guild {self.bot.get_em('cross')}", ephemeral = True)

        if invite:
            await interaction.response.send_message(f"Invite Generated for **[{self.guild}]( {invite} )**", ephemeral = True)
  
    @discord.ui.button(label = "Leave Guild", style = discord.ButtonStyle.red)
    async def leaveguild(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        if not self.bot.get_guild(self.guild.id):
            await self.ctx.send(embed = discord.Embed(description = f"Error Bot is not in **[{self.guild}]({self.guild.icon})**", color = discord.Color.red()))
            return
        await interaction.response.defer()
        command = self.bot.get_command("leave")
        await command(self.ctx, self.guild)

    @discord.ui.button(emoji = get_em("trash"), style = discord.ButtonStyle.blurple)
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):
        await self.message.edit(view = None)