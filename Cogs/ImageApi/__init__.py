from bot import Horus
from .imageapi import ImageApi

def setup(bot: Horus):
    bot.add_cog(ImageApi(bot))