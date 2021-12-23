from bot import Horus
from .dev import Dev

def setup(bot: Horus):
    bot.add_cog(Dev(bot))