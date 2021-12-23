from bot import Horus
from .listeners import Listeners

def setup(bot: Horus):
    bot.add_cog(Listeners(bot))