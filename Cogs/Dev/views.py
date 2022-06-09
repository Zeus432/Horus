from cProfile import label
import discord
from Core.bot import Horus, HorusCtx
from discord.ext import commands


class ConfirmShutdown(discord.ui.View):
    """ A view for confirming shutdown """
    def __init__(self, bot: Horus, ctx: HorusCtx, timeout: float = 30.0, **kwargs) -> None:
        super().__init__(timeout = timeout)
        self.kwargs = kwargs
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.message: discord.Message
    
    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True
        
        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False
    
    @discord.ui.button(label = 'Confirm', style = discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.message.edit(content = "https://tenor.com/view/nick-fury-mother-damn-it-gone-bye-bye-gif-16387502", view = None)
        await self.ctx.try_add_reaction("<:TickYes:904315692311011360>")
        self.stop()
        await self.bot.close()
    
    @discord.ui.button(label = 'Cancel', style = discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item.label == button.label else discord.ButtonStyle.gray 
        self.stop()
        await self.message.edit(content = "Cancelled Shutdown...", view = self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item.label == "Cancel" else discord.ButtonStyle.gray 
        await self.message.edit(content = "Decide faster next time", view = self)

class ChangeStatus(discord.ui.View):
    def __init__(self, bot: Horus, ctx: HorusCtx, timeout: float = 90.0, **kwargs) -> None:
        super().__init__(timeout = timeout)
        self.kwargs = kwargs
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.message: discord.Message

        for item in self.children:
            if ctx.guild.me.status.name == item.custom_id:
                item.disabled = True
    
    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if self.user.id == interaction.user.id:
            return True
        
        await interaction.response.send_message('This is not your button to click!', ephemeral = True)
        return False
    
    async def change_status(self, interaction: discord.Interaction, state: discord.Status):
        await self.bot.change_presence(status = state, activity = self.ctx.guild.me.activity)

        embed = discord.Embed(colour = self.bot.colour)
        embed.add_field(name = "Status:", value = f"{self.bot.get_em(self.ctx.guild.me.status.name)} {self.ctx.guild.me.status.name.capitalize()}", inline = False)
        if (act := self.ctx.guild.me.activity) is not None:
            embed.add_field(name = "Activity:", value = f"```{act.type.name.capitalize()} {act.name}```", inline = False)

        for item in self.children:
            item.disabled = True if self.ctx.guild.me.status.name == item.custom_id else False

        await interaction.response.edit_message(embed = embed, view = self)
    
    @discord.ui.button(emoji = '<:_:984147000540930109>', style = discord.ButtonStyle.grey, custom_id = "online")
    async def online(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, discord.Status.online)
    
    @discord.ui.button(emoji = '<:_:984147387629052004>', style = discord.ButtonStyle.grey, custom_id = "idle")
    async def idle(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, discord.Status.idle)
    
    @discord.ui.button(emoji = '<:_:984147117306183781>', style = discord.ButtonStyle.grey, custom_id = "dnd")
    async def dnd(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, discord.Status.dnd)
    
    @discord.ui.button(emoji = '<:_:984147221094215700>', style = discord.ButtonStyle.grey, custom_id = "offline")
    async def offline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, discord.Status.offline)
    
    @discord.ui.button(label = 'Change Activity', style = discord.ButtonStyle.blurple, row = 1)
    async def activity(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Activity(ctx = self.ctx, bot = self.bot))
    
    @discord.ui.button(label = 'Clear Activity', style = discord.ButtonStyle.red, row = 1)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.change_presence(status = self.ctx.guild.me.status)
        
        embed = discord.Embed(colour = self.bot.colour)
        embed.add_field(name = "Status:", value = f"{self.bot.get_em(self.ctx.guild.me.status.name)} {self.ctx.guild.me.status.name.capitalize()}", inline = False)
        if (act := self.ctx.guild.me.activity) is not None:
            embed.add_field(name = "Activity:", value = f"```{act.type.name.capitalize()} {act.name}```", inline = False)

        for item in self.children:
            item.disabled = True if self.ctx.guild.me.status.name == item.custom_id else False

        await interaction.response.edit_message(embed = embed, view = self)
    
    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        
        await self.message.edit(view = self)

class Activity(discord.ui.Modal):
    def __init__(self, *, ctx: HorusCtx, bot: Horus) -> None:
        super().__init__(title = "Change Bot Activity")
        self.bot = bot
        self.ctx = ctx

        atype = discord.ui.Select(
            placeholder = "Activity Type",
            options = [
                discord.SelectOption(label = "Competing"),
                discord.SelectOption(label = "Listening"),
                discord.SelectOption(label = "Playing"),
                discord.SelectOption(label = "Watching")
            ]
        )

        for item in atype.options:
            if ctx.guild.me.activity and ctx.guild.me.activity.type.name == item.label.lower():
                item.default = True
        
        self.add_item(atype)
        self.atype = atype

        aname = discord.ui.TextInput(
            label = "Activity Name",
            style = discord.TextStyle.long,
            placeholder = "for @Horus help..." if ctx.guild.me.activity is None else f"{ctx.guild.me.activity.name}",
            required = True,
            max_length = 128,
        )
        self.add_item(aname)
        self.aname = aname
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        activity = {"Competing": discord.ActivityType.competing, "Listening": discord.ActivityType.listening, "Playing": discord.ActivityType.playing, "Watching": discord.ActivityType.watching}
        await self.bot.change_presence(status = self.ctx.guild.me.status, activity = discord.Activity(type = activity[self.atype.values[0]], name = self.aname.value))

        embed = discord.Embed(colour = self.bot.colour)
        embed.add_field(name = "Status:", value = f"{self.bot.get_em(self.ctx.guild.me.status.name)} {self.ctx.guild.me.status.name.capitalize()}", inline = False)
        embed.add_field(name = "Activity:", value = f"```{self.atype.values[0]} {self.aname.value}```", inline = False)

        await interaction.response.edit_message(embed = embed)