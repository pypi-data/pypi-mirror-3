# jsb/utils/source.py
#
#

""" get the location of a source """

## basic imports

import os
import logging
import sys

## getsource function

def getsource(mod):
    splitted = mod.split(".")
    if True:
        try:
            import pkg_resources
            source = pkg_resources.resource_filename(".".join(splitted[:len(splitted)-1]), splitted[-1])
        except ImportError:
            try:
                import jsb3.contrib.pkg_resources as pkg_resources
                source = pkg_resources.resource_filename(".".join(splitted[:len(splitted)-1]), splitted[-1])
            except ImportError: pass
    logging.warn("datadir - source is %s" % source)
    return source
