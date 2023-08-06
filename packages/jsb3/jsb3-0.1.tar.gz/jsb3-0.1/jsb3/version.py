# jsb/version.py
#
#

""" version related stuff. """

## jsb imports

from jsb3.lib.config import getmainconfig

## basic imports

import os
import binascii

## defines

version = "0.1"

## getversion function

def getversion(txt=""):
    """ return a version string. """
    return "JSONBOT 3 version %s DEVELOPMENT %s" % (version, txt)
