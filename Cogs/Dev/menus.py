import disnake
from disnake.ext import commands

import asyncio

from Core.Utils.useful import get_em

class ConfirmLeave(disnake.ui.View):
    """ View to Confirm Leave """
    def __init__(self, ctx: commands.Context, guild: disnake.Guild, bot: commands.Bot, timeout: float = 180.0) -> bool:
        super().__init__(timeout = timeout)
        self.ctx = ctx
        self.guild = guild
        self.bot = bot
        self.value = None
    
    @disnake.ui.button(label = 'Confirm', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
                return
        for item in self.children:
            item.disabled = True
        button.style = disnake.ButtonStyle.green
        try:
            await self.guild.leave()
        except:
            button.style = disnake.ButtonStyle.red
            await interaction.message.edit(embed = disnake.Embed(description = f"I was unable to leave **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})**!", color = disnake.Colour.red()), view = self)
        else:
            self.value = True
            await interaction.message.edit(embed = disnake.Embed(description = f"I have left **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})**, sucks for them {self.bot.get_em('shinobubully')}", color = disnake.Colour.green()), view = self)
        self.stop()

    @disnake.ui.button(label = 'Cancel', style = disnake.ButtonStyle.grey)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            return
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.red if item == button else disnake.ButtonStyle.gray
        self.value = False
        await interaction.message.edit(embed = disnake.Embed(description = f"Guess I'm not leaving **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})** today", colour = disnake.Colour.red()), view = self)
        self.stop()
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.red if item.label == "Cancel" else disnake.ButtonStyle.gray
        self.value = False
        await self.message.edit(embed = disnake.Embed(description = f"You took too long to respond!", colour = disnake.Colour.red()), view = self)

class WhoAsked(disnake.ui.View):
    """ View for Whoasked """
    def __init__(self, *, timeout: float = 180):
        super().__init__(timeout = timeout)
        self.playing = False
        self.message: disnake.Message
    
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
                await self.message.edit(content = "Now playing: \nWho Asked (Feat. Nobody Did)\n" + "────"*x + "⬤" + "────"*(4-x), view = self)
            except: pass
        
        playpause.label = "▶"
        self.playing = False
        await self.message.edit(view = self)

    @disnake.ui.button(label = "◄◄", style = disnake.ButtonStyle.gray, custom_id = 'prevtrack')
    async def prevtrack(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        pass

    @disnake.ui.button(label = "▶", style = disnake.ButtonStyle.gray, custom_id = 'play')
    async def play(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if self.playing:
            return
        await interaction.response.defer()
        await self.playmusic()

    @disnake.ui.button(label = "►►", style = disnake.ButtonStyle.gray, custom_id = 'nextrack')
    async def nexttrack(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        pass

    @disnake.ui.button(label = "0:00 / 3:56", style = disnake.ButtonStyle.gray, custom_id = 'time')
    async def time(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        pass

    @disnake.ui.button(label= "━━━━━◉", emoji = "\U0001f50a", style = disnake.ButtonStyle.gray, custom_id = 'sound')
    async def sound(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        button.label = "◉━━━━━" if button.label == "━━━━━◉" else "━━━━━◉"
        button.emoji = "\U0001f507" if button.label != "━━━━━◉" else "\U0001f50a"
        await self.message.edit(view = self)
    
    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view = self)

class GuildButtons(disnake.ui.View):
    """ View for getguild """
    def __init__(self, ctx: commands.Context, bot: commands.Bot, guild: disnake.Guild):
        super().__init__(timeout = 90)
        self.ctx = ctx
        self.bot = bot
        self.guild = guild
        self.user = ctx.author
    
    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(content = f"This is not your button to interact with", ephemeral = True)
        return True

    @disnake.ui.button(label = "Join Guild", style = disnake.ButtonStyle.green)
    async def joinguild(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        for chan in self.guild.text_channels:
            try:
                invite = await chan.create_invite(reason = f"Requested by {self.user}", max_age = 7, temporary = True)
                break
            except: 
                return await interaction.response.send_message(f"I was unable to generate an invite to this guild {self.bot.get_em('cross')}", ephemeral = True)

        if invite:
            await interaction.response.send_message(f"Invite Generated for **[{self.guild}]( {invite} )**", ephemeral = True)
  
    @disnake.ui.button(label = "Leave Guild", style = disnake.ButtonStyle.red)
    async def leaveguild(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user.id != self.user.id:
            return
        if not self.bot.get_guild(self.guild.id):
            await self.ctx.send(embed = disnake.Embed(description = f"Error Bot is not in **[{self.guild}]({self.guild.icon})**", color = disnake.Color.red()))
            return
        await interaction.response.defer()
        command = self.bot.get_command("leave")
        await command(self.ctx, self.guild)

    @disnake.ui.button(emoji = get_em("trash"), style = disnake.ButtonStyle.blurple)
    async def delete(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.user.id != self.user.id:
            return
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):
        await self.message.edit(view = None)

class ConfirmShutdown(disnake.ui.View):
    """ Confirm Shutdown """
    def __init__(self, bot: commands.Bot, ctx: commands.Context, timeout: float = 180.0, **kwargs):
        super().__init__(timeout = timeout)
        self.kwargs = kwargs
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
    
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True
        return await interaction.response.send_message('This is not your button to click!', ephemeral = True)
    
    @disnake.ui.button(label = 'Confirm', style = disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.message.edit(content = "https://tenor.com/view/nick-fury-mother-damn-it-gone-bye-bye-gif-16387502", view = None)
        try:
            await self.ctx.message.add_reaction(self.bot.get_em('tick'))
        except:
            pass
        self.stop()
        await self.bot.close()
    
    @disnake.ui.button(label = 'Cancel', style = disnake.ButtonStyle.grey)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.red if item == button else disnake.ButtonStyle.gray 
        self.stop()
        await self.message.edit(content = "Cancelled Shutdown...", view = self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.red if item.label == "Cancel" else disnake.ButtonStyle.gray 
        await self.message.edit(content = "Cancelled Shutdown...", view = self)