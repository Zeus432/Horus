from discord.ext import commands

class BlType(commands.Converter):
    async def convert(self, ctx: commands.Context, argument) -> str | None:
        if argument in ["channel", "channels", "chan"]:
            return "channel"

        elif argument in ["users", "user"]:
            return "user"
        
        elif argument in ["role", "roles"]:
            return "role"
        
        return None