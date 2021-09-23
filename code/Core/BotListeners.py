from discord.ext import commands
from Utils.Useful import *
from Utils.Menus import *

class BotListeners(commands.Cog, name = "Listeners"):
    """ Bot Listeners for Major Bot Events """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if self.bot.devmode:
            return
        embed = discord.Embed(colour = discord.Color.random())
        embed.add_field(name="Command Used:", value=f"`{ctx.message.content}`", inline=False)
        embed.add_field(name="Author:", value=f"**{ctx.author}**\n (`{ctx.author.id}`)")
        if ctx.guild:
            embed.add_field(name="Channel:", value=f"**#{ctx.channel}**\n (`{ctx.channel.id}`)")
            embed.add_field(name="Guild:", value=f"**{ctx.guild}**\n (`{ctx.guild.id}`)")
        else:
            embed.add_field(name="Dm Channel:", value=f"**#{ctx.channel}**\n (`{ctx.channel.id}`)")
        embed.add_field(name="Message ID:", value=f"`{ctx.message.id}`")

        channel = self.bot.get_channel(889515203891449877)
        self.bot.cmdchannel = channel
        view = discord.ui.View()
        view.add_item(discord.ui.Button(url = f"{ctx.message.jump_url}", label = "Jump to Source", emoji = "\U0001f517"))
        await channel.send(embed = embed, view = view)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        channel = self.bot.get_channel(880294858600894494)
        if message.guild is None and not message.author.bot:
            final = message.content
            view = discord.ui.View()
            if len(message.content) > 1900:
                fl = await mystbin(data = message.content)
                final = f"Message too long to Display"
                view.add_item(discord.ui.Button(label="MystBin", style=discord.ButtonStyle.link, url=f"{fl}"))
            await channel.send(f"\u200b\n**{message.author}** (`{message.author.id}`) [<t:{round(message.created_at.timestamp())}:T>]\n{final}",view=view,files=[await attachment.to_file() for attachment in message.attachments])
        #await self.bot.process_commands(message)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if "zeus" in message.content.lower() or "sid" in message.content.lower():
            user = self.bot.get_user(760823877034573864)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(url = f"{message.jump_url}", label = "Jump to Source", emoji = "\U0001f517"))
            embed = discord.Embed(title = "Global Highlight", description = f"You were mentioned in {message.guild}" if message.guild else f"You were mentioned in my private dms with {message.author}", colour = self.bot.colour)
            embed.add_field(name="Author:", value=f"**{message.author}**\n (`{message.author.id}`)")
            if message.guild:
                embed.add_field(name="Channel:", value=f"**#{message.channel}**\n (`{message.channel.id}`)")
                embed.add_field(name="Guild:", value=f"**{message.guild}**\n (`{message.guild.id}`)")
            else:
                embed.add_field(name="Dm Channel:", value=f"**#{message.channel}**\n (`{message.channel.id}`)")
            embed.add_field(name="Message ID:", value=f"`{message.id}`")

            await user.send(f"{message.content}", files = [await attachment.to_file() for attachment in message.attachments], view = view, embed = embed)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        embed = guildanalytics(bot = self.bot, join=False, guild = guild)
        channel = self.bot.get_channel(874212184828297297)
        self.bot.log_channel = channel
        await self.bot.log_channel.send(embed=embed)
    
    async def on_guild_join(self, guild):
        channel = self.bot.get_channel(874212184828297297)
        self.bot.log_channel = channel
        embed = guildanalytics(bot = self.bot, join=True, guild = guild)
        await self.bot.log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(BotListeners(bot))
