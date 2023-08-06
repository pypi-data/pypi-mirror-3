#!/usr/bin/env python3
#
#

target = "jsb3" # BHJTW change this to /var/cache/jsb on debian

import os

try: from setuptools import setup
except: print("i need setuptools to properly install JSB3") ; os._exit(1)

upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir): print("%s does not exist" % dir) ; os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc"):
                continue
            upl.append(d)

    return upl

setup(
    name='jsb3',
    version='0.4.1',
    url='http://jsb3.googlecode.com/',
    download_url="http://code.google.com/p/jsb3/downloads", 
    author='Bart Thate',
    author_email='bthate@gmail.com',
    description='JSONBOT 3 on Python 3',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/jsb3',
             'bin/jsb3-fleet',
             'bin/jsb3-irc',
             'bin/jsb3-sleek',
             'bin/jsb3-tornado',
            ],
    packages=['jsb3',
              'jsb3.db',
              'jsb3.drivers',
              'jsb3.drivers.console',
              'jsb3.drivers.irc',
              'jsb3.drivers.sleek',
              'jsb3.drivers.tornado',
              'jsb3.lib', 
              'jsb3.utils',
              'jsb3.plugs',
              'jsb3.plugs.db',
              'jsb3.plugs.core',
              'jsb3.plugs.extra',
              'jsb3.contrib',
              'jsb3.contrib.bs4',
              'jsb3.contrib.bs4.builder',
              'jsb3.contrib.tornado',
              'jsb3.contrib.tornado.platform',
              'jsb3/contrib/sleekxmpp',
              'jsb3/contrib/sleekxmpp/stanza',   
              'jsb3/contrib/sleekxmpp/test',     
              'jsb3/contrib/sleekxmpp/roster',   
              'jsb3/contrib/sleekxmpp/xmlstream',
              'jsb3/contrib/sleekxmpp/xmlstream/matcher',
              'jsb3/contrib/sleekxmpp/xmlstream/handler',
              'jsb3/contrib/sleekxmpp/plugins',
              'jsb3/contrib/sleekxmpp/plugins/xep_0004',
              'jsb3/contrib/sleekxmpp/plugins/xep_0004/stanza',
              'jsb3/contrib/sleekxmpp/plugins/xep_0009',
              'jsb3/contrib/sleekxmpp/plugins/xep_0009/stanza',
              'jsb3/contrib/sleekxmpp/plugins/xep_0030',
              'jsb3/contrib/sleekxmpp/plugins/xep_0030/stanza',
              'jsb3/contrib/sleekxmpp/plugins/xep_0050',
              'jsb3/contrib/sleekxmpp/plugins/xep_0059',
              'jsb3/contrib/sleekxmpp/plugins/xep_0060',
              'jsb3/contrib/sleekxmpp/plugins/xep_0060/stanza',
              'jsb3/contrib/sleekxmpp/plugins/xep_0066',
              'jsb3/contrib/sleekxmpp/plugins/xep_0078',
              'jsb3/contrib/sleekxmpp/plugins/xep_0085',
              'jsb3/contrib/sleekxmpp/plugins/xep_0086',
              'jsb3/contrib/sleekxmpp/plugins/xep_0092',
              'jsb3/contrib/sleekxmpp/plugins/xep_0128',
              'jsb3/contrib/sleekxmpp/plugins/xep_0199',
              'jsb3/contrib/sleekxmpp/plugins/xep_0202',
              'jsb3/contrib/sleekxmpp/plugins/xep_0203',
              'jsb3/contrib/sleekxmpp/plugins/xep_0224',
              'jsb3/contrib/sleekxmpp/plugins/xep_0249',
              'jsb3/contrib/sleekxmpp/features',
              'jsb3/contrib/sleekxmpp/features/feature_mechanisms',
              'jsb3/contrib/sleekxmpp/features/feature_mechanisms/stanza',
              'jsb3/contrib/sleekxmpp/features/feature_starttls',
              'jsb3/contrib/sleekxmpp/features/feature_bind',   
              'jsb3/contrib/sleekxmpp/features/feature_session',
              'jsb3/contrib/sleekxmpp/thirdparty',
              'jsb3/contrib/sleekxmpp/thirdparty/suelta',
              'jsb3/contrib/sleekxmpp/thirdparty/suelta/mechanisms',
           ],
    long_description = """ To get it right ;] """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
