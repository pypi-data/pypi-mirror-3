# jsb/exit.py
#
#

""" jsb's finaliser """

## jsb imports

from jsb3.utils.locking import globallocked
from jsb3.utils.exception import handle_exception
from jsb3.utils.trace import whichmodule
from jsb3.memcached import killmcdaemon
from jsb3.lib.persist import cleanup
from .runner import defaultrunner, cmndrunner, callbackrunner, waitrunner

## basic imports

import atexit
import os
import time
import sys
import logging

## functions

@globallocked
def globalshutdown(exit=True):
    """ shutdown the bot. """
    try:
        try: sys.stdout.write("\n")
        except: pass
        logging.error('shutting down'.upper())
        from .fleet import getfleet
        fleet = getfleet()
        if fleet:
            logging.warn('shutting down fleet')
            fleet.exit()
        logging.warn('shutting down plugins')
        from jsb3.lib.plugins import plugs
        plugs.exit()
        logging.warn("shutting down runners")
        cmndrunner.stop()
        callbackrunner.stop()
        waitrunner.stop()
        logging.warn("cleaning up any open files")
        while cleanup(): time.sleep(1)
        try: os.remove('jsb3.pid')
        except: pass
        killmcdaemon()
        logging.warn('done')
        print("")
        if exit: os._exit(0)
    except Exception as ex:
        print(str(ex))
        if exit: os._exit(1)
