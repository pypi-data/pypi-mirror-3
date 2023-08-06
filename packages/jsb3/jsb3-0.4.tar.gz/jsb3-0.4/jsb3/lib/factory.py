# jsb/lib/factory.py
#
#

""" Factory to produce instances of classes. """

## jsb imports

from jsb3.utils.exception import handle_exception
from jsb3.lib.errors import NoSuchBotType, NoUserProvided

## basic imports

import logging

## Factory base class

class Factory(object):
     pass

## BotFactory class

class BotFactory(Factory):

    def create(self, type=None, cfg={}):
        try: type = cfg['type'] or type or None
        except KeyError: pass
        try:
            if 'xmpp' in type:
                try:
                    import waveapi
                    from jsb3.drivers.gae.xmpp.bot import XMPPBot
                    bot = XMPPBot(cfg)
                except ImportError:   
                    from jsb3.drivers.xmpp.bot import SXMPPBot
                    bot = SXMPPBot(cfg)
            elif type == 'web':
                from jsb3.drivers.gae.web.bot import WebBot
                bot = WebBot(cfg)
            elif type == 'wave': 
                from jsb3.drivers.gae.wave.bot import WaveBot
                bot = WaveBot(cfg, domain=cfg.domain)
            elif type == 'irc':
                from jsb3.drivers.irc.bot import IRCBot
                bot = IRCBot(cfg)
            elif type == 'console':
                from jsb3.drivers.console.bot import ConsoleBot
                bot = ConsoleBot(cfg)
            elif type == 'base':
                from jsb3.lib.botbase import BotBase
                bot = BotBase(cfg)
            elif type == 'convore':
                from jsb3.drivers.convore.bot import ConvoreBot
                bot = ConvoreBot(cfg)
            elif type == 'tornado':
                from jsb3.drivers.tornado.bot import TornadoBot
                bot = TornadoBot(cfg)
            elif type == 'sleek':
                from jsb3.drivers.sleek.bot import SleekBot
                bot = SleekBot(cfg)
            else: raise NoSuchBotType('%s bot .. unproper type %s' % (type, cfg.dump()))
            return bot
        except NoUserProvided as ex: logging.info("%s - %s" % (cfg.name, str(ex)))
        except AssertionError as ex: logging.warn("%s - assertion error: %s" % (cfg.name, str(ex)))
        except Exception as ex: handle_exception()

bot_factory = BotFactory()
