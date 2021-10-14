import discord
from discord.ext import commands

from typing import Optional

from Utils.Useful import *
from Utils.Embeds import *
from Utils.Buttons import *

# Guild Embed Confirm Buttons View

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        self.value = True
        for item in self.children:
            item.disabled = True
        try:
            await self.guild.leave()
            await interaction.message.edit(view=self,embed=discord.Embed(description=f"I have left **[{self.guild}]({self.guild.icon})**, sucks for them {botemojis('shinobubully')}",color=discord.Colour.green()))
        except:
            await interaction.message.edit(view=self,embed=discord.Embed(description=f"I was unable to leave **[{self.guild}]({self.guild.icon})** {botemojis('error')}",color=discord.Colour.red()))
            button.style = discord.ButtonStyle.red
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        self.value = False
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.red
        await interaction.message.edit(view=self,embed=discord.Embed(description=f"Guess I'm not leaving **[{self.guild}]({self.guild.icon})** today",color=discord.Colour.red()))
        self.stop()
    
    async def on_timeout(self):
        self.value = False
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            if item.label == "Cancel":
                item.style = discord.ButtonStyle.red
            item.disabled = True
        await self.msg.edit(view=self,embed=discord.Embed(description=f"You took too long to respond!",color=discord.Colour.blurple()))
        self.stop()

# Guild Embed Buttons

class GuildButtons(discord.ui.View):
    def __init__(self,guild,ctx,bot,user):
        super().__init__(timeout=90)
        self.guild = guild
        self.ctx = ctx
        self.bot = bot
        self.user = user
    
    @discord.ui.button(label= "Join Guild", style=discord.ButtonStyle.green)
    async def joinguild(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        for chan in self.guild.text_channels:
            try:
                invite = await chan.create_invite()
                break
            except: pass
        if invite or None:
            await interaction.response.send_message(f"Invite Generated for **[{self.guild}]( {invite} )**", ephemeral=True)
        else:
            await interaction.response.send_message(f"I was unable to generate an invite to this guild {botemojis('error')}", ephemeral=True)
    
    @discord.ui.button(label= "Leave Guild", style=discord.ButtonStyle.red)
    async def leaveguild(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        if not self.bot.get_guild(self.guild.id):
            await self.ctx.send(embed = discord.Embed(description=f"Error Bot is not in **[{self.guild}]({self.guild.icon})**",color=discord.Color.red()))
            return
        await interaction.response.defer()
        embed = discord.Embed(description=f"Are you sure you want to leave **[{self.guild}]({self.guild.icon})**?",colour=self.bot.colour)
        confview = Confirm()
        confview.msg = await self.ctx.send(embed=embed,view=confview)
        confview.user,confview.guild = self.user,self.guild
    
    @discord.ui.button(emoji = botemojis("trash"), style=discord.ButtonStyle.blurple)
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):
        await self.message.edit(view=None)


# Errors Pagination

class ErrorsPagination(discord.ui.View):
    def __init__(self, start, pages, oldview: discord.ui.View, lastmsg):
        super().__init__(timeout=300)
        for item in oldview.children:
            item.disabled = False
            self.add_item(item)
        self.pages = pages
        self.tpage = len(pages)
        self.cpage = pages[0]
        self.page = start
        self.add_item(discord.ui.Button(label= "Error Logs Channel", style=discord.ButtonStyle.link, url=f"{lastmsg}", emoji = "<:channel:869062202131382292>"))
        self.children[2].label = f'{self.page}/{self.tpage}'

        if self.page <= 1:
            for item in self.children:
                if "\N{BLACK LEFT-POINTING TRIANGLE}" in item.label:
                    item.disabled = True
        
        if self.page >= self.tpage:
            for item in self.children:
                if "\N{BLACK RIGHT-POINTING TRIANGLE}" in item.label:
                    item.disabled = True
        
            
    
    async def button_pressed(self, button, interaction: discord.Interaction, change: int = 0):
        if interaction.user != self.user:
            return
        
        self.page += change
        current = self.pages[self.page - 1]
        embed = current['embed'].copy()
        embed.title = f"Error #{self.page}"

        for item in self.children:
            item.disabled = False

        if self.page <= 1:
            for item in self.children:
                if "\N{BLACK LEFT-POINTING TRIANGLE}" in item.label:
                    item.disabled = True
        
        if self.page >= self.tpage:
            for item in self.children:
                if "\N{BLACK RIGHT-POINTING TRIANGLE}" in item.label:
                    item.disabled = True
        
        for item in self.children:
            if "/" in item.label:
                item.label = f'{self.page}/{self.tpage}'

        await interaction.message.edit(f"```py\n{current['error']}```", embed = embed, view = self)


    @discord.ui.button(label='\N{BLACK LEFT-POINTING TRIANGLE}\N{BLACK LEFT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction, change=int(f"{1-self.page}"))
    
    @discord.ui.button(label='\N{BLACK LEFT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction, change=-1)
    
    @discord.ui.button(label=f'1/1', style=discord.ButtonStyle.blurple, row=1)
    async def cpage(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return
        await interaction.message.delete()
    
    @discord.ui.button(label='\N{BLACK RIGHT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction, change=+1)
    
    @discord.ui.button(label='\N{BLACK RIGHT-POINTING TRIANGLE}\N{BLACK RIGHT-POINTING TRIANGLE}', style=discord.ButtonStyle.gray, row=1)
    async def end(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_pressed(button, interaction, change=+int(f"{self.tpage-self.page}"))
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

# Poll Menu

class PollMenu(discord.ui.View):
    def __init__(self, amount:int ,bot:commands.Bot, message:discord.Message, author, timestring:str, webhook:discord.Webhook = None, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.num = amount
        self.count = []
        self.webhook = webhook
        self.message = message
        self.user = author
        self.tm = timestring
        self.originalmessage = message.content
        for c in range(amount):
            self.count.append(0)
        self.disable = False
        self.bot = bot
        self.lst = {}
        for i in range(amount):
            self.add_item(PollButton(number = i))
    
    async def endpoll(self):
        for item in self.children:
            item.disabled = True
        i = int(datetime.datetime.timestamp(datetime.datetime.now()))
        content = self.originalmessage + "\n\n" + "\U000030fb".join([f"{botemojis(i)}: `{self.count[i-1]}` " for i in range(1,self.num + 1)]) + f"\n\nPoll closed on <t:{i}:F> (<t:{i}:R>)"
        await self.message.edit(content = content, view = self, allowed_mentions = discord.AllowedMentions.none())
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, url = f"{self.message.jump_url}", label = "Jump to Poll"))
        await self.message.reply(f"Poll closed on <t:{i}:F> (<t:{i}:R>)\n\n**Final Results:**\n\n" + "\U000030fb".join([f"{botemojis(i)}: `{self.count[i-1]}` " for i in range(1,self.num + 1)]) + "\n\u200b", view = view) 
    
    @discord.ui.button(label= "Close Poll", style=discord.ButtonStyle.red, row = 3)
    async def ClosePoll(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(f"Only the owner of this poll ({self.user.mention}) can close this poll", ephemeral = True)
            return
        self.disable = True
        await self.endpoll()

    async def on_timeout(self):
        if not self.disable:
            await self.endpoll()

# Buttons
class DeleteView(discord.ui.View):
    def __init__(self, ctx, timeout:int = 30, **kwargs):
        self.user = ctx.author
        super().__init__(timeout=timeout, **kwargs)
    
    @discord.ui.button(label = "Exit", emoji = f"{botemojis('trash')}", style = discord.ButtonStyle.blurple)
    async def callback(self,button: discord.ui.Button, interaction: discord.Interaction):
        if self.user.id != interaction.user.id:
            return
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view = self)

class ConfirmBl(discord.ui.View):
    def __init__(self, user, confirm, cancel, timeout:int = 30):
        self.value = None
        self.user = user
        self.confirm = confirm
        self.cancel = cancel
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirmed(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        self.value = True
        for item in self.children:
            item.disabled = True
        button.style = discord.ButtonStyle.green
        await interaction.message.edit(f"{self.confirm}", view=self, allowed_mentions = discord.AllowedMentions.none())
        self.stop()


    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def canceled(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return
        self.value = False
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.red
        await interaction.message.edit(f"{self.cancel}", view=self, allowed_mentions = discord.AllowedMentions.none())
        self.stop()
    
    async def on_timeout(self):
        self.value = False
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            if item.label == "Cancel":
                item.style = discord.ButtonStyle.red
            item.disabled = True
        await self.message.edit("Timed Out!", view=self)
        self.stop()