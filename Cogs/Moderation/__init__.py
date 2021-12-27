from bot import Horus
from .moderation import Moderation

def setup(bot: Horus):
    bot.add_cog(Moderation(bot))