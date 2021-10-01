import discord
from discord.ext import commands
from Utils.Useful import *

import matplotlib.figure
import time
import io

class Misc(commands.Cog):
    """ Miscellaneous Bot Info and Stats commands """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.bot.launch_time = bot.launch_time
    

    async def cog_check(self, ctx):
        return ctx.guild
 

    @commands.command(name = "botinfo", help = "View some info about the bot", brief = "Get Bot Info", aliases = ['info', "about"])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def info(self, ctx):
        who = self.bot.get_user(760823877034573864)
        emb = discord.Embed(colour = discord.Colour(10263807))
        emb.add_field(name="Bot Dev:",value=f"**[{who}](https://www.youtube.com/watch?v=Uj1ykZWtPYI)**")
        emb.add_field(name="Coded in:",value=f"**Language:** **[`python 3.8.5`](https://www.python.org/)**\n**Library:** **[`discord.py 2.0`](https://github.com/Rapptz/discord.py)**\nㅤㅤㅤㅤ{self.bot.emojislist('replyend')} Master Branch")
        emb.add_field(name="About Horus:",value=f"Horus is a private bot made for fun, has simple moderation, fun commands and is also called as Whorus <:YouWantItToMoveButItWont:873921001023500328>",inline = False)
        emb.add_field(name="Analytics:",value=f"**Servers:** {len([g.id for g in self.bot.guilds])} servers\n**Users:** {len([g.id for g in self.bot.users])}")
        emb.add_field(name="Bot Uptime:",value=get_uptime(self.bot))
        emb.add_field(name="On Discord Since:",value=f"<t:{round(ctx.me.created_at.timestamp())}:D>")
        emb.set_thumbnail(url=ctx.me.avatar)
        view = discord.ui.View()
        button = discord.ui.Button(label= "Request Bot Invite", style=discord.ButtonStyle.blurple)
        async def callback(interaction):
            em = discord.Embed(description=f"Bot isn't fully set up yet <:hadtodoittoem:874263602897502208>",colour = self.bot.colour)
            await ctx.reply(embed = em, mention_author = False)
            await ctx.send("https://tenor.com/view/dance-moves-dancing-singer-groovy-gif-17029825")
        button.callback = callback
        view.add_item(button)
        view.add_item(discord.ui.Button(label= "Horus Support", style=discord.ButtonStyle.link, url=f"https://discord.gg/8BQMHAbJWk"))
        await ctx.send(embed = emb, view=view)


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
    async def uptime(self, ctx: commands.Context):
        """ Get an Invite to Horus' Support Server """
        msg = "<#892767470379749456>: For bot support and For reporting bugs" if ctx.guild.id == 873127663840137256 else "Here is an invite to my Support Server.\n**[ https://discord.gg/8BQMHAbJWk ]**"
        await ctx.reply(msg)


    @commands.command(name = "pie-bot")
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