import discord
from discord.ext import commands

import psutil
import os

from Core.Utils.useful import _size
from .useful import get_uptime, total_stuff
from.menus import InfoButtons

class BotStuff(commands.Cog):
    """ Bot Info, Stats and Stuff commands """ 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name = "info", help = "View some info about the bot", brief = "Get Bot Info", aliases = ['about','botinfo'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def info(self, ctx):
        embed = discord.Embed(title = "About Horus",  description = f"Horus is a semi-private bot written in about `{total_stuff('.')[1]}` lines. It was initially made for testing but now includes a lot more now\nIt has Simple Utility, Fun Commands. Run `{ctx.clean_prefix}help` to get started. For bot support join the support server by clicking the button below\n\u200b")
        embed.add_field(name = "Developed By", value = f"**[{self.bot.zeus}](https://www.youtube.com/watch?v=Uj1ykZWtPYI)**")
        embed.add_field(name = "Coded in", value = f"**Language:** **[`python 3.8.5`](https://www.python.org/)**\n**Library:** **[`discord.py 2.0`](https://github.com/Rapptz/discord.py)**\nㅤㅤㅤㅤ{self.bot.get_em('replyend')}Master Branch")
        embed.add_field(name = "\u200b", value = "**Bot Analytics**", inline = False)
        embed.add_field(name = "Running On", value = f"{self.bot.get_em('horus')} `v0.1.1-alpha`\n\u200b")
        embed.add_field(name = "On Discord Since", value = f"<t:{round(self.bot.user.created_at.timestamp())}:D>")
        embed.add_field(name = "Bot Uptime", value = f"{get_uptime(self.bot)}")
        embed.add_field(name = "Statistics", value = f"```yaml\nUsers:    {len([g.id for g in self.bot.users])}\nServers:  {len([g.id for g in self.bot.guilds])}\nChannels: {sum([len([chan.id for chan in guild.channels]) for guild in self.bot.guilds])}\nCommands: {len(list(self.bot.walk_commands()))}```")
        embed.add_field(name = "System", value = f"```yaml\nSystem OS:{' '*6}macOS\nCPU Usage:{' '*6}{round(psutil.getloadavg()[2]/os.cpu_count()*100, 2)}%\nRAM Usage:{' '*6}{round(psutil.virtual_memory()[2], 2)}%\nVirtual Memory: {_size(psutil.Process().memory_full_info().vms)}```")
        embed.set_thumbnail(url = self.bot.user.display_avatar)

        view = InfoButtons(ctx = ctx, bot = self.bot)

        view.message = await ctx.send(embed = embed, view = view)