from bot import Horus
from .admin import Admin

def setup(bot: Horus):
    bot.add_cog(Admin(bot))