import discord
from discord.ext import commands

import matplotlib.figure
import psutil
import time
import sys
import os
import io

from Utils.Useful import get_uptime, _size

class Misc(commands.Cog):
    """ Miscellaneous Bot Info and Stats commands """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.bot.launch_time = bot.launch_time
    

    async def cog_check(self, ctx):
        return ctx.guild
 

    @commands.command(name = "info", help = "View some info about the bot", brief = "Get Bot Info", aliases = ['about','botinfo'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def info(self, ctx):
        who = self.bot.get_user(760823877034573864)
        emb = discord.Embed(colour = self.bot.colour, title = "About Horus", description = f"Horus is a private bot and will continue to be so for the foreseeable future. It was initially made for testing but includes a lot more now\nIt has Simple Utility, Fun Commands. Run `{ctx.clean_prefix}help` to get started. For bot support join the support server by clicking the button below\n\u200b")
        emb.add_field(name="Coded in:",value=f"**Language:** **[`python 3.8.5`](https://www.python.org/)**\n**Library:** **[`discord.py 2.0`](https://github.com/Rapptz/discord.py)**\nㅤㅤㅤㅤ{self.bot.emojislist('replyend')} Master Branch")
        emb.add_field(name="Bot Developer",value=f"**[{who}](https://www.youtube.com/watch?v=Uj1ykZWtPYI)**")
        emb.add_field(name="\u200b",value="**Bot Analytics**", inline = False)
        emb.add_field(name="Version:",value="<:Horus:896358537268195370> `0.1.0`\n\u200b")
        emb.add_field(name="On Discord Since:",value=f"<t:{round(ctx.me.created_at.timestamp())}:D>")
        emb.add_field(name="Bot Uptime:",value=get_uptime(self.bot))
        emb.add_field(name = "Statistics:", value=f"```yaml\nServers:  {len([g.id for g in self.bot.guilds])}\nUsers:    {len([g.id for g in self.bot.users])}\nChannels: {sum([len([chan.id for chan in guild.channels]) for guild in self.bot.guilds])}\nCommands: {len(list(self.bot.walk_commands()))}```")
        emb.add_field(name = "System:", value = f"```yaml\nSystem OS:{' '*6}macOS\nCPU Usage:{' '*6}{round(psutil.getloadavg()[2]/os.cpu_count()*100, 2)}%\nRAM Usage:{' '*6}{round(psutil.virtual_memory()[2], 2)}%\nVirtual Memory: {_size(psutil.Process().memory_full_info().vms)}```")
        emb.set_thumbnail(url=ctx.me.avatar)

        class Buttons(discord.ui.View):
            def __init__(self, user: discord.Member, bot):
                super().__init__(timeout = 300)
                self.user = user
                self.bot = bot
            
            @discord.ui.button(label = "Request Bot Invite", style = discord.ButtonStyle.blurple)
            async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user != self.user:
                    return await interaction.response.send_message("Not your menu to interact with!", ephemeral = True)
                em = discord.Embed(description=f"Bot isn't fully set up yet <:hadtodoittoem:874263602897502208>",colour = self.bot.colour)
                em.set_image(url = "https://c.tenor.com/Z6gmDPeM6dgAAAAC/dance-moves.gif")
                await ctx.reply(embed = em, mention_author = True)
            
            async def on_timeout(self):
                for item in self.children:
                    item.disabled = True
                await self.message.edit(view = self)

        view = Buttons(user = ctx.author, bot = self.bot)
        view.add_item(discord.ui.Button(label= "Horus Support", style=discord.ButtonStyle.link, url=f"https://discord.gg/8BQMHAbJWk"))
        view.message = await ctx.send(embed = emb, view=view)


    @commands.command(name = "ping", help = "View the ping of the bot", brief = "Take a wild guess")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def ping(self, ctx):
        start = time.perf_counter()
        msg = await ctx.send(f"{self.bot.emojislist('loading')} Pinging")
        await ctx.author.trigger_typing()
        end = time.perf_counter()
        typing_ping = (end - start) * 1000

        start = time.perf_counter()
        await self.bot.db.execute('SELECT 1')
        end = time.perf_counter()
        sql_ping = (end - start) * 1000
        await msg.edit(content=f"Pong {self.bot.emojislist('catpong')}\n**Typing**: `{round(typing_ping, 1)} ms`\n**Websocket**: `{round(self.bot.latency*1000)} ms`\n**Database**: `{round(sql_ping, 1)} ms`")


    @commands.command(name='uptime', brief = "Bot Uptime")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def uptime(self, ctx: commands.Context):
        """Gets the uptime of the bot"""
        uptime_string = get_uptime(self.bot)
        await ctx.channel.send(f'Whorus has been up for {uptime_string}.\nSince <t:{round(self.bot.launch_ts)}>')
    

    @commands.command(name='support', brief = "Bot Support")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def support(self, ctx: commands.Context):
        """ Get an Invite to Horus' Support Server """
        msg = "<#892767470379749456>: For bot support and For reporting bugs" if ctx.guild.id == 873127663840137256 else "Here is an invite to my Support Server.\n**[ https://discord.gg/8BQMHAbJWk ]**"
        await ctx.reply(msg)


    @commands.command(name = "pie-bot", brief = "Bot/Member ratio")
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def pie_bot(self, ctx):
        """Make a pie chart of server bots."""

        async def pie_gen():
            prc = round(sum(m.bot for m in ctx.guild.members) / len(ctx.guild.members) * 100, 3)

            labels = ["Bots", "Non-Bots"]
            sizes = [prc, 100 - prc]
            colors = ["lightcoral", "lightskyblue"]

            fig = matplotlib.figure.Figure(figsize=(5, 5))
            ax = fig.add_subplot()
            patches, _ = ax.pie(sizes, colors=colors, startangle=90)
            ax.legend(patches, labels)

            fp = io.BytesIO()
            fig.savefig(fp)
            fp.seek(0)

            return [fp, prc]

        fp, prc = await pie_gen()

        fp = discord.File(fp, filename="piechart.png")

        await ctx.send(f":white_check_mark: {prc}% of the server's members are bots.", file=fp)

  
def setup(bot: commands.Bot):
    bot.add_cog(Misc(bot))