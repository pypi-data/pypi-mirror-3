# jsb/imports.py
#
#

""" provide a import wrappers for the contrib packages. """

## lib imports

from jsb3.lib.jsbimport import myimport

## basic imports

import logging

## getjson function

def getjson():
    mod = myimport("json")
    logging.debug("json module is %s" % str(mod))
    return mod

## getfeedparser function

def getfeedparser():
    try: mod = myimport("feedparser")
    except: mod = myimport("jsb3.contrib.feedparser")
    logging.info("feedparser module is %s" % str(mod))
    return mod

def getoauth():
    try: mod = myimport("oauth")
    except:
        mod = myimport("jsb3.contrib.oauth")
    logging.info("oauth module is %s" % str(mod))
    return mod

def getrequests():
    try: mod = myimport("requests")
    except: mod = None
    logging.info("requests module is %s" % str(mod))
    return mod

def gettornado():
    try: mod = myimport("tornado")
    except: mod = _import("jsb3.contrib.tornado")
    logging.info("tornado module is %s" % str(mod))
    return mod

def getBeautifulSoup():
    try: mod = myimport("BeautifulSoup")
    except: mod = myimport("jsb3.contrib.BeautifulSoup")
    logging.info("BeautifulSoup module is %s" % str(mod))
    return mod

def getsleek():
    try: mod = myimport("sleekxmpp")
    except: mod = myimport("jsb3.contrib.sleekxmpp")
    logging.info("sleek module is %s" % str(mod))
    return mod
