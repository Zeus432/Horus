from discord.ext import commands
import discord

class BlType(commands.Converter):
    async def convert(self, ctx: commands.Context, argument) -> str | None:
        if argument in ["channel", "channels", "chan"]:
            return "channel"

        elif argument in ["users", "user"]:
            return "user"
        
        elif argument in ["role", "roles"]:
            return "role"
        
        return None

def format_items(category: str, items: list):
    start = "<@!" if category == "user" else "<#" if category == "channel" else "<@&"

    for item in items:
        print()