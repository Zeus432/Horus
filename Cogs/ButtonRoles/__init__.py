from bot import Horus
from .buttonroles import ButtonRoles

def setup(bot: Horus):
    bot.add_cog(ButtonRoles(bot))