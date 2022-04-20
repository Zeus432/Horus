import disnake
from disnake.ext import commands

from loguru import logger
import traceback

async def send_error(bot: commands.Bot, ctx: commands.Context | disnake.MessageInteraction, error):
    """ Properly send error to error channel and log it in the error logs """
    embed = disnake.Embed(title = "Command Error!", description = f"This error has been forwarded to the bot developer and will be fixed soon.\nIn the meanwhile please refrain from trying to recreate this error unnecessarily.\n\n```py\n{error}```", colour = disnake.Colour(0x2F3136))
    embed.set_footer(text = "Spamming errored commands will get you blacklisted!", icon_url = ctx.author.avatar or ctx.author.default_avatar)

    if isinstance(ctx, disnake.MessageInteraction):
        await ctx.response.send_message(embed = embed, ephemeral = True)
    else:
        await ctx.reply(embed = embed, mention_author = False)

    # Log in Error Logs
    traceback_error = traceback.format_exception(type(error), error, error.__traceback__)
    logger.opt(exception = error).error(f"Ignoring exception in command {ctx.command}\nCommand Used - {ctx.message.content}\n")

    # Now Log in Error Channel
    embed.description = f"{ctx.message.content}"

    embed.add_field(name = "Author:", value = f"{ctx.author.mention}\n (`{ctx.author.id}`)")
    if ctx.guild:
        embed.add_field(name = "Channel:", value = f"{ctx.channel.mention}\n (`{ctx.channel.id}`)")
        embed.add_field(name = "Guild:", value = f"**{ctx.guild}**\n (`{ctx.guild.id}`)")
    else:
        embed.add_field(name = "Dm Channel:", value = f"<#{ctx.channel.id}>\n (`{ctx.channel.id}`)")
    embed.add_field(name = "Message ID:", value = f"`{ctx.message.id}`")
    embed.add_field(name = "\u200b", value = f"**[\U0001f517 Jump to Error]({ctx.message.jump_url})**")

    # Split Error if it's longer than 1900k Charecter to fit discord limits
    split_error, final_error = "", []
    for line in traceback_error:
        if len(split_error + line) < 1900:
            split_error += f"\n{line}"

        else:
            final_error.append(split_error)
            split_error = ""

    final_error.append(split_error)

    error_channel = bot.get_channel(bot._config["errorchannel"])
    await error_channel.send(embed = embed)

    for e in final_error:
        await error_channel.send(f"```py\n{e}```")