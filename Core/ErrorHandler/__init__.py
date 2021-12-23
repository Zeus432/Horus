from bot import Horus
from .errorhandler import ErrorHandler

def setup(bot: Horus):
    bot.add_cog(ErrorHandler(bot))