from bot import Horus
from .sniper import Sniper

def setup(bot: Horus):
    bot.add_cog(Sniper(bot))