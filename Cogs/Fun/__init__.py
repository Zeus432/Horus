from bot import Horus
from .fun import Fun

def setup(bot: Horus):
    bot.add_cog(Fun(bot))