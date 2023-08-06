# jsb/plugs/core/count.py
#
#

""" count number of items in result queue. """

## jsb imports

from jsb3.lib.commands import cmnds
from jsb3.utils.generic import waitforqueue
from jsb3.lib.examples import examples

## basic imports

import time

## count command

def handle_count(bot, ievent):
    """ no arguments - show nr of elements in result list .. use this command in a pipeline. """
    #if ievent.prev: ievent.prev.wait()
    a = ievent.inqueue
    size = len(a)
    ievent.reply(size)

cmnds.add('count', handle_count, ['OPER', 'USER', 'GUEST'])
examples.add('count', 'count nr of items', 'list ! count')
