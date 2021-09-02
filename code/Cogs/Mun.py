from discord import embeds, message
from discord.ext import commands
import discord
from discord.ext.commands import bot
from discord.ui import view
from Core.CustomHelp import *
from Core.settings import *
from Utils.Useful import *
from Utils.Menus import *
import asyncio

# Buttons
class Choose(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=30)
        self.value = 3
    

    @discord.ui.button(label= "Send via EB", style=discord.ButtonStyle.green)
    async def viaeb(self, button: discord.ui.Button, interaction: discord.Interaction):
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.green
        await self.msg.edit(view=self)
        self.value = 1
        self.stop()

    @discord.ui.button(label= "Send Private", style=discord.ButtonStyle.blurple)
    async def private(self, button: discord.ui.Button, interaction: discord.Interaction):
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.green
        button.style = discord.ButtonStyle.green
        await self.msg.edit(view=self)
        self.value = 2
        self.stop()

    @discord.ui.button(label= "Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            item.disabled = True
        button.style = discord.ButtonStyle.red
        await self.msg.edit(view=self)
        self.value = 3
        self.stop()
    
    async def on_timeout(self):
        for item in self.children:
            item.style = discord.ButtonStyle.grey
            if item.label == "Cancel":
                item.style = discord.ButtonStyle.red
            item.disabled = True
        self.value = 4
        await self.msg.edit(view=self)


class Examples(discord.ui.Select):
    def __init__(self):
        options = [
                        discord.SelectOption(label='Send via Eb'),
                        discord.SelectOption(label='Send Privately'),
                        discord.SelectOption(label='Cancel')
                    ]
        super().__init__(placeholder='Examples', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        example = {'Send via Eb':'**[Send Via Eb]( https://cdn.discordapp.com/attachments/873251816102584330/879812848975491122/send_via_Eb.mov )**','Send Privately':'**[Send Privately]( https://cdn.discordapp.com/attachments/873251816102584330/879812845984964618/send_private.mov )**','Cancel':'**[Cancel]( https://cdn.discordapp.com/attachments/873251816102584330/879812825369968670/send_cancel.mov )**'}
        for i in self.values:
            await interaction.response.send_message(content=f"**Example:** {example[i]}",ephemeral=True)


class FaqButtons(discord.ui.Select):
    def __init__(self, ctx, bot):
        self.ctx = ctx
        self.bot = bot
        options = [
                        discord.SelectOption(label='About Gt Mun', description='Important Information about the event',emoji=botemojis('UNSC')),
                        discord.SelectOption(label='Server Rules', description='Follow the server rules',emoji=botemojis('rules')),
                        discord.SelectOption(label='About Horus', description='Wanna know about the bot?',emoji=botemojis('tokitosip')),
                        discord.SelectOption(label='Usage of the h!send command', description='Learn more about the h!send used for chit passing',emoji=botemojis('staff')),
                        discord.SelectOption(label='Other Horus Commands', description='Other commands that might be useful',emoji=botemojis('cogs'))
                    ]
        super().__init__(placeholder='About GT Mun and How to use Horus', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        #embed1
        #sub embed 11
        emb11 = discord.Embed(colour=discord.Colour(0xf5d376),description="GTMUN is a student forward event conducted by GTA Vidhya Mandir, Neelankarai. The main goal of the event is to foster a culture of debate and diplomacy among students and strengthen the budding MUN circuit of Chennai.\n\nThis is the official server for GT Model United Nations 2021. Chit passing and all other communications (including Unmoderated caucus) during the days of the event will happen here. Kindly check <#876089163454218290> before you start texting.",title = "Gt Model United Nations")
        emb11.set_thumbnail(url="https://cdn.discordapp.com/attachments/873251816102584330/880351261701062686/Screenshot_2021-08-26_at_12.48.22_PM.png")

        #sub embed 12
        emb12 = discord.Embed(colour=discord.Colour(0xf5d376),description = "Presenting the Secretariat and Executive Board for the 3rd edition of GT MUN 2021  \u200b")
        emb12.set_author(name="Executive Board",icon_url="https://cdn.discordapp.com/attachments/873251816102584330/880388939146493983/imageedit_2_6113823624.png")
        emb12.add_field(name="Secretary General",value="Rajnandan ~ <@401717120918093846>\n\u200b")
        emb12.add_field(name="Director General",value="Shaman ~ <@772701276735668245>\n\u200b")
        emb12.add_field(name="United Nations Security Council",value="Rajnandan ~ <@401717120918093846>\nShaina ~ <@768423375286435900>\n\u200b",inline = False)
        emb12.add_field(name="United Nations Human Rights Council",value="Raghav ~ <@699461820578136084>\nAbhinav ~ <@740246853563449404>\n\u200b",inline = False)
        emb12.add_field(name="World Health Organisation",value="Shaman ~ <@772701276735668245>\nPavan ~ <@796060531081216070>",inline = False)

        #sub embed 13
        emb13 = discord.Embed(colour=discord.Colour(0xf5d376),description="Click below for the links to the Mun's Instagram Page and Official Website. Please refer to the Oficial Website for the Country Matrix and Background Guides for all the Committees")

        #embed2
        emb2 = discord.Embed(colour=discord.Colour(0xf5d376),description="**1)** **No Cross-talk**\n> Only discussions related to the MUN will be allowed. Kindly refrain from making irrelevant comments during your respective committee sessions.\n\n**2)** **No Toxicity, Vulgarity or Obscene language**\n> Maintain decency. Toxicity, vulgarity and the usage of Obscene language is not allowed. When addressing a delegate do so formally.\n\n**3)** **Questions**\n> Contact the tech head or a volunteer for any questions you may have related to the functioning of this server. For Mun related doubts, please contact the respective chairs.\n \n**Other:**\nFollow **[Discord Terms of Service](https://discord.com/terms)** and **[Community Guidelines](https://discord.com/guidelines)**\nRun `h!faq` and if you have any other questions feel free to ask a <@&876700774082695198>",title = "Code of Conduct")
        emb2.set_author(name="Gt Model United Nations",icon_url="https://cdn.discordapp.com/icons/876044372460838922/d9870f417e49bc16a43e5a08b19aceeb.png?size=1024")

        #embed3
        who = self.bot.get_user(760823877034573864)
        from Utils.Useful import get_uptime
        emb3 = discord.Embed(colour = discord.Colour(10263807))
        emb3.add_field(name="Bot Dev:",value=f"**[{who}](https://www.youtube.com/watch?v=Uj1ykZWtPYI)**")
        emb3.add_field(name="Coded in:",value=f"**Language:** **[`python 3.8.5`](https://www.python.org/)**\n**Library:** **[`discord.py 2.0`](https://github.com/Rapptz/discord.py)**\nㅤㅤㅤㅤ{botemojis('replyend')} Master Branch")
        emb3.add_field(name="About Horus:",value=f"Horus is a private bot made for fun, has simple moderation, fun commands and I am really bad at making a bot info description lmao <:YouWantItToMoveButItWont:873921001023500328>",inline = False)
        emb3.add_field(name="Analytics:",value=f"**Servers:** {len([g.id for g in self.bot.guilds])} servers\n**Users:** {len([g.id for g in self.bot.users])}")
        emb3.add_field(name="Bot Uptime:",value=get_uptime(self.bot))
        emb3.add_field(name="On Discord Since:",value=f"<t:{round(self.bot.get_user(858335663571992618).created_at.timestamp())}:D>")
        emb3.set_thumbnail(url=self.bot.get_user(858335663571992618).avatar)

        #embed4
        emb4 = discord.Embed(colour = self.bot.colour,title="How to use h!send",timestamp=interaction.message.created_at)
        emb4.description = "`h!send` is a command used for chit-passing during committee sessions.\n```yaml\nUsage: h!send <member>```\nWhere `<member>` is the user you wish to send a message to.\nThis command can be run in a channel in this server or in your dms with <@858335663571992618>"
        emb4.add_field(name="Proper Usage",value=f"h!send <@760823877034573864>\nh!send Zeuѕ#0002\nh!send 760823877034573864\n\nThe last one is done by using the user's id (`760823877034573864` for example)\nThis can be done by enabling **[Developer Mode](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)** in your `User Settings`",inline=False)
        emb4.add_field(name="Requirements",value=f"{botemojis('parrow')} You need to be a part of a council to be able to use this command\n{botemojis('parrow')} You can only message users who are a part of the same council as you",inline=False)
        emb4.add_field(name="Walkthrough",value="After you run the command and if all the requirements are met then the bot will ask you to send the message you wish to sent to the other user.\n\nYou have 5 minutes to send your message, after which the bot will ask whether you wish to send your message via Eb or privately. Here is an **[example](https://imgur.com/8D711qf)** of how it looks\n\nIf you chose either Send via Eb or Send privately then the bot will dm the user with the message. Look below for some examples on the usage of this command\n\n**Note:** You are required to follow **[Discord's Terms of Service](https://discord.com/terms)** and **[Community Guidelines](https://discord.com/guidelines)**. This includes but is not limited to - no hate speech and discrimination.")
        if interaction.user.avatar:
            emb4.set_footer(text=f"Requested by {interaction.user}",icon_url=f"{interaction.user.avatar}")
        else:
            emb4.set_footer(text=f"Requested by {interaction.user}")

        #embed5
        emb5 = discord.Embed(colour = self.bot.colour,title="Horus Commands",timestamp=interaction.message.created_at)
        emb5.description = f"Another command which could be useful is `h!ui`, so this command essentially just shows all the discord related information about the mentioned user.\n\nThere are also some 'Gt Mun Badges' which shows which Committee a user belongs to or whether they're the Committee Chair etc.\n\nHere is a list of all currently present Badges:\n{botemojis('mod')} **[Organiser]({interaction.user.avatar})**\n{botemojis('judge')} **[Council Chair]({interaction.user.avatar})**\n{botemojis('staff')} **[Volunteer]({interaction.user.avatar})**\n{botemojis('UNSC')} **[UNSC](https://discord.gg/GYqqjQeZKs)**\n{botemojis('UNHRC')} **[UNHRC](https://discord.gg/GYqqjQeZKs)**\n{botemojis('WHO')} **[WHO](https://discord.gg/GYqqjQeZKs)**\n\nHorus does have other commands that can be used, but not really relevant to this event but feel free to test them out. You can run `h!help` to view a list of all the commands"
        emb5.set_footer(text=f"GT Model United Nations",icon_url=self.bot.get_user(858335663571992618).avatar)
        

        faq = {'About Gt Mun':[emb11,emb12,emb13],'Server Rules':[emb2],'About Horus':[emb3],'Usage of the h!send command':[emb4],'Other Horus Commands':[emb5]}
        view = discord.ui.View()
        if self.values[0] == 'Usage of the h!send command':
            view.add_item(Examples())
        elif self.values[0] == 'About Gt Mun':
            view.add_item(discord.ui.Button(label= "Instagram Page", style=discord.ButtonStyle.link, url="https://www.instagram.com/gtmun2021/"))
            view.add_item(discord.ui.Button(label= "Official Website", style=discord.ButtonStyle.link, url="http://gtvm.school/Mun/"))
        await interaction.response.send_message(embeds=faq[f'{self.values[0]}'],view=view,ephemeral=True)
        if self.values[0] == 'Usage of the h!send command':
            await view.wait()
            await interaction.message.edit(view=view)



class Mun(commands.Cog): 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.chairs =  {876703407551938580:[None],876703436048044092:[None],876703447083253770:[None],True:[None]} 
        self.channel = {876703407551938580:877031734485581954,876703436048044092:877031755792662618,876703447083253770:877031787182841866,True:877854960090513438}

    async def cog_check(self, ctx):
        guild = self.bot.get_guild(876044372460838922)
        if ctx.command.qualified_name == 'send':
            return guild.get_member(ctx.author.id) and ctx.guild in [None,guild]
        return ctx.guild == self.bot.get_guild(876044372460838922)

    @commands.command(cooldown_after_parsing=True, name = "send", help = "Send a message to your fellow delegates via dms", brief = "Send a message")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def send(self, ctx, member: discord.Member):
        if ctx.author.id in self.bot.usingsend:
            await ctx.reply('This command can only be used once per user at the same time')
            return
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.author.dm_channel.id
        guild = self.bot.get_guild(876044372460838922)
        member = guild.get_member(member.id)
        user = guild.get_member(ctx.author.id)
        chk,match = False,False
        if member == user and user.id != 760823877034573864:
            await ctx.send(f'Why are you trying to dm yourself {botemojis("yikes")}')
            return
        if member.bot:
            await ctx.send(f"You'll have better luck trying to get a response from a wall {botemojis('yikes')}")
            return
        if member:
            for i in [876703407551938580,876703436048044092,876703447083253770]:
                if i in [r.id for r in user.roles]:
                    council,chk = i,True
                    if council in [r.id for r in member.roles]:
                        match = True
                        break
            for i in [876704912149475378,876700774082695198]:
                if i in [r.id for r in user.roles] and not match:
                    council = chk = match = True
            if user.id in [401717120918093846] and not match:
                council = chk = match = True
            if not chk:
                await ctx.reply("You need to be a part of the council to use this command!")
            if chk and not match:
                await ctx.reply("You can only send messages to delegates in your own council!")
                return
        else:
            await ctx.reply(f'You can only dm users who are a part of the councils in **{guild}**')
            return
        if self.bot.usingsendchk[council] == False:
            await ctx.send('Chit passing has been disabled for this committee')
            return
        if council and member:
            try:
                self.bot.usingsend.append(ctx.author.id)
                msg = await user.send(f"Enter the message you want to send to {member.mention}")
                if ctx.guild:
                    await ctx.message.add_reaction('\U0001f4e5')
                    await ctx.reply(embed = discord.Embed(description = f'**[Click here]({msg.jump_url})**'))
            except:
                self.bot.usingsend.remove(ctx.author.id)
                await ctx.reply('You need to keep your dms open to use this command!')
                await ctx.message.add_reaction(f'{botemojis("error")}')
                return
            try:
                reply = await self.bot.wait_for(event='message', check=check, timeout=300)
                if reply == None:
                    await msg.reply('Timed out')
                    return
            except asyncio.TimeoutError:
                self.bot.usingsend.remove(ctx.author.id)
                await msg.reply("Response Timed Out!")
            else:
                if len(reply.content) > 2000:
                    self.bot.usingsend.remove(ctx.author.id)
                    await ctx.send(f"Your message can't have more than **2000** charecters! Your message had **{len(reply.content)}** charecters, if required send multiple messages consecutively rather than in one big message")
                    return
                msg2embed = discord.Embed(title="GT Model United Nations",description=f'`Send via Eb` to send your message to {member.mention} (`{member}`) via the EB\n`Send Private` to send your message to {member.mention} (`{member}`) only\n`Cancel` to cancel this process',color=self.bot.colour,timestamp=ctx.message.created_at)
                view = Choose()
                view.msg = await msg.reply(embed=msg2embed, view = view)
                msg2 = view.msg
                await view.wait()
                if view.value == 1:
                    try:
                        embed = discord.Embed(title="New Message recieved!",description=f"You've been sent a new dm by {ctx.author.mention} (`{ctx.author.id}`)", color=self.bot.colour, timestamp=reply.created_at)
                        await member.send(f"{reply.content}" or "[No Message Content]",embed=embed,files=[await attachment.to_file() for attachment in reply.attachments])
                        embed = discord.Embed(title="New Message Sent!",description=f"**From:** {ctx.author.mention} (`{ctx.author.id}`)\n**To:** {member.mention} (`{member.id}`)", color=self.bot.colour, timestamp=reply.created_at)
                        success = []
                        try:
                            for i in self.chairs[council]:
                                if user.id != i and member.id != i:
                                    try:
                                        chair = self.bot.get_user(i)
                                        await chair.send(f"\u200b\n{reply.content}" or "[No Message Content]",embed=embed,files=[await attachment.to_file() for attachment in reply.attachments])
                                        success.append(f"**{chair}**")
                                    except: pass
                        except: pass
                        try:
                            embed.add_field(name="Sent via Eb:", value="\n".join(success) or "No other Eb found")
                            await guild.get_channel(self.channel[council]).send(f"\u200b\n{reply.content}" or "\u200b\n[No Message Content]",embed=embed,files=[await attachment.to_file() for attachment in reply.attachments])
                        except: pass
                        msg2embed.add_field(name="Success!",value=f"Message has been sent via EB to {member.mention}")
                        msg2embed.color = discord.Color.green()
                        await msg2.edit(view=view,embed = msg2embed)
                    except:
                        msg2embed.add_field(name="Error!",value="\nI was unable to dm this user. Make sure their dms isn't closed")
                        msg2embed.color = discord.Color.red()
                        view.children[0].style = discord.ButtonStyle.red
                        await msg2.edit(view=view,embed = msg2embed)
                if view.value == 2:
                    try:
                        embed = discord.Embed(title="New Message recieved!",description=f"You've been sent a new dm by {ctx.author.mention} (`{ctx.author.id}`)", color=self.bot.colour, timestamp=reply.created_at)
                        await member.send(f"{reply.content}" or "[No Message Content]",embed=embed,files=[await attachment.to_file() for attachment in reply.attachments])
                        msg2embed.add_field(name="Success!",value=f"Message has been sent privately to {member.mention}")
                        msg2embed.color = discord.Color.green()
                        await msg2.edit(view=view,embed = msg2embed)
                    except:
                        msg2embed.add_field(name="Error!",value="I was unable to dm this user. Make sure their dms isn't closed")
                        msg2embed.color = discord.Color.red()
                        view.children[1].style = discord.ButtonStyle.red
                        await msg2.edit(view=view,embed = msg2embed)
                elif view.value in [3,4]:
                    msg2embed.color = discord.Color.red()
                    msg2embed.description += "\n\n**Process Cancelled**" if view.value == 3 else "\n\n**You Took too Long to Respond**"
                    await msg2.edit(embed=msg2embed)
                self.bot.usingsend.remove(ctx.author.id)
    
    @commands.command(name = "faq", help = "Here are answers to some Frequently Asked Questions", brief = "Event and Bot FAQs",  aliases = ['usage'])
    @commands.guild_only()
    async def faq(self, ctx):
        view = discord.ui.View()
        view.add_item(FaqButtons(ctx=ctx,bot=self.bot))
        msg = await ctx.send(f"{ctx.author.mention}",view=view)
        await view.wait()
        for item in view.children:
            item.disabled = True
        await msg.edit(view=view)
    
    @commands.command(name = "enablechit", help = "Enable Chit passing for your respective committee", brief = "Enable Chit passing",  aliases = ['enchit','ec'])
    @commands.guild_only()
    async def enablechit(self, ctx, committee: str):
        chk = False
        guild = self.bot.get_guild(876044372460838922)
        user = guild.get_member(ctx.author.id)
        for i in [876086016333717505,880020873489317920,876700774082695198,876704912149475378]:
            if i in [r.id for r in user.roles]:
                chk = True
                break
        if not chk:
            return
        try:
            committeerole = {'unsc':876703407551938580,'unhrc':876703436048044092,'hrc':876703436048044092,'who':876703447083253770}[committee.lower()]
        except: 
            committeerole = None
        if committeerole not in self.bot.usingsendchk:
            await ctx.reply(f'Could not find committee: {committee}')
            return
        if self.bot.usingsendchk[committeerole] == True:
            await ctx.reply(f'Chit passing has already been enabled for {committee.upper()}')
            return
        self.bot.usingsendchk[committeerole] = True
        await ctx.reply(f'Chit passing has been enabled for {committee.upper()}')

    
    @commands.command(name = "disablechit", help = "Disbale Chit passing for your respective committee", brief = "Disable Chit passing",  aliases = ['diechit','dc'])
    @commands.guild_only()
    async def disablechit(self, ctx, committee: str):
        chk = False
        guild = self.bot.get_guild(876044372460838922)
        user = guild.get_member(ctx.author.id)
        for i in [876086016333717505,880020873489317920,876700774082695198,876704912149475378]:
            if i in [r.id for r in user.roles]:
                chk = True
                break
        if not chk:
            return
        try:
            committeerole = {'unsc':876703407551938580,'unhrc':876703436048044092,'hrc':876703436048044092,'who':876703447083253770}[committee.lower()]
        except: 
            committeerole = None
        if committeerole not in self.bot.usingsendchk:
            await ctx.reply(f'Could not find committee: {committee}')
            return
        if self.bot.usingsendchk[committeerole] == False:
            await ctx.reply(f'Chit passing has already been disabled for {committee.upper()}')
            return
        self.bot.usingsendchk[committeerole] = False
        await ctx.reply(f'Chit passing has been disabled for {committee.upper()}')
    
    async def cog_command_error(self, ctx, error):
        """This method will be called if a command in this cog raises an error.""" 
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(f'This command is not available here', delete_after = 10)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.reply(f'I was unable to find this user')
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.reply(f'Command is on cooldown, Try again in {round(error.retry_after, 1)} seconds')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.reply(f'This command is disabled.')
        else:
            await senderror(bot=self.bot,ctx=ctx,error=error)

def setup(bot: commands.Bot):
    bot.add_cog(Mun(bot))