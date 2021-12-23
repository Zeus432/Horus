from bot import Horus
from .blacklists import Blacklists

def setup(bot: Horus):
    bot.add_cog(Blacklists(bot))