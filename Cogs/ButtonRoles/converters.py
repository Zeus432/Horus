import emojis
from disnake.ext import commands

class EmojiConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            emoji = await commands.EmojiConverter().convert(ctx, argument)

        except commands.EmojiNotFound:
            emoji = emojis.db.get_emoji_by_code(argument)
            if not emoji:
                raise commands.EmojiNotFound(argument)
            return emoji.emoji

        else:
            return emoji