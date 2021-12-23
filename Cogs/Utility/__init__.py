from bot import Horus
from .utility import Utility

def setup(bot: Horus):
    bot.add_cog(Utility(bot))