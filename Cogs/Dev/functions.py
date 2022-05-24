import discord
from Core.bot import HorusCtx
from discord.ext import commands

def get_reply(ctx: HorusCtx) -> discord.Message | discord.DeletedReferencedMessage | None:
    """ Returns the reference to message of given ctx or None """
    if ctx.message.reference:
        return ctx.message.reference.resolved
    return None

def cleanup_code(content: str) -> str:
    """Automatically removes code blocks from the code."""
    if content.startswith('```') and content.endswith('```'):
        num = 6 if content.startswith('```py\n') else (4 if content.startswith('```\n') else 3)
        return content[num:-3]
    else: return content