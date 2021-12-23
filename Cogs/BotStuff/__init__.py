from bot import Horus
from .botstuff import BotStuff

def setup(bot: Horus):
    bot.add_cog(BotStuff(bot))