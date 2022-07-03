from datetime import datetime
import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from Core.Utils.functions import emojis


class ConfirmShutdown(discord.ui.View):
    """ A view for confirming shutdown """
    def __init__(self, bot: Horus, ctx: HorusCtx, timeout: float = 30) -> None:
        super().__init__(timeout = timeout)
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.message: discord.Message

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False

    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.message.edit(content = "https://tenor.com/view/nick-fury-mother-damn-it-gone-bye-bye-gif-16387502", view = None)
        await self.ctx.try_add_reaction("<:TickYes:904315692311011360>")
        self.stop()
        await self.bot.close()

    @discord.ui.button(label = "Cancel", style = discord.ButtonStyle.grey)
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
    def __init__(self, bot: Horus, ctx: HorusCtx, timeout: float = 90) -> None:
        super().__init__(timeout = timeout)
        self.user = ctx.author
        self.bot = bot
        self.ctx = ctx
        self.message: discord.Message

        for item in self.children:
            if ctx.guild.me.status.name == item.custom_id:
                item.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
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

    @discord.ui.button(emoji = emojis("online"), style = discord.ButtonStyle.grey, custom_id = "online")
    async def online(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, discord.Status.online)

    @discord.ui.button(emoji = emojis("idle"), style = discord.ButtonStyle.grey, custom_id = "idle")
    async def idle(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, discord.Status.idle)

    @discord.ui.button(emoji = emojis("dnd"), style = discord.ButtonStyle.grey, custom_id = "dnd")
    async def dnd(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, discord.Status.dnd)

    @discord.ui.button(emoji = emojis("offline"), style = discord.ButtonStyle.grey, custom_id = "offline")
    async def offline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_status(interaction, discord.Status.offline)

    @discord.ui.button(label = "Change Activity", style = discord.ButtonStyle.blurple, row = 1)
    async def activity(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Activity(ctx = self.ctx, bot = self.bot))

    @discord.ui.button(label = "Clear Activity", style = discord.ButtonStyle.red, row = 1)
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


class ConfirmLeave(discord.ui.View):
    def __init__(self, bot: Horus, ctx: HorusCtx, timeout: float = 90):
        super().__init__(timeout = timeout)
        self.bot = bot
        self.ctx = ctx
        self.guild = ctx.guild
        self.user = ctx.author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            await interaction.response.defer()
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False

    async def edit_embed(self, button, interaction, message, colour):
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.gray if item != button else button.style

        await interaction.message.edit(embed = discord.Embed(description = message, colour = colour), view = self)

    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.guild.leave()
        except:
            button.style = discord.ButtonStyle.red
            await self.edit_embed(button, interaction, f"I was unable to leave **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})**!", discord.Colour.red())
        else:
            await self.edit_embed(button, interaction, f"I have left **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})**, sucks for them.", discord.Colour.green())
        self.stop()

    @discord.ui.button(label = "Cancel", style = discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.style = discord.ButtonStyle.red
        await self.edit_embed(button, interaction, f"Guess I'm not leaving **[{self.guild}]({self.guild.icon or self.bot.user.display_avatar})** today", discord.Colour.red())
        self.stop()

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = discord.ButtonStyle.red if item.label == "Cancel" else discord.ButtonStyle.gray

        await self.message.edit(embed = discord.Embed(description = f"You took too long to respond!", colour = discord.Colour.red()), view = self)


class GuildView(discord.ui.View):
    def __init__(self, bot: Horus, ctx: HorusCtx, timeout: float = 90):
        super().__init__(timeout = timeout)
        self.bot = bot
        self.ctx = ctx
        self.guild = ctx.guild
        self.user = ctx.author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False

    @discord.ui.button(label = "Join Guild", style = discord.ButtonStyle.green)
    async def joinguild(self, interaction: discord.Interaction, button: discord.ui.Button):
        for chan in self.guild.text_channels:
            try:
                invite = await chan.create_invite(reason = f"Requested by {self.user}", max_age = 7, temporary = True)
                break
            except: pass

        if invite:
            return await interaction.response.send_message(f"Invite Generated for **[{self.guild}]( {invite} )**", ephemeral = True)
        await interaction.response.send_message(f"I was unable to generate an invite to this guild {self.bot.get_em('cross')}", ephemeral = True)

    @discord.ui.button(label = "Leave Guild", style = discord.ButtonStyle.red)
    async def leaveguild(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if self.bot.get_guild(self.guild.id) is None:
            await self.ctx.send(embed = discord.Embed(description = f"Error Bot is not in **[{self.guild}]({self.guild.icon})**", color = discord.Color.red()))
            return

        command = self.bot.get_command("leave")
        await command(self.ctx, self.guild)

    @discord.ui.button(emoji = emojis("trash"), style = discord.ButtonStyle.blurple)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):
        await self.message.edit(view = None)


class ConfirmBlacklist(discord.ui.View):
    def __init__(self, bot: Horus, ctx: HorusCtx, what: discord.User | discord.Guild, what_type: str, blacklist: bool = True, timeout: float = 30):
        super().__init__(timeout = timeout)
        self.bot = bot
        self.ctx = ctx
        self.what = what
        self.what_type = what_type
        self.blacklist = blacklist
        self.user = ctx.author
        self.message: discord.Message

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user.id == interaction.user.id:
            return True

        await interaction.response.send_message("This is not your button to click!", ephemeral = True)
        return False

    async def disable(self, style: discord.ButtonStyle, message: str, interaction: discord.Interaction = None, timeout: bool = False):
        for item in self.children:
            item.style = style if item.style == style else discord.ButtonStyle.gray
            item.disabled = True

        if timeout is True:
            return await self.message.edit(content = message, view = self)

        await interaction.response.edit_message(content = message, view = self)
        self.stop()

    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.blacklist is True: # if action is to blacklist
            if blacklists := await self.bot.db.fetchval(f"SELECT blacklists FROM {self.what_type}data WHERE {self.what_type}id = $1", self.what.id):

                blacklists.update({
                    'blacklisted': True,
                    'since': round(datetime.now().timestamp()),
                    'doneby': self.user.id,
                    'history': [*[h for h in blacklists.get('history')], {'blnum': (blacklists.get('prevbl') or 0) + 1, 'doneby': self.user.id, 'since': round(datetime.now().timestamp())}]
                })

                await self.bot.db.execute(f"UPDATE {self.what_type}data SET blacklists = $2 WHERE {self.what_type}id = $1", self.what.id, blacklists)

            else:
                await self.bot.db.execute(f"INSERT INTO {self.what_type}data({self.what_type}id, blacklists) VALUES($1, $2) ON CONFLICT ({self.what_type}id) DO UPDATE SET blacklists = $2", self.what.id, {'prevbl': 0, 'blacklisted': True, 'doneby': self.user.id, 'since': round(datetime.now().timestamp()), 'history': [{'blnum': 1, 'doneby': self.user.id, 'since': round(datetime.now().timestamp())}]})

            await self.bot.redis.rpush("blacklist", self.what.id) # add the user / guild id to blacklist cache
            await self.disable(button.style, f"{getattr(self.what, 'mention', None) or getattr(self.what, 'name', None) or '[Could not fetch guild]'} (`{self.what.id}`) has been blacklisted!", interaction)

            if isinstance(self.what, discord.Guild):
                await self.what.leave() # Leave guild when blacklisted
                await interaction.followup.send("I have left this guild!")

        elif self.blacklist is False: # if action is to unblacklist
            if blacklists := await self.bot.db.fetchval(f"SELECT blacklists FROM {self.what_type}data WHERE {self.what_type}id = $1", self.what.id):
                blacklists.update({'blacklisted': False, 'prevbl': blacklists.get('prevbl') + 1, 'doneby': self.user.id, 'since': round(datetime.now().timestamp())})
                await self.bot.db.execute(f"UPDATE {self.what_type}data SET blacklists = $2 WHERE {self.what_type}id = $1", self.what.id, blacklists)

            else:
                await self.bot.db.execute(f"INSERT INTO {self.what_type}data({self.what_type}id, blacklists) VALUES($1, $2) ON CONFLICT ({self.what_type}id) DO UPDATE SET blacklists = $2", self.what.id, {'prevbl': 1, 'blacklisted': False, 'doneby': self.user.id, 'since': round(datetime.now().timestamp())})

            await self.bot.redis.lrem("blacklist", 0, self.what.id) # remove the user / guild id from blacklist cache
            await self.disable(button.style, f"{getattr(self.what, 'mention', None) or getattr(self.what, 'name', None) or '[Could not fetch guild]'} (`{self.what.id}`) has been unblacklisted!", interaction)

    @discord.ui.button(label = "Cancel", style = discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.disable(button.style, "Cancelled " + ("un" if self.blacklist is False else "") + f"blacklisting {getattr(self.what, 'mention', None) or getattr(self.what, 'name', None) or '[Could not fetch guild]'} (`{self.what.id}`)", interaction)

    async def on_timeout(self):
        await self.disable(discord.ButtonStyle.red, "You took too long to respond!", timeout = True)