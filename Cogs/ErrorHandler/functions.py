import discord
from discord.ext import commands
from Core.bot import Horus, HorusCtx

from loguru import logger
import traceback


async def send_error(bot: Horus, ctx: HorusCtx, error: commands.CommandError):
    """ Properly send error to error channel and log it in the error logs """
    embed = discord.Embed(title = "Command Error!", description = f"This error has been forwarded to the bot developer and will be fixed soon.\nIn the meantime please refrain from trying to recreate this error unnecessarily.\n```{error}```", colour = discord.Colour(0x2F3136))
    embed.set_footer(text = "Spamming errored commands will get you blacklisted!", icon_url = ctx.author.display_avatar.url)

    await ctx.reply(embed = embed, mention_author = False, delete_after = 30)

    tracederror = traceback.format_exception(type(error), error, error.__traceback__)
    logger.opt(exception = error).error(f"Ignoring exception in command {ctx.command}\nCommand Used : {ctx.message.content}\n")

    embed.description = discord.utils.escape_markdown(ctx.message.content)
    embed.add_field(name = "Author:", value = f"{ctx.author.mention}\n (`{ctx.author.id}`)")

    if ctx.guild:
        embed.add_field(name = "Channel:", value = f"{ctx.channel.mention}\n (`{ctx.channel.id}`)")
        embed.add_field(name = "Guild:", value = f"**{ctx.guild}**\n (`{ctx.guild.id}`)")
    else:
        embed.add_field(name = "Dm Channel:", value = f"<#{ctx.channel.id}>\n (`{ctx.channel.id}`)")
    
    embed.add_field(name = "Message ID:", value = f"`{ctx.message.id}`")
    embed.add_field(name = "\u200b", value = f"**[\U0001f517 Jump to Error]({ctx.message.jump_url})**")

    webhook = await bot.fetch_webhook(bot._config.get('errorlog'))
    await webhook.send(embed = embed)
    senderror = ""

    for line in tracederror: # To send the error as multiple messages if it's beyond 1900 charecters
        if len(senderror + line) < 1900:
            senderror += line

        else:
            await webhook.send("```py\n" + senderror + "```")
            senderror = ""
    
    if senderror:
        await webhook.send("```py\n" + senderror + "```")